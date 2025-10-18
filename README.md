# T&C Clarity - Legal Terms AI Summarizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
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
- Python 3.9+
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
# - DATABASE_URL
# - REDIS_URL
```

4. **Start services with Docker**
```bash
docker-compose up -d
```

5. **Run migrations**
```bash
alembic upgrade head
```

6. **Start the API server**
```bash
uvicorn app.main:app --reload
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
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── analyze.py
│   │   │   │   ├── query.py
│   │   │   │   └── documents.py
│   │   │   └── router.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── services/
│   │   ├── document_processor.py
│   │   ├── summarizer.py
│   │   ├── risk_analyzer.py
│   │   └── rag_engine.py
│   ├── models/
│   │   ├── database.py
│   │   └── schemas.py
│   ├── chains/
│   │   ├── summarization_chain.py
│   │   ├── qa_chain.py
│   │   └── risk_detection_chain.py
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
│       ├── test_datasets/
│       └── metrics.py
├── monitoring/
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── dashboards/
├── scripts/
│   ├── setup_db.py
│   ├── seed_data.py
│   └── evaluate_model.py
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
├── .github/
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
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **MLflow**: http://localhost:5000

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

- [API Documentation](docs/API.md) - Complete API reference
- [Architecture Guide](docs/ARCHITECTURE.md) - System design details
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Contributing Guide](docs/CONTRIBUTING.md) - Development guidelines

## 🗺️ Roadmap

### Phase 1: Core Features (Weeks 1-6) ✅
- [x] Document processing pipeline
- [x] Basic summarization
- [x] Vector database integration
- [x] RAG implementation

### Phase 2: Analysis Engine (Weeks 7-9) ✅
- [x] Red flag detection
- [x] Risk scoring
- [x] Section classification

### Phase 3: LLMOps (Weeks 10-12) 🔄
- [x] Monitoring setup
- [x] Evaluation framework
- [ ] CI/CD pipeline
- [ ] Automated testing

### Phase 4: Advanced Features (Future)
- [ ] Multi-language support
- [ ] Comparison mode (multiple T&Cs)
- [ ] Browser extension
- [ ] Mobile app

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
- Project Link: [https://github.com/NihalKA/legal-terms-ai-summarizer](https://github.com/NihalKA/legal-terms-ai-summarizer)

## 🔗 Related Projects

- [LangChain](https://github.com/langchain-ai/langchain)
- [ChromaDB](https://github.com/chroma-core/chroma)
- [FastAPI](https://github.com/tiangolo/fastapi)

---

⭐ **Star this repo** if you find it helpful!

📝 **Report issues** via GitHub Issues

💡 **Share feedback** to help improve the project