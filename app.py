"""
T&C Clarity - MVP Version
Simple, functional legal terms analyzer with three input methods
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from typing import Optional
import PyPDF2
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import os
import re
from transformers import pipeline

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://tcuser:tcpass@localhost:5432/tcclarity")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Document(Base):
    """Database model for storing documents"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String, nullable=False)  # 'file', 'url', 'text'
    source_name = Column(String, nullable=False)  # filename, URL, or "Direct Input"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(engine)

# ============================================================================
# AI MODEL SETUP (Phase 2: Legal Risk Analysis)
# ============================================================================

print("Loading AI model for legal analysis...")
# Flan-T5 for AI catch-all (finding unusual clauses)
analyzer = pipeline("text2text-generation", model="google/flan-t5-large")
print("✅ AI model loaded")


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TextInput(BaseModel):
    """Model for text or URL input"""
    text: Optional[str] = None
    url: Optional[HttpUrl] = None


class DocumentResponse(BaseModel):
    """Response model for document operations"""
    document_id: int
    source_type: str
    source: str
    length: int
    preview: str
    created_at: datetime


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="T&C Clarity - MVP",
    description="Legal Terms AI Summarizer - Analyze T&Cs from text, URL, or files",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")


def scrape_url(url: str) -> str:
    """Scrape text content from URL or download PDF"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; TCClarity/1.0; +https://github.com/NihalKA/legal-terms-ai-summarizer)'
        }
        response = requests.get(str(url), headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check if response is a PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' in content_type or str(url).lower().endswith('.pdf'):
            # Extract text from PDF
            return extract_pdf(response.content)
        
        # Otherwise, parse as HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, and other non-content elements
        for element in soup(["script", "style", "header", "footer", "nav"]):
            element.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing URL content: {str(e)}")


def save_to_db(content: str, source_name: str, source_type: str) -> int:
    """Save document to database and return document ID"""
    db = SessionLocal()
    try:
        doc = Document(
            content=content,
            source_name=source_name,
            source_type=source_type
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc.id
    finally:
        db.close()


def get_document_from_db(doc_id: int) -> Optional[Document]:
    """Retrieve document from database"""
    db = SessionLocal()
    try:
        return db.query(Document).filter(Document.id == doc_id).first()
    finally:
        db.close()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
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


@app.post("/analyze", response_model=DocumentResponse)
async def analyze_document(
    text_input: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Main endpoint: Accepts three types of input
    
    1. Copy-paste text: Send as form field 'text_input'
    2. URL: Send as form field 'url'
    3. File upload: Send as multipart file 'file' (PDF or TXT)
    
    Returns document ID and preview
    """
    
    content = ""
    source_type = ""
    source_name = ""
    
    # Priority: File > URL > Text
    if file:
        # Option 3: File Upload
        source_type = "file"
        source_name = file.filename
        
        if file.filename.endswith('.pdf'):
            pdf_content = await file.read()
            content = extract_pdf(pdf_content)
        elif file.filename.endswith('.txt'):
            content = (await file.read()).decode('utf-8')
        else:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported"
            )
    
    elif url:
        # Option 2: URL
        source_type = "url"
        source_name = url
        content = scrape_url(url)
    
    elif text_input:
        # Option 1: Direct Text Input
        source_type = "text"
        source_name = "Direct Input"
        content = text_input
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide one of: text_input, url, or file"
        )
    
    # Validate content
    if not content or len(content.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Content too short. Please provide at least 50 characters."
        )
    
    # Save to database
    doc_id = save_to_db(content, source_name, source_type)
    
    # Get saved document for response
    doc = get_document_from_db(doc_id)
    
    return DocumentResponse(
        document_id=doc.id,
        source_type=doc.source_type,
        source=doc.source_name,
        length=len(doc.content),
        preview=doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
        created_at=doc.created_at
    )


@app.get("/documents/{doc_id}")
async def get_document(doc_id: int):
    """Get full document details by ID"""
    doc = get_document_from_db(doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": doc.id,
        "source_type": doc.source_type,
        "source": doc.source_name,
        "content": doc.content,
        "length": len(doc.content),
        "created_at": doc.created_at
    }


@app.get("/documents")
async def list_documents(skip: int = 0, limit: int = 10):
    """List all documents with pagination"""
    db = SessionLocal()
    try:
        documents = db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
        total = db.query(Document).count()
        
        return {
            "total": total,
            "documents": [
                {
                    "id": doc.id,
                    "source_type": doc.source_type,
                    "source": doc.source_name,
                    "length": len(doc.content),
                    "preview": doc.content[:150] + "..." if len(doc.content) > 150 else doc.content,
                    "created_at": doc.created_at
                }
                for doc in documents
            ]
        }
    finally:
        db.close()


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int):
    """Delete a document by ID"""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        db.delete(doc)
        db.commit()
        
        return {"message": f"Document {doc_id} deleted successfully"}
    finally:
        db.close()


def chunk_document(text: str, chunk_size: int = 3000, overlap: int = 200) -> list:
    """
    Split document into overlapping chunks to avoid missing important information
    
    - chunk_size: Characters per chunk (3000 = ~750 tokens)
    - overlap: Characters that overlap between chunks (prevents cutting sentences)
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # If not the last chunk, try to break at sentence boundary
        if end < len(text):
            # Look for last period in last 200 chars to avoid cutting sentences
            last_period = chunk.rfind('. ', -200)
            if last_period > 0:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1
        
        chunks.append(chunk)
        start = end - overlap  # Move back by overlap amount
    
    return chunks


def extract_context(text: str, match_pos: int, context_chars: int = 200) -> str:
    """Extract context around a match position"""
    start = max(0, match_pos - context_chars)
    end = min(len(text), match_pos + context_chars)
    context = text[start:end].strip()
    # Clean up
    context = ' '.join(context.split())
    return context


def find_legal_patterns(text: str) -> dict:
    """
    Extract key legal information using pattern matching
    Returns structured findings with actual numbers and clear terms
    NOW WITH 16 CATEGORIES for comprehensive coverage!
    """
    findings = {
        "interest_rates": [],
        "fees_charges": [],
        "penalties": [],
        "termination_rights": [],
        "obligations": [],
        "security_collateral": [],
        "loan_amount": [],
        "repayment_terms": [],
        "loan_duration": [],
        "default_consequences": [],
        "change_terms_rights": [],
        "grace_period": [],
        "insurance_requirements": [],
        "personal_guarantee": [],
        "prepayment_rules": [],
        "jurisdiction": []
    }
    
    text_lower = text.lower()
    
    # Pattern 1: Interest rates (IMPROVED - multiple strategies)
    interest_patterns = [
        # Direct percentage patterns
        r'interest.*?(?:rate|@).*?(\d+\.?\d*)\s*%\s*(?:per\s+annum|p\.?a\.?|yearly|annually)',
        r'(?:rate\s+of\s+interest|interest\s+rate).*?(\d+\.?\d*)\s*%',
        r'(?:fixed|floating|variable)\s+(?:rate|interest).*?(\d+\.?\d*)\s*%',
        # ROI patterns
        r'roi.*?(\d+\.?\d*)\s*%',
        r'rate.*?(\d+\.?\d*)\s*%.*?(?:per\s+annum|p\.?a\.?)',
        # Interest in schedule/table format
        r'interest.*?[:=]\s*(\d+\.?\d*)\s*%',
        # Default/penal interest
        r'(?:default|penal|additional)\s+interest.*?(\d+\.?\d*)\s*%',
    ]
    
    for pattern in interest_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 200)
            # Clean and deduplicate
            if context not in findings["interest_rates"]:
                findings["interest_rates"].append(context)
            if len(findings["interest_rates"]) >= 5:
                break
        if len(findings["interest_rates"]) >= 5:
            break
    
    # Pattern 2: Fees and charges (IMPROVED)
    fee_patterns = [
        r'(?:processing|administration|service|maintenance|annual|prepayment|foreclosure)\s+(?:fee|charge|cost)s?.*?(?:rs\.?|₹|inr)?\s*(\d+[\d,]*)',
        r'(?:fee|charge)s?.*?(?:of\s+)?(?:rs\.?|₹|inr)\s*(\d+[\d,]*)',
        r'pay(?:able|ment).*?(?:rs\.?|₹|inr)\s*(\d+[\d,]*)',
        r'(?:rs\.?|₹|inr)\s*(\d+[\d,]*).*?(?:fee|charge|cost)'
    ]
    
    for pattern in fee_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            # Filter relevant contexts
            if any(word in context.lower() for word in ['fee', 'charge', 'cost', 'payment', 'rs', '₹']):
                if context not in findings["fees_charges"]:
                    findings["fees_charges"].append(context)
                if len(findings["fees_charges"]) >= 5:
                    break
        if len(findings["fees_charges"]) >= 5:
            break
    
    # Pattern 3: Penalties (IMPROVED)
    penalty_patterns = [
        r'(?:penalty|penal).*?(?:interest|rate|charge).*?(\d+\.?\d*)\s*%',
        r'late\s+(?:payment|fee|charge).*?(?:rs\.?|₹|inr)?\s*(\d+[\d,]*)',
        r'default.*?(?:charge|fee|penalty|interest).*?(\d+\.?\d*)',
        r'overdue.*?(?:interest|charge).*?(\d+\.?\d*)',
        r'breach.*?penalty.*?(?:rs\.?|₹|inr)?\s*(\d+[\d,]*)'
    ]
    
    for pattern in penalty_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if context not in findings["penalties"]:
                findings["penalties"].append(context)
            if len(findings["penalties"]) >= 5:
                break
        if len(findings["penalties"]) >= 5:
            break
    
    # Pattern 4: Termination/recall rights
    termination_patterns = [
        r'(?:bank|lender|company).*?(?:may|shall|can|entitled to).*?(?:terminate|cancel|recall|revoke).*?(?:facility|loan|agreement)',
        r'(?:terminate|cancel|recall).*?(?:loan|facility|agreement).*?(?:if|when|upon)',
        r'(?:demand|call).*?(?:immediate|full).*?(?:repayment|payment)',
        r'(?:accelerate|acceleration).*?payment',
        r'(?:right\s+to|may).*?(?:terminate|cancel|withdraw).*?(?:facility|loan)'
    ]
    
    for pattern in termination_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 200)
            if len(context) > 40 and context not in findings["termination_rights"]:
                findings["termination_rights"].append(context)
            if len(findings["termination_rights"]) >= 5:
                break
        if len(findings["termination_rights"]) >= 5:
            break
    
    # Pattern 5: Borrower obligations
    obligation_patterns = [
        r'borrower.*?(?:shall|must|required to|obligated to|agrees? to).*?(?:maintain|pay|provide|submit|notify|inform)',
        r'(?:you|your).*?(?:must|shall|required to|agree to).*?(?:maintain|pay|provide|submit|notify)',
        r'borrower.*?(?:covenant|undertake|agree)s?.*?to',
        r'(?:maintain|pay|provide|submit).*?(?:to\s+the\s+)?(?:bank|lender)'
    ]
    
    for pattern in obligation_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if len(context) > 50 and context not in findings["obligations"]:
                findings["obligations"].append(context)
            if len(findings["obligations"]) >= 6:
                break
        if len(findings["obligations"]) >= 6:
            break
    
    # Pattern 6: Security/Collateral
    security_patterns = [
        r'(?:security|collateral).*?(?:property|asset|immovable|movable)',
        r'(?:mortgage|pledge|hypothecate).*?(?:property|asset)',
        r'(?:guarantee|guarantor).*?(?:personal|corporate)',
        r'(?:lien|charge).*?(?:on|over|upon).*?(?:property|asset|account)',
        r'(?:property|asset).*?(?:as\s+)?(?:security|collateral)'
    ]
    
    for pattern in security_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if len(context) > 40 and context not in findings["security_collateral"]:
                findings["security_collateral"].append(context)
            if len(findings["security_collateral"]) >= 5:
                break
        if len(findings["security_collateral"]) >= 5:
            break
    
    # ========== NEW PATTERNS: 10 CRITICAL MISSING CATEGORIES ==========
    
    # Pattern 7: Loan Amount/Limit
    loan_amount_patterns = [
        r'(?:loan|facility)\s+amount.*?(?:rs\.?|₹|inr)\s*([\d,]+(?:\.\d{2})?)',
        r'(?:sanctioned|approved).*?(?:limit|amount).*?(?:rs\.?|₹|inr)\s*([\d,]+)',
        r'(?:maximum|upto|up\s+to).*?(?:rs\.?|₹|inr)\s*([\d,]+).*?(?:lakh|crore|million)?',
        r'credit\s+limit.*?(?:rs\.?|₹|inr)\s*([\d,]+)',
        r'(?:rs\.?|₹|inr)\s*([\d,]+).*?(?:loan|facility|credit)'
    ]
    
    for pattern in loan_amount_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if any(word in context.lower() for word in ['loan', 'facility', 'amount', 'limit', 'credit', 'rs', '₹']):
                if context not in findings["loan_amount"]:
                    findings["loan_amount"].append(context)
                if len(findings["loan_amount"]) >= 3:
                    break
        if len(findings["loan_amount"]) >= 3:
            break
    
    # Pattern 8: Repayment Terms/EMI
    repayment_patterns = [
        r'(?:emi|equated\s+monthly\s+instalment).*?(?:rs\.?|₹|inr)\s*([\d,]+)',
        r'(?:monthly|quarterly|annual)\s+(?:payment|instalment|repayment).*?(?:rs\.?|₹|inr)\s*([\d,]+)',
        r'repayment.*?(?:of|@).*?(?:rs\.?|₹|inr)\s*([\d,]+).*?(?:per|every)\s+month',
        r'(?:pay|repay).*?(?:rs\.?|₹|inr)\s*([\d,]+).*?(?:monthly|per\s+month)',
        r'instalment.*?schedule'
    ]
    
    for pattern in repayment_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if any(word in context.lower() for word in ['emi', 'payment', 'repay', 'instalment', 'monthly']):
                if context not in findings["repayment_terms"]:
                    findings["repayment_terms"].append(context)
                if len(findings["repayment_terms"]) >= 4:
                    break
        if len(findings["repayment_terms"]) >= 4:
            break
    
    # Pattern 9: Loan Duration/Tenure
    duration_patterns = [
        r'(?:tenure|period|term|duration).*?(\d+)\s*(?:month|year)s?',
        r'(?:loan|facility).*?(?:for|of)\s+(\d+)\s*(?:month|year)s?',
        r'repay.*?(?:within|over|in)\s+(\d+)\s*(?:month|year)s?',
        r'(\d+)\s*(?:month|year)s?.*?(?:tenure|period|term)'
    ]
    
    for pattern in duration_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if any(word in context.lower() for word in ['tenure', 'period', 'term', 'duration', 'month', 'year']):
                if context not in findings["loan_duration"]:
                    findings["loan_duration"].append(context)
                if len(findings["loan_duration"]) >= 3:
                    break
        if len(findings["loan_duration"]) >= 3:
            break
    
    # Pattern 10: Default Consequences (specific actions)
    default_consequences_patterns = [
        r'(?:in\s+case\s+of|upon|if).*?default.*?(?:bank|lender).*?(?:may|shall|will|can).*?(?:seize|sell|auction|attach|recover)',
        r'(?:miss|fail).*?(?:\d+).*?(?:payment|instalment).*?(?:shall|will|may).*?(?:accelerate|recall|demand)',
        r'default.*?(?:result|lead|entitle).*?(?:in|to).*?(?:legal|civil|criminal).*?(?:action|proceeding)',
        r'(?:credit\s+score|cibil|credit\s+bureau).*?(?:negative|adverse|impact)',
        r'recovery.*?(?:agent|proceeding|legal\s+action)'
    ]
    
    for pattern in default_consequences_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 200)
            if len(context) > 50 and context not in findings["default_consequences"]:
                findings["default_consequences"].append(context)
            if len(findings["default_consequences"]) >= 4:
                break
        if len(findings["default_consequences"]) >= 4:
            break
    
    # Pattern 11: Rights to Change Terms
    change_terms_patterns = [
        r'(?:bank|lender|company).*?(?:reserve|retain).*?(?:right|discretion).*?(?:to\s+)?(?:change|modify|amend|alter|vary).*?(?:term|rate|condition|fee)',
        r'(?:change|modify|amend|alter).*?(?:interest\s+rate|fee|charge|term).*?(?:without|with).*?(?:notice|consent|approval)',
        r'(?:discretion|sole\s+discretion).*?(?:to\s+)?(?:change|modify|amend|revise)',
        r'(?:unilateral|at\s+our\s+discretion).*?(?:change|modify|alter)'
    ]
    
    for pattern in change_terms_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 200)
            if len(context) > 50 and context not in findings["change_terms_rights"]:
                findings["change_terms_rights"].append(context)
            if len(findings["change_terms_rights"]) >= 4:
                break
        if len(findings["change_terms_rights"]) >= 4:
            break
    
    # Pattern 12: Grace Period
    grace_period_patterns = [
        r'grace\s+period.*?(\d+)\s*(?:day|month)s?',
        r'(\d+)\s*(?:day|month)s?.*?grace.*?period',
        r'(?:late\s+payment|overdue).*?(?:after|within)\s+(\d+)\s*(?:day|month)s?',
        r'payment.*?(?:due|overdue).*?(\d+)\s*(?:day|month)s?'
    ]
    
    for pattern in grace_period_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if any(word in context.lower() for word in ['grace', 'day', 'late', 'overdue', 'due']):
                if context not in findings["grace_period"]:
                    findings["grace_period"].append(context)
                if len(findings["grace_period"]) >= 3:
                    break
        if len(findings["grace_period"]) >= 3:
            break
    
    # Pattern 13: Insurance Requirements
    insurance_patterns = [
        r'(?:borrower|you).*?(?:must|shall|required\s+to|obligated\s+to).*?(?:obtain|maintain|purchase).*?insurance',
        r'insurance.*?(?:policy|cover).*?(?:required|mandatory|compulsory)',
        r'(?:life|property|vehicle|home)\s+insurance.*?(?:in\s+favour\s+of|assigned\s+to).*?(?:bank|lender)',
        r'insurance.*?(?:premium|cost).*?(?:paid\s+by|borne\s+by).*?borrower'
    ]
    
    for pattern in insurance_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if len(context) > 50 and context not in findings["insurance_requirements"]:
                findings["insurance_requirements"].append(context)
            if len(findings["insurance_requirements"]) >= 3:
                break
        if len(findings["insurance_requirements"]) >= 3:
            break
    
    # Pattern 14: Personal Guarantee
    guarantee_patterns = [
        r'(?:personal|individual)\s+guarantee.*?(?:by|from|of)',
        r'guarantor.*?(?:liable|responsible|obligation).*?(?:for|to\s+repay)',
        r'(?:jointly|severally).*?(?:liable|responsible).*?(?:with|along\s+with)',
        r'co-?borrower.*?(?:liable|responsible|guarantee)'
    ]
    
    for pattern in guarantee_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if len(context) > 50 and context not in findings["personal_guarantee"]:
                findings["personal_guarantee"].append(context)
            if len(findings["personal_guarantee"]) >= 3:
                break
        if len(findings["personal_guarantee"]) >= 3:
            break
    
    # Pattern 15: Prepayment Rules
    prepayment_patterns = [
        r'(?:prepayment|pre-payment|foreclosure|early\s+repayment).*?(?:charge|fee|penalty).*?(?:rs\.?|₹|inr|%)?\s*([\d,]+)',
        r'(?:close|foreclose|repay\s+early).*?(?:before|prior\s+to).*?(?:charge|fee).*?(?:rs\.?|₹|inr|%)?\s*([\d,]+)',
        r'(?:no|zero|nil).*?(?:prepayment|foreclosure).*?(?:charge|fee)',
        r'prepayment.*?(?:allowed|permitted|not\s+allowed|not\s+permitted)'
    ]
    
    for pattern in prepayment_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if any(word in context.lower() for word in ['prepayment', 'foreclosure', 'early', 'close']):
                if context not in findings["prepayment_rules"]:
                    findings["prepayment_rules"].append(context)
                if len(findings["prepayment_rules"]) >= 3:
                    break
        if len(findings["prepayment_rules"]) >= 3:
            break
    
    # Pattern 16: Jurisdiction
    jurisdiction_patterns = [
        r'(?:subject\s+to|under).*?(?:jurisdiction|laws?).*?(?:of|in)\s+([a-z]+(?:\s+[a-z]+)?)',
        r'(?:court|tribunal)s?.*?(?:at|in|of)\s+([a-z]+).*?(?:shall\s+have|have).*?jurisdiction',
        r'disputes.*?(?:resolved|settled).*?(?:in|at)\s+([a-z]+)',
        r'jurisdiction.*?(?:court|tribunal)s?.*?(?:at|in|of)\s+([a-z]+)'
    ]
    
    for pattern in jurisdiction_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            context = extract_context(text, match.start(), 180)
            if any(word in context.lower() for word in ['jurisdiction', 'court', 'tribunal', 'dispute', 'law']):
                if context not in findings["jurisdiction"]:
                    findings["jurisdiction"].append(context)
                if len(findings["jurisdiction"]) >= 2:
                    break
        if len(findings["jurisdiction"]) >= 2:
            break
    
    return findings


@app.get("/summarize/{doc_id}")
async def summarize_document(doc_id: int, method: str = "comprehensive"):
    """
    Generate comprehensive AI-powered legal risk analysis
    
    - **doc_id**: ID of the document to analyze
    - **method**: Only 'comprehensive' is supported (deep risk analysis)
    - Returns: Detailed analysis with key risks and obligations
    
    Analysis includes:
    - Pattern matching across 16 legal categories
    - AI catch-all for unusual clauses
    - Risk level assessment
    - Legal terms glossary
    """
    db = SessionLocal()
    try:
        # Get document from database
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Only comprehensive method is supported
        if method != "comprehensive":
            raise HTTPException(status_code=400, detail="Only 'comprehensive' method is supported. Use method=comprehensive")
        
        if True:  # Always run comprehensive
            # IMPROVED LEGAL RISK ANALYSIS - Pure pattern matching, no AI noise
            print(f"📄 Analyzing document {doc_id} with pattern matching...")
            
            # Extract key information using pattern matching
            findings = find_legal_patterns(doc.content)
            
            # Count findings
            total_findings = sum(len(v) for v in findings.values())
            print(f"  ✓ Found {total_findings} key clauses across 16 categories")
            
            # HYBRID: AI catch-all for unusual/unexpected clauses
            print(f"  🤖 Running AI catch-all for unusual clauses...")
            unusual_clauses = []
            
            # Sample 3 random chunks for AI analysis to catch anything we missed
            chunk_size = 1800
            if len(doc.content) > chunk_size * 3:
                import random
                chunks = [doc.content[i:i+chunk_size] for i in range(0, len(doc.content), chunk_size)]
                sample_chunks = random.sample(chunks, min(3, len(chunks)))
            else:
                sample_chunks = [doc.content[:chunk_size]]
            
            for idx, chunk in enumerate(sample_chunks):
                prompt = f"""Find unusual or hidden clauses in this legal document that a person might miss:
- Arbitration restrictions (can't sue in court)
- Automatic renewal at higher price
- Liability limits (not responsible for damages)
- Data/privacy issues (sharing your info)
- IP rights (they own what you create)

List max 2 concerning clauses found. Be specific.

Text: {chunk[:1400]}"""
                
                try:
                    ai_result = analyzer(prompt, max_length=100, do_sample=False, truncation=True)
                    ai_text = ai_result[0]['generated_text'].strip()
                    
                    # Filter out garbage AI responses (IMPROVED)
                    is_valid = (
                        len(ai_text) > 30 and
                        not ai_text.startswith(('m', 'a', 'the', ' ', 'list', 'find', 'be specific')) and
                        not any(bad in ai_text.lower() for bad in ['list max', 'be specific', 'find unusual', 'concerning clauses']) and
                        any(keyword in ai_text.lower() for keyword in ['borrower', 'lender', 'bank', 'clause', 'agreement', 'party', 'right', 'term', 'shall', 'may', 'must', 'payment'])
                    )
                    
                    if is_valid:
                        unusual_clauses.append(ai_text)
                        print(f"    ✓ Chunk {idx+1}: Found unusual clause")
                    else:
                        print(f"    - Chunk {idx+1}: Nothing unusual or AI garbage filtered")
                except Exception as e:
                    print(f"    ⚠️ Chunk {idx+1}: AI error ({str(e)[:40]})")
            
            # Deduplicate and limit
            unusual_clauses = list(set(unusual_clauses))[:4]
            print(f"  ✓ AI catch-all complete: {len(unusual_clauses)} unusual clauses")
            
            # Add to findings for display
            findings["unusual_clauses"] = unusual_clauses
            
            # Count findings
            total_findings = sum(len(v) for v in findings.values())
            print(f" TOTAL: {total_findings} clauses found")
            
            # Risk assessment based on findings count
            risk_counts = {
                "interest_rates": len(findings["interest_rates"]),
                "fees_charges": len(findings["fees_charges"]),
                "penalties": len(findings["penalties"]),
                "termination_rights": len(findings["termination_rights"]),
                "obligations": len(findings["obligations"]),
                "security_collateral": len(findings["security_collateral"]),
                "loan_amount": len(findings["loan_amount"]),
                "repayment_terms": len(findings["repayment_terms"]),
                "loan_duration": len(findings["loan_duration"]),
                "default_consequences": len(findings["default_consequences"]),
                "change_terms_rights": len(findings["change_terms_rights"]),
                "grace_period": len(findings["grace_period"]),
                "insurance_requirements": len(findings["insurance_requirements"]),
                "personal_guarantee": len(findings["personal_guarantee"]),
                "prepayment_rules": len(findings["prepayment_rules"]),
                "jurisdiction": len(findings["jurisdiction"]),
                "unusual_clauses": len(findings.get("unusual_clauses", []))
            }
            
            # Calculate risk level (UPDATED with new categories)
            high_risk_indicators = (
                risk_counts["penalties"] >= 2 or
                risk_counts["termination_rights"] >= 3 or
                risk_counts["security_collateral"] >= 3 or
                risk_counts["default_consequences"] >= 2 or
                risk_counts["change_terms_rights"] >= 2 or
                risk_counts["unusual_clauses"] >= 2
            )
            
            medium_risk_indicators = (
                risk_counts["fees_charges"] >= 3 or
                risk_counts["obligations"] >= 5 or
                risk_counts["insurance_requirements"] >= 2
            )
            
            if high_risk_indicators:
                risk_level = "⚠️ HIGH RISK"
                risk_msg = "Multiple penalties, termination rights, and security requirements found"
            elif medium_risk_indicators:
                risk_level = "⚡ MEDIUM RISK"  
                risk_msg = "Several fees, obligations, and terms require careful review"
            else:
                risk_level = "✅ LOWER RISK"
                risk_msg = "Fewer concerning clauses identified"
            
            # Format clean output (NO AI explanations, just extracted clauses)
            def format_findings(items, empty_msg):
                if not items:
                    return [empty_msg]
                # Clean up and limit to top 5
                return [item.strip() for item in items[:5]]
            
            print(f"  ✅ Analysis complete!")
            
            # Legal terms glossary (EXPANDED)
            glossary = {
                "Interest Rate": "The percentage charged on the loan amount per year (e.g., 12% p.a. means you pay ₹12 for every ₹100 borrowed annually)",
                "Default/Penal Interest": "Extra interest charged when you miss payments or break terms (usually 2-5% extra)",
                "Processing Fee": "One-time fee charged when loan is approved (non-refundable)",
                "Prepayment Charge": "Fee for repaying loan before due date (usually 2-5% of amount)",
                "Terminate/Recall": "Bank's right to cancel loan and demand immediate full repayment",
                "Security/Collateral": "Your property/assets that bank can seize if you don't repay (house, car, FD, etc.)",
                "Mortgage": "Bank's legal claim on your property until loan is fully repaid",
                "Guarantee": "Another person promises to repay if you can't (guarantor's property also at risk)",
                "Lien": "Bank's right to keep your asset (like FD) until you repay the loan",
                "Acceleration": "Bank demanding entire loan amount immediately (not in installments)",
                "Covenant": "Promise/obligation you must fulfill (like maintaining insurance, not selling property)",
                "Default": "Failing to meet loan terms (missing payment, breaking rules)",
                "EMI": "Equated Monthly Installment - fixed amount you pay every month (principal + interest)",
                "Tenure": "Total time period to repay the loan (e.g., 5 years = 60 months)",
                "Grace Period": "Extra time given after due date before penalty starts (e.g., 7 days grace)",
                "Arbitration": "Dispute resolution outside court - you may lose right to sue",
                "Jurisdiction": "Which city/court handles legal disputes (affects your legal costs)",
                "Unilateral Change": "Lender can change terms without your consent"
            }
            
            return {
                "document_id": doc_id,
                "source": doc.source_name,
                "method": "comprehensive",
                "analysis_type": "Pattern-Based Legal Risk Analysis",
                "risk_level": risk_level,
                "risk_summary": risk_msg,
                "findings_summary": {
                    "💰 Interest Rates Found": risk_counts["interest_rates"],
                    "💳 Fees & Charges Found": risk_counts["fees_charges"],
                    "⚡ Penalties Found": risk_counts["penalties"],
                    "🚫 Termination Clauses Found": risk_counts["termination_rights"],
                    "📋 Your Obligations Found": risk_counts["obligations"],
                    "🏠 Security/Collateral Found": risk_counts["security_collateral"],
                    "💵 Loan Amount/Limit Found": risk_counts["loan_amount"],
                    "📅 Repayment Terms Found": risk_counts["repayment_terms"],
                    "⏱️ Loan Duration Found": risk_counts["loan_duration"],
                    "⚠️ Default Consequences Found": risk_counts["default_consequences"],
                    "🔄 Change Terms Rights Found": risk_counts["change_terms_rights"],
                    "⏰ Grace Period Found": risk_counts["grace_period"],
                    "🛡️ Insurance Required": risk_counts["insurance_requirements"],
                    "👥 Personal Guarantee Found": risk_counts["personal_guarantee"],
                    "💰 Prepayment Rules Found": risk_counts["prepayment_rules"],
                    "⚖️ Jurisdiction Found": risk_counts["jurisdiction"],
                    "🔍 Unusual Clauses (AI)": risk_counts["unusual_clauses"]
                },
                "key_clauses_found": {
                    "💰 Interest Rates": format_findings(findings["interest_rates"], "⚠️ No clear interest rate found - ASK LENDER before signing!"),
                    "💳 Fees & Charges": format_findings(findings["fees_charges"], "No specific fees identified"),
                    "⚡ Penalties & Late Fees": format_findings(findings["penalties"], "No specific penalties identified"),
                    "🚫 When They Can Terminate/Demand Full Payment": format_findings(findings["termination_rights"], "No specific termination clauses identified"),
                    "📋 What You MUST Do (Your Obligations)": format_findings(findings["obligations"], "No specific obligations identified"),
                    "🏠 What's At Risk (Security/Collateral)": format_findings(findings["security_collateral"], "No specific security requirements identified"),
                    "💵 Loan Amount/Credit Limit": format_findings(findings["loan_amount"], "⚠️ Loan amount not clearly stated"),
                    "📅 Repayment Terms (EMI/Monthly Payment)": format_findings(findings["repayment_terms"], "⚠️ Repayment terms not clearly stated"),
                    "⏱️ Loan Duration/Tenure": format_findings(findings["loan_duration"], "⚠️ Loan tenure not clearly stated"),
                    "⚠️ What Happens If You Default": format_findings(findings["default_consequences"], "No specific default consequences identified"),
                    "🔄 Can They Change Terms?": format_findings(findings["change_terms_rights"], "No unilateral change rights identified"),
                    "⏰ Grace Period (Days Before Penalty)": format_findings(findings["grace_period"], "No grace period information found"),
                    "🛡️ Insurance You Must Buy": format_findings(findings["insurance_requirements"], "No mandatory insurance identified"),
                    "👥 Personal Guarantee Required": format_findings(findings["personal_guarantee"], "No personal guarantee clauses identified"),
                    "💰 Prepayment/Foreclosure Rules": format_findings(findings["prepayment_rules"], "No prepayment rules identified"),
                    "⚖️ Which Court/City Has Jurisdiction": format_findings(findings["jurisdiction"], "No jurisdiction information found"),
                    "🔍 Unusual/Hidden Clauses (AI Detected)": format_findings(findings.get("unusual_clauses", []), "✅ No unusual clauses detected by AI")
                },
                "legal_terms_glossary": glossary,
                "document_stats": {
                    "original_length": len(doc.content),
                    "analysis_method": "Hybrid: Pattern matching (16 categories) + AI catch-all for unusual clauses",
                    "clauses_extracted": total_findings,
                    "categories_analyzed": 17,
                    "analysis_time": "~10-20 seconds"
                },
                "important_notes": [
                    "📌 Read EVERY clause shown above - these are direct quotes from the document",
                    "📌 CRITICAL: Check loan amount, interest rate, EMI, and tenure - these define your obligation",
                    "📌 Check what property/assets are 'security' - you can lose them if you don't pay",
                    "📌 Understand when they can 'terminate' or demand full payment immediately",
                    "📌 Check if they can change terms (interest rate, fees) without your consent",
                    "📌 Know what happens if you miss 2-3 payments (default consequences)",
                    "📌 AI detected unusual clauses - review these carefully as they may be hidden risks",
                    "📌 This analysis helps you ask the RIGHT QUESTIONS to the lender"
                ],
                "disclaimer": "⚠️ This is AI-assisted analysis for informational purposes only. Always read the full document and consult a qualified lawyer before signing any legal agreement."
            }
    
    except Exception as e:
        if "404" in str(e):
            raise
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
    finally:
        db.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db = SessionLocal()
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    finally:
        db.close()
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "1.0.0"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting T&C Clarity API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
