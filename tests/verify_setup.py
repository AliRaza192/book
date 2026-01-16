#!/usr/bin/env python3
"""
Verification script to test the RAG embeddings setup without making actual API calls.

This script verifies:
1. Configuration loading from .env file
2. Import of all required dependencies
3. Basic functionality without external API calls
"""

import sys
import os
import importlib.util
from pathlib import Path

def test_imports():
    """Test that all required dependencies can be imported."""
    print("🔍 Testing required imports...")

    required_modules = [
        ('asyncio', None),
        ('os', None),
        ('logging', None),
        ('tiktoken', 'tiktoken'),
        ('cohere', 'cohere'),
        ('dotenv', 'python-dotenv'),
        ('qdrant_client', 'qdrant-client'),
        ('playwright', 'playwright'),
        ('langchain_text_splitters', 'langchain-text-splitters'),
        ('bs4', 'beautifulsoup4'),
        ('requests', 'requests')
    ]

    failed_imports = []

    for module_name, package_name in required_modules:
        try:
            if module_name == 'dotenv':
                importlib.import_module('dotenv')
            elif module_name == 'qdrant_client':
                importlib.import_module('qdrant_client')
            elif module_name == 'langchain_text_splitters':
                importlib.import_module('langchain_text_splitters')
            elif module_name == 'bs4':
                importlib.import_module('bs4')
            else:
                importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            failed_imports.append((module_name, package_name))
            print(f"❌ {module_name} (requires: {package_name or module_name}) - {str(e)}")

    return len(failed_imports) == 0

def test_config_loading():
    """Test that configuration can be loaded from .env file."""
    print("\n🔍 Testing configuration loading...")

    try:
        # Add the backend directory to the Python path to import the main module
        backend_dir = Path(__file__).parent.parent / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        # Now import the main module
        import main
        load_config = main.load_config

        # Attempt to load config
        config = load_config()

        print("✅ Configuration loading function works")

        # Check if .env file exists
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            print("✅ .env file exists")
        else:
            print("⚠️  .env file not found (this is okay for initial setup)")

        # Check if required keys are in environment
        required_keys = ['cohere_api_key', 'qdrant_api_key', 'qdrant_url']
        missing_keys = [key for key in required_keys if not config.get(key)]

        if missing_keys:
            print(f"⚠️  Missing required config keys (expected for verification): {missing_keys}")
        else:
            print("✅ All required config keys are present")

        return True

    except Exception as e:
        print(f"❌ Configuration loading failed: {str(e)}")
        return False

def test_token_counting():
    """Test token counting functionality."""
    print("\n🔍 Testing token counting functionality...")

    try:
        # Add the backend directory to the Python path to import the main module
        backend_dir = Path(__file__).parent.parent / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        # Now import the main module
        import main
        count_tokens = main.count_tokens

        # Test with sample text
        sample_text = "This is a sample text for testing token counting."
        token_count = count_tokens(sample_text)

        print(f"✅ Token counting works: '{sample_text[:20]}...' -> {token_count} tokens")
        return True

    except Exception as e:
        print(f"❌ Token counting failed: {str(e)}")
        return False

def test_chunking_functionality():
    """Test chunking functionality."""
    print("\n🔍 Testing chunking functionality...")

    try:
        # Add the backend directory to the Python path to import the main module
        backend_dir = Path(__file__).parent.parent / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        # Now import the main module
        import main
        chunk_documents = main.chunk_documents

        # Test with sample content
        sample_content = "This is a sample content that will be chunked into smaller pieces. " * 20
        chunks = chunk_documents(sample_content, max_chunk_size=100, overlap=20)

        print(f"✅ Chunking works: Created {len(chunks)} chunks from sample content")
        if chunks:
            print(f"   First chunk size: {chunks[0]['size']} tokens")

        return True

    except Exception as e:
        print(f"❌ Chunking functionality failed: {str(e)}")
        return False

def test_environment_variables():
    """Test environment variable handling."""
    print("\n🔍 Testing environment variable handling...")

    required_env_vars = [
        'COHERE_API_KEY',
        'QDRANT_API_KEY',
        'QDRANT_URL'
    ]

    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing environment variables (expected for verification): {missing_vars}")
    else:
        print("✅ All required environment variables are set")

    # Test with sample values
    sample_vars = {
        'CHUNK_SIZE': '800',
        'CHUNK_OVERLAP': '100',
        'BATCH_SIZE': '96',
        'MAX_RETRIES': '3',
        'RETRY_DELAY': '1.0',
        'COLLECTION_NAME': 'rag_embeddings',
        'VECTOR_SIZE': '1024'
    }

    for var, default_val in sample_vars.items():
        val = os.getenv(var, default_val)
        print(f"   {var}: {val}")

    return True

def run_basic_verification():
    """Run all verification tests."""
    print("🚀 Starting RAG Embeddings Setup Verification...\n")

    all_passed = True

    # Run all tests
    all_passed &= test_imports()
    all_passed &= test_config_loading()
    all_passed &= test_token_counting()
    all_passed &= test_chunking_functionality()
    all_passed &= test_environment_variables()

    print(f"\n{'✅' if all_passed else '❌'} Verification {'PASSED' if all_passed else 'FAILED'}")

    if all_passed:
        print("\n🎉 Setup verification completed successfully!")
        print("   All dependencies are available and core functionality works.")
        print("   You can now run the main pipeline with 'python backend/main.py'")
    else:
        print("\n⚠️  Some verification steps failed.")
        print("   Please check the errors above and resolve them before running the pipeline.")

    return all_passed

if __name__ == "__main__":
    success = run_basic_verification()
    sys.exit(0 if success else 1)