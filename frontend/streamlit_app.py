# frontend/streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import json
from typing import Dict, List, Optional

# Configuration

API_BASE_URL = "http://localhost:8000"

# Page configuration

st.set_page_config(
    page_title="Clutter Flow",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
    }
    .processing-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_documents() -> List[Dict]:
    """Fetch all documents from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            return response.json()["documents"]
        return []
    except Exception as e:
        st.error(f"Error fetching documents: {e}")
        return []

@st.cache_data(ttl=5)  # Cache for 5 seconds
def get_document_summary(document_id: str) -> Optional[Dict]:
    """Fetch document summary"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/summary")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=5)
def get_document_classification(document_id: str) -> Optional[Dict]:
    """Fetch document classification"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/classification")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=10)
def get_processing_tasks() -> List[Dict]:
    """Fetch processing tasks"""
    try:
        response = requests.get(f"{API_BASE_URL}/tasks")
        if response.status_code == 200:
            return response.json()["tasks"]
        return []
    except:
        return []

@st.cache_data(ttl=30)
def get_analytics() -> Dict:
    """Fetch analytics data"""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/overview")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def upload_file(file) -> Optional[Dict]:
    """Upload file to API"""
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/extract", files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Upload error: {e}")
        return None

def trigger_summarization(document_id: str, summary_type: str = "brief") -> bool:
    """Manually trigger summarization"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/documents/{document_id}/summarize",
            json={"summary_type": summary_type}
        )
        return response.status_code == 200
    except:
        return False

def trigger_classification(document_id: str) -> bool:
    """Manually trigger classification"""
    try:
        response = requests.post(f"{API_BASE_URL}/documents/{document_id}/classify", json={})
        return response.status_code == 200
    except:
        return False

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Clutter Flow</h1>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Document Processing & Organization**")
    
    # Sidebar
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📤 Upload Documents", "📋 Document Library", "📊 Analytics Dashboard", "⚙️ Processing Queue"]
    )
    
    # Page routing
    if page == "📤 Upload Documents":
        upload_page()
    elif page == "📋 Document Library":
        library_page()
    elif page == "📊 Analytics Dashboard":
        analytics_page()
    elif page == "⚙️ Processing Queue":
        queue_page()

def upload_page():
    st.header("📤 Upload Documents")
    st.write("Upload PDFs or images to extract text and generate AI summaries & classifications.")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="Supported formats: PDF, PNG, JPG, JPEG (Max 50MB)"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Filename:** {uploaded_file.name}")
        with col2:
            st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.write(f"**Type:** {uploaded_file.type}")
        
        # Upload button
        if st.button("🚀 Process Document", type="primary"):
            with st.spinner("Processing document... This may take a moment."):
                result = upload_file(uploaded_file)
                
                if result and result.get("success"):
                    st.markdown('<div class="success-box">✅ <strong>Upload Successful!</strong></div>', unsafe_allow_html=True)
                    
                    # Display results
                    st.subheader("📄 Extraction Results")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Confidence", f"{result['extracted_text']['confidence']:.1%}")
                    with col2:
                        st.metric("Pages", result['extracted_text']['page_count'])
                    with col3:
                        st.metric("Processing Time", f"{result['extracted_text']['processing_time']:.2f}s")
                    
                    # Show extracted text
                    with st.expander("📝 Extracted Text", expanded=True):
                        st.text_area(
                            "Raw text:",
                            result['extracted_text']['raw_text'][:1000] + "..." if len(result['extracted_text']['raw_text']) > 1000 else result['extracted_text']['raw_text'],
                            height=200,
                            disabled=True
                        )
                    
                    # AI Processing status
                    st.markdown('<div class="processing-box">🤖 <strong>AI Processing Started</strong><br>Summarization and classification are running in the background. Check the Document Library in ~60 seconds!</div>', unsafe_allow_html=True)
                    
                    # Auto-refresh suggestion
                    if st.button("📋 Go to Document Library"):
                        st.experimental_rerun()
                else:
                    st.error("Upload failed. Please try again.")

def library_page():
    st.header("📋 Document Library")
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    # Get documents
    documents = get_documents()
    
    if not documents:
        st.info("No documents uploaded yet. Go to the Upload page to get started!")
        return
    
    # Search and filter
    search_term = st.text_input("🔍 Search documents:", placeholder="Search by filename...")
    
    # Filter documents
    if search_term:
        documents = [doc for doc in documents if search_term.lower() in doc['filename'].lower()]
    
    # Display documents
    for doc in documents:
        with st.expander(f"📄 {doc['filename']} ({doc['status']})", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Upload Date:** {datetime.fromisoformat(doc['upload_date'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**File Type:** {doc['file_type']}")
                st.write(f"**Status:** {doc['status']}")
            
            with col2:
                # Manual trigger buttons
                if st.button(f"📝 Summarize", key=f"sum_{doc['id']}"):
                    if trigger_summarization(doc['id']):
                        st.success("Summarization queued!")
                    else:
                        st.error("Failed to queue summarization")
                
                if st.button(f"🏷️ Classify", key=f"class_{doc['id']}"):
                    if trigger_classification(doc['id']):
                        st.success("Classification queued!")
                    else:
                        st.error("Failed to queue classification")
            
            # Get and display summary
            summary = get_document_summary(doc['id'])
            if summary:
                st.markdown("### 📝 Summary")
                st.markdown(f"**Type:** {summary['summary_type'].title()}")
                st.markdown(f"**Model:** {summary['model_used']}")
                st.write(summary['summary_text'])
            else:
                st.info("🤖 Summary not available yet (AI processing in progress)")
            
            # Get and display classification
            classification = get_document_classification(doc['id'])
            if classification:
                st.markdown("### 🏷️ Classification")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Topic", classification['primary_topic'])
                with col2:
                    st.metric("Category", classification['category'])
                with col3:
                    st.metric("Confidence", f"{classification['confidence']:.1%}" if classification['confidence'] else "N/A")
                
                if classification.get('tags'):
                    st.markdown("**Tags:** " + ", ".join([f"`{tag}`" for tag in classification['tags']]))
            else:
                st.info("🤖 Classification not available yet (AI processing in progress)")

def analytics_page():
    st.header("📊 Analytics Dashboard")
    
    # Refresh button
    if st.button("🔄 Refresh Analytics"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    # Get analytics data
    analytics = get_analytics()
    documents = get_documents()
    tasks = get_processing_tasks()
    
    # Overview metrics
    st.subheader("📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", len(documents))
    with col2:
        completed_docs = len([d for d in documents if d['status'] == 'completed'])
        st.metric("Processed Documents", completed_docs)
    with col3:
        pending_tasks = len([t for t in tasks if t['status'] == 'pending'])
        st.metric("Pending Tasks", pending_tasks)
    with col4:
        failed_tasks = len([t for t in tasks if t['status'] == 'failed'])
        st.metric("Failed Tasks", failed_tasks)
    
    # Topic distribution
    if analytics.get('topic_distribution'):
        st.subheader("🏷️ Topic Distribution")
        topic_data = analytics['topic_distribution']
        df = pd.DataFrame(topic_data)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(df.set_index('topic')['count'])
        with col2:
            st.dataframe(df)
    
    # Processing status
    st.subheader("⚙️ Processing Status")
    if documents:
        status_counts = {}
        for doc in documents:
            status = doc['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
        st.bar_chart(status_df.set_index('Status'))
    
    # Recent activity
    st.subheader("📅 Recent Documents")
    recent_docs = sorted(documents, key=lambda x: x['upload_date'], reverse=True)[:5]
    
    for doc in recent_docs:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"📄 {doc['filename']}")
        with col2:
            st.write(doc['status'])
        with col3:
            upload_time = datetime.fromisoformat(doc['upload_date'].replace('Z', '+00:00'))
            st.write(upload_time.strftime('%m/%d %H:%M'))

def queue_page():
    st.header("⚙️ Processing Queue")
    
    # Refresh button
    if st.button("🔄 Refresh Queue"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    # Get tasks
    tasks = get_processing_tasks()
    
    if not tasks:
        st.info("No processing tasks in queue.")
        return
    
    # Filter by status
    status_filter = st.selectbox("Filter by status:", ["All", "pending", "processing", "completed", "failed"])
    
    if status_filter != "All":
        tasks = [t for t in tasks if t['status'] == status_filter]
    
    # Display tasks
    for task in tasks:
        status_emoji = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'failed': '❌'
        }
        
        emoji = status_emoji.get(task['status'], '❓')
        
        with st.expander(f"{emoji} {task['task_type'].title()} Task - {task['status']}", expanded=task['status'] in ['processing', 'failed']):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Document ID:** {task['document_id']}")
                st.write(f"**Task Type:** {task['task_type']}")
                st.write(f"**Priority:** {task['priority']}")
                st.write(f"**Status:** {task['status']}")
            
            with col2:
                created_time = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
                st.write(f"**Created:** {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if task.get('started_at'):
                    started_time = datetime.fromisoformat(task['started_at'].replace('Z', '+00:00'))
                    st.write(f"**Started:** {started_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if task.get('completed_at'):
                    completed_time = datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                    st.write(f"**Completed:** {completed_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if task.get('error_message'):
                st.error(f"Error: {task['error_message']}")

if __name__ == "__main__":
    main()