from __future__ import annotations

import logging

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL, SEMANTIC_TOP_K
from app.models.schemas import PlayerRecord

logger = logging.getLogger(__name__)

class SemanticSearcher:
    def __init__(self, faiss_index_path: str, players: list[PlayerRecord]):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = faiss.read_index(str(faiss_index_path))
        # Important: Assumes players list is in the exact order as added to the FAISS index.
        self.players = players

    def search(self, query: str, top_k: int = SEMANTIC_TOP_K) -> tuple[list[PlayerRecord], list[float]]:
        query_emb = self.model.encode([query], normalize_embeddings=True)
        query_emb = np.array(query_emb, dtype=np.float32)

        distances, indices = self.index.search(query_emb, top_k)
        
        candidates = []
        scores = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.players):
                candidates.append(self.players[idx])
                scores.append(float(dist))
                
        return candidates, scores
