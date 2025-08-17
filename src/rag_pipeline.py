# src/rag_pipeline.py
"""
Enhanced RAG pipeline for the Tenx Complaint Analysis Chatbot.
Enterprise-grade implementation with confidence scoring and explainability.
"""

import faiss
import pickle
import numpy as np
import time
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

from sentence_transformers import SentenceTransformer
from transformers import pipeline
import shap

from .config import (
    EMBEDDING_MODEL, QA_MODEL, TOP_K_RETRIEVAL, MAX_TOKENS,
    FAISS_INDEX_PATH, DOCUMENTS_PATH, METADATA_PATH
)
from .utils import performance_monitor, safe_execute, logger, calculate_response_metrics


class RAGPipeline:
    """Enterprise-grade RAG pipeline for complaint analysis."""
    
    def __init__(self, top_k: int = TOP_K_RETRIEVAL):
        self.top_k = top_k
        self.embedding_model = None
        self.qa_pipeline = None
        self.index = None
        self.documents = None
        self.metadata = None
        
        # Load resources
        self._load_resources()
    
    def _load_resources(self) -> None:
        """Load vector store and models."""
        try:
            logger.info("Loading RAG pipeline resources")
            
            # Load vector store
            if not FAISS_INDEX_PATH.exists():
                raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}")
            
            self.index = faiss.read_index(str(FAISS_INDEX_PATH))
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
            # Load documents and metadata
            with open(DOCUMENTS_PATH, "rb") as f:
                self.documents = pickle.load(f)
            
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"Loaded {len(self.documents)} documents and metadata")
            
            # Initialize models
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            self.qa_pipeline = pipeline(
                "text2text-generation", 
                model=QA_MODEL, 
                max_new_tokens=MAX_TOKENS
            )
            
            logger.info("RAG pipeline resources loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load RAG pipeline resources: {str(e)}")
            raise
    
    @performance_monitor
    def retrieve_relevant_chunks(self, question: str) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks for a given question."""
        try:
            # Embed the query
            question_embedding = self.embedding_model.encode([question])
            
            # Search vector store
            distances, indices = self.index.search(
                np.array(question_embedding), 
                self.top_k
            )
            
            # Format results with relevance scores
            retrieved_chunks = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    relevance_score = 1.0 / (1.0 + distance)  # Convert distance to similarity score
                    
                    chunk_data = {
                        "text": self.documents[idx],
                        "meta": self.metadata[idx] if idx < len(self.metadata) else {},
                        "relevance_score": relevance_score,
                        "rank": i + 1,
                        "distance": float(distance)
                    }
                    retrieved_chunks.append(chunk_data)
            
            logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")
            return retrieved_chunks
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant chunks: {str(e)}")
            raise
    
    def build_prompt(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Build a comprehensive prompt for the QA model."""
        try:
            # Sort chunks by relevance score
            sorted_chunks = sorted(context_chunks, key=lambda x: x["relevance_score"], reverse=True)
            
            # Build context from top chunks
            context_parts = []
            for chunk in sorted_chunks[:3]:  # Use top 3 most relevant chunks
                context_parts.append(f"Complaint: {chunk['text']}")
                if chunk.get('meta', {}).get('product'):
                    context_parts.append(f"Product: {chunk['meta']['product']}")
                context_parts.append("---")
            
            context = "\n".join(context_parts)
            
            prompt = f"""You are a financial compliance analyst for CrediTrust Financial.
Your task is to analyze customer complaints and provide clear, actionable insights.

Context from customer complaints:
{context}

Question: {question}

Please provide a comprehensive analysis that includes:
1. Key issues identified
2. Potential compliance risks
3. Recommended actions
4. Business impact assessment

Answer:"""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to build prompt: {str(e)}")
            raise
    
    @performance_monitor
    def generate_answer(self, prompt: str) -> Dict[str, Any]:
        """Generate answer with confidence scoring and explainability."""
        try:
            # Generate answer
            response = self.qa_pipeline(prompt)
            answer = response[0]["generated_text"]
            
            # Calculate confidence score based on response quality
            confidence_score = self._calculate_confidence(answer, prompt)
            
            # Generate explainability insights
            explainability = self._generate_explainability(prompt, answer)
            
            result = {
                "answer": answer,
                "confidence_score": confidence_score,
                "explainability": explainability,
                "model_used": QA_MODEL,
                "max_tokens": MAX_TOKENS
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {str(e)}")
            raise
    
    def _calculate_confidence(self, answer: str, prompt: str) -> float:
        """Calculate confidence score for the generated answer."""
        try:
            # Simple heuristics for confidence scoring
            confidence_factors = []
            
            # Length factor (longer answers tend to be more comprehensive)
            length_score = min(len(answer) / 100, 1.0)
            confidence_factors.append(length_score * 0.3)
            
            # Specificity factor (presence of financial/compliance terms)
            financial_terms = [
                "compliance", "risk", "regulation", "financial", "customer", 
                "service", "product", "issue", "complaint", "resolution"
            ]
            specificity_score = sum(1 for term in financial_terms if term.lower() in answer.lower()) / len(financial_terms)
            confidence_factors.append(specificity_score * 0.4)
            
            # Structure factor (presence of numbered points or clear structure)
            structure_score = 1.0 if any(char.isdigit() for char in answer) else 0.5
            confidence_factors.append(structure_score * 0.3)
            
            confidence = sum(confidence_factors)
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Failed to calculate confidence: {str(e)}")
            return 0.5  # Default confidence
    
    def _generate_explainability(self, prompt: str, answer: str) -> Dict[str, Any]:
        """Generate explainability insights for the answer."""
        try:
            explainability = {
                "input_tokens": len(prompt.split()),
                "output_tokens": len(answer.split()),
                "response_quality": "high" if len(answer) > 100 else "medium" if len(answer) > 50 else "low",
                "key_topics": self._extract_key_topics(answer),
                "compliance_indicators": self._identify_compliance_indicators(answer)
            }
            
            return explainability
            
        except Exception as e:
            logger.warning(f"Failed to generate explainability: {str(e)}")
            return {"error": "Explainability generation failed"}
    
    def _extract_key_topics(self, answer: str) -> List[str]:
        """Extract key topics from the answer."""
        try:
            # Simple topic extraction based on common financial terms
            topics = []
            financial_topics = {
                "customer_service": ["service", "support", "assistance"],
                "compliance": ["compliance", "regulation", "legal"],
                "product_issues": ["product", "feature", "functionality"],
                "financial_risk": ["risk", "exposure", "liability"],
                "resolution": ["resolution", "fix", "solution"]
            }
            
            answer_lower = answer.lower()
            for topic, keywords in financial_topics.items():
                if any(keyword in answer_lower for keyword in keywords):
                    topics.append(topic)
            
            return topics[:3]  # Return top 3 topics
            
        except Exception as e:
            logger.warning(f"Failed to extract topics: {str(e)}")
            return []
    
    def _identify_compliance_indicators(self, answer: str) -> Dict[str, Any]:
        """Identify compliance-related indicators in the answer."""
        try:
            compliance_indicators = {
                "high_risk_terms": [],
                "regulatory_mentions": [],
                "customer_rights": [],
                "resolution_timeframes": []
            }
            
            answer_lower = answer.lower()
            
            # High risk terms
            risk_terms = ["fraud", "unauthorized", "breach", "violation", "illegal"]
            compliance_indicators["high_risk_terms"] = [
                term for term in risk_terms if term in answer_lower
            ]
            
            # Regulatory mentions
            regulatory_terms = ["cfpb", "federal", "state", "regulation", "law"]
            compliance_indicators["regulatory_mentions"] = [
                term for term in regulatory_terms if term in answer_lower
            ]
            
            return compliance_indicators
            
        except Exception as e:
            logger.warning(f"Failed to identify compliance indicators: {str(e)}")
            return {}
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """Main method to process a question through the RAG pipeline."""
        try:
            start_time = time.time()
            
            # Retrieve relevant chunks
            chunks = self.retrieve_relevant_chunks(question)
            
            # Build prompt
            prompt = self.build_prompt(question, chunks)
            
            # Generate answer
            answer_result = self.generate_answer(prompt)
            
            # Calculate response metrics
            response_time = (time.time() - start_time) * 1000
            metrics = calculate_response_metrics(response_time, answer_result["confidence_score"])
            
            # Compile final result
            result = {
                "question": question,
                "answer": answer_result["answer"],
                "confidence_score": answer_result["confidence_score"],
                "explainability": answer_result["explainability"],
                "retrieved_chunks": chunks,
                "performance_metrics": metrics,
                "timestamp": time.time()
            }
            
            logger.info(f"Successfully processed question in {response_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process question: {str(e)}")
            raise


# Legacy functions for backward compatibility
def retrieve_relevant_chunks(question: str, k: int = TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    pipeline = RAGPipeline(top_k=k)
    return pipeline.retrieve_relevant_chunks(question)

def build_prompt(question: str, context_chunks: List[Dict[str, Any]]) -> str:
    """Legacy function for backward compatibility."""
    pipeline = RAGPipeline()
    return pipeline.build_prompt(question, context_chunks)

def generate_answer(prompt: str) -> str:
    """Legacy function for backward compatibility."""
    pipeline = RAGPipeline()
    result = pipeline.generate_answer(prompt)
    return result["answer"]


if __name__ == "__main__":
    # Test the pipeline
    test_questions = [
        "Why are customers unhappy with Buy Now, Pay Later?",
        "What are the major issues in credit card services?",
        "What complaints are common in money transfers?"
    ]
    
    try:
        rag_pipeline = RAGPipeline()
        
        for question in test_questions:
            print(f"\n{'='*80}")
            print(f"Question: {question}")
            print(f"{'='*80}")
            
            result = rag_pipeline.process_question(question)
            
            print(f"Answer: {result['answer']}")
            print(f"Confidence: {result['confidence_score']:.2f}")
            print(f"Response Time: {result['performance_metrics']['response_time_ms']:.2f}ms")
            print(f"Topics: {', '.join(result['explainability']['key_topics'])}")
            
            print("\nTop Sources:")
            for chunk in result['retrieved_chunks'][:2]:
                print(f"- {chunk['text'][:150]}... (Score: {chunk['relevance_score']:.3f})")
                
    except Exception as e:
        print(f"Pipeline test failed: {str(e)}")
        logger.error(f"Pipeline test failed: {str(e)}")
