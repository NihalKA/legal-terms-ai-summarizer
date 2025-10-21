# T&C Clarity - Legal Terms AI Summarizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)](https://www.langchain.com/)

An intelligent application that analyzes Terms & Conditions documents to extract key information, identify hidden clauses, and provide plain-language summaries. Never blindly accept T&Cs again!

## 🎯 Project Overview

This LLMOps project demonstrates production-ready implementation of:
- **OpenAPI** - RESTful API design and documentation
- **Hugging Face** - LLM models for summarization and embeddings
- **Vector Database** - Semantic search using ChromaDB
- **LangChain** - LLM workflow orchestration
- **MLOps Best Practices** - Monitoring, versioning, and evaluation

## ✨ Features

### Core Capabilities
- 📄 **Multi-format Support** - Process PDF, text files, and web URLs
- 🎯 **Smart Summarization** - Generate concise executive summaries
- 🚩 **Red Flag Detection** - Identify concerning clauses automatically
- 📊 **Risk Scoring** - Calculate overall risk score (0-100)
- 💬 **Interactive Q&A** - RAG-powered question answering
- 🔍 **Semantic Search** - Find similar clauses across documents
- 📑 **Section Classification** - Automatically categorize T&C sections

### LLMOps Features
- 🔄 **Experiment Tracking** - MLflow integration
- 📈 **Monitoring** - Prometheus + Grafana dashboards
- 🧪 **Automated Testing** - Evaluation metrics (ROUGE, accuracy)
- 🚀 **CI/CD Pipeline** - GitHub Actions automation
- 📝 **Prompt Versioning** - Git-based prompt management
- ⚡ **Performance Optimization** - Redis caching

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend/CLI  │
└────────┬────────┘
         │
    ┌────▼────────────┐
    │   FastAPI       │
    │   REST API      │
    └────┬────────────┘
         │
    ┌────▼────────────────────────┐
    │    LangChain Orchestration  │
    └───┬─────────────┬───────────┘
        │             │
   ┌────▼───┐   ┌────▼──────────┐
   │ HF     │   │  ChromaDB     │
   │ Models │   │  Vector Store │
   └────────┘   └───────────────┘
         │             │
    ┌────▼─────────────▼───┐
    │   PostgreSQL DB      │
    └──────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Git
- Hugging Face API key (free tier available)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/NihalKA/legal-terms-ai-summarizer.git
cd legal-terms-ai-summarizer
```

2. **Set up environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings:
# - HUGGINGFACE_API_KEY
# - LANGCHAIN_API_KEY
# - DATABASE_URL
# - REDIS_URL
```

4. **Start services with Docker**
```bash
docker-compose up -d
```

5. **Initialize database**
```bash
python scripts/init_db.py
```

6. **Start the API server**
```bash
uvicorn src.api.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📖 Usage

### API Endpoints

#### Upload and Analyze Document
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@terms.pdf"
```

#### Query Document with RAG
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "123", "question": "What data do they collect?"}'
```

#### Get Risk Analysis
```bash
curl -X GET "http://localhost:8000/api/v1/documents/123/risks"
```

### Python SDK Example
```python
from tc_clarity import TCClarityClient

client = TCClarityClient(api_key="your-api-key")

# Analyze document
result = client.analyze_document("path/to/terms.pdf")

print(f"Risk Score: {result.risk_score}/100")
print(f"Summary: {result.summary}")
print(f"Red Flags: {result.red_flags}")

# Ask questions
answer = client.query("What is the refund policy?", result.document_id)
print(answer.text)
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI | REST API with OpenAPI docs |
| **LLM Orchestration** | LangChain | Chain workflows, RAG |
| **Models** | Hugging Face | BART, Sentence Transformers |
| **Vector DB** | ChromaDB | Semantic search |
| **Database** | PostgreSQL | Document metadata |
| **Cache** | Redis | Semantic caching |
| **Monitoring** | Prometheus + Grafana | Metrics & dashboards |
| **Experiment Tracking** | MLflow | Model versioning |
| **Tracing** | LangSmith | LLM call debugging |

## 📊 Project Structure

```
tc-clarity/
├── data/                    # All data storage
│   ├── raw/                # Raw uploaded documents
│   ├── processed/          # Processed/cleaned data
│   ├── vector_store/       # ChromaDB vector store
│   └── knowledge_base/     # Curated knowledge base
├── src/                    # Source code
│   ├── api/               # FastAPI application
│   │   ├── main.py       # API entry point
│   │   ├── routes/       # API endpoints
│   │   └── dependencies.py
│   ├── rag/              # RAG implementation
│   │   ├── retriever.py
│   │   ├── generator.py
│   │   └── embeddings.py
│   ├── preprocessing/    # Document processing
│   │   ├── pdf_parser.py
│   │   ├── text_cleaner.py
│   │   └── chunker.py
│   ├── evaluation/       # Metrics & evaluation
│   │   ├── metrics.py
│   │   └── evaluators.py
│   ├── monitoring/       # Observability
│   │   ├── metrics.py
│   │   └── logging.py
│   ├── database/         # Database models
│   │   ├── models.py
│   │   └── connection.py
│   └── utils/            # Utility functions
├── models/               # Downloaded model files
│   ├── embeddings/
│   └── summarization/
├── prompts/              # Versioned prompts
│   ├── summarization.py
│   ├── risk_detection.py
│   └── qa.py
├── tests/                # Test suites
│   ├── unit/
│   ├── integration/
│   └── evaluation/
├── notebooks/            # Jupyter notebooks
├── infra/                # Infrastructure as code
│   ├── terraform/
│   └── kubernetes/
├── configs/              # Configuration files
│   ├── prometheus.yml
│   └── grafana/
├── scripts/              # Utility scripts
│   ├── init_db.py
│   ├── seed_data.py
│   └── evaluate_model.py
├── docs/                 # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
├── .github/              # CI/CD workflows
│   └── workflows/
│       ├── ci.yml
│       ├── deploy.yml
│       └── evaluate.yml
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

**Structure Explanation:**

- `data/` - All data storage (documents, embeddings, knowledge base)
- `src/` - All source code organized by function
- `models/` - Downloaded/trained model files
- `prompts/` - Version-controlled prompt templates
- `tests/` - Test suites (unit, integration, evaluation)
- `notebooks/` - Jupyter notebooks for experimentation
- `infra/` - Infrastructure as code (Terraform, K8s configs)
- `configs/` - Configuration files (Prometheus, Grafana)

## 🧪 Testing & Evaluation

### Run Tests
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Evaluation metrics
python scripts/evaluate_model.py
```

### Evaluation Metrics
- **Summarization**: ROUGE-L > 0.4
- **Red Flag Detection**: Accuracy > 85%
- **RAG Answer Relevance**: > 80%
- **API Latency**: p95 < 2 seconds

## 📈 Monitoring

Access monitoring dashboards:
- **API Docs**: http://localhost:8000/docs
- **MLflow**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

Key metrics tracked:
- API request latency
- Model inference time
- Token usage
- Cache hit rate
- Error rates
- Red flag detection accuracy

## 🚢 Deployment

### Docker Deployment
```bash
# Build image
docker build -t tc-clarity:latest .

# Run container
docker run -p 8000:8000 --env-file .env tc-clarity:latest
```

### Cloud Deployment
See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- AWS deployment guide
- GCP deployment guide
- Azure deployment guide
- Kubernetes manifests

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

### Phase 10: CI/CD Pipeline (Week 11)
- [ ] GitHub Actions
- [ ] Automated testing
- [ ] Deployment automation

### Phase 11: Frontend (Week 12) - Optional
- [ ] Streamlit UI
- [ ] Upload interface
- [ ] Results display

### Phase 12: Documentation & Polish (Week 13)
- [ ] Complete documentation
- [ ] Demo video
- [ ] Project presentation

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Hugging Face for providing excellent pre-trained models
- LangChain community for orchestration framework
- FastAPI for the amazing web framework
- ChromaDB for vector database capabilities

## 📧 Contact

**Project Maintainer**: Nihal KA
- GitHub: [@NihalKA](https://github.com/NihalKA)
- Confluence: [LLMOps Space](https://ernihalka.atlassian.net/wiki/spaces/LLMOps)
- Jira: [KAN Project](https://ernihalka.atlassian.net/jira/software/projects/KAN)

## 🔗 Related Projects

- [LangChain](https://github.com/langchain-ai/langchain)
- [ChromaDB](https://github.com/chroma-core/chroma)
- [FastAPI](https://github.com/tiangolo/fastapi)

---

⭐ **Star this repo** if you find it helpful!

📝 **Report issues** via GitHub Issues

💡 **Share feedback** to help improve the project

**Complete Setup Guide**: See [Phase 0 in Confluence](https://ernihalka.atlassian.net/wiki/spaces/LLMOps/pages/426051) for detailed setup instructions