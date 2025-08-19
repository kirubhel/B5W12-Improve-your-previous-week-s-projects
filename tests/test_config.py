# tests/test_config.py
"""
Unit tests for configuration module.
Tests all configuration settings and path management.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import (
    PROJECT_ROOT, DATA_DIR, VECTOR_STORE_DIR, REPORTS_DIR,
    EMBEDDING_MODEL, QA_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
    TOP_K_RETRIEVAL, FAISS_INDEX_PATH, DOCUMENTS_PATH, METADATA_PATH,
    MAX_TOKENS, DEFAULT_THEME, ENABLE_LOGGING,
    MAX_RESPONSE_TIME_MS, MIN_CONFIDENCE_THRESHOLD,
    COMPLIANCE_MODE, AUDIT_TRAIL_ENABLED, DATA_RETENTION_DAYS
)


class TestConfigPaths:
    """Test configuration path management."""
    
    def test_project_root_path(self):
        """Test PROJECT_ROOT path is correctly set."""
        assert isinstance(PROJECT_ROOT, Path)
        assert PROJECT_ROOT.exists()
        assert PROJECT_ROOT.name == "week12"
    
    def test_data_directory_path(self):
        """Test DATA_DIR path is correctly set."""
        assert isinstance(DATA_DIR, Path)
        assert DATA_DIR == PROJECT_ROOT / "data"
    
    def test_vector_store_directory_path(self):
        """Test VECTOR_STORE_DIR path is correctly set."""
        assert isinstance(VECTOR_STORE_DIR, Path)
        assert VECTOR_STORE_DIR == PROJECT_ROOT / "vector_store"
    
    def test_reports_directory_path(self):
        """Test REPORTS_DIR path is correctly set."""
        assert isinstance(REPORTS_DIR, Path)
        assert REPORTS_DIR == PROJECT_ROOT / "reports"
    
    def test_paths_exist_or_can_be_created(self):
        """Test that all directory paths can be created if they don't exist."""
        test_paths = [DATA_DIR, VECTOR_STORE_DIR, REPORTS_DIR]
        
        for path in test_paths:
            # Test that path can be created
            assert path.parent.exists()  # Parent directory should exist
            # Test that we can create the path if needed
            path.mkdir(exist_ok=True)
            assert path.exists() or path.parent.exists()


class TestModelConfiguration:
    """Test model configuration settings."""
    
    def test_embedding_model_setting(self):
        """Test EMBEDDING_MODEL is correctly set."""
        assert EMBEDDING_MODEL == "all-MiniLM-L6-v2"
        assert isinstance(EMBEDDING_MODEL, str)
        assert len(EMBEDDING_MODEL) > 0
    
    def test_qa_model_setting(self):
        """Test QA_MODEL is correctly set."""
        assert QA_MODEL == "google/flan-t5-base"
        assert isinstance(QA_MODEL, str)
        assert len(QA_MODEL) > 0
    
    def test_chunk_size_setting(self):
        """Test CHUNK_SIZE is correctly set."""
        assert CHUNK_SIZE == 300
        assert isinstance(CHUNK_SIZE, int)
        assert CHUNK_SIZE > 0
    
    def test_chunk_overlap_setting(self):
        """Test CHUNK_OVERLAP is correctly set."""
        assert CHUNK_OVERLAP == 50
        assert isinstance(CHUNK_OVERLAP, int)
        assert CHUNK_OVERLAP >= 0
        assert CHUNK_OVERLAP < CHUNK_SIZE
    
    def test_top_k_retrieval_setting(self):
        """Test TOP_K_RETRIEVAL is correctly set."""
        assert TOP_K_RETRIEVAL == 5
        assert isinstance(TOP_K_RETRIEVAL, int)
        assert TOP_K_RETRIEVAL > 0


class TestVectorStoreConfiguration:
    """Test vector store configuration settings."""
    
    def test_faiss_index_path(self):
        """Test FAISS_INDEX_PATH is correctly set."""
        assert isinstance(FAISS_INDEX_PATH, Path)
        assert FAISS_INDEX_PATH == VECTOR_STORE_DIR / "faiss_index.index"
    
    def test_documents_path(self):
        """Test DOCUMENTS_PATH is correctly set."""
        assert isinstance(DOCUMENTS_PATH, Path)
        assert DOCUMENTS_PATH == VECTOR_STORE_DIR / "documents.pkl"
    
    def test_metadata_path(self):
        """Test METADATA_PATH is correctly set."""
        assert isinstance(METADATA_PATH, Path)
        assert METADATA_PATH == VECTOR_STORE_DIR / "metadata.pkl"
    
    def test_vector_store_paths_consistency(self):
        """Test that all vector store paths are in the same directory."""
        vector_store_paths = [FAISS_INDEX_PATH, DOCUMENTS_PATH, METADATA_PATH]
        
        for path in vector_store_paths:
            assert path.parent == VECTOR_STORE_DIR


class TestUIConfiguration:
    """Test UI configuration settings."""
    
    def test_max_tokens_setting(self):
        """Test MAX_TOKENS is correctly set."""
        assert MAX_TOKENS == 200
        assert isinstance(MAX_TOKENS, int)
        assert MAX_TOKENS > 0
    
    def test_default_theme_setting(self):
        """Test DEFAULT_THEME is correctly set."""
        assert DEFAULT_THEME == "light"
        assert isinstance(DEFAULT_THEME, str)
        assert DEFAULT_THEME in ["light", "dark"]
    
    def test_enable_logging_setting(self):
        """Test ENABLE_LOGGING is correctly set."""
        assert ENABLE_LOGGING is True
        assert isinstance(ENABLE_LOGGING, bool)


class TestPerformanceConfiguration:
    """Test performance configuration settings."""
    
    def test_max_response_time_setting(self):
        """Test MAX_RESPONSE_TIME_MS is correctly set."""
        assert MAX_RESPONSE_TIME_MS == 3000
        assert isinstance(MAX_RESPONSE_TIME_MS, int)
        assert MAX_RESPONSE_TIME_MS > 0
    
    def test_min_confidence_threshold_setting(self):
        """Test MIN_CONFIDENCE_THRESHOLD is correctly set."""
        assert MIN_CONFIDENCE_THRESHOLD == 0.7
        assert isinstance(MIN_CONFIDENCE_THRESHOLD, float)
        assert 0.0 <= MIN_CONFIDENCE_THRESHOLD <= 1.0


class TestComplianceConfiguration:
    """Test compliance configuration settings."""
    
    def test_compliance_mode_setting(self):
        """Test COMPLIANCE_MODE is correctly set."""
        assert COMPLIANCE_MODE is True
        assert isinstance(COMPLIANCE_MODE, bool)
    
    def test_audit_trail_enabled_setting(self):
        """Test AUDIT_TRAIL_ENABLED is correctly set."""
        assert AUDIT_TRAIL_ENABLED is True
        assert isinstance(AUDIT_TRAIL_ENABLED, bool)
    
    def test_data_retention_days_setting(self):
        """Test DATA_RETENTION_DAYS is correctly set."""
        assert DATA_RETENTION_DAYS == 90
        assert isinstance(DATA_RETENTION_DAYS, int)
        assert DATA_RETENTION_DAYS > 0


class TestConfigurationValidation:
    """Test configuration validation and consistency."""
    
    def test_chunk_size_greater_than_overlap(self):
        """Test that chunk size is greater than overlap."""
        assert CHUNK_SIZE > CHUNK_OVERLAP
    
    def test_confidence_threshold_range(self):
        """Test that confidence threshold is in valid range."""
        assert 0.0 <= MIN_CONFIDENCE_THRESHOLD <= 1.0
    
    def test_response_time_positive(self):
        """Test that response time threshold is positive."""
        assert MAX_RESPONSE_TIME_MS > 0
    
    def test_retention_days_reasonable(self):
        """Test that data retention days is reasonable."""
        assert 30 <= DATA_RETENTION_DAYS <= 365
    
    def test_top_k_reasonable(self):
        """Test that top k retrieval is reasonable."""
        assert 1 <= TOP_K_RETRIEVAL <= 20


if __name__ == "__main__":
    pytest.main([__file__]) 