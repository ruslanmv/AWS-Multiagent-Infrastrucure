# Contributing to AWS Orchestrator

First off, thank you for considering contributing to AWS Orchestrator! It's people like you that make this project a great tool for the community.

## 🎯 **Code of Conduct**

This project and everyone participating in it is governed by respect, professionalism, and inclusivity. By participating, you are expected to uphold these values.

## 🚀 **How Can I Contribute?**

### **Reporting Bugs**

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, configurations, etc.)
- **Describe the behavior you observed and what you expected**
- **Include logs and error messages**
- **Specify your environment** (Python version, OS, AWS region, etc.)

**Example Bug Report:**
```markdown
## Bug: PII detection fails for UK phone numbers

**Steps to reproduce:**
1. Create a task with query: "Call me at +44 20 7123 4567"
2. Run with guardrails enabled
3. Observe that phone number is not masked

**Expected:** Phone number should be detected and masked as [PHONE_REDACTED]
**Actual:** Phone number remains visible in response

**Environment:**
- Python 3.11.5
- AWS Orchestrator 0.1.0
- Region: eu-west-1
```

### **Suggesting Enhancements**

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any alternative solutions or features you've considered**

### **Pull Requests**

1. **Fork the repository** and create your branch from `main`
2. **Follow the coding standards** (see below)
3. **Add tests** for any new functionality
4. **Ensure all tests pass**: `make test`
5. **Run the audit**: `make audit`
6. **Update documentation** if needed
7. **Write a clear commit message**

## 🛠️ **Development Setup**

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended)
- Git
- AWS CLI configured (for integration tests)

### Setup Steps

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/AWS-Multiagent-Infrastructure.git
cd AWS-Multiagent-Infrastructure

# 2. Install dependencies
make install
# or manually: uv sync

# 3. Activate virtual environment (if not using uv)
source .venv/bin/activate

# 4. Run tests to verify setup
make test
```

## 📝 **Coding Standards**

We maintain high code quality standards:

### **Python Style Guide**

- **PEP 8 compliance** with Ruff formatting
- **Maximum line length**: 100 characters
- **Import sorting**: Automatic with Ruff
- **Type hints**: Required for all functions (100% coverage)
- **Docstrings**: Google-style for all public APIs

### **Type Hints**

All code must have complete type annotations:

```python
# ✅ Good
async def process_task(self, request: TaskRequest) -> TaskResponse:
    """Process a task request."""
    ...

# ❌ Bad
async def process_task(self, request):
    """Process a task request."""
    ...
```

### **Docstrings**

Use Google-style docstrings:

```python
def calculate_score(value: float, threshold: float = 0.5) -> bool:
    """Calculate if a value exceeds the threshold.

    Args:
        value: The value to evaluate
        threshold: The threshold to compare against (default: 0.5)

    Returns:
        True if value exceeds threshold, False otherwise

    Raises:
        ValueError: If value is negative

    Example:
        >>> calculate_score(0.7)
        True
        >>> calculate_score(0.3)
        False
    """
    if value < 0:
        raise ValueError("Value must be non-negative")
    return value > threshold
```

### **Testing Requirements**

- **All new features require tests**
- **Aim for >90% code coverage**
- **Use pytest fixtures** for common setup
- **Use async tests** for async code (`@pytest.mark.asyncio`)
- **Mock external dependencies** (AWS services, etc.)

```python
# Example test structure
class TestOrchestrator:
    """Test Orchestrator functionality."""

    @pytest.fixture
    def orchestrator(self) -> Orchestrator:
        """Create orchestrator for testing."""
        config = OrchestratorConfig(name="test")
        return Orchestrator(config)

    @pytest.mark.asyncio
    async def test_process_task(self, orchestrator: Orchestrator) -> None:
        """Test task processing."""
        request = TaskRequest(user_id="test", query="Test")
        response = await orchestrator.process_task(request)
        assert response.status == AgentStatus.SUCCESS
```

## 🔍 **Code Review Process**

All submissions require review. We use GitHub pull requests for this:

1. **Automated Checks**: CI/CD runs tests, linting, type checking, and security scans
2. **Human Review**: A maintainer reviews the code for quality and design
3. **Feedback**: Address any requested changes
4. **Merge**: Once approved, your PR will be merged

### **What We Look For**

- ✅ Code follows style guidelines
- ✅ Tests are comprehensive
- ✅ Type hints are complete
- ✅ Documentation is updated
- ✅ Commits are well-formatted
- ✅ No security vulnerabilities
- ✅ Performance is acceptable

## 📦 **Commit Message Guidelines**

We follow conventional commit messages for clarity:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### **Types**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### **Examples**

```bash
feat(orchestrator): add support for custom agent types

- Added CustomAgent base class
- Updated agent registry to support plugins
- Added tests for custom agent loading

Closes #123

---

fix(compliance): improve PII detection for international phone numbers

- Added regex patterns for UK, EU phone formats
- Updated masking logic
- Added comprehensive test cases

Fixes #456
```

## 🏗️ **Project Structure**

Understanding the project layout:

```
aws-orchestrator/
├── src/aws_orchestrator/       # Source code
│   ├── core/                   # Core orchestration engine
│   │   ├── models.py          # Pydantic models
│   │   └── orchestrator.py    # Main orchestrator
│   ├── agents/                 # Agent implementations
│   │   ├── base.py            # Base agent class
│   │   └── bedrock.py         # Bedrock agent
│   ├── guardrails/             # Compliance features
│   │   └── compliance.py      # PII detection, etc.
│   ├── utils/                  # Utilities
│   │   └── logger.py          # Logging setup
│   └── cli/                    # CLI interface
│       └── main.py            # Typer commands
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                       # Documentation
├── Makefile                    # Development commands
├── pyproject.toml             # Project configuration
└── Dockerfile                 # Docker image
```

## 🧪 **Running Tests**

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_orchestrator.py -v

# Run with coverage report
pytest --cov=src/aws_orchestrator --cov-report=html

# Run only fast tests (skip integration)
pytest -m "not integration"
```

## 🔒 **Security**

- **Never commit secrets** (API keys, credentials, etc.)
- **Run Bandit** before submitting: `make audit`
- **Report security issues privately** to contact@ruslanmv.com
- **Use `.env` files** for local secrets (add to `.gitignore`)

## 📚 **Documentation**

When adding features:

1. **Update docstrings** in code
2. **Update README.md** if user-facing
3. **Add examples** for new functionality
4. **Update type hints** for API changes

## 🎉 **Recognition**

Contributors will be:

- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Credited in documentation

## 📞 **Questions?**

- **GitHub Discussions**: For questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Email**: contact@ruslanmv.com for private inquiries

---

**Thank you for contributing to AWS Orchestrator!** 🚀

Every contribution, no matter how small, makes this project better for everyone.
