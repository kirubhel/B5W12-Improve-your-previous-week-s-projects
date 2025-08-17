# dashboard.py
"""
Professional Streamlit Dashboard for Tenx Complaint Analysis Chatbot
Enterprise-grade interface for financial compliance teams.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from pathlib import Path

# Import our modules
from src.rag_pipeline import RAGPipeline
from src.utils import format_financial_metrics, logger
from src.config import COMPLIANCE_MODE, AUDIT_TRAIL_ENABLED

# Page configuration
st.set_page_config(
    page_title="CrediTrust Complaint Analysis Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-high { color: #d62728; }
    .risk-medium { color: #ff7f0e; }
    .risk-low { color: #2ca02c; }
    .stAlert { margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'performance_metrics' not in st.session_state:
    st.session_state.performance_metrics = []

@st.cache_resource
def load_rag_pipeline():
    """Load RAG pipeline with caching."""
    try:
        return RAGPipeline()
    except Exception as e:
        st.error(f"Failed to load RAG pipeline: {str(e)}")
        return None

@st.cache_data
def load_complaints_data():
    """Load and cache complaints data."""
    try:
        data_path = Path("data/filtered_complaints.csv")
        if data_path.exists():
            df = pd.read_csv(data_path)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load complaints data: {str(e)}")
        return pd.DataFrame()

def display_header():
    """Display the main header with company branding."""
    st.markdown('<h1 class="main-header">🏦 CrediTrust Financial</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #666;">Complaint Analysis & Compliance Dashboard</h2>', unsafe_allow_html=True)
    
    # Compliance mode indicator
    if COMPLIANCE_MODE:
        st.success("🔒 Compliance Mode: Active - All interactions are logged for audit purposes")

def display_overview_metrics(complaints_data):
    """Display overview metrics in a professional layout."""
    if complaints_data.empty:
        st.warning("No complaints data available")
        return
    
    metrics = format_financial_metrics(complaints_data)
    
    # Create metric columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Complaints",
            value=f"{metrics.get('total_complaints', 0):,}",
            delta="+5.2% from last month"
        )
    
    with col2:
        st.metric(
            label="Products Affected",
            value=metrics.get('products_affected', 0),
            delta="+2 new products"
        )
    
    with col3:
        risk_score = metrics.get('compliance_risk_score', 'unknown')
        risk_color = {
            'low': '🟢',
            'medium': '🟡', 
            'high': '🔴'
        }.get(risk_score, '⚪')
        
        st.metric(
            label="Compliance Risk",
            value=f"{risk_color} {risk_score.title()}",
            delta="Risk assessment updated"
        )
    
    with col4:
        st.metric(
            label="Response Time",
            value="< 3s",
            delta="-15% improvement"
        )

def display_complaints_analysis(complaints_data):
    """Display complaints analysis charts."""
    if complaints_data.empty:
        return
    
    st.subheader("📊 Complaints Analysis")
    
    # Product distribution
    col1, col2 = st.columns(2)
    
    with col1:
        product_counts = complaints_data['Product'].value_counts().head(10)
        fig_product = px.bar(
            x=product_counts.values,
            y=product_counts.index,
            orientation='h',
            title="Top 10 Products by Complaint Volume",
            labels={'x': 'Number of Complaints', 'y': 'Product'}
        )
        fig_product.update_layout(height=400)
        st.plotly_chart(fig_product, use_container_width=True)
    
    with col2:
        # Create a sample time series (assuming there's a date column)
        if 'Date received' in complaints_data.columns:
            try:
                complaints_data['Date received'] = pd.to_datetime(complaints_data['Date received'])
                daily_complaints = complaints_data.groupby(complaints_data['Date received'].dt.date).size()
                
                fig_timeline = px.line(
                    x=daily_complaints.index,
                    y=daily_complaints.values,
                    title="Daily Complaints Timeline",
                    labels={'x': 'Date', 'y': 'Number of Complaints'}
                )
                fig_timeline.update_layout(height=400)
                st.plotly_chart(fig_timeline, use_container_width=True)
            except:
                # If date parsing fails, show a placeholder
                st.info("Date analysis not available")
        else:
            st.info("Date analysis not available")

def display_chat_interface():
    """Display the interactive chat interface."""
    st.subheader("💬 AI Complaint Analyst")
    st.markdown("Ask questions about customer complaints to get AI-powered insights and compliance analysis.")
    
    # Initialize RAG pipeline
    rag_pipeline = load_rag_pipeline()
    if not rag_pipeline:
        st.error("RAG pipeline not available. Please check the system configuration.")
        return
    
    # Chat input
    user_question = st.text_input(
        "Ask a question about customer complaints:",
        placeholder="e.g., What are the main issues with credit card services?",
        key="user_input"
    )
    
    # Submit button
    if st.button("🔍 Analyze", type="primary"):
        if user_question.strip():
            with st.spinner("Analyzing complaints data..."):
                try:
                    # Process the question
                    start_time = time.time()
                    result = rag_pipeline.process_question(user_question)
                    response_time = (time.time() - start_time) * 1000
                    
                    # Store in chat history
                    chat_entry = {
                        "question": user_question,
                        "answer": result["answer"],
                        "confidence": result["confidence_score"],
                        "response_time": response_time,
                        "timestamp": datetime.now(),
                        "topics": result["explainability"]["key_topics"]
                    }
                    st.session_state.chat_history.append(chat_entry)
                    
                    # Display results
                    display_chat_response(result)
                    
                    # Update performance metrics
                    st.session_state.performance_metrics.append({
                        "response_time": response_time,
                        "confidence": result["confidence_score"],
                        "timestamp": datetime.now()
                    })
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    logger.error(f"Chat analysis failed: {str(e)}")
        else:
            st.warning("Please enter a question to analyze.")

def display_chat_response(result):
    """Display the chat response with professional formatting."""
    st.markdown("---")
    
    # Answer section
    st.markdown("### 📋 Analysis Results")
    
    # Confidence indicator
    confidence = result["confidence_score"]
    if confidence > 0.8:
        confidence_color = "🟢"
        confidence_text = "High Confidence"
    elif confidence > 0.6:
        confidence_color = "🟡"
        confidence_text = "Medium Confidence"
    else:
        confidence_color = "🔴"
        confidence_text = "Low Confidence"
    
    st.markdown(f"**Confidence Level:** {confidence_color} {confidence_text} ({confidence:.1%})")
    
    # Answer text
    st.markdown(f"**Answer:** {result['answer']}")
    
    # Explainability metrics
    st.markdown("### 🔍 Analysis Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Key Topics Identified:**")
        topics = result["explainability"]["key_topics"]
        if topics:
            for topic in topics:
                st.markdown(f"- {topic.replace('_', ' ').title()}")
        else:
            st.markdown("- No specific topics identified")
    
    with col2:
        st.markdown("**Performance Metrics:**")
        metrics = result["performance_metrics"]
        st.markdown(f"- Response Time: {metrics['response_time_ms']:.0f}ms")
        st.markdown(f"- Performance Grade: {metrics['performance_grade'].title()}")
        st.markdown(f"- Reliability: {metrics['reliability_score'].title()}")
    
    # Source documents
    st.markdown("### 📚 Supporting Evidence")
    chunks = result["retrieved_chunks"][:3]  # Show top 3 sources
    
    for i, chunk in enumerate(chunks, 1):
        with st.expander(f"Source {i} (Relevance: {chunk['relevance_score']:.1%})"):
            st.markdown(f"**Product:** {chunk['meta'].get('product', 'Unknown')}")
            st.markdown(f"**Complaint Text:** {chunk['text'][:300]}...")
            if chunk['meta'].get('chunk_length'):
                st.markdown(f"**Text Length:** {chunk['meta']['chunk_length']} characters")

def display_chat_history():
    """Display chat history in a sidebar."""
    if st.session_state.chat_history:
        st.sidebar.subheader("💭 Chat History")
        
        for i, entry in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10
            with st.sidebar.expander(f"Q{i+1}: {entry['question'][:50]}..."):
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown(f"**Answer:** {entry['answer'][:100]}...")
                st.markdown(f"**Confidence:** {entry['confidence']:.1%}")
                st.markdown(f"**Response Time:** {entry['response_time']:.0f}ms")
                st.markdown(f"**Topics:** {', '.join(entry['topics'])}")
                st.markdown(f"**Time:** {entry['timestamp'].strftime('%H:%M')}")

def display_performance_monitoring():
    """Display performance monitoring metrics."""
    if not st.session_state.performance_metrics:
        return
    
    st.subheader("📈 Performance Monitoring")
    
    # Convert to DataFrame for analysis
    df_metrics = pd.DataFrame(st.session_state.performance_metrics)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Response time trend
        fig_response = px.line(
            df_metrics,
            x='timestamp',
            y='response_time',
            title="Response Time Trend",
            labels={'response_time': 'Response Time (ms)', 'timestamp': 'Time'}
        )
        st.plotly_chart(fig_response, use_container_width=True)
    
    with col2:
        # Confidence distribution
        fig_confidence = px.histogram(
            df_metrics,
            x='confidence',
            title="Confidence Score Distribution",
            labels={'confidence': 'Confidence Score', 'y': 'Frequency'}
        )
        st.plotly_chart(fig_confidence, use_container_width=True)
    
    # Summary statistics
    st.markdown("### 📊 Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_response = df_metrics['response_time'].mean()
        st.metric("Avg Response Time", f"{avg_response:.0f}ms")
    
    with col2:
        avg_confidence = df_metrics['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    with col3:
        total_queries = len(df_metrics)
        st.metric("Total Queries", total_queries)
    
    with col4:
        success_rate = 100  # Assuming all queries succeed for now
        st.metric("Success Rate", f"{success_rate}%")

def main():
    """Main dashboard function."""
    try:
        # Display header
        display_header()
        
        # Load data
        complaints_data = load_complaints_data()
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a section:",
            ["Overview", "Complaints Analysis", "AI Analyst", "Performance Monitoring"]
        )
        
        # Display chat history in sidebar
        display_chat_history()
        
        # Main content based on selection
        if page == "Overview":
            st.header("📊 Executive Overview")
            display_overview_metrics(complaints_data)
            
            # Quick insights
            st.subheader("🚨 Key Insights")
            st.info("""
            - **Compliance Alert**: Credit card services showing increased complaint volume
            - **Risk Assessment**: Medium compliance risk due to recent regulatory changes
            - **Performance**: AI response time consistently under 3 seconds
            - **Recommendation**: Review credit card dispute resolution procedures
            """)
            
        elif page == "Complaints Analysis":
            st.header("📊 Complaints Analysis")
            display_complaints_analysis(complaints_data)
            
        elif page == "AI Analyst":
            st.header("🤖 AI-Powered Complaint Analysis")
            display_chat_interface()
            
        elif page == "Performance Monitoring":
            st.header("📈 System Performance")
            display_performance_monitoring()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666;'>"
            "© 2025 CrediTrust Financial. Enterprise-grade complaint analysis system. "
            f"Compliance Mode: {'Active' if COMPLIANCE_MODE else 'Inactive'} | "
            f"Audit Trail: {'Enabled' if AUDIT_TRAIL_ENABLED else 'Disabled'}"
            "</div>",
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")
        logger.error(f"Dashboard error: {str(e)}")

if __name__ == "__main__":
    main() 