# Contributing to T&C Clarity

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards others

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- Git
- A Hugging Face account (free tier)

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/YOUR_USERNAME/legal-terms-ai-summarizer.git
cd legal-terms-ai-summarizer
git remote add upstream https://github.com/NihalKA/legal-terms-ai-summarizer.git
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. **Set Up Pre-commit Hooks**
```bash
pre-commit install
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start Services**
```bash
docker-compose up -d postgres redis chromadb
alembic upgrade head
```

## How to Contribute

### Types of Contributions

- 🐛 **Bug Reports** - Found a bug? Open an issue
- ✨ **Feature Requests** - Have an idea? Suggest it
- 📝 **Documentation** - Improve docs or add examples
- 🔧 **Code** - Fix bugs or add features
- 🧪 **Testing** - Add or improve tests

### Contribution Workflow

1. **Create/Find an Issue**
   - Check existing issues first
   - Comment to claim it
   - Wait for maintainer approval

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

   Branch naming:
   - `feature/` - New features
   - `fix/` - Bug fixes
   - `docs/` - Documentation
   - `refactor/` - Code refactoring
   - `test/` - Test improvements

3. **Make Changes**
   - Write clean, readable code
   - Follow coding standards
   - Add tests
   - Update documentation

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add risk score calculation"
   ```

   Commit format:
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```

   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## Coding Standards

### Python Style Guide

We follow PEP 8:

```python
def calculate_risk_score(
    red_flags: List[RedFlag],
    weights: Dict[str, float]
) -> float:
    """
    Calculate overall risk score from red flags.

    Args:
        red_flags: List of identified red flags
        weights: Weight for each red flag type

    Returns:
        Risk score between 0 and 100

    Raises:
        ValueError: If weights don't sum to 1.0
    """
    if not math.isclose(sum(weights.values()), 1.0):
        raise ValueError("Weights must sum to 1.0")
    
    return min(max(score, 0), 100)
```

### Code Formatting

```bash
# Format with Black
black app/ tests/

# Check linting
flake8 app/ tests/

# Type checking
mypy app/

# Sort imports
isort app/ tests/
```

### Naming Conventions

```python
# Classes: PascalCase
class DocumentProcessor:
    pass

# Functions/variables: snake_case
def process_document(doc_id: str) -> Document:
    return processed_doc

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 50 * 1024 * 1024
```

## Testing Guidelines

### Writing Tests

```python
import pytest
from app.services.document_processor import DocumentProcessor

@pytest.fixture
def sample_document():
    return Document(
        id="test-doc-001",
        content="Sample terms...",
        filename="terms.pdf"
    )

def test_extract_text(sample_document):
    processor = DocumentProcessor()
    text = processor.extract_text(sample_document)
    
    assert text is not None
    assert len(text) > 0
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/unit/test_document_processor.py

# With coverage
pytest --cov=app --cov-report=html

# Parallel execution
pytest -n auto
```

### Test Coverage

- Minimum 80% coverage for new code
- All new features must include tests
- Bug fixes must include regression tests

## Pull Request Process

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] Commits follow conventions

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests passing
```

## LLMOps Best Practices

### Prompt Management

```python
# app/prompts/summarization.py
SUMMARY_PROMPT_V1 = """
Summarize the following terms...
"""

# Track versions
CURRENT_SUMMARY_PROMPT = SUMMARY_PROMPT_V1
```

### Experiment Tracking

```python
import mlflow

with mlflow.start_run(run_name="summarization_v2"):
    mlflow.log_param("model", "bart-large-cnn")
    mlflow.log_metric("rouge_l", rouge_score)
```

## Community

### Getting Help

1. Check documentation and existing issues
2. Search GitHub Discussions
3. Create a GitHub Discussion for questions

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project website

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to T&C Clarity! 🎉