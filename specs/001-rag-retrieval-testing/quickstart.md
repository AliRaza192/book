# Quickstart: RAG Retrieval Testing

## Prerequisites
- Python 3.10+
- Access to Cohere API (API key in environment)
- Access to Qdrant vector database from Spec-1
- Pip package manager

## Setup
1. Install dependencies:
   ```bash
   pip install cohere qdrant-client python-dotenv pandas
   ```

2. Configure environment variables:
   ```bash
   # Create .env file with:
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_HOST=your_qdrant_host
   QDRANT_API_KEY=your_qdrant_api_key  # if required
   COLLECTION_NAME=your_collection_name_from_spec1
   ```

## Running Tests
1. Prepare test queries:
   - Update `test_queries.json` with your test dataset
   - Ensure proper format with query_text, expected_answer, and metadata

2. Execute the retrieval tests:
   ```bash
   python backend/retrieval_test.py
   ```

## Sample Test Query Format
```json
{
  "queries": [
    {
      "id": "test001",
      "query_text": "What are the key principles of RAG systems?",
      "expected_answer": ["retrieval augmented generation", "vector search", "semantic similarity"],
      "category": "conceptual",
      "difficulty": "medium"
    }
  ]
}
```

## Expected Output
The test will output:
- Individual query results with retrieved chunks and metadata
- Aggregate metrics (MRR, Precision@k, Recall@k)
- Performance statistics (latency, throughput)
- Summary report with pass/fail status against success criteria