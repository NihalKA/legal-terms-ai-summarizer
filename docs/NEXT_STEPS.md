# Next Steps - Feature Implementation Guide

This guide provides implementation details for upcoming phases.

## ✅ Completed Phases

### Phase 1: Core Upload & Storage ✅
- Three input methods (text, URL, file)
- PostgreSQL storage with SQLAlchemy
- PDF extraction (PyPDF2)
- URL scraping (BeautifulSoup)
- CRUD endpoints
- Docker Compose setup
- Test suite

### Phase 2: Legal Risk Analysis ✅
- 16 pattern categories (100+ regex patterns)
- Flan-T5 AI catch-all for unusual clauses
- Risk level calculation (HIGH/MEDIUM/LOW)
- `/summarize/{doc_id}` endpoint
- Legal glossary (18 terms)
- Web UI with 3 input methods
- Results display with accordion
- Download report feature

**Current Performance:**
- 20-30 clauses extracted in 10-20 seconds
- Finds: interest rates, penalties, termination rights, security requirements, etc.
- HIGH RISK correctly identified for ABCD loan document

---

## 🎯 Phase 3: RAG Q&A System (Next - 1 Week)

### Goal
Enable users to ask questions about their document:
- "What happens if I miss 2 payments?"
- "Can they change the interest rate without telling me?"
- "What property is at risk?"
- "How much is the prepayment charge?"

### What to Build
Add ChromaDB vector store + semantic search + context-aware Q&A endpoint.

---

### Implementation Steps

#### Step 1: Install Dependencies (5 minutes)
```bash
# Add to pyproject.toml
uv add chromadb sentence-transformers

# Or with pip
pip install chromadb sentence-transformers
```

#### Step 2: Initialize ChromaDB (app.py)
```python
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

# Add after Flan-T5 initialization
print("Loading ChromaDB and embeddings model...")
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./data/vector_store"
))

collection = chroma_client.get_or_create_collection(
    name="documents",
    metadata={"description": "T&C document chunks"}
)

# Lightweight embedding model (80MB)
embedder = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ ChromaDB ready")
```

#### Step 3: Add Chunking Function
```python
def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Split text into overlapping chunks for better context"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_text = ' '.join(words[i:i + chunk_size])
        if len(chunk_text) > 50:  # Minimum viable chunk
            chunks.append(chunk_text)
    
    return chunks
```

#### Step 4: Modify Upload Endpoint to Create Embeddings
```python
@app.post("/analyze", response_model=DocumentResponse)
async def analyze_document(...):
    # ... existing upload code ...
    
    doc_id = save_to_db(content, source_name, source_type)
    
    # NEW: Create embeddings for Q&A
    print(f"  📦 Creating embeddings for doc {doc_id}...")
    chunks = chunk_document(content)
    
    # Generate embeddings
    embeddings = embedder.encode(chunks).tolist()
    
    # Store in ChromaDB
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"doc{doc_id}_chunk{i}" for i in range(len(chunks))],
        metadatas=[{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
    )
    
    print(f"  ✅ {len(chunks)} chunks embedded")
    
    # ... return response ...
```

#### Step 5: Add Q&A Endpoint
```python
@app.post("/ask/{doc_id}")
async def ask_question(doc_id: int, question: str):
    """Ask questions about a specific document using RAG"""
    
    # Verify document exists
    doc = get_document_from_db(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Generate question embedding
    question_embedding = embedder.encode([question]).tolist()[0]
    
    # Query ChromaDB for relevant chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        where={"doc_id": doc_id},
        n_results=3  # Top 3 most relevant chunks
    )
    
    if not results['documents'] or not results['documents'][0]:
        return {
            "question": question,
            "answer": "I couldn't find relevant information in the document.",
            "confidence": "low"
        }
    
    # Combine relevant chunks as context
    context = "\n\n".join(results['documents'][0])
    
    # Use Flan-T5 to generate answer
    prompt = f"""Based on this legal document excerpt, answer the question.

Context:
{context[:1200]}

Question: {question}

Answer:"""
    
    answer_result = analyzer(prompt, max_length=150, do_sample=False, truncation=True)
    answer = answer_result[0]['generated_text'].strip()
    
    return {
        "document_id": doc_id,
        "question": question,
        "answer": answer,
        "relevant_excerpts": results['documents'][0][:2],  # Show top 2 sources
        "confidence": "high" if len(context) > 200 else "medium"
    }
```

#### Step 6: Test Q&A
```bash
# Upload document
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@ABCD_Loan.pdf"

# Ask question
curl -X POST "http://localhost:8000/ask/1" \
  -H "Content-Type: application/json" \
  -d '{"question": "What happens if I miss 2 EMI payments?"}'
```

#### Step 7: Add to Web UI (frontend/index.html)
```html
<!-- Add after results section -->
<div id="qaSection" style="display: none;">
  <h3>Ask Questions About This Document</h3>
  <input type="text" id="questionInput" placeholder="e.g., What happens if I miss payments?" />
  <button id="askBtn">Ask</button>
  <div id="answerSection"></div>
</div>
```

```javascript
// In script.js
async function askQuestion() {
    const question = questionInput.value.trim();
    const response = await fetch(`${API_BASE_URL}/ask/${currentDocId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question})
    });
    const data = await response.json();
    displayAnswer(data);
}
```

---

### Phase 3 Expected Outcomes
- ✅ Users can ask natural language questions
- ✅ System retrieves relevant document sections
- ✅ AI generates context-aware answers
- ✅ Shows source excerpts for verification
- ✅ 3-5 second response time

---
    
    return chunks
```

#### 3. Update Analyze Endpoint to Store Embeddings
```python
# Modify analyze_document() endpoint
# After saving to database, add:

# Chunk the document
chunks = chunk_text(content)

# Generate embeddings and store in ChromaDB
for idx, chunk in enumerate(chunks):
    collection.add(
        documents=[chunk],
        metadatas=[{
            "document_id": doc_id,
            "chunk_index": idx,
            "source": source_name
        }],
        ids=[f"doc_{doc_id}_chunk_{idx}"]
    )
```

#### 4. Add Q&A Endpoint
```python
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask/{doc_id}")
async def ask_question(doc_id: int, request: QuestionRequest):
    """Ask a question about a specific document"""
    
    # Find relevant chunks from vector database
    results = collection.query(
        query_texts=[request.question],
        n_results=3,
        where={"document_id": doc_id}
    )
    
    if not results['documents'] or len(results['documents'][0]) == 0:
        raise HTTPException(status_code=404, detail="No relevant content found")
    
    # Get context from top results
    context = "\n\n".join(results['documents'][0])
    
    # Simple answer generation (improve with LLM later)
    answer = f"Based on the document:\n\n{context[:500]}..."
    
    return {
        "question": request.question,
        "answer": answer,
        "relevant_chunks": len(results['documents'][0]),
        "context": context
    }
```

#### 5. Test It
```bash
# Ask a question
curl -X POST "http://localhost:8000/ask/1" \
  -H "Content-Type: application/json" \
  -d '{"question": "What data do they collect?"}'
```

#### 6. Improve (Optional)
- Use actual LLM for answer generation
- Add source citations
- Improve chunking strategy
- Add semantic caching

---

## 🎯 Phase 4: Red Flag Detection (1 day)

### What to Build
Automatically identify concerning clauses and calculate risk scores.

### Implementation Steps

#### 1. Define Red Flags
```python
# Add to app.py

RED_FLAG_PATTERNS = {
    "arbitration": {
        "keywords": ["arbitration", "arbitrator", "arbitral"],
        "severity": "high",
        "description": "Requires disputes to be resolved through arbitration"
    },
    "class_action_waiver": {
        "keywords": ["class action waiver", "no class action", "waive.*class"],
        "severity": "critical",
        "description": "Prevents participation in class action lawsuits"
    },
    "liability_limitation": {
        "keywords": ["limit.*liability", "no liability", "not liable"],
        "severity": "medium",
        "description": "Limits company's legal liability"
    },
    "unilateral_changes": {
        "keywords": ["modify.*any time", "change.*without notice", "reserve.*right.*modify"],
        "severity": "high",
        "description": "Company can change terms at any time"
    },
    "data_collection": {
        "keywords": ["collect.*data", "personal information", "tracking"],
        "severity": "medium",
        "description": "Collects personal data"
    },
    "third_party_sharing": {
        "keywords": ["share.*third party", "sell.*information", "disclose.*partners"],
        "severity": "high",
        "description": "Shares data with third parties"
    }
}
```

#### 2. Add Red Flag Detection Function
```python
import re

def detect_red_flags(content: str) -> dict:
    """Detect red flags in document content"""
    content_lower = content.lower()
    found_flags = []
    
    for flag_name, flag_info in RED_FLAG_PATTERNS.items():
        for keyword in flag_info["keywords"]:
            # Use regex for flexible matching
            if re.search(keyword, content_lower):
                found_flags.append({
                    "type": flag_name,
                    "severity": flag_info["severity"],
                    "description": flag_info["description"]
                })
                break  # Don't add same flag multiple times
    
    # Calculate risk score (0-100)
    severity_scores = {"low": 10, "medium": 20, "high": 30, "critical": 40}
    risk_score = min(100, sum(severity_scores.get(flag["severity"], 0) for flag in found_flags))
    
    return {
        "flags": found_flags,
        "risk_score": risk_score,
        "flag_count": len(found_flags)
    }
```

#### 3. Add Risk Analysis Endpoint
```python
@app.get("/risks/{doc_id}")
async def analyze_risks(doc_id: int):
    """Analyze document for red flags and calculate risk score"""
    doc = get_document_from_db(doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis = detect_red_flags(doc.content)
    
    return {
        "document_id": doc_id,
        "risk_score": analysis["risk_score"],
        "total_flags": analysis["flag_count"],
        "red_flags": analysis["flags"],
        "risk_level": (
            "Low" if analysis["risk_score"] < 30 else
            "Medium" if analysis["risk_score"] < 60 else
            "High" if analysis["risk_score"] < 80 else
            "Critical"
        )
    }
```

#### 4. Test It
```bash
curl "http://localhost:8000/risks/1"
```

#### 5. Improve (Optional)
- Use ML model for better detection
- Add context extraction (show where flag appears)
- Add severity explanations
- Allow custom red flag patterns

---

## 🎯 Phase 5: Polish & UI (Optional)

### Simple Web Interface with Streamlit

Create `streamlit_app.py`:
```python
import streamlit as st
import requests

st.title("🔍 T&C Clarity")
st.subheader("Analyze Terms & Conditions Documents")

# Input methods
input_type = st.radio("Choose input method:", ["Text", "URL", "File"])

if input_type == "Text":
    text = st.text_area("Paste T&C text here:", height=200)
    if st.button("Analyze") and text:
        response = requests.post(
            "http://localhost:8000/analyze",
            data={"text_input": text}
        )
        doc_id = response.json()["document_id"]
        show_results(doc_id)

elif input_type == "URL":
    url = st.text_input("Enter URL:")
    if st.button("Analyze") and url:
        response = requests.post(
            "http://localhost:8000/analyze",
            data={"url": url}
        )
        doc_id = response.json()["document_id"]
        show_results(doc_id)

elif input_type == "File":
    file = st.file_uploader("Upload PDF or TXT:", type=["pdf", "txt"])
    if st.button("Analyze") and file:
        response = requests.post(
            "http://localhost:8000/analyze",
            files={"file": file}
        )
        doc_id = response.json()["document_id"]
        show_results(doc_id)

def show_results(doc_id):
    # Get summary
    summary = requests.get(f"http://localhost:8000/summarize/{doc_id}").json()
    st.subheader("📄 Summary")
    st.write(summary["summary"])
    
    # Get risks
    risks = requests.get(f"http://localhost:8000/risks/{doc_id}").json()
    st.subheader("🚩 Risk Analysis")
    st.metric("Risk Score", f"{risks['risk_score']}/100", risks['risk_level'])
    
    for flag in risks['red_flags']:
        st.warning(f"⚠️ {flag['description']} ({flag['severity']})")
    
    # Q&A
    st.subheader("💬 Ask Questions")
    question = st.text_input("Ask about the document:")
    if question:
        response = requests.post(
            f"http://localhost:8000/ask/{doc_id}",
            json={"question": question}
        ).json()
        st.write(response["answer"])
```

Run with:
```bash
streamlit run streamlit_app.py
```

---

## 🔄 Later Improvements

1. **Caching** - Add Redis for frequently accessed documents
2. **Better Models** - Use GPT-3.5/4 or Claude for better summaries
3. **Batch Processing** - Handle multiple documents
4. **Comparison** - Compare T&Cs from different companies
5. **Monitoring** - Add Prometheus metrics
6. **Testing** - Add pytest suite
7. **CI/CD** - GitHub Actions pipeline

---

## 📚 Resources

- **ChromaDB Docs**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/
- **Hugging Face Transformers**: https://huggingface.co/docs/transformers/
- **Streamlit**: https://docs.streamlit.io/

---

**Remember**: Implement one feature at a time, test it works, then move to the next. Don't try to build everything at once!
