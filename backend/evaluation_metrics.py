"""
Evaluation Metrics for RAG Retrieval Testing

This module provides functions to calculate various evaluation metrics
for the RAG retrieval pipeline, including Mean Reciprocal Rank (MRR),
Precision@k, and Recall@k.
"""

import os
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import json

def calculate_mrr(retrieved_results: List[Dict[str, Any]], expected_keywords: List[str]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR) for a single query.

    Args:
        retrieved_results: List of retrieved chunks with their content and score.
        expected_keywords: List of keywords expected in relevant chunks.

    Returns:
        The Reciprocal Rank (RR) for the query. 0 if no relevant document is found.
    """
    import re

    for i, result in enumerate(retrieved_results):
        content = result.get('content', '')

        # Check each keyword to see if it exists in a non-negated context
        for keyword in expected_keywords:
            # Find all matches of the keyword
            matches = list(re.finditer(r'\b' + re.escape(keyword) + r'\b', content, re.IGNORECASE))

            # For this document to be considered relevant, at least one occurrence
            # of the keyword should NOT be in a negated context
            found_non_negated_match = False

            for match in matches:
                # Get the sentence that contains the match
                # Find the preceding sentence boundary (look for ., !, ?)
                prev_sentence_end = max(
                    content.rfind('.', 0, match.start()),
                    content.rfind('!', 0, match.start()),
                    content.rfind('?', 0, match.start())
                )

                if prev_sentence_end == -1:
                    # No sentence boundary found, start from beginning
                    sentence_start = 0
                else:
                    sentence_start = prev_sentence_end + 1

                # Find the following sentence boundary
                next_sentence_start = min(
                    content.find('.', match.end()),
                    content.find('!', match.end()),
                    content.find('?', match.end())
                )

                if next_sentence_start == -1:
                    # No sentence boundary found, go to end
                    sentence_end = len(content)
                else:
                    sentence_end = next_sentence_start + 1

                sentence = content[sentence_start:sentence_end].strip()

                # Extract the part before the keyword within the sentence
                keyword_in_sentence_pos = match.start() - sentence_start
                part_before_keyword = sentence[:keyword_in_sentence_pos].lower()

                # Check for negation words in the sentence part before the keyword
                negation_words = ['not', 'no', 'never', 'nothing', 'nowhere', 'neither', 'nobody', 'none', 'lack', 'absence', 'without']
                has_negation = any(neg_word in part_before_keyword for neg_word in negation_words)

                if not has_negation:
                    # Found a non-negated occurrence of the keyword
                    found_non_negated_match = True
                    break  # No need to check other matches of this keyword in this document

            if found_non_negated_match:
                # This document contains the keyword in a non-negated context
                return 1.0 / (i + 1)

    # If we reach here, no document contained the keyword in a non-negated context
    return 0.0

def calculate_precision_at_k(retrieved_results: List[Dict[str, Any]], expected_keywords: List[str], k: int) -> float:
    """
    Calculate Precision@k for a single query.

    Args:
        retrieved_results: List of retrieved chunks with their content and score.
        expected_keywords: List of keywords expected in relevant chunks.
        k: The number of top results to consider.

    Returns:
        Precision@k for the query.
    """
    if k == 0: return 0.0
    relevant_count = 0
    for i in range(min(k, len(retrieved_results))):
        content = retrieved_results[i].get('content', '').lower()
        if any(keyword.lower() in content for keyword in expected_keywords):
            relevant_count += 1
    return relevant_count / min(k, len(retrieved_results))

def calculate_recall_at_k(retrieved_results: List[Dict[str, Any]], expected_keywords: List[str], k: int, total_relevant: int = 1) -> float:
    """
    Calculate Recall@k for a single query.

    Args:
        retrieved_results: List of retrieved chunks with their content and score.
        expected_keywords: List of keywords expected in relevant chunks.
        k: The number of top results to consider.
        total_relevant: Total number of relevant documents (assumed 1 if not specified).

    Returns:
        Recall@k for the query.
    """
    if total_relevant == 0: return 1.0 # If no relevant documents, perfect recall is 1.0
    if k == 0: return 0.0

    found_relevant_count = 0
    for i in range(min(k, len(retrieved_results))):
        content = retrieved_results[i].get('content', '').lower()
        if any(keyword.lower() in content for keyword in expected_keywords):
            found_relevant_count += 1

    return found_relevant_count / total_relevant

def evaluate_retrieval(query: str, results: List[Dict[str, Any]], expected: List[str], top_k: int = 5) -> Dict[str, float]:
    """
    Calculate MRR, Precision@k, and Recall@k for a single query.

    Args:
        query: The original query text (not used in calculations, but for context).
        results: List of retrieved chunks with their content and score.
        expected: List of expected keywords in relevant chunks.
        top_k: The number of top results to consider for P@k and R@k.

    Returns:
        Dictionary containing calculated metrics.
    """
    mrr = calculate_mrr(results, expected)
    precision = calculate_precision_at_k(results, expected, top_k)
    recall = calculate_recall_at_k(results, expected, top_k, total_relevant=len(expected) if expected else 1)

    return {
        'mrr': mrr,
        'precision_at_k': precision,
        'recall_at_k': recall
    }

def generate_report(all_results: List[Dict[str, Any]], total_execution_time_ms: float) -> Dict[str, Any]:
    """
    Generate summary statistics and a JSON report from all test results.

    Args:
        all_results: List of detailed results for each query.
        total_execution_time_ms: Total time taken for all queries in milliseconds.

    Returns:
        Dictionary with summary statistics.
    """
    df = pd.DataFrame(all_results)

    # Calculate average metrics
    avg_mrr = df['metrics'].apply(lambda x: x['mrr']).mean()
    avg_precision = df['metrics'].apply(lambda x: x['precision_at_k']).mean()
    avg_recall = df['metrics'].apply(lambda x: x['recall_at_k']).mean()
    avg_query_latency = df['query_latency_ms'].mean()

    # Calculate overall accuracy (simple example: proportion of queries with MRR > 0)
    overall_accuracy = (df['metrics'].apply(lambda x: x['mrr']) > 0).mean()

    # Performance checks
    latency_pass_count = (df['query_latency_ms'] < 500).sum()
    latency_pass_rate = latency_pass_count / len(df)

    # Top-3 accuracy (assuming 'precision_at_k' is calculated for k=3 if it exists or use default k)
    top_3_accuracy_pass_count = (df['metrics'].apply(lambda x: x['precision_at_k'] if 'precision_at_k' in x else 0.0) >= 0.90).sum() # Assuming k=3 is implied for 'top_3_accuracy'
    top_3_accuracy_pass_rate = top_3_accuracy_pass_count / len(df)

    # Prepare report structure
    report = {
        'total_queries_run': len(all_results),
        'total_execution_time_ms': total_execution_time_ms,
        'avg_query_latency': avg_query_latency,
        'overall_accuracy': overall_accuracy,
        'avg_mrr': avg_mrr,
        'avg_precision_at_k': avg_precision,
        'avg_recall_at_k': avg_recall,
        'latency_pass_rate': latency_pass_rate,
        'top_3_accuracy_pass_rate': top_3_accuracy_pass_rate,
        'pass_fail_summary': {
            'retrieval_accuracy': "PASS" if overall_accuracy >= 0.8 else "FAIL",
            'query_latency': "PASS" if latency_pass_rate >= 1.0 else "FAIL", # All queries must be < 500ms
            'top_3_accuracy': "PASS" if top_3_accuracy_pass_rate >= 0.9 else "FAIL"
        }
    }

    # Save detailed results to a JSON file
    results_dir = "backend/results"
    os.makedirs(results_dir, exist_ok=True)
    report_file_path = os.path.join(results_dir, "retrieval_report.json")
    with open(report_file_path, 'w') as f:
        json.dump(all_results, f, indent=2)

    return report