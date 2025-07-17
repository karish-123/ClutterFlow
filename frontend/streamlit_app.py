import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Optional
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your API URL
SUPPORTED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg']

# Set page config
st.set_page_config(
    page_title="ClutterFlow - Smart Document Organization",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .subject-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .upload-area {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f9f9f9;
    }
    .processing-badge {
        background: #ffc107;
        color: #212529;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .completed-badge {
        background: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .failed-badge {
        background: #dc3545;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def make_api_request(endpoint: str, method: str = "GET", data: dict = None, files: dict = None, show_error: bool = True):
    """Make API request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, data=data, timeout=60)
            else:
                response = requests.post(url, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, timeout=30)
        
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.exceptions.Timeout:
        if show_error:
            st.error("⏱️ Request timeout. The server might be busy.")
        return None
    except requests.exceptions.HTTPError as e:
        if show_error:
            if response.status_code == 500:
                st.error("🔧 Server error. Please check the backend logs.")
            elif response.status_code == 400:
                st.error("⚠️ Bad request. There might be a database query issue.")
            else:
                st.error(f"HTTP Error {response.status_code}: {str(e)}")
        return None
    except requests.exceptions.ConnectionError:
        if show_error:
            st.error("🔌 Cannot connect to API. Make sure the backend is running.")
        return None
    except requests.exceptions.RequestException as e:
        if show_error:
            st.error(f"API Error: {str(e)}")
        return None

def safe_api_call(endpoint: str, method: str = "GET", data: dict = None, files: dict = None, fallback_value=None):
    """Safe API call that returns fallback value on error"""
    result = make_api_request(endpoint, method, data, files, show_error=False)
    return result if result is not None else fallback_value

def get_status_badge(status: str):
    """Get HTML badge for document status"""
    badges = {
        "processing": '<span class="processing-badge">Processing</span>',
        "completed": '<span class="completed-badge">Completed</span>',
        "failed": '<span class="failed-badge">Failed</span>'
    }
    return badges.get(status, status)

# Initialize session state
if 'refresh_subjects' not in st.session_state:
    st.session_state.refresh_subjects = False
if 'refresh_documents' not in st.session_state:
    st.session_state.refresh_documents = False

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌊 ClutterFlow</h1>
        <p>Smart Document Organization for Students</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📁 Dashboard", "📤 Upload Documents", "📚 Subjects", "📊 Analytics", "⚙️ Settings"]
    )
    
    # Clear selected document when navigating away from dashboard
    if page != "📁 Dashboard" and 'selected_doc' in st.session_state:
        del st.session_state.selected_doc
    
    if page == "📁 Dashboard":
        dashboard_page()
    elif page == "📤 Upload Documents":
        upload_page()
    elif page == "📚 Subjects":
        subjects_page()
    elif page == "📊 Analytics":
        analytics_page()
    elif page == "⚙️ Settings":
        settings_page()

def dashboard_page():
    st.title("📁 Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    # Get analytics data with error handling
    analytics = safe_api_call("/analytics/overview", fallback_value={})
    
    with col1:
        total_docs = analytics.get('total_documents', 0) if analytics else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_docs}</h3>
            <p>Total Documents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        processing_tasks = analytics.get('processing_stats', {}).get('total_tasks', 0) if analytics else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{processing_tasks}</h3>
            <p>Processing Tasks</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Get subjects count with error handling
    subjects = safe_api_call("/subjects", fallback_value=[])
    
    with col3:
        subject_count = len(subjects) if subjects else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{subject_count}</h3>
            <p>Active Subjects</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Check API health
        health = safe_api_call("/", fallback_value=None)
        status_emoji = "✅" if health else "❌"
        status_text = "Online" if health else "Offline"
        st.markdown(f"""
        <div class="metric-card">
            <h3>{status_emoji}</h3>
            <p>{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent documents
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Recent Documents")
        documents = safe_api_call("/documents?limit=10", fallback_value={'documents': []})
        
        if documents and documents.get('documents'):
            for doc in documents['documents']:
                # Highlight selected document
                is_selected = st.session_state.get('selected_doc') == doc['id']
                expanded = is_selected
                
                with st.expander(f"📄 {doc['filename']} - {get_status_badge(doc['status'])}", expanded=expanded):
                    if is_selected:
                        st.success("👁️ Currently viewing details below")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**File Type:** {doc['file_type']}")
                        st.write(f"**Upload Date:** {doc['created_at'][:10]}")
                        st.write(f"**Status:** {doc['status']}")
                    with col_b:
                        if st.button(f"View Details", key=f"view_{doc['id']}"):
                            st.session_state.selected_doc = doc['id']
                            st.rerun()
                        if st.button(f"🗑️ Delete", key=f"del_{doc['id']}"):
                            if make_api_request(f"/documents/{doc['id']}", method="DELETE"):
                                st.success("Document deleted!")
                                st.rerun()
        else:
            st.info("No documents found. Upload your first document!")
    
    # Show document details if one is selected
    if st.session_state.get('selected_doc'):
        st.markdown("---")
        show_document_details(st.session_state.selected_doc)
    
    with col2:
        st.subheader("📚 Quick Subject Access")
        
        # Try to get subjects with stats, fallback to basic subjects
        subjects_with_stats = safe_api_call("/subjects?include_stats=true", fallback_value=None)
        if subjects_with_stats is None:
            st.warning("⚠️ Subject stats temporarily unavailable")
            subjects_basic = safe_api_call("/subjects", fallback_value=[])
            subjects_to_show = subjects_basic[:5] if subjects_basic else []
        else:
            subjects_to_show = subjects_with_stats[:5] if subjects_with_stats else []
        
        if subjects_to_show:
            for subject in subjects_to_show:
                doc_count = subject.get('document_count', 'N/A')
                st.markdown(f"""
                <div class="subject-card">
                    <strong>{subject['subject_name']}</strong><br>
                    <small>{doc_count} documents</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No subjects created yet.")
        
        if st.button("➕ Add New Subject"):
            st.session_state.show_add_subject = True

def upload_page():
    st.title("📤 Upload Documents")
    
    st.markdown("""
    <div class="upload-area">
        <h3>🎯 Smart Document Processing</h3>
        <p>Upload your documents and let AI organize them automatically!</p>
        <p><strong>Supported formats:</strong> PDF, PNG, JPG, JPEG</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.subheader(f"📁 {len(uploaded_files)} file(s) selected")
        
        # Process files
        if st.button("🚀 Process Documents", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Upload file
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                result = make_api_request("/extract", method="POST", files=files)
                
                if result and result.get('success'):
                    st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                    
                    # Show document details
                    doc = result.get('document')
                    if doc:
                        with st.expander(f"📄 {doc['filename']} Details"):
                            st.write(f"**Document ID:** {doc['id']}")
                            st.write(f"**Status:** {doc['status']}")
                            st.write(f"**File Type:** {doc['file_type']}")
                            st.write("**Note:** Document is being processed for classification and subject assignment.")
                else:
                    st.error(f"❌ Failed to process {uploaded_file.name}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("✅ All files processed!")
            st.balloons()
            
            # Add note about background processing
            st.info("🔄 Documents are being analyzed in the background. Check the Dashboard for updates on classification and subject assignment.")

def subjects_page():
    st.title("📚 Subject Management")
    
    # Add new subject section
    with st.expander("➕ Add New Subject", expanded=False):
        with st.form("add_subject_form"):
            subject_name = st.text_input("Subject Name", placeholder="e.g., Mathematics, Computer Science")
            description = st.text_area("Description (Optional)", placeholder="Brief description of the subject")
            keywords = st.text_input("Keywords (Optional)", placeholder="Comma-separated keywords for better classification")
            
            submitted = st.form_submit_button("Create Subject")
            if submitted and subject_name:
                subject_data = {
                    "subject_name": subject_name,
                    "description": description or None,
                    "keywords": [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
                }
                
                result = make_api_request("/subjects", method="POST", data=subject_data)
                if result:
                    st.success(f"✅ Subject '{subject_name}' created successfully!")
                    st.rerun()
    
    # Display existing subjects
    st.subheader("📋 Your Subjects")
    
    # Try to get subjects with stats first, fallback to basic subjects
    subjects = safe_api_call("/subjects?include_stats=true", fallback_value=None)
    if subjects is None:
        st.warning("⚠️ Unable to load subject statistics. Showing basic subject list.")
        subjects = safe_api_call("/subjects", fallback_value=[])
    
    if subjects:
        for subject in subjects:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### 📚 {subject['subject_name']}")
                    if subject.get('description'):
                        st.write(subject['description'])
                    if subject.get('keywords'):
                        st.markdown(f"**Keywords:** {', '.join(subject['keywords'])}")
                    
                    # Show document count if available
                    doc_count = subject.get('document_count')
                    if doc_count is not None:
                        st.write(f"**Documents:** {doc_count}")
                    else:
                        st.write("**Documents:** Loading...")
                
                with col2:
                    if st.button(f"👁️ View Documents", key=f"view_docs_{subject['id']}"):
                        show_subject_documents(subject['id'], subject['subject_name'])
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_subject_{subject['id']}"):
                        if st.session_state.get(f"confirm_delete_{subject['id']}", False):
                            result = make_api_request(f"/subjects/{subject['id']}", method="DELETE")
                            if result:
                                st.success(f"Subject '{subject['subject_name']}' deleted!")
                                st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{subject['id']}"] = True
                            st.warning("Click again to confirm deletion")
                
                st.markdown("---")
    else:
        st.info("No subjects created yet. Add your first subject above!")

def show_subject_documents(subject_id: str, subject_name: str):
    """Show documents for a specific subject"""
    st.subheader(f"📄 Documents in {subject_name}")
    
    documents = make_api_request(f"/subjects/{subject_id}/documents")
    if documents and documents.get('documents'):
        for doc in documents['documents']:
            with st.expander(f"📄 {doc['filename']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Status:** {doc['status']}")
                    st.write(f"**Upload Date:** {doc['created_at'][:10]}")
                    st.write(f"**File Type:** {doc['file_type']}")
                with col2:
                    if st.button(f"View Summary", key=f"summary_{doc['id']}"):
                        show_document_summary(doc['id'])
                    if st.button(f"View Classification", key=f"class_{doc['id']}"):
                        show_document_classification(doc['id'])
    else:
        st.info(f"No documents found in {subject_name}")

def show_document_summary(doc_id: str):
    """Show document summary"""
    summary = make_api_request(f"/documents/{doc_id}/summary")
    if summary:
        st.write("**Summary:**")
        st.write(summary.get('summary', 'No summary available'))
    else:
        st.info("Summary not yet available")

def show_document_classification(doc_id: str):
    """Show document classification"""
    classification = make_api_request(f"/documents/{doc_id}/classification")
    if classification:
        st.write("**Classification:**")
        st.write(f"Category: {classification.get('category', 'Unknown')}")
        st.write(f"Confidence: {classification.get('confidence', 0):.2%}")
    else:
        st.info("Classification not yet available")

def show_document_details(doc_id: str):
    """Show detailed view of a document"""
    st.subheader("📄 Document Details")
    
    # Get document details
    doc_details = make_api_request(f"/documents/{doc_id}")
    if not doc_details:
        st.error("Document not found")
        if st.button("← Back to Dashboard"):
            del st.session_state.selected_doc
            st.rerun()
        return
    
    document = doc_details.get('document')
    extracted_text = doc_details.get('extracted_text')
    
    # Document info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### 📄 {document['filename']}")
        st.write(f"**File Type:** {document['file_type']}")
        st.write(f"**Status:** {document['status']}")
        st.write(f"**Upload Date:** {document['created_at'][:19]}")
        if document.get('file_size'):
            st.write(f"**File Size:** {document['file_size']:,} bytes")
    
    with col2:
        # Action buttons
        if st.button("📝 View Summary"):
            summary = make_api_request(f"/documents/{doc_id}/summary")
            if summary:
                st.write("**Summary:**")
                st.write(summary.get('summary', 'No summary available'))
            else:
                st.info("Summary not yet available")
                if st.button("🔄 Generate Summary"):
                    result = make_api_request(f"/documents/{doc_id}/summarize", method="POST")
                    if result:
                        st.success("Summary generation queued!")
        
        if st.button("🏷️ View Classification"):
            classification = make_api_request(f"/documents/{doc_id}/classification")
            if classification:
                st.write("**Classification:**")
                st.write(f"**Category:** {classification.get('category', 'Unknown')}")
                st.write(f"**Confidence:** {classification.get('confidence', 0):.2%}")
                st.write(f"**Subject ID:** {classification.get('subject_id', 'None')}")
            else:
                st.info("Classification not yet available")
                if st.button("🔄 Generate Classification"):
                    result = make_api_request(f"/documents/{doc_id}/classify", method="POST")
                    if result:
                        st.success("Classification generation queued!")
    
    with col3:
        if st.button("← Back to Dashboard"):
            del st.session_state.selected_doc
            st.rerun()
        
        if st.button("🗑️ Delete Document"):
            if st.button("⚠️ Confirm Delete", key="confirm_delete"):
                if make_api_request(f"/documents/{doc_id}", method="DELETE"):
                    st.success("Document deleted!")
                    del st.session_state.selected_doc
                    st.rerun()
    
    # Extracted text
    if extracted_text:
        st.markdown("---")
        st.subheader("📝 Extracted Text")
        
        # Text stats
        text_length = len(extracted_text.get('raw_text', ''))
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Characters", f"{text_length:,}")
        with col2:
            st.metric("Words", f"{len(extracted_text.get('raw_text', '').split()):,}")
        with col3:
            st.metric("Confidence", f"{extracted_text.get('confidence', 0):.1%}")
        with col4:
            st.metric("Method", extracted_text.get('method_used', 'Unknown'))
        
        # Show text content
        if st.checkbox("Show full text", value=False):
            st.text_area(
                "Raw Text", 
                extracted_text.get('raw_text', ''), 
                height=300,
                disabled=True
            )
        else:
            # Show preview
            preview_text = extracted_text.get('raw_text', '')[:500]
            st.text_area(
                "Text Preview (first 500 characters)", 
                preview_text + "..." if len(extracted_text.get('raw_text', '')) > 500 else preview_text,
                height=150,
                disabled=True
            )
    else:
        st.warning("No extracted text available for this document")

def analytics_page():
    st.title("📊 Analytics & Insights")
    
    # Get analytics data
    overview = make_api_request("/analytics/overview")
    subject_analytics = make_api_request("/analytics/subjects")
    
    if overview:
        # Overview metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Documents", overview.get('total_documents', 0))
        with col2:
            st.metric("Processing Tasks", overview.get('processing_stats', {}).get('total_tasks', 0))
        with col3:
            if subject_analytics:
                st.metric("Active Subjects", subject_analytics.get('active_subjects', 0))
        
        # Topic distribution chart
        if overview.get('topic_distribution'):
            st.subheader("📈 Topic Distribution")
            topic_data = overview['topic_distribution']
            df = pd.DataFrame(topic_data)
            
            if not df.empty:
                fig = px.pie(df, values='count', names='topic', title="Document Categories")
                st.plotly_chart(fig, use_container_width=True)
    
    if subject_analytics:
        # Subject distribution
        st.subheader("📚 Subject Distribution")
        subject_dist = subject_analytics.get('subject_distribution', [])
        if subject_dist:
            df_subjects = pd.DataFrame(subject_dist)
            fig = px.bar(df_subjects, x='subject_name', y='document_count', 
                        title="Documents per Subject")
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top subjects
        st.subheader("🏆 Top Subjects")
        top_subjects = subject_analytics.get('top_subjects', [])[:5]
        for i, subject in enumerate(top_subjects, 1):
            st.write(f"{i}. **{subject.get('subject_name')}** - {subject.get('document_count', 0)} documents")

def settings_page():
    st.title("⚙️ Settings")
    
    # API Health Check
    st.subheader("🏥 System Health")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Check API Health"):
            with st.spinner("Checking API connection..."):
                health = make_api_request("/")
                if health:
                    st.success(f"✅ API Online - Version: {health.get('version', 'Unknown')}")
                    st.info(health.get('message', ''))
                else:
                    st.error("❌ API Offline")
    
    with col2:
        if st.button("🧪 Test All Endpoints"):
            endpoints_to_test = [
                ("/", "Health Check"),
                ("/subjects", "Subjects"),
                ("/documents?limit=1", "Documents"),
                ("/analytics/overview", "Analytics")
            ]
            
            for endpoint, name in endpoints_to_test:
                result = safe_api_call(endpoint, fallback_value=None)
                if result is not None:
                    st.success(f"✅ {name}")
                else:
                    st.error(f"❌ {name}")
    
    st.subheader("🔌 API Configuration")
    current_api = st.text_input("API Base URL", value=API_BASE_URL)
    
    # Show current API status
    if current_api != API_BASE_URL:
        st.warning("⚠️ API URL changed. Restart the app to apply changes.")
    
    st.subheader("📁 File Management")
    st.info(f"Supported file types: {', '.join(SUPPORTED_EXTENSIONS)}")
    
    # Debug Information
    st.subheader("🐛 Debug Information")
    if st.button("Show Recent API Logs"):
        # Get recent tasks
        tasks = safe_api_call("/tasks?limit=10", fallback_value={'tasks': []})
        if tasks and tasks.get('tasks'):
            st.write("**Recent Processing Tasks:**")
            for task in tasks['tasks']:
                status_color = "🟢" if task.get('status') == 'completed' else "🟡" if task.get('status') == 'processing' else "🔴"
                st.write(f"{status_color} {task.get('task_type')} - {task.get('status')} - {task.get('created_at', '')[:19]}")
        else:
            st.info("No recent tasks found")
    
    # Unclassified documents
    st.subheader("📋 Unclassified Documents")
    if st.button("Show Unclassified Documents"):
        unclassified = safe_api_call("/documents/unclassified", fallback_value={'documents': []})
        if unclassified and unclassified.get('documents'):
            st.write(f"Found {len(unclassified['documents'])} unclassified documents:")
            for doc in unclassified['documents']:
                with st.expander(f"📄 {doc['filename']}"):
                    st.write(f"**Status:** {doc['status']}")
                    st.write(f"**Upload Date:** {doc['created_at'][:10]}")
                    
                    # Get AI suggestion
                    if st.button(f"🤖 Get AI Suggestion", key=f"suggest_{doc['id']}"):
                        suggestion = safe_api_call(f"/documents/{doc['id']}/suggest-subject", fallback_value=None)
                        if suggestion and suggestion.get('suggestion'):
                            st.write(f"**AI Suggestion:** {suggestion['suggestion']['subject_name']}")
                            st.write(f"**Confidence:** {suggestion['suggestion']['confidence']:.2%}")
                        else:
                            st.warning("No suggestion available")
        else:
            st.success("✅ All documents are classified!")
    
    st.subheader("🧹 Cleanup & Maintenance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Cache", type="secondary"):
            if 'subject_cache' in st.session_state:
                del st.session_state.subject_cache
            if 'document_cache' in st.session_state:
                del st.session_state.document_cache
            st.success("Cache cleared!")
    
    with col2:
        if st.button("📊 Force Analytics Refresh", type="secondary"):
            analytics = make_api_request("/analytics/overview")
            if analytics:
                st.success("Analytics refreshed!")
            else:
                st.error("Failed to refresh analytics")
    
    with col3:
        if st.button("🔧 Reset Session", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Session reset!")
            st.rerun()

if __name__ == "__main__":
    main()