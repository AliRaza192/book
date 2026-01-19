# API Contract: RAG Retrieval Testing

## Overview
This contract defines the interface for the RAG retrieval testing system that validates the accuracy and performance of the vector search functionality.

## Endpoints

### Embed Query
- **Function**: `embed_query(query_text)`
- **Description**: Converts a text query into a vector embedding using Cohere's embed-english-v3.0 model
- **Input**:
  - query_text (string): The text to convert to embedding
- **Output**:
  - embedding (array[float]): 1024-dimensional vector representation
  - model (string): The model used for embedding
- **Errors**:
  - 500: API connection failure
  - 429: Rate limit exceeded

### Search Qdrant
- **Function**: `search_qdrant(query_vector, top_k=5)`
- **Description**: Performs cosine similarity search in Qdrant vector database
- **Input**:
  - query_vector (array[float]): 1024-dimensional query vector
  - top_k (int, optional): Number of top results to return (default: 5)
- **Output**:
  - results (array[object]): Array of retrieved chunks with scores and metadata
  - query_latency (float): Time taken for the search operation in milliseconds
- **Errors**:
  - 500: Database connection failure
  - 404: Collection not found

### Evaluate Retrieval
- **Function**: `evaluate_retrieval(query, results, expected_answer)`
- **Description**: Calculates evaluation metrics comparing retrieved results with expected answers
- **Input**:
  - query (string): Original query text
  - results (array[object]): Retrieved chunks from search_qdrant
  - expected_answer (string/array): Expected answer or relevant keywords
- **Output**:
  - metrics (object): Object containing MRR, Precision@k, Recall@k scores
  - relevance_scores (array[float]): Individual relevance scores for each result
- **Errors**:
  - 400: Missing required parameters

### Run Retrieval Tests
- **Function**: `run_retrieval_tests()`
- **Description**: Executes comprehensive test suite with all test queries
- **Input**:
  - test_dataset_path (string, optional): Path to test queries JSON file
- **Output**:
  - summary (object): Overall test results and aggregate metrics
  - detailed_results (array[object]): Individual query results
  - test_metadata (object): Information about test execution
- **Errors**:
  - 500: Test execution failure