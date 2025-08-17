# src/embedding_indexing.py
"""
Enhanced embedding and indexing module for the Tenx Complaint Analysis Chatbot.
Enterprise-grade implementation with proper error handling and monitoring.
"""

import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import faiss
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .config import (
    DATA_DIR, VECTOR_STORE_DIR, CHUNK_SIZE, CHUNK_OVERLAP,
    EMBEDDING_MODEL, FAISS_INDEX_PATH, DOCUMENTS_PATH, METADATA_PATH
)
from .utils import performance_monitor, safe_execute, validate_input_data, logger


class ComplaintIndexer:
    """Enterprise-grade complaint indexing system."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_model = None
        self.documents = []
        self.metadatas = []
        self.embeddings = None
        self.faiss_index = None
        
    def load_complaints_data(self, file_path: str = None) -> pd.DataFrame:
        """Load and validate complaints data."""
        if file_path is None:
            file_path = DATA_DIR / "filtered_complaints.csv"
        
        logger.info(f"Loading complaints data from {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            validation_result = validate_input_data(df)
            
            if not validation_result["is_valid"]:
                raise ValueError(f"Data validation failed: {validation_result['issues']}")
            
            logger.info(f"Successfully loaded {len(df)} complaints")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load complaints data: {str(e)}")
            raise
    
    @performance_monitor
    def chunk_complaints(self, df: pd.DataFrame) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Chunk complaint narratives into smaller pieces."""
        logger.info("Starting complaint chunking process")
        
        documents = []
        metadatas = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Chunking complaints"):
            try:
                narrative = str(row.get("cleaned_narrative", ""))
                if not narrative or narrative == "nan":
                    continue
                    
                chunks = self.text_splitter.split_text(narrative)
                
                for chunk in chunks:
                    if chunk.strip():  # Only add non-empty chunks
                        documents.append(chunk)
                        metadatas.append({
                            "product": row.get("Product", "Unknown"),
                            "original_index": idx,
                            "chunk_id": f"{idx}_{len(documents)}",
                            "chunk_length": len(chunk)
                        })
                        
            except Exception as e:
                logger.warning(f"Failed to process row {idx}: {str(e)}")
                continue
        
        logger.info(f"Created {len(documents)} chunks from {len(df)} complaints")
        return documents, metadatas
    
    @performance_monitor
    def generate_embeddings(self, documents: List[str]) -> np.ndarray:
        """Generate embeddings for document chunks."""
        logger.info("Initializing embedding model")
        
        try:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            logger.info(f"Using embedding model: {EMBEDDING_MODEL}")
            
            logger.info("Generating embeddings")
            embeddings = self.embedding_model.encode(
                documents, 
                show_progress_bar=True,
                batch_size=32
            )
            
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    @performance_monitor
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS index for efficient similarity search."""
        logger.info("Building FAISS index")
        
        try:
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype('float32'))
            
            logger.info(f"FAISS index built with {index.ntotal} vectors")
            return index
            
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {str(e)}")
            raise
    
    def save_vector_store(self, index: faiss.Index, documents: List[str], metadatas: List[Dict]) -> None:
        """Save vector store and metadata to disk."""
        logger.info("Saving vector store to disk")
        
        try:
            VECTOR_STORE_DIR.mkdir(exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(index, str(FAISS_INDEX_PATH))
            logger.info(f"FAISS index saved to {FAISS_INDEX_PATH}")
            
            # Save documents
            with open(DOCUMENTS_PATH, "wb") as f:
                pickle.dump(documents, f)
            logger.info(f"Documents saved to {DOCUMENTS_PATH}")
            
            # Save metadata
            with open(METADATA_PATH, "wb") as f:
                pickle.dump(metadatas, f)
            logger.info(f"Metadata saved to {METADATA_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")
            raise
    
    def create_index(self, file_path: str = None) -> Dict[str, Any]:
        """Main method to create the complete vector index."""
        logger.info("Starting vector index creation process")
        
        try:
            # Load data
            df = self.load_complaints_data(file_path)
            
            # Chunk complaints
            documents, metadatas = self.chunk_complaints(df)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(documents)
            
            # Build FAISS index
            faiss_index = self.build_faiss_index(embeddings)
            
            # Save everything
            self.save_vector_store(faiss_index, documents, metadatas)
            
            # Store for later use
            self.documents = documents
            self.metadatas = metadatas
            self.embeddings = embeddings
            self.faiss_index = faiss_index
            
            result = {
                "total_documents": len(documents),
                "total_chunks": len(documents),
                "embedding_dimension": embeddings.shape[1],
                "index_size": faiss_index.ntotal,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }
            
            logger.info("Vector index creation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Vector index creation failed: {str(e)}")
            raise


def main():
    """Main execution function for standalone use."""
    try:
        indexer = ComplaintIndexer()
        result = indexer.create_index()
        print("✅ Vector store created successfully!")
        print(f"📊 Index Statistics: {result}")
        
    except Exception as e:
        print(f"❌ Failed to create vector store: {str(e)}")
        logger.error(f"Main execution failed: {str(e)}")


if __name__ == "__main__":
    main()
