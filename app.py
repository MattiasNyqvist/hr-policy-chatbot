"""
HR Policy Chatbot - RAG-powered assistant for HR policy questions

Copyright (c) 2025 Mattias Nyqvist
Licensed under the MIT License - see LICENSE file for details
"""

import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from document_processor import process_document
from vector_store import VectorStore
from chat_engine import ChatEngine
from export_utils import export_chat_to_text, export_chat_to_json
from version import __version__, __author__, __license__

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="HR Policy Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStore()

if 'chat_engine' not in st.session_state:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        st.session_state.chat_engine = ChatEngine(api_key=api_key)
    else:
        st.session_state.chat_engine = None

if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

if 'language' not in st.session_state:
    st.session_state.language = "Swedish"

# Title
st.title("HR Policy Chatbot")
st.markdown("Ask questions about HR policies and get instant answers with source citations.")

# Sidebar - Document Management
st.sidebar.header("Document Management")

# File uploader
uploaded_files = st.sidebar.file_uploader(
    "Upload HR Policy Documents",
    type=['pdf', 'docx'],
    accept_multiple_files=True,
    help="Upload PDF or DOCX files containing HR policies"
)

if uploaded_files:
    if st.sidebar.button("Process Documents", type="primary"):
        with st.sidebar.status("Processing documents...", expanded=True) as status:
            # Create upload directory if not exists
            upload_dir = Path("data/uploaded_docs")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            total_chunks = 0
            newly_processed = []
            errors = []
            
            for uploaded_file in uploaded_files:
                try:
                    # Skip if already processed
                    if uploaded_file.name in st.session_state.processed_files:
                        st.write(f"Skipping {uploaded_file.name} (already processed)")
                        continue
                    
                    # Save file temporarily
                    file_path = upload_dir / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Process document
                    st.write(f"Processing {uploaded_file.name}...")
                    chunks = process_document(str(file_path))
                    
                    if chunks:
                        # Add to vector store
                        st.session_state.vector_store.add_documents(chunks)
                        total_chunks += len(chunks)
                        newly_processed.append(uploaded_file.name)
                        st.session_state.processed_files.append(uploaded_file.name)
                        st.write(f"✓ Extracted {len(chunks)} chunks from {uploaded_file.name}")
                    else:
                        errors.append(f"{uploaded_file.name}: No text extracted")
                        st.warning(f"Could not extract text from {uploaded_file.name}")
                
                except Exception as e:
                    errors.append(f"{uploaded_file.name}: {str(e)}")
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            status.update(label="Processing complete!", state="complete")
            
            # Summary
            if newly_processed:
                st.sidebar.success(f"Successfully processed {len(newly_processed)} new documents ({total_chunks} chunks)")
            
            if errors:
                with st.sidebar.expander("Errors"):
                    for error in errors:
                        st.error(error)

# Show collection stats
st.sidebar.markdown("---")
st.sidebar.subheader("Database Status")

doc_count = st.session_state.vector_store.get_collection_count()
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Chunks", doc_count)
with col2:
    st.metric("Files", len(st.session_state.processed_files))

# Show processed files
if st.session_state.processed_files:
    with st.sidebar.expander("Processed Files"):
        for filename in st.session_state.processed_files:
            st.text(f"- {filename}")

# Clear database
if doc_count > 0:
    st.sidebar.markdown("---")
    if st.sidebar.button("Clear All Documents", type="secondary"):
        if st.sidebar.checkbox("Confirm deletion"):
            st.session_state.vector_store.clear_collection()
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.session_state.processed_files = []
            st.sidebar.success("All documents cleared")
            st.rerun()

# Language selection
st.sidebar.markdown("---")
st.sidebar.subheader("Language / Språk")

language = st.sidebar.radio(
    "Select response language:",
    ["Swedish", "English"],
    help="Choose the language for AI responses"
)

st.session_state.language = language

# Main chat interface
if doc_count == 0:
    st.info("Upload HR policy documents to get started. The chatbot will answer questions based on the uploaded content.")
    
    st.markdown("### Example Questions")
    st.markdown("""
    Once you upload documents, you can ask questions like:
    - How many vacation days do employees get?
    - What is the sick leave policy?
    - How do I request time off?
    - What are the remote work guidelines?
    - What is the parental leave policy?
    """)
    st.stop()

if not st.session_state.chat_engine:
    st.error("API key not configured. Please set ANTHROPIC_API_KEY in .env file.")
    st.code("ANTHROPIC_API_KEY=your-api-key-here", language="bash")
    st.stop()

# Suggested questions
if not st.session_state.messages:
    st.markdown("### Suggested Questions")
    col1, col2, col3 = st.columns(3)
    
    suggestions = [
        "How many vacation days do I get?",
        "What is the sick leave policy?",
        "How do I request time off?"
    ]
    
    for i, (col, suggestion) in enumerate(zip([col1, col2, col3], suggestions)):
        with col:
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                
                with st.spinner("Searching policies..."):
                    answer, sources = st.session_state.chat_engine.answer_question(
                        suggestion,
                        st.session_state.chat_history,
                        language=st.session_state.language
                    )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
                
                st.session_state.chat_history.append({"role": "user", "content": suggestion})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
                st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show sources if available
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    source_name = source['metadata'].get('source', 'Unknown')
                    st.markdown(f"**Source {i}:** {source_name}")
                    
                    if 'page' in source['metadata']:
                        st.markdown(f"**Page:** {source['metadata']['page']}")
                    
                    if 'paragraph' in source['metadata']:
                        st.markdown(f"**Paragraph:** {source['metadata']['paragraph']}")
                    
                    # Show relevance score if available
                    if source.get('distance') is not None:
                        relevance = 1 - source['distance']
                        st.markdown(f"**Relevance:** {relevance:.1%}")
                    
                    st.markdown(f"**Excerpt:**")
                    st.text(source['text'][:300] + "..." if len(source['text']) > 300 else source['text'])
                    
                    if i < len(message["sources"]):
                        st.markdown("---")

# Chat input
if prompt := st.chat_input("Ask a question about HR policies..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from chat engine
    with st.chat_message("assistant"):
        with st.spinner("Searching policies..."):
            try:
                answer, sources = st.session_state.chat_engine.answer_question(
                    prompt,
                    st.session_state.chat_history,
                    language=st.session_state.language
                )
                
                st.markdown(answer)
                
                # Show sources
                if sources:
                    with st.expander("View Sources"):
                        for i, source in enumerate(sources, 1):
                            source_name = source['metadata'].get('source', 'Unknown')
                            st.markdown(f"**Source {i}:** {source_name}")
                            
                            if 'page' in source['metadata']:
                                st.markdown(f"**Page:** {source['metadata']['page']}")
                            
                            if 'paragraph' in source['metadata']:
                                st.markdown(f"**Paragraph:** {source['metadata']['paragraph']}")
                            
                            if source.get('distance') is not None:
                                relevance = 1 - source['distance']
                                st.markdown(f"**Relevance:** {relevance:.1%}")
                            
                            st.markdown(f"**Excerpt:**")
                            st.text(source['text'][:300] + "..." if len(source['text']) > 300 else source['text'])
                            
                            if i < len(sources):
                                st.markdown("---")
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
                
                # Update chat history for context
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                st.info("Please try rephrasing your question or check if documents are properly loaded.")

# Chat controls
if st.session_state.messages:
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()

# Export chat
if st.session_state.messages:
    st.markdown("---")
    st.subheader("Export Chat")
    
    col1, col2 = st.columns(2)
    
    with col1:
        chat_text = export_chat_to_text(st.session_state.messages)
        st.download_button(
            label="Download as Text",
            data=chat_text,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        chat_json = export_chat_to_json(st.session_state.messages)
        st.download_button(
            label="Download as JSON",
            data=chat_json,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Footer
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("**HR Policy Chatbot** | AI-powered document search")
with col2:
    st.markdown(f"v{__version__}")

st.caption(f"© 2025 {__author__}")