from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Fix path to allow importing app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.schemas import QueryRequest, QueryResponse, PlayerSummary
from app.ingestion.load_datasets import load_players_from_json
from app.ingestion.build_index import load_collision_index
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.relevance_gate import RelevanceGate
from app.generation.answer_generator import AnswerGenerator
from app.verification.citation_verifier import CitationVerifier
from app.llm.client import GroqClient
import faiss
from app.config import FAISS_INDEX_FILE

# Global state
players = []
collision_index = {}
hybrid_retriever = None
llm_client = None
answer_generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global players, collision_index, hybrid_retriever, llm_client, answer_generator
    players = load_players_from_json()
    collision_index = load_collision_index()
    
    # Load FAISS
    import faiss
    import numpy as np
    index = faiss.read_index(str(FAISS_INDEX_FILE))
    
    # Reattach embeddings to players for hybrid retriever
    # (assuming same order as faiss index)
    for i, p in enumerate(players):
        vec = np.zeros((1, index.d), dtype=np.float32)
        index.reconstruct(i, vec[0])
        p.embedding = vec[0].tolist()
        
    from app.retrieval.entity_matcher import EntityMatcher
    from app.retrieval.semantic_search import SemanticSearcher
    entity_matcher = EntityMatcher(players, collision_index)
    semantic_searcher = SemanticSearcher(str(FAISS_INDEX_FILE), players)
    hybrid_retriever = HybridRetriever(entity_matcher, semantic_searcher)
    try:
        llm_client = GroqClient()
        verifier = CitationVerifier(llm_client)
        answer_generator = AnswerGenerator(llm_client, verifier)
    except Exception as e:
        print(f"Warning: Failed to init GroqClient (missing key?): {e}")
        llm_client = None
        answer_generator = None

    yield
    # Cleanup


app = FastAPI(lifespan=lifespan, title="Cited Sports Encyclopedia API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "players_loaded": len(players)}

@app.get("/api/players", response_model=list[PlayerSummary])
def get_players():
    return [
        PlayerSummary(
            id=p.id,
            name=p.name,
            dataset=p.dataset,
            category=p.category,
            excel_row=p.excel_row,
            fields=p.fields,
            performances=p.performances
        ) for p in players
    ]

@app.get("/api/player/{player_id}")
def get_player(player_id: str):
    for p in players:
        if p.id == player_id:
            return p.model_dump(exclude={"embedding", "search_text"})
    raise HTTPException(status_code=404, detail="Player not found")

@app.post("/api/query", response_model=QueryResponse)
def query_api(req: QueryRequest):
    # 1. Retrieve
    retrieval_res = hybrid_retriever.retrieve(req.query)
    
    # 2. Relevance Gate (Corrective RAG)
    relevance_gate = RelevanceGate()
    gate_decision = relevance_gate.evaluate(req.query, retrieval_res)
    
    if gate_decision.should_refuse:
        return QueryResponse(
            answer=gate_decision.refusal_message,
            method="refusal",
            collision_detected=False
        )
        
    # 3. Generate (Adaptive + Self-RAG)
    verified_answer = answer_generator.generate_answer(
        query=req.query,
        gate_decision=gate_decision
    )
    
    return QueryResponse(
        answer=verified_answer.answer,
        citations=verified_answer.citations,
        source_cards=verified_answer.source_cards,
        method=verified_answer.method,
        collision_detected=retrieval_res.collision_detected,
        collision_tokens=retrieval_res.collision_tokens
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
