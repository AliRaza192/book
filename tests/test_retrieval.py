"""
Unit and integration tests for the RAG retrieval testing system.

This module contains unit tests for embed_query, search_qdrant functions
and integration tests for the full pipeline. It also includes mock Qdrant responses
to ensure tests can run without external dependencies.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add backend to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.retrieval_test import embed_query, search_qdrant, run_retrieval_tests, initialize_clients, load_config
from backend.evaluation_metrics import (
    calculate_mrr, calculate_precision_at_k, calculate_recall_at_k,
    evaluate_retrieval, generate_report
)


class TestEmbedQuery(unittest.TestCase):
    """Test the embed_query function."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_cohere_client = Mock()

    @patch('backend.retrieval_test.cohere.Client')
    def test_embed_query_success(self, mock_cohere_class):
        """Test that embed_query returns correct embedding vector."""
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
        mock_cohere_class.return_value = mock_client_instance

        query_text = "test query"

        # Act
        result = embed_query(query_text, mock_client_instance)

        # Assert
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_client_instance.embed.assert_called_once_with(
            texts=[query_text],
            model='embed-english-v3.0',
            input_type='search_query'
        )

    @patch('backend.retrieval_test.cohere.Client')
    def test_embed_query_different_model(self, mock_cohere_class):
        """Test that embed_query uses correct model and input type."""
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.embed.return_value = Mock(embeddings=[[0.5, 0.6, 0.7]])
        mock_cohere_class.return_value = mock_client_instance

        query_text = "another test query"

        # Act
        result = embed_query(query_text, mock_client_instance)

        # Assert
        self.assertEqual(result, [0.5, 0.6, 0.7])
        mock_client_instance.embed.assert_called_once_with(
            texts=[query_text],
            model='embed-english-v3.0',
            input_type='search_query'
        )


class TestSearchQdrant(unittest.TestCase):
    """Test the search_qdrant function."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Qdrant hit objects
        self.mock_hit1 = Mock()
        self.mock_hit1.id = "chunk_1"
        self.mock_hit1.score = 0.9
        self.mock_hit1.payload = {
            'content': 'This is content about Python programming.',
            'source_url': 'http://example.com/python',
            'title': 'Python Guide',
            'module': 'python_basics'
        }

        self.mock_hit2 = Mock()
        self.mock_hit2.id = "chunk_2"
        self.mock_hit2.score = 0.8
        self.mock_hit2.payload = {
            'content': 'Advanced Python concepts and techniques.',
            'source_url': 'http://example.com/advanced-python',
            'title': 'Advanced Python',
            'module': 'python_advanced'
        }

    def test_search_qdrant_success(self):
        """Test that search_qdrant returns properly formatted results."""
        # Arrange
        mock_query_result = Mock()
        mock_query_result.points = [self.mock_hit1, self.mock_hit2]

        mock_qdrant_client = Mock()
        mock_qdrant_client.query_points.return_value = mock_query_result

        query_vector = [0.1, 0.2, 0.3]
        collection_name = 'documents'
        top_k = 2

        # Act
        results = search_qdrant(query_vector, mock_qdrant_client, collection_name, top_k)

        # Assert
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['chunk_id'], 'chunk_1')
        self.assertEqual(results[0]['content'], 'This is content about Python programming.')
        self.assertEqual(results[0]['score'], 0.9)
        self.assertEqual(results[0]['source_url'], 'http://example.com/python')
        self.assertEqual(results[0]['title'], 'Python Guide')
        self.assertEqual(results[0]['module'], 'python_basics')
        self.assertEqual(results[0]['position'], 1)

        self.assertEqual(results[1]['chunk_id'], 'chunk_2')
        self.assertEqual(results[1]['content'], 'Advanced Python concepts and techniques.')
        self.assertEqual(results[1]['position'], 2)

    def test_search_qdrant_empty_payload_fields(self):
        """Test that search_qdrant handles missing payload fields gracefully."""
        # Arrange
        mock_hit_with_missing_fields = Mock()
        mock_hit_with_missing_fields.id = "chunk_3"
        mock_hit_with_missing_fields.score = 0.7
        mock_hit_with_missing_fields.payload = {
            'content': 'Content without other fields',
            # Missing source_url, title, module
        }

        mock_query_result = Mock()
        mock_query_result.points = [mock_hit_with_missing_fields]

        mock_qdrant_client = Mock()
        mock_qdrant_client.query_points.return_value = mock_query_result

        query_vector = [0.1, 0.2, 0.3]
        collection_name = 'documents'
        top_k = 1

        # Act
        results = search_qdrant(query_vector, mock_qdrant_client, collection_name, top_k)

        # Assert
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['chunk_id'], 'chunk_3')
        self.assertEqual(results[0]['content'], 'Content without other fields')
        self.assertEqual(results[0]['score'], 0.7)
        self.assertEqual(results[0]['source_url'], '')  # Default empty string
        self.assertEqual(results[0]['title'], '')      # Default empty string
        self.assertEqual(results[0]['module'], '')     # Default empty string


class TestEvaluationMetrics(unittest.TestCase):
    """Test the evaluation metrics functions."""

    def test_calculate_mrr_perfect_ranking(self):
        """Test MRR calculation when relevant result is at top position."""
        # Arrange
        retrieved_results = [
            {'content': 'This document contains the expected keyword.'},
            {'content': 'This document does not contain the keyword.'}
        ]
        expected_keywords = ['keyword']

        # Act
        mrr = calculate_mrr(retrieved_results, expected_keywords)

        # Assert
        self.assertEqual(mrr, 1.0)  # First position -> reciprocal rank = 1/1 = 1.0

    def test_calculate_mrr_second_position(self):
        """Test MRR calculation when relevant result is at second position."""
        # Arrange
        retrieved_results = [
            {'content': 'This document does not contain the keyword.'},
            {'content': 'This document contains the expected keyword.'},
            {'content': 'Another irrelevant document.'}
        ]
        expected_keywords = ['keyword']

        # Act
        mrr = calculate_mrr(retrieved_results, expected_keywords)

        # Assert
        self.assertEqual(mrr, 0.5)  # Second position -> reciprocal rank = 1/2 = 0.5

    def test_calculate_mrr_no_relevant_found(self):
        """Test MRR calculation when no relevant results are found."""
        # Arrange
        retrieved_results = [
            {'content': 'This document does not contain the keyword.'},
            {'content': 'Neither does this one.'}
        ]
        expected_keywords = ['keyword']

        # Act
        mrr = calculate_mrr(retrieved_results, expected_keywords)

        # Assert
        self.assertEqual(mrr, 0.0)  # No relevant results -> MRR = 0.0

    def test_calculate_precision_at_k_full_precision(self):
        """Test Precision@k calculation with all relevant results."""
        # Arrange
        retrieved_results = [
            {'content': 'Document with keyword1'},
            {'content': 'Document with keyword2'},
            {'content': 'Document with keyword3'}
        ]
        expected_keywords = ['keyword1', 'keyword2', 'keyword3']
        k = 3

        # Act
        precision = calculate_precision_at_k(retrieved_results, expected_keywords, k)

        # Assert
        self.assertEqual(precision, 1.0)  # All 3 out of 3 are relevant -> precision = 1.0

    def test_calculate_precision_at_k_partial_precision(self):
        """Test Precision@k calculation with some relevant results."""
        # Arrange
        retrieved_results = [
            {'content': 'Document with keyword1'},
            {'content': 'Document without keywords'},
            {'content': 'Document with keyword2'}
        ]
        expected_keywords = ['keyword1', 'keyword2', 'keyword3']
        k = 3

        # Act
        precision = calculate_precision_at_k(retrieved_results, expected_keywords, k)

        # Assert
        self.assertEqual(precision, 2/3)  # 2 out of 3 are relevant -> precision = 2/3

    def test_calculate_precision_at_k_zero_k(self):
        """Test Precision@k calculation when k is zero."""
        # Arrange
        retrieved_results = [{'content': 'any content'}]
        expected_keywords = ['any keyword']
        k = 0

        # Act
        precision = calculate_precision_at_k(retrieved_results, expected_keywords, k)

        # Assert
        self.assertEqual(precision, 0.0)  # When k=0, precision is 0

    def test_calculate_recall_at_k_perfect_recall(self):
        """Test Recall@k calculation with perfect recall."""
        # Arrange
        retrieved_results = [
            {'content': 'Document with keyword1'},
            {'content': 'Document with keyword2'}
        ]
        expected_keywords = ['keyword1', 'keyword2']
        k = 2
        total_relevant = 2  # Both keywords are relevant

        # Act
        recall = calculate_recall_at_k(retrieved_results, expected_keywords, k, total_relevant)

        # Assert
        self.assertEqual(recall, 1.0)  # Found both out of 2 relevant -> recall = 1.0

    def test_calculate_recall_at_k_partial_recall(self):
        """Test Recall@k calculation with partial recall."""
        # Arrange
        retrieved_results = [
            {'content': 'Document with keyword1'},
            {'content': 'Document without keywords'}
        ]
        expected_keywords = ['keyword1', 'keyword2']  # Two relevant keywords
        k = 2
        total_relevant = 2  # Two keywords are relevant

        # Act
        recall = calculate_recall_at_k(retrieved_results, expected_keywords, k, total_relevant)

        # Assert
        self.assertEqual(recall, 0.5)  # Found 1 out of 2 relevant -> recall = 0.5

    def test_calculate_recall_at_k_zero_total_relevant(self):
        """Test Recall@k calculation when total relevant is zero."""
        # Arrange
        retrieved_results = [{'content': 'any content'}]
        expected_keywords = []
        k = 1
        total_relevant = 0  # No relevant documents

        # Act
        recall = calculate_recall_at_k(retrieved_results, expected_keywords, k, total_relevant)

        # Assert
        self.assertEqual(recall, 1.0)  # When no relevant documents exist, recall is 1.0

    def test_evaluate_retrieval_comprehensive(self):
        """Test the comprehensive evaluate_retrieval function."""
        # Arrange
        query = "test query"
        results = [
            {'content': 'Document with keyword1'},
            {'content': 'Document with keyword2'},
            {'content': 'Document without keywords'}
        ]
        expected = ['keyword1', 'keyword2']
        top_k = 3

        # Act
        metrics = evaluate_retrieval(query, results, expected, top_k)

        # Assert
        self.assertIn('mrr', metrics)
        self.assertIn('precision_at_k', metrics)
        self.assertIn('recall_at_k', metrics)
        # With keyword1 at position 1 and keyword2 at position 2:
        # MRR = 1/1 = 1.0 (first relevant item at position 1)
        # Precision@3 = 2/3 (2 relevant out of 3)
        # Recall@3 = 2/2 (found 2 out of 2 relevant items)


class TestConfigAndInitialization(unittest.TestCase):
    """Test configuration loading and client initialization."""

    @patch.dict(os.environ, {
        'COHERE_API_KEY': 'test-cohere-key',
        'QDRANT_HOST': 'test-host',
        'QDRANT_PORT': '6334',
        'COLLECTION_NAME': 'test-collection',
        'TOP_K': '10',
        'SIMILARITY_THRESHOLD': '0.7'
    })
    def test_load_config_with_env_vars(self):
        """Test that load_config correctly reads environment variables."""
        # Act
        config = load_config()

        # Assert
        self.assertEqual(config['cohere_api_key'], 'test-cohere-key')
        self.assertEqual(config['qdrant_host'], 'test-host')
        self.assertEqual(config['qdrant_port'], 6334)
        self.assertEqual(config['collection_name'], 'test-collection')
        self.assertEqual(config['top_k'], 10)
        self.assertEqual(config['similarity_threshold'], 0.7)

    @patch.dict(os.environ, {}, clear=True)  # Empty environment
    def test_load_config_defaults(self):
        """Test that load_config provides sensible defaults when env vars are missing."""
        # Act
        config = load_config()

        # Assert
        self.assertIsNone(config['cohere_api_key'])
        self.assertEqual(config['qdrant_host'], 'localhost')
        self.assertEqual(config['qdrant_port'], 6333)
        self.assertEqual(config['collection_name'], 'documents')
        self.assertEqual(config['top_k'], 5)
        self.assertEqual(config['similarity_threshold'], 0.5)


class TestReportGeneration(unittest.TestCase):
    """Test the report generation functionality."""

    def test_generate_report_basic(self):
        """Test that generate_report creates a proper report structure."""
        # Arrange
        all_results = [
            {
                'query_text': 'Test query 1',
                'query_latency_ms': 100.0,
                'metrics': {
                    'mrr': 1.0,
                    'precision_at_k': 1.0,
                    'recall_at_k': 1.0
                },
                'expected_keywords': ['keyword1']
            },
            {
                'query_text': 'Test query 2',
                'query_latency_ms': 200.0,
                'metrics': {
                    'mrr': 0.5,
                    'precision_at_k': 0.6,
                    'recall_at_k': 0.8
                },
                'expected_keywords': ['keyword2']
            }
        ]
        total_execution_time = 300.0

        # Act
        report = generate_report(all_results, total_execution_time)

        # Assert
        self.assertEqual(report['total_queries_run'], 2)
        self.assertEqual(report['total_execution_time_ms'], 300.0)
        self.assertAlmostEqual(report['avg_query_latency'], 150.0)  # (100+200)/2
        self.assertAlmostEqual(report['avg_mrr'], 0.75)  # (1.0+0.5)/2
        self.assertAlmostEqual(report['avg_precision_at_k'], 0.8)  # (1.0+0.6)/2
        self.assertAlmostEqual(report['avg_recall_at_k'], 0.9)  # (1.0+0.8)/2
        self.assertIn('pass_fail_summary', report)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full pipeline."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary test queries file
        self.test_queries_data = {
            "queries": [
                {
                    "id": "test_001",
                    "query": "What is Python?",
                    "expected_keywords": ["programming language"],
                    "category": "factual",
                    "difficulty": "easy",
                    "module": "python_basics"
                }
            ]
        }

        with open('backend/test_integration_queries.json', 'w') as f:
            json.dump(self.test_queries_data, f)

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists('backend/test_integration_queries.json'):
            os.remove('backend/test_integration_queries.json')

    @patch('backend.retrieval_test.initialize_clients')
    @patch('backend.retrieval_test.embed_query')
    @patch('backend.retrieval_test.search_qdrant')
    @patch('backend.evaluation_metrics.evaluate_retrieval')
    def test_run_retrieval_tests_mocked(self, mock_evaluate_retrieval, mock_search_qdrant,
                                       mock_embed_query, mock_initialize_clients):
        """Test the full run_retrieval_tests function with mocked dependencies."""
        # Arrange
        mock_cohere_client = Mock()
        mock_qdrant_client = Mock()
        mock_initialize_clients.return_value = (mock_cohere_client, mock_qdrant_client)

        mock_embed_query.return_value = [0.1, 0.2, 0.3]
        mock_search_qdrant.return_value = [
            {
                'chunk_id': 'test_chunk',
                'content': 'Python is a programming language',
                'score': 0.9,
                'source_url': 'http://example.com',
                'title': 'Python Intro',
                'module': 'python_basics',
                'position': 1
            }
        ]
        mock_evaluate_retrieval.return_value = {
            'mrr': 1.0,
            'precision_at_k': 1.0,
            'recall_at_k': 1.0
        }

        # Act
        results = run_retrieval_tests('backend/test_integration_queries.json')

        # Assert
        self.assertIn('summary', results)
        self.assertIn('detailed_results', results)
        self.assertIn('test_metadata', results)
        self.assertEqual(results['test_metadata']['total_queries'], 1)
        self.assertTrue(mock_embed_query.called)
        self.assertTrue(mock_search_qdrant.called)
        self.assertTrue(mock_evaluate_retrieval.called)


if __name__ == '__main__':
    unittest.main()