"""
Unit tests for the RAG embeddings generation system.

These tests verify the functionality of individual components without requiring
external services or network calls.
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the backend directory to the path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.main import (
    load_config,
    log_progress,
    count_tokens,
    get_urls,
    chunk_documents,
    generate_embeddings,
    store_in_qdrant,
    scrape_content
)


def test_load_config():
    """Test configuration loading from environment variables."""
    # Mock environment variables
    with patch.dict(os.environ, {
        'COHERE_API_KEY': 'test_cohere_key',
        'QDRANT_API_KEY': 'test_qdrant_key',
        'QDRANT_URL': 'https://test-qdrant.com',
        'SOURCE_URLS': 'https://example.com,https://test.com',
        'CHUNK_SIZE': '800',
        'CHUNK_OVERLAP': '100',
        'BATCH_SIZE': '96',
        'MAX_RETRIES': '3',
        'RETRY_DELAY': '1.0',
        'COLLECTION_NAME': 'test_collection',
        'VECTOR_SIZE': '1024'
    }):
        config = load_config()

        assert config['cohere_api_key'] == 'test_cohere_key'
        assert config['qdrant_api_key'] == 'test_qdrant_key'
        assert config['qdrant_url'] == 'https://test-qdrant.com'
        assert config['source_urls'] == ['https://example.com', 'https://test.com']
        assert config['chunk_size'] == 800
        assert config['chunk_overlap'] == 100
        assert config['batch_size'] == 96
        assert config['max_retries'] == 3
        assert config['retry_delay'] == 1.0
        assert config['collection_name'] == 'test_collection'
        assert config['vector_size'] == 1024


def test_load_config_missing_required():
    """Test configuration loading with missing required variables."""
    # Clear environment variables to test missing case
    with patch.dict(os.environ, {}, clear=True):
        try:
            load_config()
            assert False, "Expected ValueError for missing configuration"
        except ValueError as e:
            assert "Missing required configuration" in str(e)


def test_log_progress():
    """Test progress logging functionality."""
    # This is difficult to test directly since it just logs,
    # but we can at least ensure it doesn't crash
    try:
        log_progress(5, 10, "Test progress")
        assert True  # If we get here, no exception was raised
    except Exception:
        assert False, "log_progress raised an exception"


def test_count_tokens():
    """Test token counting functionality."""
    text = "This is a test sentence."
    token_count = count_tokens(text)

    # Token count should be positive
    assert token_count > 0

    # Empty text should return 0
    assert count_tokens("") == 0


def test_get_urls():
    """Test URL collection from configuration."""
    # Test with environment variable
    with patch.dict(os.environ, {'SOURCE_URLS': 'https://example.com,https://test.com'}):
        urls = get_urls()
        assert urls == ['https://example.com', 'https://test.com']

    # Test with no environment variable (should return defaults)
    with patch.dict(os.environ, {}, clear=True):
        urls = get_urls()
        assert len(urls) > 0  # Should have default URLs


def test_chunk_documents():
    """Test document chunking functionality."""
    long_text = "This is a test. " * 100  # Create a longer text

    chunks = chunk_documents(long_text, max_chunk_size=50, overlap=10)

    # Should have multiple chunks
    assert len(chunks) > 1

    # Each chunk should have content and metadata
    for chunk in chunks:
        assert 'content' in chunk
        assert 'size' in chunk
        assert 'chunk_id' in chunk
        assert 'total_chunks' in chunk
        assert len(chunk['content']) > 0


def test_chunk_documents_short_content():
    """Test chunking with content shorter than max size."""
    short_text = "Short text."

    chunks = chunk_documents(short_text, max_chunk_size=100, overlap=10)

    # Should have only one chunk
    assert len(chunks) == 1
    assert chunks[0]['content'] == short_text


@patch('backend.main.cohere.Client')
def test_generate_embeddings(mock_cohere_client):
    """Test embedding generation (mocked)."""
    # Mock the Cohere client response
    mock_response = MagicMock()
    mock_response.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    mock_cohere_client.return_value.embed.return_value = mock_response

    # Mock environment variable
    with patch.dict(os.environ, {
        'COHERE_API_KEY': 'test_key',
        'QDRANT_API_KEY': 'test_qdrant_key',
        'QDRANT_URL': 'https://test.com'
    }):
        texts = ["test text 1", "test text 2"]
        embeddings = generate_embeddings(texts, batch_size=2)

        assert embeddings is not None
        assert len(embeddings) == 2
        # Verify the client was called
        mock_cohere_client.return_value.embed.assert_called()


def test_generate_embeddings_no_api_key():
    """Test embedding generation with no API key."""
    with patch.dict(os.environ, {
        'COHERE_API_KEY': '',
        'QDRANT_API_KEY': 'test_qdrant_key',
        'QDRANT_URL': 'https://test.com'
    }):
        embeddings = generate_embeddings(["test"])
        assert embeddings is None


@patch('backend.main.QdrantClient')
def test_store_in_qdrant(mock_qdrant_client):
    """Test storing embeddings in Qdrant (mocked)."""
    # Mock the Qdrant client
    mock_client_instance = MagicMock()
    mock_qdrant_client.return_value = mock_client_instance

    # Mock environment variables
    with patch.dict(os.environ, {
        'COHERE_API_KEY': 'test_key',
        'QDRANT_API_KEY': 'test_qdrant_key',
        'QDRANT_URL': 'https://test.com',
        'COLLECTION_NAME': 'test_collection'
    }):
        # Mock that collection doesn't exist initially
        mock_client_instance.get_collection.side_effect = Exception("Collection not found")

        # Test data
        embeddings_data = [{
            'embedding': [0.1, 0.2, 0.3],
            'content': 'test content',
            'title': 'test title',
            'url': 'https://test.com',
            'module': 'test_module',
            'chunk_id': 0,
            'total_chunks': 1
        }]

        result = store_in_qdrant(embeddings_data)

        assert result is True
        # Verify the client methods were called
        mock_qdrant_client.assert_called()
        mock_client_instance.create_collection.assert_called()
        mock_client_instance.upsert.assert_called()


if __name__ == '__main__':
    # Run the tests
    test_load_config()
    test_load_config_missing_required()
    test_log_progress()
    test_count_tokens()
    test_get_urls()
    test_chunk_documents()
    test_chunk_documents_short_content()
    test_generate_embeddings_no_api_key()
    print("All tests passed!")