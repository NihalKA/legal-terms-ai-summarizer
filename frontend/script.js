// ============================================================================
// T&C Clarity - Client-side JavaScript
// API Integration and UI Logic
// ============================================================================

const API_BASE_URL = 'http://localhost:8000';

// State
let currentDocId = null;
let analysisData = null;

// ============================================================================
// DOM Elements
// ============================================================================

const fileInput = document.getElementById('fileInput');
const urlInput = document.getElementById('urlInput');
const textInput = document.getElementById('textInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const fileName = document.getElementById('fileName');
const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const downloadBtn = document.getElementById('downloadBtn');
const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
const toggleGlossary = document.getElementById('toggleGlossary');
const glossaryContent = document.getElementById('glossaryContent');

// ============================================================================
// Event Listeners
// ============================================================================

fileInput.addEventListener('change', handleFileSelect);
urlInput.addEventListener('input', handleUrlInput);
textInput.addEventListener('input', handleTextInput);
analyzeBtn.addEventListener('click', handleAnalyze);
analyzeAnotherBtn.addEventListener('click', resetApp);
downloadBtn.addEventListener('click', downloadReport);
toggleGlossary.addEventListener('click', toggleGlossaryContent);

// ============================================================================
// File/URL/Text Input Handlers
// ============================================================================

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        fileName.textContent = `Selected: ${file.name}`;
        urlInput.value = '';
        textInput.value = '';
        analyzeBtn.disabled = false;
    }
}

function handleUrlInput(event) {
    const url = event.target.value.trim();
    if (url.length > 10) {
        fileInput.value = '';
        fileName.textContent = '';
        textInput.value = '';
        analyzeBtn.disabled = false;
    } else if (!fileInput.files[0] && !textInput.value.trim()) {
        analyzeBtn.disabled = true;
    }
}

function handleTextInput(event) {
    const text = event.target.value.trim();
    if (text.length >= 50) {
        fileInput.value = '';
        fileName.textContent = '';
        urlInput.value = '';
        analyzeBtn.disabled = false;
    } else if (!fileInput.files[0] && !urlInput.value.trim()) {
        analyzeBtn.disabled = true;
    }
}

// ============================================================================
// Main Analysis Flow
// ============================================================================

async function handleAnalyze() {
    const file = fileInput.files[0];
    const url = urlInput.value.trim();
    const text = textInput.value.trim();
    
    if (!file && !url && !text) {
        alert('Please select a file, enter a URL, or paste text');
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        // Step 1: Upload document
        updateLoadingStep(1, 'complete');
        updateLoadingStep(2, 'active');
        
        let uploadResponse;
        
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            
            uploadResponse = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                body: formData
            });
        } else if (url) {
            const formData = new FormData();
            formData.append('url', url);
            
            uploadResponse = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                body: formData
            });
        } else {
            const formData = new FormData();
            formData.append('text_input', text);
            
            uploadResponse = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                body: formData
            });
        }
        
        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.statusText}`);
        }
        
        const uploadData = await uploadResponse.json();
        currentDocId = uploadData.document_id;
        
        updateLoadingStep(2, 'complete');
        updateLoadingStep(3, 'active');
        
        // Step 2: Comprehensive analysis
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const analysisResponse = await fetch(
            `${API_BASE_URL}/summarize/${currentDocId}?method=comprehensive`
        );
        
        if (!analysisResponse.ok) {
            throw new Error(`Analysis failed: ${analysisResponse.statusText}`);
        }
        
        analysisData = await analysisResponse.json();
        
        updateLoadingStep(3, 'complete');
        updateLoadingStep(4, 'complete');
        
        // Display results
        await new Promise(resolve => setTimeout(resolve, 500));
        displayResults(analysisData);
        
    } catch (error) {
        console.error('Analysis error:', error);
        alert(`Error: ${error.message}\n\nPlease make sure the API server is running at ${API_BASE_URL}`);
        resetApp();
    }
}

// ============================================================================
// UI State Management
// ============================================================================

function showLoading() {
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    // Reset loading steps
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        step.classList.remove('active', 'complete');
    }
    updateLoadingStep(1, 'active');
}

function updateLoadingStep(stepNum, status) {
    const step = document.getElementById(`step${stepNum}`);
    step.classList.remove('active', 'complete');
    step.classList.add(status);
    
    if (status === 'complete') {
        step.textContent = step.textContent.replace('⏳', '✓');
    }
}

function resetApp() {
    uploadSection.style.display = 'block';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    fileInput.value = '';
    urlInput.value = '';
    textInput.value = '';
    fileName.textContent = '';
    analyzeBtn.disabled = true;
    currentDocId = null;
    analysisData = null;
}

// ============================================================================
// Results Display
// ============================================================================

function displayResults(data) {
    // Show results section
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Risk Banner
    displayRiskBanner(data);
    
    // Document Info
    displayDocumentInfo(data);
    
    // Findings Summary
    displayFindingsSummary(data);
    
    // Detailed Clauses
    displayDetailedClauses(data);
    
    // Legal Glossary
    displayGlossary(data);
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayRiskBanner(data) {
    const banner = document.getElementById('riskBanner');
    const riskLevel = document.getElementById('riskLevel');
    const riskSummary = document.getElementById('riskSummary');
    
    riskLevel.textContent = data.risk_level;
    riskSummary.textContent = data.risk_summary;
    
    // Determine risk class
    let riskClass = 'low';
    if (data.risk_level.includes('HIGH')) {
        riskClass = 'high';
    } else if (data.risk_level.includes('MEDIUM')) {
        riskClass = 'medium';
    }
    
    banner.className = `risk-banner ${riskClass}`;
}

function displayDocumentInfo(data) {
    document.getElementById('docSource').textContent = data.source;
    document.getElementById('docLength').textContent = 
        `${data.document_stats.original_length.toLocaleString()} characters`;
    document.getElementById('clausesFound').textContent = 
        data.document_stats.clauses_extracted;
    document.getElementById('analysisTime').textContent = 
        data.document_stats.analysis_time;
}

function displayFindingsSummary(data) {
    const grid = document.getElementById('findingsGrid');
    grid.innerHTML = '';
    
    const summary = data.findings_summary;
    
    // Define critical categories (in red)
    const criticalCategories = [
        '⚡ Penalties Found',
        '🚫 Termination Clauses Found',
        '⚠️ Default Consequences Found',
        '🔄 Change Terms Rights Found'
    ];
    
    for (const [label, count] of Object.entries(summary)) {
        const item = document.createElement('div');
        item.className = 'finding-item';
        
        if (count > 0) {
            item.classList.add('has-findings');
        }
        
        if (criticalCategories.includes(label) && count > 0) {
            item.classList.add('critical');
        }
        
        item.innerHTML = `
            <div class="finding-label">${label}</div>
            <div class="finding-count ${count === 0 ? 'zero' : ''}">${count}</div>
        `;
        
        grid.appendChild(item);
    }
}

function displayDetailedClauses(data) {
    const accordion = document.getElementById('clausesAccordion');
    accordion.innerHTML = '';
    
    const clauses = data.key_clauses_found;
    
    for (const [category, items] of Object.entries(clauses)) {
        const item = document.createElement('div');
        item.className = 'accordion-item';
        
        const count = Array.isArray(items) ? items.length : 0;
        const hasItems = count > 0 && !items[0].startsWith('⚠️') && !items[0].startsWith('✅') && !items[0].startsWith('No ');
        
        const header = document.createElement('button');
        header.className = 'accordion-header';
        header.innerHTML = `
            <span>${category}</span>
            <span class="accordion-badge ${hasItems ? 'has-items' : 'zero'}">${count}</span>
        `;
        
        const content = document.createElement('div');
        content.className = 'accordion-content';
        
        const body = document.createElement('div');
        body.className = 'accordion-body';
        
        if (hasItems) {
            const list = document.createElement('ul');
            list.className = 'clause-list';
            
            items.forEach(clause => {
                const li = document.createElement('li');
                li.className = 'clause-item';
                
                // Mark warnings and critical items
                if (clause.includes('terminate') || clause.includes('default') || clause.includes('penalty')) {
                    li.classList.add('critical');
                } else if (clause.includes('may') || clause.includes('change') || clause.includes('right')) {
                    li.classList.add('warning');
                }
                
                li.textContent = clause;
                list.appendChild(li);
            });
            
            body.appendChild(list);
        } else {
            body.innerHTML = `<p style="color: var(--gray-600); font-style: italic;">${items[0]}</p>`;
        }
        
        content.appendChild(body);
        
        header.addEventListener('click', () => {
            const isActive = header.classList.contains('active');
            
            // Close all other accordions
            document.querySelectorAll('.accordion-header').forEach(h => {
                h.classList.remove('active');
            });
            document.querySelectorAll('.accordion-content').forEach(c => {
                c.classList.remove('active');
            });
            
            // Toggle current
            if (!isActive) {
                header.classList.add('active');
                content.classList.add('active');
            }
        });
        
        item.appendChild(header);
        item.appendChild(content);
        accordion.appendChild(item);
    }
}

function displayGlossary(data) {
    const glossaryContainer = document.getElementById('glossaryContent');
    glossaryContainer.innerHTML = '';
    
    const glossary = data.legal_terms_glossary;
    
    for (const [term, definition] of Object.entries(glossary)) {
        const item = document.createElement('div');
        item.className = 'glossary-item';
        item.innerHTML = `
            <div class="glossary-term">${term}</div>
            <div class="glossary-definition">${definition}</div>
        `;
        glossaryContainer.appendChild(item);
    }
}

function toggleGlossaryContent() {
    const isVisible = glossaryContent.style.display === 'block';
    glossaryContent.style.display = isVisible ? 'none' : 'block';
    toggleGlossary.textContent = isVisible ? 'Show Glossary ▼' : 'Hide Glossary ▲';
}

// ============================================================================
// Download Report
// ============================================================================

function downloadReport() {
    if (!analysisData) {
        alert('No analysis data available');
        return;
    }
    
    // Create text report
    let report = '='.repeat(80) + '\n';
    report += 'T&C CLARITY - LEGAL ANALYSIS REPORT\n';
    report += '='.repeat(80) + '\n\n';
    
    report += `Document: ${analysisData.source}\n`;
    report += `Risk Level: ${analysisData.risk_level}\n`;
    report += `Risk Summary: ${analysisData.risk_summary}\n`;
    report += `Clauses Found: ${analysisData.document_stats.clauses_extracted}\n`;
    report += `Analysis Time: ${analysisData.document_stats.analysis_time}\n\n`;
    
    report += '='.repeat(80) + '\n';
    report += 'FINDINGS SUMMARY\n';
    report += '='.repeat(80) + '\n\n';
    
    for (const [label, count] of Object.entries(analysisData.findings_summary)) {
        report += `${label}: ${count}\n`;
    }
    
    report += '\n' + '='.repeat(80) + '\n';
    report += 'DETAILED CLAUSES\n';
    report += '='.repeat(80) + '\n\n';
    
    for (const [category, items] of Object.entries(analysisData.key_clauses_found)) {
        report += `\n${category}\n`;
        report += '-'.repeat(80) + '\n';
        
        if (Array.isArray(items) && items.length > 0) {
            items.forEach((item, idx) => {
                report += `${idx + 1}. ${item}\n\n`;
            });
        } else {
            report += 'No items found\n\n';
        }
    }
    
    report += '\n' + '='.repeat(80) + '\n';
    report += 'LEGAL TERMS GLOSSARY\n';
    report += '='.repeat(80) + '\n\n';
    
    for (const [term, definition] of Object.entries(analysisData.legal_terms_glossary)) {
        report += `${term}:\n${definition}\n\n`;
    }
    
    report += '\n' + '='.repeat(80) + '\n';
    report += 'IMPORTANT NOTES\n';
    report += '='.repeat(80) + '\n\n';
    
    analysisData.important_notes.forEach((note, idx) => {
        report += `${idx + 1}. ${note}\n\n`;
    });
    
    report += '\n' + '='.repeat(80) + '\n';
    report += analysisData.disclaimer + '\n';
    report += '='.repeat(80) + '\n';
    
    // Create and download file
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tc-clarity-report-${currentDocId}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ============================================================================
// Initialize
// ============================================================================

console.log('T&C Clarity UI initialized');
console.log(`API Base URL: ${API_BASE_URL}`);
console.log('Make sure the FastAPI server is running!');
