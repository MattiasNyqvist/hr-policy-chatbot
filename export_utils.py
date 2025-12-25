"""
Utility functions for exporting chat history and document summaries.

Copyright (c) 2024 Mattias Nyqvist
Licensed under the MIT License - see LICENSE file for details
"""

from datetime import datetime
from typing import List, Dict
import json

def export_chat_to_text(messages: List[Dict]) -> str:
    """
    Export chat history to formatted text.
    
    Args:
        messages: List of chat messages
        
    Returns:
        Formatted text string
    """
    output = []
    output.append("HR POLICY CHATBOT - CHAT HISTORY")
    output.append(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 60)
    output.append("")
    
    for i, msg in enumerate(messages, 1):
        role = msg['role'].upper()
        content = msg['content']
        
        output.append(f"[{i}] {role}:")
        output.append(content)
        output.append("")
        
        # Add sources if available
        if msg['role'] == 'assistant' and 'sources' in msg and msg['sources']:
            output.append("SOURCES:")
            for j, source in enumerate(msg['sources'], 1):
                source_name = source['metadata'].get('source', 'Unknown')
                page = source['metadata'].get('page', '')
                location = f"{source_name}"
                if page:
                    location += f", Page {page}"
                output.append(f"  {j}. {location}")
            output.append("")
        
        output.append("-" * 60)
        output.append("")
    
    return "\n".join(output)


def export_chat_to_json(messages: List[Dict]) -> str:
    """
    Export chat history to JSON.
    
    Args:
        messages: List of chat messages
        
    Returns:
        JSON string
    """
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'message_count': len(messages),
        'messages': messages
    }
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)