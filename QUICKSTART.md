# 🚀 Quick Start Guide

Get T&C Clarity running in 5 minutes!

## Prerequisites

- Python 3.10+ installed
- Docker Desktop running
- Terminal/Command Prompt

## Step-by-Step Setup

### 1. Start PostgreSQL

```bash
# In project directory
docker-compose up -d

# Verify it's running
docker ps
```

You should see `tcclarity-postgres` running.

### 2. Set Up Environment with uv

```bash
# Create venv and install dependencies (one command!)
uv sync

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

You'll see `(.venv)` in your terminal prompt.

**What just happened?** `uv sync` automatically:
- Created a virtual environment in `.venv/`
- Read dependencies from `pyproject.toml`
- Installed all dependencies (10-100x faster than pip!)
- Generated `uv.lock` for reproducible builds

This will take a few minutes. Go grab coffee! ☕

### 4. Set up Environment

```bash
# Copy the example env file
cp .env.example .env

# The defaults work perfectly for local development!
```

### 5. Run the Application

```bash
python app.py
```

You should see:
```
🚀 Starting T&C Clarity API...
📚 API Documentation: http://localhost:8000/docs
🏥 Health Check: http://localhost:8000/health
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Test It!

Open your browser to:
- **http://localhost:8000/docs** - Interactive API documentation
- **http://localhost:8000/health** - Health check

Or run the test script:
```bash
# In a new terminal (keep the app running)
python test_api.py
```

## 🎉 You're Done!

Try uploading a document:

1. Go to http://localhost:8000/docs
2. Click on "POST /analyze"
3. Click "Try it out"
4. Enter some text or upload a file
5. Click "Execute"
6. See your document analyzed!

## 🧪 Quick Test Examples

### Test with curl

```bash
# Test text input
curl -X POST "http://localhost:8000/analyze" \
  -F "text_input=Terms: You agree to arbitration for all disputes."

# Test URL
curl -X POST "http://localhost:8000/analyze" \
  -F "url=https://www.google.com/intl/en/policies/terms/"

# Test file upload (create a test file first)
echo "Test terms and conditions document content here." > test.txt
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@test.txt"
```

## 🐛 Troubleshooting

### PostgreSQL won't start
```bash
# Stop and remove containers
docker-compose down

# Start fresh
docker-compose up -d
```

### Port 8000 already in use
```bash
# Find what's using port 8000
lsof -ti :8000

# Kill it
lsof -ti :8000 | xargs kill -9

# Or change the port in app.py
```

### Module not found errors
```bash
# Make sure venv is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall dependencies
uv sync --reinstall
```

### Database connection error
```bash
# Check PostgreSQL is running
docker ps

# Check logs
docker logs tcclarity-postgres

# Restart database
docker-compose restart
```

## 📚 Next Steps

Once everything works:

1. Read [MVP_GUIDE.md](docs/MVP_GUIDE.md) to understand the approach
2. Check [NEXT_STEPS.md](docs/NEXT_STEPS.md) for implementing new features
3. Look at [API_MVP.md](docs/API_MVP.md) for API details

## 💡 Pro Tips

- Keep Docker Desktop running when developing
- Use the `/docs` page for testing - it's faster than curl
- Check the terminal logs if something goes wrong
- PostgreSQL data persists even if you stop the container

## 🎯 What You Just Built

You now have a working API that can:
- ✅ Accept T&C documents (text, URL, or file)
- ✅ Extract text from PDFs
- ✅ Scrape content from URLs
- ✅ Store everything in PostgreSQL
- ✅ Retrieve and list documents

**Next**: Add summarization, RAG, and red flag detection! 🚀
