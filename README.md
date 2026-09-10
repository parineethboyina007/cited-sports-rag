Here is the **entire `README.md`**, clean and copy-paste ready:

```markdown
# Cited Sports Encyclopedia

A Retrieval-Augmented Generation (RAG) application that answers sports-related questions using information from provided datasets while ensuring grounded responses, inline citations, and safe handling of unsupported queries.

---

## Overview

**Cited Sports Encyclopedia** is a multi-document Retrieval-Augmented Generation (RAG) system designed to answer questions about sports players using structured datasets.

The system currently works with two datasets:

- World Cricketers
- Indian Olympic Players

Instead of allowing the language model to answer questions solely from its pretrained knowledge, the application first retrieves relevant information from the provided datasets and then generates an answer based only on the retrieved content.

This approach helps reduce hallucinations and ensures that generated responses are traceable to their source data.

---

## Features

- Hybrid Retrieval using RapidFuzz and semantic search
- Local FAISS Vector Database
- Sentence Transformer Embeddings
- Multi-Document RAG
- Inline Source Citations
- Fuzzy Name Matching
- Citation Verification
- Out-of-Scope Refusal
- Wrong Attribution Prevention
- Top-K Document Retrieval
- FastAPI Backend
- React + Vite Frontend
- Local Vector Index Generation

---

## Architecture

```text
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

## How It Works

The application follows a Retrieval-Augmented Generation pipeline.

### 1. User Query

The user enters a question through the React frontend.

Example:

```text
Who is Don Bradman?
```

### 2. Entity Matching

The system identifies player names in the query using RapidFuzz fuzzy matching.

This allows the system to handle minor spelling mistakes and variations in player names.

For example:

```text
Don Brandon
```

can be matched with:

```text
Don Bradman
```

when the similarity is sufficiently high.

### 3. Semantic Retrieval

The query is converted into an embedding using a Sentence Transformer model.

The resulting vector is searched against the locally stored FAISS index.

### 4. Hybrid Retrieval

The system combines:

- Fuzzy entity matching
- Semantic similarity search

to identify the most relevant player profiles.

### 5. Top-K Retrieval

The most relevant documents are selected and passed to the generation layer.

### 6. Prompt Construction

The retrieved player information is inserted into the prompt given to the language model.

The model is instructed to answer using only the retrieved information.

### 7. LLM Generation

The Groq API is used to generate the final natural-language response.

### 8. Citation Verification

Generated citations are checked against the retrieved source documents before the response is returned.

This helps prevent incorrect or unsupported citations.

---

## Datasets

The application currently uses two datasets.

### World Cricketers

Contains profiles and information about international cricketers.

Example players include:

- Don Bradman
- Glenn McGrath
- Shane Warne
- Steve Waugh
- Sachin Tendulkar

### Indian Olympic Players

Contains profiles and information about Indian Olympic athletes.

Example:

- Neeraj Chopra

The system is designed so additional datasets can be incorporated into the ingestion pipeline.

---

## Example Queries

### Standard Retrieval

**Input:**

```text
Who is Don Bradman?
```

**Expected Output:**

```text
Don Bradman is an Australian cricketer widely regarded as the greatest batsman in cricket history with a Test average of 99.94. [CRI-001]
```

---

### Fuzzy Entity Matching

**Input:**

```text
Who is Don Brandon?
```

**Expected Output:**

```text
There is no player named "Don Brandon" in the dataset.

The closest matching player is Don Bradman. [CRI-001]
```

This demonstrates the system's ability to handle approximate or misspelled player names.

---

### Multi-Document Comparison

**Input:**

```text
Compare Glenn McGrath and Shane Warne.
```

**Expected Output:**

```text
Both Glenn McGrath and Shane Warne represented Australia.

Glenn McGrath was a right-arm fast-medium bowler with 563 Test wickets. [CRI-005]

Shane Warne was a legendary leg-spinner with 708 Test wickets. [CRI-002]
```

The response uses information retrieved for both players and provides separate citations.

---

### Cross-Dataset Retrieval

**Input:**

```text
Who is Neeraj Chopra?
```

**Expected Output:**

```text
Neeraj Chopra is an Indian javelin throw athlete and Olympic gold medalist. [OLY-001]
```

This demonstrates retrieval from the Indian Olympic Players dataset.

---

### Unsupported Attribute

**Input:**

```text
How many Test wickets did Don Bradman take?
```

If the dataset does not contain the requested information, the system should not invent an answer.

**Expected Output:**

```text
The provided datasets do not contain enough information to answer this question.
```

---

### Out-of-Scope Query

**Input:**

```text
Who is Lionel Messi?
```

If Lionel Messi is not present in the provided datasets, the system refuses to provide unsupported information.

**Expected Output:**

```text
The provided datasets do not contain enough information to answer this question.
```

---

## Grounding and Hallucination Prevention

A major objective of the application is to ensure that responses are grounded in the provided datasets.

The language model is not treated as the primary source of factual information.

Instead, the system follows this pipeline:

```text
User Query
     │
     ▼
Dataset Retrieval
     │
     ▼
Relevant Player Profiles
     │
     ▼
LLM Generation
     │
     ▼
Citation Verification
     │
     ▼
Grounded Response
```

If the required information cannot be found in the retrieved documents, the system is designed to refuse the query rather than generate unsupported information.

---

## Citation System

Each dataset entry is assigned a unique citation identifier.

Examples:

```text
[CRI-001]
[CRI-002]
[CRI-005]
[OLY-001]
```

Cricket records use the:

```text
CRI-XXX
```

format.

Olympic player records use the:

```text
OLY-XXX
```

format.

Citations are included directly within generated responses so users can identify which retrieved record supports the answer.

---

## Retrieval Pipeline

The retrieval system combines multiple techniques.

### RapidFuzz

RapidFuzz is used for approximate string matching.

This is particularly useful for:

- Misspelled player names
- Minor variations in names
- Fuzzy entity matching

Example:

```text
Don Brandon
      │
      ▼
Fuzzy Matching
      │
      ▼
Don Bradman
```

---

### Sentence Transformers

Sentence Transformer models are used to convert player profiles and queries into numerical embeddings.

These embeddings allow the system to perform semantic similarity search.

For example, a query such as:

```text
Who was this Australian fast bowler?
```

can retrieve relevant profiles even when the exact wording does not appear in the dataset.

---

### FAISS

FAISS (Facebook AI Similarity Search) is used as the local vector search engine.

The application stores document embeddings in a FAISS index and performs similarity searches against user queries.

The vector database runs locally rather than requiring a hosted vector database service.

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite

### Backend

- Python
- FastAPI

### Retrieval

- RapidFuzz
- Sentence Transformers
- FAISS

### LLM

- Groq API

### Data Processing

- Python
- Excel datasets

---

## Project Structure

```text
backend/
│
├── app/
│   ├── generation/
│   ├── ingestion/
│   ├── llm/
│   ├── models/
│   ├── retrieval/
│   └── verification/
│
├── data/
│   └── raw/
│       ├── World_Cricketers.xlsx
│       └── Indian_Olympic_Players.xlsx
│
└── tests/
    └── test_acceptance_suite.py
│
frontend/
│
└── ...
│
docs/
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/parineethboyina007/16_BruteForceSquad.git

cd 16_BruteForceSquad
```

---

## 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Create a file:

```text
backend/.env
```

Add your Groq API key:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Replace `YOUR_GROQ_API_KEY` with your actual Groq API key.

The `.env` file should not be committed to the repository.

---

## 4. Generate the Vector Database

The project uses a local FAISS vector database.

First validate the datasets:

```bash
python -m app.ingestion.load_datasets --validate
```

Then generate the vector index:

```bash
python -m app.ingestion.build_index --verify-collisions
```

This generates the required retrieval artifacts, including:

- Player registry
- Embeddings
- FAISS vector index
- Collision index

---

## 5. Run the Backend

From the `backend` directory:

### Linux / macOS

```bash
export PYTHONPATH=.

uvicorn app.main:app --reload
```

### Windows PowerShell

```powershell
$env:PYTHONPATH="."

uvicorn app.main:app --reload
```

The FastAPI server will start locally.

---

## 6. Run the Frontend

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend can then be accessed through the local development URL provided by Vite.

---

## Running Tests

Navigate to the backend:

```bash
cd backend
```

Set the Python path.

### Linux / macOS

```bash
export PYTHONPATH=.
```

### Windows PowerShell

```powershell
$env:PYTHONPATH="."
```

Run the test suite:

```bash
pytest tests/test_acceptance_suite.py -v
```

---

## Test Cases

The following queries can be used to test the system:

```text
Who is Don Bradman?

Who is Don Brandon?

Tell me about Glenn McGrath.

Who is Steve Waugh?

Who is Shane Warne?

Tell me about Sachin Tendulkar.

Compare Glenn McGrath and Shane Warne.

Compare Don Bradman and Steve Waugh.

Compare Don Bradman and Neeraj Chopra.

Who is Neeraj Chopra?

Who is Lionel Messi?

How many Test wickets did Don Bradman take?
```

These test cases cover:

- Standard retrieval
- Semantic search
- Fuzzy name matching
- Multi-document retrieval
- Cross-dataset retrieval
- Inline citations
- Citation verification
- Unsupported attributes
- Out-of-scope queries
- Hallucination prevention

---

## Optimization Techniques

### Hybrid Retrieval

Combines lexical/fuzzy matching with semantic vector search to improve retrieval accuracy.

### Fuzzy Name Matching

Allows the system to identify players even when the query contains minor spelling errors.

### Sentence Transformer Embeddings

Provides semantic representations of queries and player profiles.

### Local FAISS Index

Enables fast similarity search without requiring a hosted vector database.

### Top-K Retrieval

Limits the context supplied to the LLM to the most relevant documents.

### Prompt Engineering

Constrains the LLM to use retrieved information when generating answers.

### Multi-Document Retrieval

Allows questions involving multiple players to retrieve multiple relevant profiles.

### Citation Verification

Validates citations generated in the response against retrieved documents.

### Out-of-Scope Refusal

Prevents the system from answering questions when the required information is not available in the datasets.

---

## Local Vector Database

The project uses **FAISS** as its local vector database.

The repository contains the source datasets and scripts required to regenerate the index.

To rebuild the index:

```bash
python -m app.ingestion.build_index --verify-collisions
```

This allows the vector database to be regenerated whenever the source datasets are modified.

---

## API Key

The application requires a Groq API key for LLM generation.

Create:

```text
backend/.env
```

and add:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Never commit the `.env` file or expose your API key publicly.

---

## Design Principles

The application is built around four main principles.

### 1. Grounded Generation

Answers should be based on retrieved dataset information rather than unsupported model knowledge.

### 2. Traceability

Generated claims should be accompanied by citations pointing to the relevant source records.

### 3. Safe Refusal

The system should refuse questions when the requested information is unavailable in the datasets.

### 4. Robust Retrieval

The retrieval layer should handle both exact and approximate player-name queries.

---

## Future Improvements

Potential extensions include:

- Adding more sports datasets
- Supporting additional player statistics
- Improving entity resolution
- Adding metadata-based filtering
- Supporting more advanced comparison queries
- Adding conversational history
- Improving citation visualization
- Supporting additional embedding models
- Adding evaluation metrics for retrieval accuracy
- Adding automated hallucination detection
- Supporting additional sports such as football, tennis, basketball, athletics, and hockey

---

## License

This project is developed for educational and research purposes.
```
