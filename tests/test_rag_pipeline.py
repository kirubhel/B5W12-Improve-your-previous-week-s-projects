# tests/test_rag_pipeline.py
"""Unit tests for RAG pipeline module."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.rag_pipeline import RAGPipeline


class TestRAGPipeline:
    """Test the RAGPipeline class."""
    
    def test_initialization_mocked(self):
        """Test RAGPipeline initialization with mocked dependencies."""
        with patch('src.rag_pipeline.FAISS_INDEX_PATH.exists', return_value=True):
            with patch('src.rag_pipeline.faiss.read_index'):
                with patch('builtins.open'):
                    with patch('pickle.load'):
                        with patch('src.rag_pipeline.SentenceTransformer'):
                            with patch('src.rag_pipeline.pipeline'):
                                pipeline = RAGPipeline()
                                assert pipeline.top_k == 5
    
    def test_build_prompt(self):
        """Test prompt building functionality."""
        pipeline = RAGPipeline.__new__(RAGPipeline)
        pipeline.top_k = 5
        
        question = "Test question"
        context_chunks = [
            {"text": "Test complaint", "relevance_score": 0.9, "meta": {"product": "Credit Card"}}
        ]
        
        prompt = pipeline.build_prompt(question, context_chunks)
        
        assert question in prompt
        assert "Test complaint" in prompt
        assert "financial compliance analyst" in prompt
    
    def test_calculate_confidence(self):
        """Test confidence score calculation."""
        pipeline = RAGPipeline.__new__(RAGPipeline)
        
        answer = "This is a comprehensive answer with financial terms like compliance and risk assessment."
        prompt = "Test prompt"
        
        confidence = pipeline._calculate_confidence(answer, prompt)
        
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)


if __name__ == "__main__":
    pytest.main([__file__]) 