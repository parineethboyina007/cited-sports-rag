# Cited Sports Encyclopedia - Architecture

This system uses a pattern called **Entity-Grounded Adaptive RAG**. It combines four specific RAG patterns to satisfy all problem statement requirements.

## 1. Adaptive RAG -> Route by answer-generation strategy
- **Component**: `backend/app/generation/answer_generator.py` (Route Decision Gate)
- **Role**: Simple, single-entity, direct-field lookups skip the LLM entirely and use a deterministic template renderer (`template_answers.py`). Complex or comparative queries go to the full generative pathway. This provides a zero-hallucination surface for basic factual lookups.

## 2. Hybrid RAG -> Multi-document exact/fuzzy name matching fused with semantic search
- **Component**: `backend/app/retrieval/hybrid_retriever.py`
- **Role**: Fuses lexical exact/fuzzy entity matching (`entity_matcher.py`, which is aware of collision groups like "Kumar") with vector search (`semantic_search.py` via FAISS). This allows exact name matches (Neeraj Chopra) and semantic matching (elegant Sri Lankan wicketkeeper) to work seamlessly.

## 3. Corrective RAG -> Relevance Gate / Refusal
- **Component**: `backend/app/retrieval/relevance_gate.py`
- **Role**: Sits between retrieval and generation to decide whether to refuse. If no candidate scores above a threshold, or if the user asks for a field not present in the canonical dataset (like "net worth"), this gate triggers a clean refusal before the LLM can hallucinate.

## 4. Self-RAG -> Anti-misattribution & citation checking
- **Component**: `backend/app/verification/citation_verifier.py`
- **Role**: A post-generation deterministic critique module. It parses every `[CRI-001]` tag out of the LLM's draft and checks: (a) was the tagged entity actually the subject of the sentence? (b) are the claimed facts (numbers/years/achievements) actually present in the source row? If it fails, one bounded repair attempt is made; if it still fails, it falls back to the deterministic template or refuses.
