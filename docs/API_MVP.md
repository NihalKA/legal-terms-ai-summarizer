# API Documentation - MVP Version

REST API for analyzing Terms & Conditions documents with comprehensive legal risk analysis.

## 🌐 Base URL
```
http://localhost:8000
```

## 📚 Interactive Documentation
Visit **http://localhost:8000/docs** for live Swagger UI with testing!

---

## 📡 Endpoints

### 1. Root / Health Check
```http
GET /
```

**Response:**
```json
{
  "message": "T&C Clarity API - MVP Version",
  "version": "1.0.0",
  "description": "Analyze Terms & Conditions from text, URL, or files",
  "docs": "/docs",
  "endpoints": {
    "analyze": "/analyze - Upload document (POST)",
    "get_document": "/documents/{id} - Get document details (GET)",
    "list_documents": "/documents - List all documents (GET)"
  }
}
```

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "1.0.0"
}
```

---

### 2. Analyze Document (Upload)

Accepts three input methods: text, URL, or file upload.

```http
POST /analyze
Content-Type: multipart/form-data
```

**Option 1: Text Input**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "text_input=Your terms and conditions text here (minimum 50 characters)..."
```

**Option 2: URL Input**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "url=https://example.com/terms"
```

**Option 3: File Upload**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@terms.pdf"
```

**Supported file types:** `.pdf`, `.txt`

**Response:**
```json
{
  "document_id": 1,
  "source_type": "file",
  "source": "terms.pdf",
  "length": 15234,
  "preview": "Terms and Conditions...",
  "created_at": "2026-01-17T10:30:00"
}
```

---

### 3. Get Document

Retrieve full document content by ID.

```http
GET /documents/{doc_id}
```

**Example:**
```bash
curl "http://localhost:8000/documents/1"
```

**Response:**
```json
{
  "id": 1,
  "source_type": "file",
  "source": "terms.pdf",
  "content": "Full document text...",
  "length": 15234,
  "created_at": "2026-01-17T10:30:00"
}
```

---

### 4. List Documents

Get all documents with pagination.

```http
GET /documents?skip=0&limit=10
```

**Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 10)

**Example:**
```bash
curl "http://localhost:8000/documents?limit=5"
```

**Response:**
```json
{
  "total": 25,
  "documents": [
    {
      "id": 1,
      "source_type": "file",
      "source": "terms.pdf",
      "length": 15234,
      "preview": "Terms and Conditions...",
      "created_at": "2026-01-17T10:30:00"
    }
  ]
}
```

---

### 5. Delete Document

Delete a document by ID.

```http
DELETE /documents/{doc_id}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/documents/1"
```

**Response:**
```json
{
  "message": "Document 1 deleted successfully"
}
```

---

### 5. Comprehensive Legal Analysis ⭐

Generate detailed legal risk analysis with 16 pattern categories + AI catch-all.

```http
GET /summarize/{doc_id}?method=comprehensive
```

**Parameters:**
- `doc_id` (required): Document ID from upload
- `method` (optional): Must be "comprehensive" (default and only supported method)

**Example:**
```bash
curl "http://localhost:8000/summarize/1?method=comprehensive"
```

**Response (abbreviated):**
```json
{
  "document_id": 1,
  "source": "ABCD_Loan_Agreement.pdf",
  "method": "comprehensive",
  "analysis_type": "Pattern-Based Legal Risk Analysis",
  "risk_level": "⚠️ HIGH RISK",
  "risk_summary": "Multiple penalties, termination rights, and security requirements found",
  "findings_summary": {
    "💰 Interest Rates Found": 3,
    "💳 Fees & Charges Found": 5,
    "⚡ Penalties Found": 4,
    "🚫 Termination Clauses Found": 3,
    "📋 Your Obligations Found": 6,
    "🏠 Security/Collateral Found": 4,
    "💵 Loan Amount/Limit Found": 2,
    "📅 Repayment Terms Found": 3,
    "⏱️ Loan Duration Found": 2,
    "⚠️ Default Consequences Found": 3,
    "🔄 Change Terms Rights Found": 2,
    "⏰ Grace Period Found": 1,
    "🛡️ Insurance Required": 2,
    "👥 Personal Guarantee Found": 1,
    "💰 Prepayment Rules Found": 2,
    "⚖️ Jurisdiction Found": 1,
    "🔍 Unusual Clauses (AI)": 2
  },
  "key_clauses_found": {
    "💰 Interest Rates": [
      "Interest rate at 12% p.a. from the date of disbursement",
      "Default interest at 2% over the agreed rate"
    ],
    "⚡ Penalties & Late Fees": [
      "Late payment charge of ₹500 if EMI not paid within 7 days",
      "Penal interest at 2% p.a. on overdue amounts"
    ]
    // ... 15 more categories
  },
  "legal_terms_glossary": {
    "Interest Rate": "The percentage charged on the loan amount per year...",
    "Default/Penal Interest": "Extra interest charged when you miss payments...",
    // ... 16 more terms
  },
  "document_stats": {
    "original_length": 45678,
    "analysis_method": "Hybrid: Pattern matching (16 categories) + AI catch-all",
    "clauses_extracted": 30,
    "categories_analyzed": 17,
    "analysis_time": "~10-20 seconds"
  },
  "important_notes": [
    "📌 Read EVERY clause shown above - these are direct quotes from the document",
    "📌 CRITICAL: Check loan amount, interest rate, EMI, and tenure",
    // ... 6 more notes
  ],
  "disclaimer": "⚠️ This is AI-assisted analysis for informational purposes only..."
}
```

**Analysis Features:**
- ✅ 16 regex-based pattern categories (100+ patterns)
- ✅ AI catch-all with Flan-T5 for unusual clauses
- ✅ Risk level: HIGH/MEDIUM/LOW
- ✅ 20-30 key clauses extracted
- ✅ Legal glossary with plain-language explanations
- ✅ 10-20 second analysis time

---

### 6. Delete Document

Delete a document by ID.

```http
DELETE /documents/{doc_id}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/documents/1"
```

**Response:**
```json
{
  "message": "Document 1 deleted successfully"
}
```

---

## 🚧 Coming in Phase 3 (RAG Q&A)

### Ask Questions About Document
```http
POST /ask/{doc_id}
{
  "question": "What happens if I miss 2 payments?"
}
```

Will use ChromaDB vector store + semantic search to answer questions about specific document.

---

## 🔧 Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Status Codes

- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error

### Example Errors

**Document not found:**
```json
{
  "detail": "Document not found"
}
```

**Invalid file type:**
```json
{
  "detail": "Only PDF and TXT files are supported"
}
```

**Content too short:**
```json
{
  "detail": "Content too short. Please provide at least 50 characters."
}
```

---

## 🧪 Testing

Use the included test script:
```bash
python test_api.py
```

Or test manually with curl or the Swagger UI at `/docs`.

---

## 📝 Notes

- No authentication required (MVP version)
- All dates in ISO 8601 format (UTC)
- Document IDs are auto-incrementing integers
- Maximum URL fetch timeout: 15 seconds
