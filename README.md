# T&C Clarity - Legal Terms AI Summarizer (MVP)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

An intelligent application that analyzes Terms & Conditions documents to extract key legal clauses, identify risks, and provide plain-language explanations. Analyze loan agreements, contracts, and T&Cs before signing!

> **Status**: Phase 2 Complete! ✅ Comprehensive legal risk analysis with 16 pattern categories + AI catch-all working!

> **MVP Approach**: Functional, simple implementation focused on getting core features working. Clean code, minimal complexity, maximum learning.

## 🎯 Project Overview

This is an LLMOps learning project with a **pragmatic MVP approach**:
- Simple, readable code structure (everything starts in `app.py`)
- Three input methods: Copy-paste text, URL scraping, File upload (PDF/TXT)
- PostgreSQL for document storage
- Ready for incremental feature additions (summarization, RAG, red flags)

## ✨ Features (Currently Working)

### ✅ Phase 1: Core Upload & Storage (COMPLETE)
- 📄 **3 Input Methods** - Copy-paste text, URL scraping, or file upload (PDF/TXT)
- 💾 **PostgreSQL Storage** - Persistent document storage
- 🐳 **Docker Setup** - One-command database deployment
- 📡 **REST API** - FastAPI with interactive docs

### ✅ Phase 2: Legal Risk Analysis (COMPLETE)
- 🔍 **16 Pattern Categories** - Interest rates, fees, penalties, termination rights, obligations, security/collateral, loan amount, repayment terms, loan duration, default consequences, change terms rights, grace period, insurance requirements, personal guarantee, prepayment rules, jurisdiction
- 🤖 **AI Catch-All** - Flan-T5 finds unusual/hidden clauses missed by patterns
- ⚠️ **Risk Assessment** - HIGH/MEDIUM/LOW risk classification
- 📊 **Comprehensive Analysis** - Finds 20-30 critical clauses in 10-20 seconds
- 📖 **Legal Glossary** - Plain-language explanations of legal terms
- 💻 **Web UI** - Clean interface with file/URL/text input

### 🚧 Coming Next (Phase 3)
- 💬 **Interactive Q&A** - RAG-powered questions about your document
- 🔍 **Semantic Search** - ChromaDB vector store integration
- 📊 **Document Com (Current)

```
┌─────────────────────────┐
│   Web UI (frontend/)    │
│   - File/URL/Text input │
│   - Results display     │
└───────────┬─────────────┘
            │
       ┌────▼────────────────┐
       │   FastAPI Backend   │
       │   (app.py)          │
       └───┬────────────┬────┘
           │            │
    ┌──────▼──────┐   ┌▼──────────────┐
    │ Flan-T5 AI  │   │ PostgreSQL DB │
    │ (3GB model) │   │ (via Docker)  │
    └─────────────┘   └───────────────┘
```

**Tech Stack:**
- **Backend**: FastAPI, SQLAlchemy, PyPDF2, BeautifulSoup
- **AI**: Hugging Face Transformers (Flan-T5-large)
- **Database**: PostgreSQL
- **Frontend**: Pure HTML/CSS/JavaScript
- **Infrastructure**: Docker, uvicorn │   PostgreSQL DB      │
    └──────────────────────┘
```

## 🚀 Quick Start (5 Minutes!)

### Prerequisites
- Python 3.10+
- 4GB+ RAM (for AI model)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/NihalKA/legal-terms-ai-summarizer.git
cd legal-terms-ai-summarizer
```

2. **Start PostgreSQL**
```bash
docker-compose up -d
```

3. **Set up Python environment**
```bash
# Create virtual environment and install dependencies
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. **Run the backend**
```bash
python app.py
```
⏳ First run downloads Flan-T5 model (3GB) - takes 2-5 minutes

5. **Open the UI**
```bash
# In a new terminal
open frontend/index.html
```

Visit **http://localhost:8000/docs** for
Visit **http://localhost:8000/docs** for interactive API documentation!

## Web UI (Recommended)
1. Open `frontend/index.html` in your browser
2. Choose input method:
   - **File Upload**: Select PDF/TXT (e.g., loan agreement)
   - **URL**: Enter terms page URL
   - **Text**: Paste T&C text directly (50+ chars)
3. Click "Analyze Document"
4. Wait 10-20 seconds for comprehensive analysis
5. Review risk level, key clauses, and glossary

### API Usage

#### 1. Upload Document (3 Methods)
```bash
# Option 1: Copy-Paste Text
curl -X POST "http://localhost:8000/analyze" \
  -F "text_input=Your terms and conditions text here..."

# Option 2: URL Scraping
curl -X POST "http://localhost:8000/analyze" \
  -F "url=https://example.com/terms"

# Option 3: File Upload (PDF or TXT)
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@path/to/terms.pdf"
```

#### 2. Get Comprehensive Analysis
```bash
curl "http://localhost:8000/summarize/{doc_id}?method=comprehensive"
```

Returns:
- ⚠️ Risk level (HIGH/MEDIUM/LOW)
- 📊 17 category findings summary
- 📋 20-30 extracted key clauses
- 📖 Legal terms glossary
- ⚡ 10-20 second analysis time

### Test All Features
```bash
python test_api.py
```

### Interactive API Docs
legal-terms-ai-summarizer/
├── app.py                    # 🎯 Backend API (950 lines)
│                             #    - 3 input methods
│                             #    - 16 pattern categories
│                             #    - AI catch-all
│                             #    - Risk calculation
│
├── frontend/                 # 💻 Web UI
│   ├── index.html           #    Main page (3 input methods)
│   ├── styles.css           #    Modern card-based design
│   ├── script.js            #    API integration
│   └── README.md            #    Frontend docs
│
├── docker-compose.yml        # 🐳 PostgreSQL setup
├── pyproject.toml            # 📦 Dependencies
├── test_api.py              # ✅ API tests
│
├── data/                    # 💾 Storage (auto-created)
│   ├── raw/                # Uploaded files
│   ├── processed/          # Processed data
│   └── vector_store/       # ChromaDB (Phase 3)
│
├── docs/                    # 📚 Documentation
│   ├── API_MVP.md          # API reference
│   ├── MVP_GUIDE.md        # Development guide
│   └── NEXT_STEPS.md       # Feature roadmap
│
└── README.md               # This file
```

**Current Philosophy:**
- ✅ **Working**: Phases 1 & 2 complete (upload + analysis)
- ✅ **Simple**: Main logic in app.py (950 lines)
- ✅ **Tested**: ABCD loan document finds 30 clauses in 15 seconds
- ✅ **Ready**: Foundation for Phase 3 (RAG Q&A)
## 📚 Documentation

- **[Phase 0: Setup Guide](https://ernihalka.atlassian.net/wiki/spaces/LLMOps/pages/426051)** - Complete setup instructions
- [API Documentation](docs/API.md) - Complete API reference
- [Architecture Guide](docs/ARCHITECTURE.md) - System design details
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Contributing Guide](docs/CONTRIBUTING.md) - Development guidelines

## 🗺️ Roadmap

### Phase 0: Setup (Week 1) ✅
- [x] Project structure
- [x] Development environment
- [x] Docker services

### Phase 1: Core Infrastructure (Week 2) 🔄
- [ ] Database models
- [ ] API skeleton
- [ ] Configuration management

### Phase 2: Document Processing (Week 3)
- [ ] PDF extraction
- [ ] Text cleaning
- [ ] Chunking logic

### Phase 3: Embedding & Vector Store (Week 4)
- [ ] Hugging Face integration
- [ ] Generate embeddings
- [ ] Chroma setup

### Phase 4: RAG Pipeline (Week 5)
- [ ] LangChain chains
- [ ] Retrieval logic
- [ ] Response generation

### Phase 5: Analysis Engine (Week 6)
- [ ] Summarization
- [ ] Red flag detection
- [ ] Risk scoring

### Phase 6: API Endpoints (Week 7)
- [ ] Upload endpoint
- [ ] Analysis endpoint
- [ ] Query endpoint

### Phase 7: Caching & Optimization (Week 8)
- [ ] Redis integration
- [ ] Semantic caching

### Phase 8: Monitoring Setup (Week 9)
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] LangSmith tracing

### Phase 9: Evaluation Framework (Week 10)
- [ ] Test dataset creation
- [ ] Metrics implementation
- [ ] MLflow integration
Development Roadmap

### ✅ Phase 1: Core Upload & Storage (COMPLETE)
- [x] Three input methods (text, URL, file)
- [x] PDF & TXT extraction
- [x] URL scraping with BeautifulSoup
- [x] PostgreSQL storage
- [x] Basic CRUD endpoints
- [x] Docker setup
- [x] API test suite

### ✅ Phase 2: Legal Risk Analysis (COMPLETE)
- [x] 16 pattern categories with 100+ regex patterns
- [x] Flan-T5 AI catch-all for unusual clauses
- [x] Risk level calculation (HIGH/MEDIUM/LOW)
- [x] `/summarize/{doc_id}` endpoint
- [x] Legal terms glossary
- [x] Web UI (file/URL/text input)
- [x] Results display with accordion
- [x] Download report feature

**Current Status:** 30 clauses found in 15 seconds (ABCD test), HIGH RISK classification working correctly

### 🚧 Phase 3: RAG Q&A System (Next - 1 week)
- [ ] Set up ChromaDB vector store
- [ ] Chunk documents (500-word chunks, 50-word overlap)
- [ ] Generate embeddings with sentence-transformers
- [ ] Create `/ask/{doc_id}` endpoint
- [ ] Context-aware Q&A (e.g., "What happens if I miss 2 payments?")
- [ ] Add Q&A section to web UI

### 📋 Phase 4: Enhancements (Future)
- [ ] Document comparison feature
- [ ] Multi-language support (Hindi, Spanish)
- [ ] Export to PDF report
- [ ] Save analysis history
- [ ] Caching with Redis
- [ ] Monitoring & metrics
- [ ] CI/CD pipeline

### 🎯 Long-term Vision
- [ ] Mobile app
- [ ] Browser extension
- [ ] Document type detection (loan/employment/rental/SaaS)
- [ ] Specialized patterns per document type
- [ ] Collaborative analysis (share with lawyer)extraction & web scraping (PyPDF2, BeautifulSoup)
- ✅ Docker containerization
- ✅ AI model integration (Hugging Face Transformers)
- ✅ Regex pattern matching for legal text
- ✅ Hybrid AI approach (patterns + ML)
- ✅ Frontend-backend integration
- 🚧 Vector databases & embeddings (Phase 3)
- 🚧 RAG (Retrieval-Augmented Generation) (Phase 3)

## 📚 Documentation

- **[docs/API_MVP.md](docs/API_MVP.md)** - Complete API reference
- **[docs/MVP_GUIDE.md](docs/MVP_GUIDE.md)** - Development philosophy  
- **[docs/NEXT_STEPS.md](docs/NEXT_STEPS.md)** - Implementation guides
- **[frontend/README.md](frontend/README.md)** - UI documentation
- **Interactive API Docs**: http://localhost:8000/docs

## 🎯 Key Achievements

- ⚡ **Fast Analysis**: 20-30 clauses in 10-20 seconds
- 🎯 **Accurate**: Finds interest rates, penalties, hidden termination rights
- 🔍 **Comprehensive**: 16 pattern categories + AI catch-all
- 💻 **User-Friendly**: Clean web UI with 3 input methods
- 📖 **Educational**: Legal glossary explains complex terms
- 🏗️ **Solid Foundation**: Ready for Phase 3 RAG Q&A