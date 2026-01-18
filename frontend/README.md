# T&C Clarity - Frontend UI

Demo interface for testing the legal terms analyzer.

## Files

- **index.html** - Main UI with 3 input methods (file upload, URL, text paste)
- **styles.css** - Modern card-based design with responsive layout
- **script.js** - API integration and results display logic

## How to Use

1. Make sure the backend is running:
   ```bash
   python app.py
   ```

2. Open `index.html` in your browser or use a local server:
   ```bash
   # Option 1: Direct open
   open frontend/index.html
   
   # Option 2: Python HTTP server (recommended)
   cd frontend
   python3 -m http.server 8080
   # Then open http://localhost:8080
   ```

3. Choose input method:
   - **File Upload**: Select PDF/TXT file (e.g., ABCD loan document)
   - **URL**: Enter URL to a terms & conditions page
   - **Text Input**: Paste text directly (min 50 characters)

4. Click "Analyze Document" and wait 10-20 seconds

## Features

- ✅ 3 input methods (file, URL, text)
- ✅ Real-time loading progress (4 steps)
- ✅ Risk level banner (HIGH/MEDIUM/LOW)
- ✅ 17 category analysis with counts
- ✅ Expandable accordion for clause details
- ✅ Legal glossary with explanations
- ✅ Download report as TXT file
- ✅ "Analyze Another" button to reset

## API Configuration

Default API endpoint: `http://localhost:8000`

To change, edit `script.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (responsive design)
