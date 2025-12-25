"""
Chat engine module for RAG-based question answering using Claude AI

Copyright (c) 2025 Mattias Nyqvist
Licensed under the MIT License - see LICENSE file for details
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
    
    def answer_question(self, question: str, chat_history: List[Dict] = None, language: str = "Swedish") -> Tuple[str, List[Dict]]:
        """
        Answer a question using RAG.
        
        Args:
            question: User question
            chat_history: Previous chat messages
            language: Response language ("Swedish" or "English")
            
        Returns:
            Tuple of (answer, relevant_sources)
        """
        # Search for relevant documents
        relevant_docs = self.vector_store.search(question, n_results=5)
        
        if not relevant_docs:
            if language == "Swedish":
                return "Jag har inga relevanta policydokument för att svara på denna fråga. Vänligen ladda upp HR-policydokument för att komma igång.", []
            else:
                return "I don't have any relevant policy documents to answer this question. Please upload HR policy documents to get started.", []
        
        # Filter out very low relevance results
        relevant_docs = [doc for doc in relevant_docs if doc.get('distance', 1.0) < 0.7]
        
        if not relevant_docs:
            if language == "Swedish":
                return "Jag kunde inte hitta relevant information i de uppladdade policyerna för att svara på denna fråga. Frågan kan ligga utanför de tillgängliga dokumentens omfattning.", []
            else:
                return "I couldn't find relevant information in the uploaded policies to answer this question. The question might be outside the scope of the available documents.", []
        
        # Build context from relevant documents
        context = self._build_context(relevant_docs)
        
        # Create prompt
        prompt = self._create_prompt(question, context, language)
        
        # Get response from Claude
        try:
            messages = []
            
            # Add recent chat history for context (last 4 messages)
            if chat_history and len(chat_history) > 0:
                recent_history = chat_history[-4:] if len(chat_history) > 4 else chat_history
                messages.extend(recent_history)
            
            messages.append({"role": "user", "content": prompt})
            
            # Set system message based on language
            system_message = (
                "Du är en svensk HR-assistent. Svara alltid på svenska, oavsett vilket språk frågan ställs på."
                if language == "Swedish"
                else "You are an HR assistant. Always respond in English, regardless of the question's language."
            )
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                temperature=0.3,
                system=system_message,
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
            source = doc['metadata'].get('source', 'Okänd')
            page = doc['metadata'].get('page', '')
            paragraph = doc['metadata'].get('paragraph', '')
            
            location = f"Källa: {source}"
            if page:
                location += f", Sida {page}"
            elif paragraph:
                location += f", Avsnitt {paragraph}"
            
            context_parts.append(f"[Dokument {i}] ({location})\n{doc['text']}")
        
        return "\n\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str, language: str = "Swedish") -> str:
        """Create prompt for Claude with language support."""
        
        if language == "Swedish":
            return f"""Du är en hjälpsam HR-assistent. Svara på medarbetarens fråga baserat på de tillhandahållna HR-policydokumenten.

POLICYDOKUMENT:
{context}

MEDARBETARENS FRÅGA: {question}

INSTRUKTIONER:
1. Svara ENDAST baserat på informationen i de tillhandahållna policydokumenten
2. Om dokumenten inte innehåller den information som behövs, säg tydligt: "Jag har ingen information om detta i de tillgängliga HR-policyerna"
3. Var specifik och referera till vilket dokument/sida du hänvisar till
4. Använd en vänlig, professionell ton
5. Om policyer är oklara eller kan tolkas på flera sätt, nämn detta
6. Håll svaren koncisa men fullständiga
7. Hitta inte på eller anta information som inte finns i dokumenten
8. Svara alltid på SVENSKA

SVAR:"""
        
        else:  # English
            return f"""You are a helpful HR assistant. Answer the employee's question based on the provided HR policy documents.

POLICY DOCUMENTS:
{context}

EMPLOYEE'S QUESTION: {question}

INSTRUCTIONS:
1. Answer ONLY based on the information in the provided policy documents
2. If the documents don't contain the needed information, clearly state: "I don't have information about this in the available HR policies"
3. Be specific and reference which document/page you're referring to
4. Use a friendly, professional tone
5. If policies are unclear or can be interpreted in multiple ways, mention this
6. Keep answers concise but complete
7. Don't make up or assume information not in the documents
8. Always respond in ENGLISH

ANSWER:"""