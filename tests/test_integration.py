# tests/test_integration.py
"""Integration tests for the complete system workflow."""

import pytest
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils import validate_input_data, format_financial_metrics
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RETRIEVAL


class TestSystemIntegration:
    """Test the complete system integration."""
    
    def test_config_consistency(self):
        """Test that configuration values are consistent across modules."""
        from src.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RETRIEVAL
        
        # Chunk size should be greater than overlap
        assert CHUNK_SIZE > CHUNK_OVERLAP
        
        # Top k should be reasonable
        assert 1 <= TOP_K_RETRIEVAL <= 20
        
        # Chunk size should be reasonable for processing
        assert 100 <= CHUNK_SIZE <= 1000
    
    def test_utility_functions_work_with_real_data(self):
        """Test utility functions with realistic data."""
        # Create realistic test data
        test_data = {
            "cleaned_narrative": [
                "Customer complaint about credit card charges",
                "Loan application processing delay",
                "Mobile banking app not working",
                "Unauthorized transaction on account",
                "Poor customer service experience"
            ],
            "Product": [
                "Credit Card",
                "Personal Loan", 
                "Mobile Banking",
                "Checking Account",
                "Customer Service"
            ]
        }
        
        df = pd.DataFrame(test_data)
        
        # Test validation
        validation_result = validate_input_data(df)
        assert validation_result["is_valid"] is True
        assert validation_result["total_rows"] == 5
        
        # Test financial metrics
        metrics = format_financial_metrics(df)
        assert metrics["total_complaints"] == 5
        assert metrics["products_affected"] == 5
        assert "Credit Card" in metrics["top_issues"]
    
    def test_config_paths_exist(self):
        """Test that all configured paths can be created."""
        from src.config import PROJECT_ROOT, DATA_DIR, VECTOR_STORE_DIR, REPORTS_DIR
        
        # All paths should be relative to project root
        assert DATA_DIR == PROJECT_ROOT / "data"
        assert VECTOR_STORE_DIR == PROJECT_ROOT / "vector_store"
        assert REPORTS_DIR == PROJECT_ROOT / "reports"
        
        # Project root should exist
        assert PROJECT_ROOT.exists()
    
    def test_imports_work(self):
        """Test that all modules can be imported without errors."""
        try:
            import src.config
            import src.utils
            import src.embedding_indexing
            import src.rag_pipeline
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


class TestDataFlow:
    """Test the data flow through the system."""
    
    def test_data_validation_flow(self):
        """Test the complete data validation flow."""
        # Test valid data
        valid_data = pd.DataFrame({
            "cleaned_narrative": ["Valid complaint text"],
            "Product": ["Credit Card"]
        })
        
        validation = validate_input_data(valid_data)
        assert validation["is_valid"] is True
        
        # Test invalid data
        invalid_data = pd.DataFrame()
        validation = validate_input_data(invalid_data)
        assert validation["is_valid"] is False
    
    def test_metrics_calculation_flow(self):
        """Test the metrics calculation flow."""
        # Test with various data sizes
        test_cases = [
            (50, "low"),      # Small dataset
            (250, "medium"),  # Medium dataset  
            (600, "high")     # Large dataset
        ]
        
        for size, expected_risk in test_cases:
            test_data = pd.DataFrame({
                "Product": ["Product"] * size
            })
            
            metrics = format_financial_metrics(test_data)
            assert metrics["compliance_risk_score"] == expected_risk


if __name__ == "__main__":
    pytest.main([__file__]) 