# Architecture Documentation

## System Overview

T&C Clarity is built using a microservices-inspired architecture with a focus on LLMOps best practices. The system processes legal documents through multiple stages, from ingestion to analysis, using state-of-the-art LLM technologies.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (Web UI / CLI / SDK / Third-party Integrations)            │
└───────────────────────┬──────────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────────┐
│                     API Gateway Layer                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  FastAPI   │  │   Auth     │  │Rate Limit  │            │
│  │  Router    │  │Middleware  │  │Middleware  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└───────────────────────┬──────────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────────┐
│                   Service Layer                               │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────┐     │
│  │   Document      │  │  Analysis    │  │    RAG     │     │
│  │   Processor     │  │   Engine     │  │   Engine   │     │
│  └─────────────────┘  └──────────────┘  └────────────┘     │
└───────┬───────────────────┬──────────────────┬──────────────┘
        │                   │                  │
┌───────▼─────┐   ┌────────▼────────┐   ┌────▼──────────┐
│  LangChain  │   │  Hugging Face   │   │   ChromaDB    │
│  Chains     │   │  Models         │   │Vector Store   │
└─────────────┘   └─────────────────┘   └───────────────┘
```

## Core Components

### 1. API Gateway Layer

**FastAPI Application**
- RESTful endpoints with OpenAPI documentation
- Async request handling for improved throughput
- Automatic request validation using Pydantic models
- Built-in error handling and logging

**Middleware Stack**
- Authentication & Authorization (JWT-based)
- Rate limiting (per user/IP)
- CORS configuration
- Request/Response logging
- Error tracking

### 2. Service Layer

#### Document Processor Service
**Responsibilities:**
- Accept multiple input formats (PDF, TXT, URLs)
- Extract text from documents
- Clean and preprocess text
- Chunk documents for optimal processing
- Store metadata in PostgreSQL

#### Analysis Engine Service
**Responsibilities:**
- Generate executive summaries
- Detect red flags and concerning clauses
- Calculate risk scores
- Classify document sections
- Extract key terms

#### RAG Engine Service
**Responsibilities:**
- Process user questions
- Retrieve relevant context from vector store
- Generate accurate answers with citations
- Handle follow-up questions with memory

### 3. Model Layer

#### Hugging Face Models

**Summarization Model**
- Model: `facebook/bart-large-cnn`
- Purpose: Generate concise summaries
- Input: Document chunks (max 1024 tokens)
- Output: Summary text (128-256 tokens)

**Embedding Model**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Purpose: Generate semantic embeddings
- Input: Text chunks
- Output: 384-dimensional vectors

### 4. Data Layer

#### PostgreSQL Schema

```sql
-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    source_type VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);

-- Chunks table
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding_id VARCHAR(255),
    metadata JSONB
);

-- Red flags table
CREATE TABLE red_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    flag_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20),
    excerpt TEXT,
    explanation TEXT
);
```

#### ChromaDB Collections

Vector database for semantic search:
- Store document chunk embeddings
- Retrieve similar content based on query
- Support metadata filtering

#### Redis Caching Strategy

**Cache Keys:**
```
document:summary:{document_id}
document:risks:{document_id}
embedding:{text_hash}
rag:answer:{query_hash}:{document_id}
```

### 5. Observability Layer

#### Prometheus Metrics

Custom metrics tracked:
- API request rates and latency
- Model inference duration
- Cache hit rates
- Error rates
- Document processing metrics

#### LangSmith Tracing

- Trace LLM calls and chains
- Debug prompt performance
- Monitor token usage
- Analyze response quality

## Data Flow

### Document Upload & Analysis Flow

```
1. Client uploads PDF
   ↓
2. API validates file
   ↓
3. DocumentProcessor extracts text
   ↓
4. Text cleaned and preprocessed
   ↓
5. Document chunked
   ↓
6. Chunks stored in PostgreSQL
   ↓
7. Embeddings generated
   ↓
8. Embeddings stored in ChromaDB
   ↓
9. AnalysisEngine processes:
   - Generate summary
   - Detect red flags
   - Calculate risk score
   ↓
10. Results cached in Redis
   ↓
11. Response returned to client
```

### RAG Query Flow

```
1. User asks question
   ↓
2. Check Redis cache
   ↓
3. If cache miss:
   - Generate query embedding
   - Search ChromaDB
   - Retrieve relevant chunks
   - Generate answer using LLM
   - Cache answer
   ↓
4. Return answer to user
```

## Security Architecture

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- API key management

### Data Protection
- Password hashing with bcrypt
- TLS/SSL for data in transit
- Encryption at rest for sensitive data
- PII detection and masking

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers
- Worker pool for document processing
- Distributed caching with Redis cluster
- Database read replicas

### Performance Targets
- API p95 latency < 2 seconds
- Document processing < 30 seconds for 50-page PDF
- RAG query response < 1 second
- Cache hit rate > 80%

## Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| API Framework | FastAPI | High performance, async, auto-docs |
| Database | PostgreSQL | ACID compliance, JSON support |
| Vector DB | ChromaDB | Easy setup, good performance |
| Cache | Redis | Fast, versatile, proven |
| Orchestration | LangChain | Rich ecosystem, composable |
| Models | Hugging Face | Open-source, extensive library |

## Future Enhancements

1. **Multi-tenancy**: Isolate data per organization
2. **Real-time collaboration**: WebSocket support
3. **Model fine-tuning**: Custom models for industries
4. **Advanced caching**: Semantic caching with similarity
5. **Distributed tracing**: OpenTelemetry integration

For implementation details, see the source code and inline documentation.