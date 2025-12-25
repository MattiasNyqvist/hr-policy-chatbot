"""
Document processing module for extracting text from PDF and DOCX files.
"""

import os
from pypdf import PdfReader
from docx import Document
from typing import List, Dict

def extract_text_from_pdf(file_path: str) -> List[Dict[str, any]]:
    """
    Extract text from PDF file, page by page.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of dictionaries with page number and text
    """
    try:
        reader = PdfReader(file_path)
        pages = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                pages.append({
                    'page': page_num,
                    'text': text,
                    'source': os.path.basename(file_path)
                })
        
        return pages
    except Exception as e:
        print(f"Error extracting PDF {file_path}: {e}")
        return []


def extract_text_from_docx(file_path: str) -> List[Dict[str, any]]:
    """
    Extract text from DOCX file, paragraph by paragraph.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        List of dictionaries with paragraph number and text
    """
    try:
        doc = Document(file_path)
        paragraphs = []
        
        for para_num, paragraph in enumerate(doc.paragraphs, start=1):
            text = paragraph.text.strip()
            if text:
                paragraphs.append({
                    'paragraph': para_num,
                    'text': text,
                    'source': os.path.basename(file_path)
                })
        
        return paragraphs
    except Exception as e:
        print(f"Error extracting DOCX {file_path}: {e}")
        return []


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for better context retrieval.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


def process_document(file_path: str) -> List[Dict[str, any]]:
    """
    Process a document (PDF or DOCX) and extract text chunks.
    
    Args:
        file_path: Path to document
        
    Returns:
        List of document chunks with metadata
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        pages = extract_text_from_pdf(file_path)
        chunks = []
        
        for page in pages:
            text_chunks = chunk_text(page['text'])
            for chunk in text_chunks:
                chunks.append({
                    'text': chunk,
                    'source': page['source'],
                    'page': page['page']
                })
        
        return chunks
    
    elif file_ext in ['.docx', '.doc']:
        paragraphs = extract_text_from_docx(file_path)
        chunks = []
        
        for para in paragraphs:
            if len(para['text']) > 500:
                text_chunks = chunk_text(para['text'])
                for chunk in text_chunks:
                    chunks.append({
                        'text': chunk,
                        'source': para['source'],
                        'paragraph': para['paragraph']
                    })
            else:
                chunks.append({
                    'text': para['text'],
                    'source': para['source'],
                    'paragraph': para['paragraph']
                })
        
        return chunks
    
    else:
        print(f"Unsupported file type: {file_ext}")
        return []