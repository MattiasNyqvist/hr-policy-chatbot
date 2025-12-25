# HR Policy Chatbot

AI-powered chatbot that reads HR policy documents and answers employee questions instantly with exact source citations.

![HR Policy Chatbot](screenshot_chat.png)

## Problem

HR departments receive 50-100 repetitive policy questions per month:
- "How many vacation days do I get?"
- "What's the sick leave policy?"
- "How do I request parental leave?"

**Current solution:** HR manually searches through multiple documents and responds individually.

**Time cost:** 10+ hours per month answering the same questions.

## Solution

AI chatbot that:
- Reads unlimited HR policy documents (PDF, DOCX)
- Answers questions instantly with exact source citations
- Available 24/7 for all employees
- Saves HR 10+ hours/month

![Document Processing](screenshot_upload.png)

## How It Works

### 1. RAG (Retrieval Augmented Generation) Architecture
```
Document Upload → Text Extraction → Chunking → Vector Embeddings → ChromaDB Storage
                                                                            ↓
Employee Question → Vector Search → Relevant Context → Claude AI → Answer + Sources
```

### 2. Key Features

**Document Processing:**
- Upload multiple PDF and DOCX files
- Automatic text extraction and chunking
- Intelligent overlap for context preservation
- Metadata tracking (page numbers, sources)

**Smart Search:**
- Semantic search using sentence transformers
- Finds relevant information across all documents
- Relevance scoring and filtering
- Returns top 5 most relevant sections

**AI-Powered Answers:**
- Uses Claude AI for natural language understanding
- Provides answers ONLY from uploaded documents
- Includes exact source citations (document name, page number)
- Responds in Swedish (configurable)

**User Experience:**
- Clean chat interface
- Suggested questions for new users
- View source documents for each answer
- Export chat history (text/JSON)
- Clear chat functionality

## Tech Stack

- **Python 3.11+** - Core language
- **Streamlit** - Web application framework
- **ChromaDB** - Vector database for embeddings
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **Claude AI (Anthropic)** - Natural language processing
- **PyPDF** - PDF text extraction
- **python-docx** - DOCX text extraction

## Installation

### Prerequisites
- Python 3.11 or higher
- Anthropic API key

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/hr-policy-chatbot.git
cd hr-policy-chatbot
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure API key:**

Create `.env` file:
```env
ANTHROPIC_API_KEY=your-api-key-here
```

5. **Run the application:**
```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

## Usage

### Upload Documents

1. Click "Upload HR Policy Documents" in sidebar
2. Select PDF or DOCX files (multiple files supported)
3. Click "Process Documents"
4. Wait for processing to complete

### Ask Questions

**Simple questions:**
- "How many vacation days do I get?"
- "What is the sick leave policy?"
- "How do I request time off?"

**Complex questions:**
- "I started March 15, 2024 and work 80%. I want to take 18 days vacation in July 2025, but have only used 3 days in 2024. How many days do I have available total in July, will I lose any days, and do I need special approval?"

The AI will:
- Search through all uploaded documents
- Find relevant policy sections
- Provide accurate answer with source citations
- Show page numbers and document names

### View Sources

Click "View Sources" under any answer to see:
- Document name
- Page number or section
- Relevance score
- Exact text excerpt used

### Export Chat

Download your conversation:
- Text format (readable transcript)
- JSON format (structured data)

## Project Structure
```
hr-policy-chatbot/
├── app.py                      # Main Streamlit application
├── document_processor.py       # PDF/DOCX text extraction
├── vector_store.py            # ChromaDB vector database management
├── chat_engine.py             # RAG logic and Claude AI integration
├── export_utils.py            # Chat export functionality
├── requirements.txt           # Python dependencies
├── .env                       # API key configuration
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
├── data/
│   └── uploaded_docs/        # Temporary document storage
├── chroma_db/                # Vector database storage
└── README.md                 # This file
```

## How RAG Works

### Traditional Approach (Expensive)
```
Question → Send ENTIRE document to LLM → Answer
Cost: Full document tokens × every question
```

### RAG Approach (Cost-Effective)
```
Question → Vector Search (finds 3-5 relevant chunks) → Send only relevant chunks to LLM → Answer
Cost: Only relevant chunks × question (90% cheaper)
```

### Example

**Scenario:** Company with 50 HR policy documents (5,000 pages total)

**Traditional:**
- Cannot upload all documents (LLM context limit)
- Must upload full docs for each question
- Cost: 5,000 pages × 2,000 tokens × 100 questions = Extremely expensive

**RAG:**
- Upload once, store in vector database
- Each question retrieves only 3-5 relevant chunks (~1,500 tokens)
- Cost: 1,500 tokens × 100 questions = 90% cheaper
- Unlimited documents supported

## Business Value

### Time Savings

**Before:**
- HR receives 100 policy questions/month
- 6 minutes per question (search + respond)
- Total: 10 hours/month

**After:**
- AI answers instantly
- HR only handles edge cases
- Time saved: 8+ hours/month

**Annual ROI:**
- 96 hours saved/year
- At 500 SEK/hour: **48,000 SEK/year**

### Additional Benefits

- **24/7 availability** - Employees get answers anytime
- **Consistency** - Same accurate answer every time
- **Scalability** - Handles unlimited questions simultaneously
- **Compliance** - Always references official policy documents
- **Onboarding** - New employees self-serve policy information

## Advanced Features

### Intelligent Chunking
- Text split into 500-character chunks
- 50-character overlap for context preservation
- Metadata preservation (page numbers, document name)

### Semantic Search
- Uses sentence-transformers for embeddings
- Cosine similarity for relevance scoring
- Filters results below 0.7 similarity threshold

### Context Management
- Maintains chat history (last 4 messages)
- Provides conversation continuity
- Resets when clearing chat

### Multi-Language Support
- Configured for Swedish responses
- Can be adapted to any language
- Responds in target language regardless of question language

## Future Enhancements

- [ ] Multiple document collections (vacation, benefits, remote work)
- [ ] Admin dashboard for document management
- [ ] User analytics (most asked questions)
- [ ] Integration with HRIS systems
- [ ] Multi-tenant support (different companies)
- [ ] Email notifications for policy updates
- [ ] Mobile-responsive design improvements
- [ ] Advanced search filters (date ranges, departments)

## Development

### Built With AI-Driven Development

This project demonstrates modern AI-augmented software development:
- Developed in 7 days using Claude AI as coding assistant
- Combines multiple AI technologies (RAG, vector search, LLMs)
- Production-ready architecture

### Key Learnings

**RAG Architecture:**
- Document chunking strategies
- Vector database optimization
- Semantic search tuning

**LLM Integration:**
- Prompt engineering for accuracy
- Source citation extraction
- Hallucination prevention

**Production Considerations:**
- Error handling
- User experience design
- Cost optimization

## License

MIT License - See LICENSE file for details

## Author

**[Your Name]**
- AI Consultant specializing in document processing and automation
- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [Your Profile](https://linkedin.com/in/your-profile)

## Acknowledgments

- Built with Claude AI (Anthropic)
- Vector search powered by ChromaDB
- Embeddings from sentence-transformers
- Sample policies for demonstration purposes

---

**Questions or want to implement this for your company?** Reach out on LinkedIn!