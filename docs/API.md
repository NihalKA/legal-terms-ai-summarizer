# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints require authentication using JWT tokens.

### Obtain Token
```http
POST /auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using Token
Include the token in the Authorization header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Core Endpoints

For complete API documentation with all endpoints, request/response schemas, error codes, and examples, visit:
- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

### Document Management

#### Upload Document
```bash
POST /documents/upload
Content-Type: multipart/form-data

file: <binary>
```

#### Get Document Status
```bash
GET /documents/{document_id}/status
```

#### List Documents
```bash
GET /documents?page=1&limit=20
```

### Analysis Endpoints

#### Get Summary
```bash
GET /documents/{document_id}/summary
```

#### Get Risk Analysis
```bash
GET /documents/{document_id}/risks
```

#### Get Sections
```bash
GET /documents/{document_id}/sections
```

### Question Answering (RAG)

#### Ask Question
```bash
POST /documents/{document_id}/query
Content-Type: application/json

{
  "question": "What is the refund policy?",
  "include_sources": true
}
```

## Rate Limits

| Tier | Requests/Hour | Documents/Day |
|------|---------------|---------------|
| Free | 100 | 10 |
| Pro | 1,000 | 100 |
| Enterprise | Unlimited | Unlimited |

## Error Responses

All errors follow this format:
```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document not found",
    "timestamp": "2025-10-18T14:50:00Z"
  }
}
```

## SDK Examples

### Python
```python
from tc_clarity import TCClarityClient

client = TCClarityClient(api_key="your_api_key")
doc = client.upload_document("terms.pdf")
risks = client.get_risks(doc.id)
```

### JavaScript
```javascript
import TCClarity from 'tc-clarity-sdk';

const client = new TCClarity({ apiKey: 'your_api_key' });
const doc = await client.uploadDocument('terms.pdf');
const risks = await client.getRisks(doc.id);
```

For detailed API specifications, see the interactive documentation at `/docs`.