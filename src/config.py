# src/config.py
"""
Configuration settings for the Tenx Complaint Analysis Chatbot.
Centralized configuration for enterprise deployment.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Model configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
QA_MODEL = "google/flan-t5-base"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 5

# Vector store configuration
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index.index"
DOCUMENTS_PATH = VECTOR_STORE_DIR / "documents.pkl"
METADATA_PATH = VECTOR_STORE_DIR / "metadata.pkl"

# UI configuration
MAX_TOKENS = 200
DEFAULT_THEME = "light"
ENABLE_LOGGING = True

# Performance thresholds
MAX_RESPONSE_TIME_MS = 3000  # 3 seconds
MIN_CONFIDENCE_THRESHOLD = 0.7

# Financial sector specific settings
COMPLIANCE_MODE = True
AUDIT_TRAIL_ENABLED = True
DATA_RETENTION_DAYS = 90 