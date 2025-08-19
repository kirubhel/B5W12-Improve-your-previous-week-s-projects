# tests/test_embedding_indexing.py
"""Unit tests for embedding and indexing module."""

import pytest
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embedding_indexing import ComplaintIndexer


class TestComplaintIndexer:
    """Test the ComplaintIndexer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.indexer = ComplaintIndexer(chunk_size=100, chunk_overlap=20)
        self.test_data = pd.DataFrame({
            "cleaned_narrative": ["Test complaint", "Another complaint"],
            "Product": ["Credit Card", "Loan"]
        })
    
    def test_initialization(self):
        """Test ComplaintIndexer initialization."""
        assert self.indexer.chunk_size == 100
        assert self.indexer.chunk_overlap == 20
        assert self.indexer.documents == []
        assert self.indexer.metadatas == []
    
    def test_text_splitter_initialization(self):
        """Test that text splitter is properly initialized."""
        assert self.indexer.text_splitter is not None
        assert hasattr(self.indexer.text_splitter, 'chunk_size')
        assert hasattr(self.indexer.text_splitter, 'chunk_overlap')
    
    def test_load_complaints_data_success(self):
        """Test successful loading of complaints data."""
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.return_value = self.test_data
            
            with patch('src.embedding_indexing.validate_input_data') as mock_validate:
                mock_validate.return_value = {"is_valid": True, "issues": []}
                
                result = self.indexer.load_complaints_data("test_file.csv")
                assert result.equals(self.test_data)
    
    def test_chunk_complaints_success(self):
        """Test successful complaint chunking."""
        with patch('src.embedding_indexing.tqdm') as mock_tqdm:
            mock_tqdm.return_value = self.test_data.iterrows()
            
            documents, metadatas = self.indexer.chunk_complaints(self.test_data)
            
            assert len(documents) > 0
            assert len(metadatas) > 0
            assert len(documents) == len(metadatas)
    
    def test_generate_embeddings_success(self):
        """Test successful embedding generation."""
        test_documents = ["Document 1", "Document 2"]
        
        with patch('src.embedding_indexing.SentenceTransformer') as mock_transformer:
            mock_model = Mock()
            mock_model.encode.return_value = np.random.rand(2, 384)
            mock_transformer.return_value = mock_model
            
            embeddings = self.indexer.generate_embeddings(test_documents)
            assert embeddings.shape == (2, 384)
    
    def test_build_faiss_index_success(self):
        """Test successful FAISS index building."""
        test_embeddings = np.random.rand(3, 384)
        
        with patch('src.embedding_indexing.faiss.IndexFlatL2') as mock_index_class:
            mock_index = Mock()
            mock_index_class.return_value = mock_index
            mock_index.ntotal = 3
            
            index = self.indexer.build_faiss_index(test_embeddings)
            assert index == mock_index


if __name__ == "__main__":
    pytest.main([__file__]) 