# Research Findings: RAG Retrieval Testing

## Decision: Query Embedding Approach
**Rationale**: Using Cohere's embed-english-v3.0 model as specified in the requirements, with input_type="search_query" for optimal query embeddings.
**Alternatives considered**: OpenAI embeddings, Hugging Face models - Cohere was specifically chosen in the spec due to its performance with search queries.

## Decision: Vector Database Connection
**Rationale**: Connecting to existing Qdrant collection from Spec-1 using cosine similarity search as specified.
**Alternatives considered**: Other vector databases like Pinecone, Weaviate - Qdrant was already established in the project.

## Decision: Evaluation Metrics
**Rationale**: Implementing standard IR metrics (MRR, Precision@k, Recall@k) for comprehensive evaluation of retrieval quality.
**Alternatives considered**: NDCG, MAP - MRR and precision/recall@k are more commonly used and understood for this type of evaluation.

## Decision: Test Dataset Structure
**Rationale**: JSON format with categorized queries (factual, conceptual, code-based) and difficulty levels for comprehensive testing.
**Alternatives considered**: YAML, CSV - JSON was chosen for its simplicity and wide support.

## Best Practices: Cohere API Usage
- Use proper API key management with environment variables
- Handle rate limiting gracefully with exponential backoff
- Specify input_type="search_query" for optimal query embeddings

## Best Practices: Qdrant Integration
- Use cosine similarity for semantic search
- Set appropriate top_k values (default 5) for retrieval
- Include metadata in results for proper attribution

## Best Practices: Evaluation Methodology
- Use diverse query types to test system comprehensively
- Establish baseline metrics before making changes
- Track both accuracy and performance metrics
- Include edge cases and error handling in tests