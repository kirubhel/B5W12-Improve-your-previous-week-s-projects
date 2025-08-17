# src/utils.py
"""
Utility functions for the Tenx Complaint Analysis Chatbot.
Includes logging, error handling, and performance monitoring.
"""

import time
import logging
import traceback
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('complaint_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            logger.info(f"{func.__name__} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {execution_time:.2f}ms: {str(e)}")
            raise
    return wrapper

def safe_execute(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Safely execute a function with error handling and logging."""
    try:
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "result": result,
            "execution_time_ms": execution_time,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        error_info = {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "execution_time_ms": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        logger.error(f"Function {func.__name__} failed: {error_info}")
        return error_info

def validate_input_data(data: pd.DataFrame) -> Dict[str, Any]:
    """Validate input data for quality and completeness."""
    validation_results = {
        "total_rows": len(data),
        "missing_values": data.isnull().sum().to_dict(),
        "duplicate_rows": data.duplicated().sum(),
        "data_types": data.dtypes.to_dict(),
        "is_valid": True,
        "issues": []
    }
    
    # Check for critical missing data
    if data.empty:
        validation_results["is_valid"] = False
        validation_results["issues"].append("Dataset is empty")
    
    # Check for required columns
    required_columns = ["cleaned_narrative", "Product"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        validation_results["is_valid"] = False
        validation_results["issues"].append(f"Missing required columns: {missing_columns}")
    
    return validation_results

def calculate_response_metrics(response_time: float, confidence_score: float) -> Dict[str, Any]:
    """Calculate response quality metrics for monitoring."""
    return {
        "response_time_ms": response_time,
        "confidence_score": confidence_score,
        "performance_grade": "excellent" if response_time < 1000 else "good" if response_time < 2000 else "needs_improvement",
        "reliability_score": "high" if confidence_score > 0.8 else "medium" if confidence_score > 0.6 else "low"
    }

def format_financial_metrics(complaints_data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate and format financial impact metrics."""
    if complaints_data.empty:
        return {}
    
    metrics = {
        "total_complaints": len(complaints_data),
        "products_affected": complaints_data["Product"].nunique(),
        "top_issues": complaints_data["Product"].value_counts().head(5).to_dict(),
        "compliance_risk_score": "low" if len(complaints_data) < 100 else "medium" if len(complaints_data) < 500 else "high"
    }
    
    return metrics 