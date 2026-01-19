# RAG Chatbot Embeddings Generator

A system that scrapes content from Docusaurus book sites, generates vector embeddings using Cohere API, and stores them in Qdrant Cloud vector database for efficient retrieval. The system chunks content optimally (800 tokens with 100-token overlap) while preserving metadata for search and retrieval.

## Features

- **Dynamic Content Scraping**: Uses Playwright to render JavaScript-heavy Docusaurus sites
- **Smart Content Chunking**: Implements LangChain's RecursiveCharacterTextSplitter for optimal chunking
- **Batch Embedding Generation**: Processes content in batches of 96 to respect API rate limits
- **Vector Storage**: Stores embeddings with rich metadata in Qdrant vector database
- **Error Handling**: Comprehensive retry logic and fallback mechanisms
- **Progress Tracking**: Real-time logging of pipeline progress

## Prerequisites

- Python 3.10+
- Playwright browser binaries (install with `playwright install chromium`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install uv  # Optional: for faster dependency resolution
uv pip install -e .  # Or use: pip install -e .
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_cloud_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
SOURCE_URLS=https://example-docs.com/page1,https://example-docs.com/page2,https://example-docs.com/page3
CHUNK_SIZE=800
CHUNK_OVERLAP=100
BATCH_SIZE=96
MAX_RETRIES=3
RETRY_DELAY=1.0
COLLECTION_NAME=rag_embeddings
VECTOR_SIZE=1024
```

### Environment Variables

- `COHERE_API_KEY`: Your Cohere API key for generating embeddings
- `QDRANT_API_KEY`: Your Qdrant Cloud API key
- `QDRANT_URL`: Your Qdrant Cloud cluster URL
- `SOURCE_URLS`: Comma-separated list of URLs to scrape
- `CHUNK_SIZE`: Maximum size of each text chunk in tokens (default: 800)
- `CHUNK_OVERLAP`: Overlap between chunks in tokens (default: 100)
- `BATCH_SIZE`: Number of texts to process in each Cohere API call (default: 96)
- `MAX_RETRIES`: Maximum retry attempts for failed operations (default: 3)
- `RETRY_DELAY`: Base delay between retries in seconds (default: 1.0)
- `COLLECTION_NAME`: Name of the Qdrant collection (default: rag_embeddings)
- `VECTOR_SIZE`: Dimension of the embedding vectors (default: 1024 for Cohere v3)

## Usage

### Running the Pipeline

Execute the main pipeline:

```bash
cd backend
python main.py
```

The pipeline will:
1. Load configuration from environment variables
2. Collect URLs to process
3. Scrape content from each URL using Playwright
4. Chunk content using LangChain's RecursiveCharacterTextSplitter
5. Generate embeddings in batches using Cohere API
6. Store embeddings with metadata in Qdrant

### Custom Configuration

You can also run with custom environment variables:

```bash
export SOURCE_URLS="https://my-docs.com/page1,https://my-docs.com/page2"
export CHUNK_SIZE=1000
python backend/main.py
```

## Architecture

### Components

1. **URL Collection (`get_urls`)**: Loads URLs from configuration
2. **Content Scraping (`scrape_content`)**: Uses Playwright for dynamic content
3. **Content Chunking (`chunk_documents`)**: Uses LangChain for smart chunking
4. **Embedding Generation (`generate_embeddings`)**: Batches requests to Cohere API
5. **Vector Storage (`store_in_qdrant`)**: Saves embeddings with metadata to Qdrant
6. **Pipeline Orchestration (`main`)**: Coordinates the entire process

### Data Flow

```
URLs → Scrape Content → Chunk Documents → Generate Embeddings → Store in Qdrant
```

Each step includes error handling and retry logic to ensure robust processing.

## Testing

Run the unit tests:

```bash
pytest tests/
```

Or run the basic tests directly:

```bash
python tests/test_main.py
```

## RAG Retrieval Testing

The system includes a comprehensive testing and validation framework for the RAG retrieval pipeline. This framework validates that embeddings in the Qdrant vector database work correctly for semantic search by querying with test questions, retrieving relevant content chunks, and measuring retrieval accuracy.

### Running Retrieval Tests

To run the retrieval tests:

```bash
python backend/retrieval_test.py
```

This will execute a comprehensive test suite with various query types (factual, conceptual, code-based) and generate detailed reports on retrieval accuracy, performance metrics, and system reliability.

### Running in Test Mode (Without Qdrant)

To run the retrieval tests in test mode without connecting to Qdrant (uses mock results for testing):

```bash
python backend/retrieval_test.py --test-mode
```

This mode is useful for testing the retrieval pipeline without requiring an active Qdrant connection. It simulates the retrieval process and generates mock results for validation.

### Retrieval Test Configuration

The system uses the following test configuration parameters (set in `.env`):

- `TOP_K`: Number of top results to retrieve (default: 5)
- `SIMILARITY_THRESHOLD`: Minimum similarity score threshold (default: 0.7)

### Test Queries Dataset

The system uses a dataset of 50+ test queries in `backend/test_queries.json` covering:

- **Factual queries**: Direct fact-based questions
- **Conceptual queries**: Abstract concept-based questions
- **Code-based queries**: Programming/code-related questions
- **Module-specific queries**: Questions specific to different modules in the documentation

### Evaluation Metrics

The system calculates the following metrics for each query:

- **Mean Reciprocal Rank (MRR)**: Measures ranking quality
- **Precision@K**: Measures precision of top-K results
- **Recall@K**: Measures recall of top-K results
- **Query Latency**: Measures response time for each query
- **Overall Accuracy**: Proportion of queries with relevant results

### Test Reports

Detailed test reports are saved to `backend/results/retrieval_report.json` with comprehensive metrics and analysis. The system aims for ≥80% accuracy in retrieval tasks.

## Installation Verification

Before running the main pipeline, verify your installation with the verification script:

```bash
python tests/verify_setup.py
```

This script will check:
- All required dependencies are installed and importable
- Configuration can be loaded from environment variables
- Core functionality works without making external API calls
- Environment variables are properly set

The verification script helps ensure everything is set up correctly before attempting to run the full pipeline with actual API calls.

Example output:
```
🚀 Starting RAG Embeddings Setup Verification...

🔍 Testing required imports...
✅ asyncio
✅ os
✅ logging
✅ tiktoken
✅ cohere
✅ python-dotenv
✅ qdrant-client
✅ playwright
✅ langchain-text-splitters
✅ beautifulsoup4
✅ requests

🔍 Testing configuration loading...
✅ Configuration loading function works
✅ .env file exists
⚠️  Missing required config keys (expected for verification): ['cohere_api_key', 'qdrant_api_key', 'qdrant_url']

✅ Verification PASSED

🎉 Setup verification completed successfully!
   All dependencies are available and core functionality works.
   You can now run the main pipeline with 'python backend/main.py'
```

## Troubleshooting

### Common Issues

1. **Browser Automation Errors**: If Playwright fails to launch the browser, ensure Chromium is installed:
   ```bash
   playwright install chromium
   ```

2. **API Rate Limits**: The system implements batch processing and delays to respect API limits. Adjust `BATCH_SIZE` and `RETRY_DELAY` if needed.

3. **Memory Issues**: For large documentation sets, consider processing in smaller batches or increasing system memory.

4. **Qdrant Connection**: Verify your Qdrant URL and API key are correct and that your IP has access to the cluster.

### Logging

The system logs detailed progress information. Check the logs to monitor pipeline progress and identify any issues.

## Performance

- **Chunk Size**: Configured to 800 tokens with 100-token overlap for optimal retrieval
- **Batch Processing**: 96 items per Cohere API call to maximize throughput
- **Retry Logic**: Exponential backoff to handle temporary failures gracefully

## Security

- API keys are loaded from environment variables, never hardcoded
- All external requests include proper headers and respect rate limits
- Input validation is performed on all configuration parameters

## License

[Specify your license here]