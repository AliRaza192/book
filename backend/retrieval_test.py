"""
RAG Retrieval Testing and Validation System

This module implements a comprehensive testing and validation system for the RAG retrieval pipeline.
It validates that embeddings in the Qdrant vector database work correctly for semantic search
by querying with test questions, retrieving relevant content chunks, and measuring retrieval accuracy.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional
import json

import cohere
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from environment variables"""
    config = {
        'cohere_api_key': os.getenv('COHERE_API_KEY'),
        'qdrant_url': os.getenv('QDRANT_URL'),  # Optional - if using cloud
        'qdrant_host': os.getenv('QDRANT_HOST', 'localhost'),
        'qdrant_port': int(os.getenv('QDRANT_PORT', 6333)),
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
        'collection_name': os.getenv('COLLECTION_NAME', 'documents'),
        'top_k': int(os.getenv('TOP_K', 5)),
        'similarity_threshold': float(os.getenv('SIMILARITY_THRESHOLD', 0.5))
    }
    return config

def initialize_clients(config: Dict[str, Any]) -> tuple:
    """
    Initialize Cohere and Qdrant clients

    Args:
        config: Configuration dictionary with API keys and connection details

    Returns:
        Tuple of (cohere_client, qdrant_client)
    """
    # Initialize Cohere client
    cohere_client = cohere.Client(config['cohere_api_key'])

    # Initialize Qdrant client - use URL if provided, otherwise use host/port
    qdrant_url = config.get('qdrant_url')
    if qdrant_url:
        qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=config.get('qdrant_api_key')
        )
    else:
        qdrant_client = QdrantClient(
            host=config['qdrant_host'],
            port=config['qdrant_port'],
            api_key=config.get('qdrant_api_key')
        )

    return cohere_client, qdrant_client

def embed_query(query_text: str, cohere_client) -> List[float]:
    """
    Convert a text query into a vector embedding using Cohere's embed-english-v3.0 model

    Args:
        query_text: The text to convert to embedding
        cohere_client: Initialized Cohere client

    Returns:
        1024-dimensional vector representation of the query
    """
    response = cohere_client.embed(
        texts=[query_text],
        model='embed-english-v3.0',
        input_type='search_query'
    )

    return response.embeddings[0]

def search_qdrant(query_vector: List[float], qdrant_client, collection_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform cosine similarity search in Qdrant vector database

    Args:
        query_vector: 1024-dimensional query vector
        qdrant_client: Initialized Qdrant client
        collection_name: Name of the collection to search in
        top_k: Number of top results to return (default: 5)

    Returns:
        List of retrieved chunks with scores and metadata
    """
    # Perform search in Qdrant - using query_points method for newer Qdrant client versions
    # The newer versions of Qdrant client have replaced the search method with query_points
    search_result = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k
    )

    # Extract points from the result
    hits = search_result.points

    # Format results
    results = []
    for hit in hits:
        result = {
            'chunk_id': hit.id,
            'content': hit.payload.get('content', ''),
            'score': hit.score,
            'source_url': hit.payload.get('source_url', ''),
            'title': hit.payload.get('title', ''),
            'module': hit.payload.get('module', ''),
            'position': len(results) + 1  # rank position
        }
        results.append(result)

    return results

def run_retrieval_tests(test_dataset_path: str = 'backend/test_queries.json', test_mode: bool = False):
    """
    Execute comprehensive test suite with all test queries

    Args:
        test_dataset_path: Path to test queries JSON file
        test_mode: If True, run in test mode without connecting to Qdrant (mock results)

    Returns:
        Dictionary with summary statistics and detailed results
    """
    logger.info("Starting retrieval tests...")

    # Load test queries
    with open(test_dataset_path, 'r') as f:
        test_data = json.load(f)

    queries = test_data.get('queries', [])
    logger.info(f"Loaded {len(queries)} test queries")

    # Load configuration
    config = load_config()

    # Initialize Cohere client (still needed for embeddings even in test mode)
    cohere_client, qdrant_client = initialize_clients(config)

    # Initialize evaluation metrics module
    from backend.evaluation_metrics import evaluate_retrieval, generate_report

    all_results = []
    total_start_time = time.time()

    for i, query_obj in enumerate(queries):
        logger.info(f"Processing query {i+1}/{len(queries)}: {query_obj['query'][:50]}...")

        query_start_time = time.time()

        # Embed the query (always needed)
        query_embedding = embed_query(query_obj['query'], cohere_client)

        if test_mode:
            # In test mode, create mock search results
            import random
            search_results = []
            for j in range(config['top_k']):
                # Create mock results with content that may or may not contain expected keywords
                mock_content = f"This is a mock result {j+1} for query '{query_obj['query'][:20]}...' containing some relevant content."

                # Sometimes include expected keywords to simulate successful retrieval
                if query_obj.get('expected_keywords') and random.random() > 0.3:  # 70% chance to include keywords
                    mock_content += " " + " ".join(query_obj['expected_keywords'][:1])  # Add one expected keyword

                mock_result = {
                    'chunk_id': f'mock_chunk_{i}_{j}',
                    'content': mock_content,
                    'score': 0.9 - (j * 0.1),  # Decreasing scores
                    'source_url': f'http://mock.example.com/doc_{i}_{j}',
                    'title': f'Mock Document {i}-{j}',
                    'module': query_obj.get('module', 'mock_module'),
                    'position': j + 1
                }
                search_results.append(mock_result)

            # Simulate query latency
            time.sleep(0.01)  # Small delay to simulate processing time
        else:
            # Search Qdrant in normal mode
            search_results = search_qdrant(
                query_vector=query_embedding,
                qdrant_client=qdrant_client,
                collection_name=config['collection_name'],
                top_k=config['top_k']
            )

        query_end_time = time.time()
        query_latency = (query_end_time - query_start_time) * 1000  # Convert to milliseconds

        # Evaluate retrieval
        evaluation_result = evaluate_retrieval(
            query=query_obj['query'],
            results=search_results,
            expected=query_obj.get('expected_keywords', [])
        )

        # Add metadata to result
        result = {
            'query_id': query_obj.get('id', f'query_{i}'),
            'query_text': query_obj['query'],
            'category': query_obj.get('category', 'unknown'),
            'difficulty': query_obj.get('difficulty', 'medium'),
            'results': search_results,
            'metrics': evaluation_result,
            'query_latency_ms': query_latency,
            'expected_keywords': query_obj.get('expected_keywords', [])
        }

        all_results.append(result)

    total_end_time = time.time()
    total_execution_time = (total_end_time - total_start_time) * 1000  # Convert to milliseconds

    # Generate final report
    report = generate_report(all_results, total_execution_time)

    # Log summary
    logger.info(f"Retrieval tests completed in {total_execution_time:.2f}ms")
    logger.info(f"Average query latency: {report['avg_query_latency']:.2f}ms")
    logger.info(f"Overall accuracy: {report['overall_accuracy']:.2%}")

    return {
        'summary': report,
        'detailed_results': all_results,
        'test_metadata': {
            'total_queries': len(queries),
            'total_execution_time_ms': total_execution_time,
            'avg_query_latency_ms': report['avg_query_latency']
        }
    }

if __name__ == "__main__":
    import sys
    # Run the retrieval tests when the script is executed directly
    # Accept command line arguments for test mode
    test_mode = '--test-mode' in sys.argv or '-t' in sys.argv

    results = run_retrieval_tests(test_dataset_path='backend/test_queries.json', test_mode=test_mode)
    print(json.dumps(results['summary'], indent=2))