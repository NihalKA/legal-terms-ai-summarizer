#!/usr/bin/env python3
"""
Quick test script for T&C Clarity API
Tests all three input methods
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("🏥 Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_text_input():
    """Test copy-paste text input"""
    print("\n" + "="*60)
    print("📝 Testing Text Input (Copy-Paste)")
    print("="*60)
    
    sample_text = """
    TERMS AND CONDITIONS
    
    1. Acceptance of Terms
    By accessing and using this service, you accept and agree to be bound by the terms and provision of this agreement.
    
    2. Arbitration Clause
    Any dispute arising out of or related to this agreement shall be resolved through binding arbitration.
    
    3. Data Collection
    We collect personal information including your name, email address, and usage data.
    
    4. Changes to Terms
    We reserve the right to modify these terms at any time without prior notice.
    """
    
    response = requests.post(
        f"{API_URL}/analyze",
        data={"text_input": sample_text}
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get("document_id")


def test_url_input():
    """Test URL input"""
    print("\n" + "="*60)
    print("🌐 Testing URL Input")
    print("="*60)
    
    # Using a public terms of service URL
    test_url = "https://www.google.com/intl/en/policies/terms/"
    
    response = requests.post(
        f"{API_URL}/analyze",
        data={"url": test_url}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Document ID: {result['document_id']}")
        print(f"Source: {result['source']}")
        print(f"Length: {result['length']}")
        print(f"Preview: {result['preview'][:200]}...")
        return result['document_id']
    else:
        print(f"Error: {response.text}")
        return None


def test_file_upload():
    """Test file upload"""
    print("\n" + "="*60)
    print("📄 Testing File Upload")
    print("="*60)
    
    # Create a temporary test file
    test_content = """
    SAMPLE TERMS AND CONDITIONS
    
    This is a test terms and conditions document.
    It contains various clauses including arbitration agreements,
    data collection policies, and liability limitations.
    """
    
    with open("temp_test.txt", "w") as f:
        f.write(test_content)
    
    with open("temp_test.txt", "rb") as f:
        response = requests.post(
            f"{API_URL}/analyze",
            files={"file": ("test_terms.txt", f, "text/plain")}
        )
    
    import os
    os.remove("temp_test.txt")
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get("document_id")


def test_get_document(doc_id):
    """Test retrieving a document"""
    print("\n" + "="*60)
    print(f"📖 Testing Get Document (ID: {doc_id})")
    print("="*60)
    
    response = requests.get(f"{API_URL}/documents/{doc_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"ID: {result['id']}")
        print(f"Source Type: {result['source_type']}")
        print(f"Source: {result['source']}")
        print(f"Length: {result['length']}")
        print(f"Content Preview: {result['content'][:200]}...")


def test_list_documents():
    """Test listing all documents"""
    print("\n" + "="*60)
    print("📋 Testing List Documents")
    print("="*60)
    
    response = requests.get(f"{API_URL}/documents")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total Documents: {result['total']}")
    print(f"Showing: {len(result['documents'])} documents")
    
    for doc in result['documents']:
        print(f"\n  - ID {doc['id']}: {doc['source_type']} - {doc['source'][:50]}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 T&C CLARITY API TEST SUITE")
    print("="*60)
    
    try:
        # Test health
        test_health()
        
        # Test text input
        doc_id_1 = test_text_input()
        if doc_id_1:
            test_get_document(doc_id_1)
        
        # Test file upload
        doc_id_2 = test_file_upload()
        
        # Test URL input (may fail if network issues)
        try:
            doc_id_3 = test_url_input()
        except Exception as e:
            print(f"URL test skipped: {e}")
        
        # List all documents
        test_list_documents()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API is running: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
