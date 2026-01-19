# Data Model: RAG Retrieval Testing

## Entities

### TestQuery
- **id**: String - Unique identifier for the test query
- **query_text**: String - The actual question/search term used to validate the retrieval system
- **expected_answer**: String - Expected answer or relevant keywords for validation
- **category**: String - Query type classification (factual, conceptual, code-based, module-specific)
- **difficulty**: String - Difficulty level (easy, medium, hard)
- **created_at**: DateTime - Timestamp when the test query was created

### RetrievedChunk
- **chunk_id**: String - Identifier of the retrieved content chunk
- **content**: String - Text content of the retrieved chunk
- **score**: Float - Similarity score from the vector search
- **source_url**: String - Original URL of the source document
- **title**: String - Title of the source document
- **module**: String - Module classification of the source
- **position**: Integer - Position/rank in the retrieval results

### EvaluationMetric
- **metric_name**: String - Name of the metric (MRR, Precision@k, Recall@k, etc.)
- **value**: Float - Calculated value of the metric
- **sample_size**: Integer - Number of queries used for calculation
- **top_k**: Integer - Value of k used for precision/recall calculations
- **calculated_at**: DateTime - Timestamp when metric was calculated

### MetadataObject
- **url**: String - Source URL of the retrieved content
- **title**: String - Title of the source document
- **module**: String - Module classification of the source
- **chunk_id**: String - Identifier linking to the content chunk
- **source_document_id**: String - ID of the original document

## Relationships
- TestQuery --(generates)--> QueryVector (via embedding)
- QueryVector --(searches)--> RetrievedChunk (via Qdrant)
- TestQuery + RetrievedChunk --(evaluates)--> EvaluationMetric
- RetrievedChunk --(contains)--> MetadataObject

## Validation Rules
- TestQuery.query_text must not be empty
- RetrievedChunk.score must be between 0 and 1
- RetrievedChunk.position must be >= 1
- EvaluationMetric.value must be between 0 and 1 (except for sample_size)
- MetadataObject.url must be a valid URL format