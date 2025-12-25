"""
Chat engine module for RAG-based question answering using Claude AI.
"""

import anthropic
import os
from typing import List, Dict, Tuple
from vector_store import VectorStore

class ChatEngine:
    """Handles RAG-based chat with document context."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize chat engine.
        
        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.vector_store = VectorStore()
    
    def answer_question(self, question: str, chat_history: List[Dict] = None) -> Tuple[str, List[Dict]]:
        """
        Answer a question using RAG.
        
        Args:
            question: User question
            chat_history: Previous chat messages
            
        Returns:
            Tuple of (answer, relevant_sources)
        """
        # Search for relevant documents
        relevant_docs = self.vector_store.search(question, n_results=5)
        
        if not relevant_docs:
            return "I don't have any relevant policy documents to answer this question. Please upload HR policy documents to get started.", []
        
        # Filter out very low relevance results
        relevant_docs = [doc for doc in relevant_docs if doc.get('distance', 1.0) < 0.7]
        
        if not relevant_docs:
            return "I couldn't find relevant information in the uploaded policies to answer this question. The question might be outside the scope of the available documents.", []
        
        # Build context from relevant documents
        context = self._build_context(relevant_docs)
        
        # Create prompt
        prompt = self._create_prompt(question, context)
        
        # Get response from Claude
        try:
            messages = []
            
            # Add recent chat history for context (last 4 messages)
            if chat_history and len(chat_history) > 0:
                recent_history = chat_history[-4:] if len(chat_history) > 4 else chat_history
                messages.extend(recent_history)
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                temperature=0.3,
                system="Du är en svensk HR-assistent. Svara alltid på svenska, oavsett vilket språk frågan ställs på.",  # NYTT
                messages=messages
            )
            
            answer = response.content[0].text
            
            return answer, relevant_docs
            
        except Exception as e:
            return f"Error generating response: {str(e)}", []
    
    def _build_context(self, relevant_docs: List[Dict]) -> str:
        """Build context string from relevant documents."""
        context_parts = []
        
        for i, doc in enumerate(relevant_docs, 1):
            source = doc['metadata'].get('source', 'Unknown')
            page = doc['metadata'].get('page', '')
            paragraph = doc['metadata'].get('paragraph', '')
            
            location = f"Source: {source}"
            if page:
                location += f", Page {page}"
            elif paragraph:
                location += f", Section {paragraph}"
            
            context_parts.append(f"[Document {i}] ({location})\n{doc['text']}")
        
        return "\n\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create prompt for Claude."""
        return f"""You are a helpful HR policy assistant. Answer the employee's question based on the provided HR policy documents.

POLICY DOCUMENTS:
{context}

EMPLOYEE QUESTION: {question}

INSTRUCTIONS:
1. Answer based ONLY on the information in the provided policy documents
2. If the documents don't contain the information needed, clearly state: "I don't have information about this in the available HR policies"
3. Be specific and cite which document/page you're referencing
4. Use a friendly, professional tone
5. If policies are unclear or could be interpreted multiple ways, mention this
6. Keep answers concise but complete
7. Don't make up or assume information not in the documents

ANSWER:"""