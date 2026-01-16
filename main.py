"""
RAG Chatbot Embeddings Generation System

This script implements a system that scrapes content from Docusaurus book sites,
generates vector embeddings using Cohere API, and stores them in Qdrant Cloud
vector database for efficient retrieval. The system chunks content optimally
(500-1000 tokens) while preserving metadata for search and retrieval.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple
from functools import wraps

import cohere
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import PointStruct
import tiktoken

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """
    Load configuration from environment variables with defaults.

    Returns:
        dict: Configuration dictionary with all parameters
    """
    config = {
        'cohere_api_key': os.getenv('COHERE_API_KEY'),
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
        'qdrant_url': os.getenv('QDRANT_URL'),
        'source_urls': os.getenv('SOURCE_URLS', '').split(',') if os.getenv('SOURCE_URLS') else [],
        'chunk_size': int(os.getenv('CHUNK_SIZE', '800')),
        'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', '100')),
        'batch_size': int(os.getenv('BATCH_SIZE', '96')),
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'retry_delay': float(os.getenv('RETRY_DELAY', '1.0')),
        'collection_name': os.getenv('COLLECTION_NAME', 'rag_embeddings'),
        'vector_size': int(os.getenv('VECTOR_SIZE', '1024'))
    }

    # Clean up source URLs
    config['source_urls'] = [url.strip() for url in config['source_urls'] if url.strip()]

    # Validate required configuration
    required_keys = ['cohere_api_key', 'qdrant_api_key', 'qdrant_url']
    missing_keys = [key for key in required_keys if not config[key]]
    if missing_keys:
        raise ValueError(f"Missing required configuration: {missing_keys}")

    return config


def log_progress(current: int, total: int, description: str = ""):
    """
    Log progress of a task.

    Args:
        current: Current progress
        total: Total amount of work
        description: Description of the task
    """
    percentage = (current / total) * 100
    logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - {description}")


def count_tokens(text: str, model_name: str = "gpt-3.5-turbo") -> int:
    """
    Count the number of tokens in a text using tiktoken.

    Args:
        text: Text to count tokens for
        model_name: Model name to use for tokenization

    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception:
        # Fallback: rough estimate (4 characters per token)
        return len(text) // 4


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
            raise last_exception
        return wrapper

    def sync_decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
            raise last_exception
        return sync_wrapper

    # Return appropriate decorator based on whether the function is async
    if asyncio.iscoroutinefunction(func):
        return decorator(func)
    else:
        return sync_decorator(func)

    return decorator


def log_progress(current: int, total: int, description: str = ""):
    """
    Log progress of a task.

    Args:
        current: Current progress
        total: Total amount of work
        description: Description of the task
    """
    percentage = (current / total) * 100
    logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - {description}")


def get_urls() -> List[str]:
    """
    Collect all Docusaurus site URLs from configuration.

    Returns:
        List of URLs to scrape
    """
    config = load_config()
    urls = config['source_urls']

    if not urls:
        logger.warning("No SOURCE_URLS found in environment. Using default example URLs.")
        return [
            "https://docusaurus.io/docs/introduction",
            "https://docusaurus.io/docs/getting-started"
        ]

    logger.info(f"Loaded {len(urls)} URLs to process")
    return urls


async def scrape_content(url: str) -> Optional[Dict[str, str]]:
    """
    Extract content from a URL using Playwright for dynamic content rendering.

    Args:
        url: URL to scrape

    Returns:
        Dictionary with content, title, and metadata or None if failed
    """
    from playwright.async_api import async_playwright
    import re
    from urllib.parse import urlparse

    try:
        async with async_playwright() as p:
            # Launch browser with stealth settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

            # Create context with realistic settings
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Connection': 'keep-alive'
                }
            )

            # Create new page
            page = await context.new_page()

            # Navigate to the URL
            await page.goto(url, wait_until='networkidle', timeout=30000)

            # Wait for content to load
            await page.wait_for_timeout(2000)

            # Extract title
            title = await page.title()

            # Extract content using multiple selectors for Docusaurus sites
            content_selectors = [
                'article',
                '[role="main"]',
                '.main-wrapper',
                '.container',
                'main',
                '.docMainContainer',
                '.theme-doc-markdown',
                '.markdown',
                '[data-testid="doc-content"]',
                '.docs-doc-page'
            ]

            content = ""
            for selector in content_selectors:
                element = await page.query_selector(selector)
                if element:
                    content = await element.inner_text()
                    break

            # If no specific content found, get body text
            if not content:
                content = await page.inner_text('body')

            # Clean up content
            content = re.sub(r'\s+', ' ', content).strip()

            # Extract module name from URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            module = path_parts[0] if path_parts and path_parts[0] else 'default_module'

            await browser.close()

            return {
                'url': url,
                'title': title,
                'content': content,
                'module': module
            }

    except Exception as e:
        logger.error(f"Failed to scrape {url}: {str(e)}")

        # Fallback to requests/bs4 if Playwright fails
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract main content (adjust selectors based on Docusaurus structure)
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "No Title"

            # Try to find main content container (common Docusaurus selectors)
            content_selectors = [
                'article',
                '[role="main"]',
                '.main-wrapper',
                '.container',
                'main',
                '.docMainContainer',
                '.theme-doc-markdown'
            ]

            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break

            if not content_element:
                # Fallback: get all paragraph content
                content_element = soup

            # Extract text content, removing script and style elements
            for script in content_element(["script", "style"]):
                script.decompose()

            content = content_element.get_text(separator=' ', strip=True)

            # Clean up excess whitespace
            content = re.sub(r'\s+', ' ', content).strip()

            # Extract module name from URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            module = path_parts[0] if path_parts and path_parts[0] else 'default_module'

            return {
                'url': url,
                'title': title,
                'content': content,
                'module': module
            }
        except Exception as fallback_error:
            logger.error(f"Fallback scraping also failed for {url}: {str(fallback_error)}")
            return None


def chunk_documents(content: str, max_chunk_size: int = 800, overlap: int = 100) -> List[Dict]:
    """
    Split content into chunks using LangChain's RecursiveCharacterTextSplitter.

    Args:
        content: Text content to chunk
        max_chunk_size: Maximum size of each chunk (in tokens)
        overlap: Overlap between chunks (in tokens)

    Returns:
        List of chunk dictionaries with content and metadata
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    # Initialize the text splitter with specified parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=overlap,
        length_function=count_tokens,  # Using our token counting function
        is_separator_regex=False,
    )

    # Split the content
    chunks = text_splitter.split_text(content)

    # Format the chunks with metadata
    formatted_chunks = []
    for i, chunk in enumerate(chunks):
        formatted_chunks.append({
            'content': chunk,
            'size': count_tokens(chunk),
            'chunk_id': i,
            'total_chunks': len(chunks)
        })

    logger.info(f"Chunked content into {len(formatted_chunks)} pieces using RecursiveCharacterTextSplitter")
    return formatted_chunks


def generate_embeddings(texts: List[str], batch_size: int = 96) -> Optional[List[List[float]]]:
    """
    Generate embeddings for a list of texts using Cohere API with batch processing.

    Args:
        texts: List of text strings to embed
        batch_size: Size of batches to process (default 96 as per requirements)

    Returns:
        List of embedding vectors or None if failed
    """
    config = load_config()
    api_key = config['cohere_api_key']

    if not api_key:
        logger.error("COHERE_API_KEY not found in environment")
        return None

    try:
        co = cohere.Client(api_key)

        all_embeddings = []

        # Process texts in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}, size: {len(batch)}")

            response = co.embed(
                texts=batch,
                model='embed-english-v3.0',
                input_type='search_document'  # Using search_document for knowledge base content
            )

            all_embeddings.extend(response.embeddings)

            # Add a small delay between batches to respect API rate limits
            time.sleep(0.1)

        logger.info(f"Generated embeddings for {len(texts)} text chunks")
        return all_embeddings

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        return None


def store_in_qdrant(embeddings_data: List[Dict]) -> bool:
    """
    Store embeddings with metadata in Qdrant vector database.

    Args:
        embeddings_data: List of dictionaries containing embeddings and metadata

    Returns:
        True if successful, False otherwise
    """
    config = load_config()
    api_key = config['qdrant_api_key']
    url = config['qdrant_url']
    collection_name = config['collection_name']
    vector_size = config['vector_size']  # Cohere embed-english-v3.0 returns 1024-dim vectors

    if not api_key or not url:
        logger.error("QDRANT_API_KEY or QDRANT_URL not found in environment")
        return False

    try:
        # Initialize Qdrant client
        client = QdrantClient(
            url=url,
            api_key=api_key,
            prefer_grpc=False  # Using REST API
        )

        # Check if collection exists, create if not
        try:
            client.get_collection(collection_name)
            logger.info(f"Collection '{collection_name}' already exists")
        except:
            logger.info(f"Creating collection '{collection_name}'")
            # Cohere embed-english-v3.0 model produces 1024-dimensional vectors
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
            )

        # Prepare points for insertion
        points = []
        for idx, data in enumerate(embeddings_data):
            point = PointStruct(
                id=idx,
                vector=data['embedding'],
                payload={
                    'content': data['content'],
                    'title': data['title'],
                    'url': data['url'],
                    'module': data.get('module', 'unknown'),
                    'chunk_size': len(data['content']),
                    'token_count': count_tokens(data['content']),
                    'chunk_id': data.get('chunk_id', 0),
                    'total_chunks': data.get('total_chunks', 1),
                    'timestamp': time.time()
                }
            )
            points.append(point)

        # Upload points to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points
        )

        logger.info(f"Stored {len(points)} embeddings in Qdrant collection '{collection_name}'")
        return True

    except Exception as e:
        logger.error(f"Failed to store embeddings in Qdrant: {str(e)}")
        return False


async def main():
    """
    Main pipeline function orchestrating the complete flow:
    1. Get URLs to process
    2. Scrape content from each URL
    3. Chunk content appropriately
    4. Generate embeddings for chunks
    5. Store embeddings in Qdrant
    """
    logger.info("Starting RAG embeddings generation pipeline")

    try:
        # Load configuration
        config = load_config()

        # Step 1: Get URLs
        urls = get_urls()
        if not urls:
            logger.error("No URLs to process. Exiting.")
            return

        all_embeddings_data = []

        # Process each URL
        for i, url in enumerate(urls):
            logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")

            # Step 2: Scrape content
            content_data = await scrape_content(url)
            if not content_data:
                logger.warning(f"Failed to scrape content from {url}, skipping...")
                continue

            # Step 3: Chunk content
            content_chunks = chunk_documents(content_data['content'],
                                           max_chunk_size=config['chunk_size'],
                                           overlap=config['chunk_overlap'])

            if not content_chunks:
                logger.warning(f"No content chunks generated from {url}, skipping...")
                continue

            # Step 4: Generate embeddings for each chunk
            texts_to_embed = [chunk['content'] for chunk in content_chunks]

            # Check if we need to batch the embedding generation due to API limits
            if len(texts_to_embed) > 0:
                embeddings = generate_embeddings(texts_to_embed, batch_size=config['batch_size'])

                if embeddings and len(embeddings) == len(texts_to_embed):
                    # Combine embeddings with content and metadata
                    for j, chunk in enumerate(content_chunks):
                        embedding_data = {
                            'embedding': embeddings[j],
                            'content': chunk['content'],
                            'title': content_data['title'],
                            'url': content_data['url'],
                            'module': content_data['module'],
                            'chunk_id': chunk['chunk_id'],
                            'total_chunks': chunk['total_chunks']
                        }
                        all_embeddings_data.append(embedding_data)

                    logger.info(f"Successfully processed {len(content_chunks)} chunks from {url}")
                else:
                    logger.warning(f"Failed to generate embeddings for {url} or mismatch in count")
            else:
                logger.warning(f"No text to embed from {url}, skipping...")

        # Step 5: Store all embeddings in Qdrant
        if all_embeddings_data:
            success = store_in_qdrant(all_embeddings_data)
            if success:
                logger.info(f"Pipeline completed successfully! Stored {len(all_embeddings_data)} embeddings.")
            else:
                logger.error("Failed to store embeddings in Qdrant")
        else:
            logger.warning("No embeddings to store - pipeline completed but no data was processed successfully")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())