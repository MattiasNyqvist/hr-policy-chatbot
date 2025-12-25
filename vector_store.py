"""
Vector store module for storing and retrieving document embeddings using ChromaDB.

Copyright (c) 2025 Mattias Nyqvist
Licensed under the MIT License - see LICENSE file for details
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os

class VectorStore:
    """Manages document embeddings and similarity search."""
    
    def __init__(self, collection_name: str = "hr_policies"):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, documents: List[Dict[str, any]]):
        """
        Add documents to vector store.
        
        Args:
            documents: List of document chunks with metadata
        """
        if not documents:
            return
        
        texts = [doc['text'] for doc in documents]
        embeddings = self.embedding_model.encode(texts).tolist()
        
        ids = [f"doc_{i}" for i in range(len(documents))]
        metadatas = []
        
        for doc in documents:
            metadata = {
                'source': doc.get('source', 'unknown'),
            }
            if 'page' in doc:
                metadata['page'] = str(doc['page'])
            if 'paragraph' in doc:
                metadata['paragraph'] = str(doc['paragraph'])
            
            metadatas.append(metadata)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query: str, n_results: int = 3) -> List[Dict[str, any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        relevant_docs = []
        
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                relevant_docs.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
        
        return relevant_docs
    
    def clear_collection(self):
        """Clear all documents from collection."""
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_collection_count(self) -> int:
        """Get number of documents in collection."""
        return self.collection.count()