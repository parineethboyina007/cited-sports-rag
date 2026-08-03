# Cited Sports Encyclopedia (PS-5)

A Retrieval-Augmented Generation (RAG) application that answers sports-related questions using only the provided datasets while ensuring grounded responses, inline citations, and safe handling of unsupported queries.

---

# Submission Details

## Team Name
BruteForceSquad

## Team Number
16

## Problem Statement
**PS-5: Cited Sports Encyclopedia**

## GitHub Repository
https://github.com/parineethboyina007/16_BruteForceSquad

## Demo Video


---

# Project Overview

This project implements a **Multi-Document Retrieval-Augmented Generation (RAG)** pipeline over two datasets:

- World Cricketers
- Indian Olympic Players

The assistant retrieves relevant player profiles before generating answers, ensuring every response is grounded in the provided datasets and supported by inline citations.

---

# Features

- Hybrid Retrieval (RapidFuzz + Semantic Search)
- Local FAISS Vector Database
- Sentence Transformer Embeddings
- Multi-document RAG
- Inline Source Citations
- Fuzzy Name Matching
- Citation Verification
- Out-of-Scope Refusal
- Wrong Attribution Prevention
- FastAPI Backend
- React + Vite Frontend

---

# Architecture

```
                User Query
                     │
                     ▼
           React Frontend
                     │
                     ▼
             FastAPI Backend
                     │
                     ▼
        RapidFuzz Entity Matching
                     │
                     ▼
   Sentence Transformer Embeddings
                     │
                     ▼
        FAISS Vector Database
                     │
                     ▼
         Hybrid Retrieval Engine
                     │
                     ▼
         Top-K Player Retrieval
                     │
                     ▼
            Prompt Construction
                     │
                     ▼
              Groq LLM
                     │
                     ▼
         Citation Verification
                     │
                     ▼
         Final Answer + Citations
```
---

# Test Prompts & Expected Behavior

The following prompts can be used to verify the application's functionality.

| Prompt | Expected Behavior |
|---------|-------------------|
| `Who is Don Bradman?` | Retrieves Don Bradman's profile with inline citation **[CRI-001]**. |
| `Tell me about Glenn McGrath.` | Retrieves Glenn McGrath's profile with citations. |
| `Who is Steve Waugh?` | Retrieves Steve Waugh's profile with citations. |
| `Who is Shane Warne?` | Retrieves Shane Warne's profile with citations. |
| `Who is Sachin Tendulkar?` | Retrieves Sachin Tendulkar's profile with citations. |
| `Who is Neeraj Chopra?` | Retrieves Neeraj Chopra's profile from the Olympic dataset with citations. |
| `Who is Don Brandon?` | Demonstrates fuzzy entity matching by correctly retrieving **Don Bradman**. |
| `Compare Glenn McGrath and Shane Warne.` | Retrieves both player profiles and generates a grounded comparison with citations for each player. |
| `Compare Don Bradman and Steve Waugh.` | Demonstrates multi-document retrieval and comparison using the cricket dataset. |
| `Compare Don Bradman and Neeraj Chopra.` | Demonstrates retrieval across two datasets and generates a comparison using retrieved information only. |
| `How many Test wickets did Don Bradman take?` | Gracefully reports that the requested attribute is unavailable instead of hallucinating. |
| `Who is Lionel Messi?` | Refuses the query because the player is not present in the provided datasets. |

---

# Example Outputs

## Example 1 – Standard Retrieval

**Input**

```text
Who is Don Bradman?
```

**Expected Output**

```text
Don Bradman is an Australian cricketer widely regarded as the greatest batsman in cricket history with a Test average of 99.94. [CRI-001]
```

---

## Example 2 – Fuzzy Entity Matching

**Input**

```text
Who is Don Brandon?
```

**Expected Output**

```text
There is no player named "Don Brandon" in the dataset.

The closest matching player is Don Bradman. [CRI-001]
```

---

## Example 3 – Multi-Document Comparison

**Input**

```text
Compare Glenn McGrath and Shane Warne.
```

**Expected Output**

```text
Both Glenn McGrath and Shane Warne represented Australia.

Glenn McGrath was a right-arm fast-medium bowler with 563 Test wickets. [CRI-005]

Shane Warne was a legendary leg-spinner with 708 Test wickets. [CRI-002]
```

---

## Example 4 – Cross Dataset Retrieval

**Input**

```text
Who is Neeraj Chopra?
```

**Expected Output**

```text
Neeraj Chopra is an Indian javelin throw athlete and Olympic gold medalist. [OLY-001]
```

---

## Example 5 – Unsupported Attribute

**Input**

```text
How many Test wickets did Don Bradman take?
```

**Expected Output**

```text
The provided datasets do not contain enough information to answer this question.
```

---

## Example 6 – Out-of-Scope Query

**Input**

```text
Who is Lionel Messi?
```

**Expected Output**

```text
The provided datasets do not contain enough information to answer this question.
```

---

# What These Tests Demonstrate

- ✅ Standard Retrieval
- ✅ Semantic Search
- ✅ RapidFuzz Fuzzy Matching
- ✅ Multi-Document Retrieval
- ✅ Cross-Dataset Retrieval
- ✅ Inline Citations
- ✅ Grounded Responses
- ✅ No Hallucinations
- ✅ Out-of-Scope Refusal
---

# Tech Stack

## Frontend

- React
- TypeScript
- Vite

## Backend

- Python
- FastAPI

## Retrieval

- RapidFuzz
- Sentence Transformers
- FAISS

## LLM

- Groq API

---

# Project Structure

```
backend/
    app/
        generation/
        ingestion/
        llm/
        models/
        retrieval/
        verification/

    data/
        raw/
            World_Cricketers.xlsx
            Indian_Olympic_Players.xlsx

frontend/

docs/
```

---

# Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/parineethboyina007/16_BruteForceSquad.git

cd 16_BruteForceSquad
```

---

## 2. Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Create a file named

```
backend/.env
```

Add:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

---

## 4. Generate the Local Vector Database

The project uses a **local FAISS vector database**.

Run:

```bash
python -m app.ingestion.load_datasets --validate

python -m app.ingestion.build_index --verify-collisions
```

This generates:

- Player registry
- Embeddings
- FAISS vector index
- Collision index

---

## 5. Run Backend

```bash
cd backend

export PYTHONPATH=.

uvicorn app.main:app --reload
```

---

## 6. Run Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Running Tests

```bash
cd backend

export PYTHONPATH=.

pytest tests/test_acceptance_suite.py -v
```

---

# Sample Questions

```
Who is Don Bradman?

Who is Don Brandon?

Tell me about Glenn McGrath.

Compare Glenn McGrath and Shane Warne.

Who is Neeraj Chopra?

Tell me about Sachin Tendulkar.

Who is Lionel Messi?

How many Test wickets did Don Bradman take?
```

---

# Optimization Techniques

- Hybrid Retrieval
- RapidFuzz Fuzzy Matching
- Sentence Transformer Embeddings
- Local FAISS Vector Database
- Top-K Retrieval
- Prompt Engineering
- Multi-document Retrieval
- Citation Verification
- Out-of-Scope Refusal

---

# Local Vector Database

This project uses **FAISS** as a local vector database.

The repository includes:

- Source datasets
- Index generation scripts

The FAISS index can be regenerated locally using:

```bash
python -m app.ingestion.build_index --verify-collisions
```

---

# API Keys

This project requires a Groq API key.

Create:

```
backend/.env
```

Example:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

---

# License

This project was developed for educational purposes as part of the PS-5 RAG assignment.