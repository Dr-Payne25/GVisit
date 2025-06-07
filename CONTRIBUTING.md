# Contributing to GVisit

Thank you for your interest in contributing to GVisit! This guide will help you get started.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Docker (optional)
- AWS CLI (optional)

### Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/GVisit.git
   cd GVisit
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/Dr-Payne25/GVisit.git
   ```
4. Install dependencies:
   ```bash
   make install
   make setup-ci
   ```

## 🔄 Development Workflow

### 1. Create a Feature Branch
Always create a new branch from main:
```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

### Branch Naming Convention
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Test additions/updates
- `chore/` - Maintenance tasks

### 2. Make Your Changes
- Write clean, readable code
- Follow Python PEP 8 style guide
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes
Run tests locally before pushing:
```bash
make test      # Run unit tests
make lint      # Check code style
make format    # Auto-format code
make security  # Run security scans
```

### 4. Commit Your Changes
Use conventional commit messages:
```bash
git add .
git commit -m "feat: Add user profile feature"
```

Commit Message Format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test additions or fixes
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📋 Pull Request Guidelines

1. **Fill out the PR template** completely
2. **Link related issues** using "Closes #123"
3. **Ensure all CI checks pass**
4. **Request review** from maintainers
5. **Respond to feedback** promptly

## ✅ Code Review Process

### What We Look For:
- Code quality and readability
- Test coverage
- Security best practices
- Performance implications
- Documentation updates

### Review Timeline:
- Initial review: 1-3 days
- Follow-up reviews: 1-2 days

## 🧪 Testing Guidelines

### Unit Tests
- Use pytest for all tests
- Aim for 80%+ code coverage
- Test edge cases and error conditions

### Running Tests:
```bash
# Run all tests
make test

# Run specific test file
make test-file FILE=tests/test_app.py

# Run with coverage report
pytest --cov=. --cov-report=html
```

## 🎨 Code Style

### Python Style
- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting

### Auto-formatting:
```bash
make format
```

### Linting:
```bash
make lint
```

## 📚 Documentation

### Where to Document:
- **Code**: Inline comments and docstrings
- **API**: Update API documentation
- **README**: Update for new features
- **CHANGELOG**: Update for notable changes

### Docstring Format:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid input provided
    """
```

## 🐛 Reporting Issues

### Before Creating an Issue:
1. Check existing issues
2. Verify it's reproducible
3. Collect relevant information

### Issue Template Includes:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots (if applicable)

## 💡 Suggesting Enhancements

### Enhancement Proposals Should Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Potential impact on existing features

## 🔒 Security

### Reporting Security Issues:
- **DO NOT** create public issues
- Email security concerns directly
- Include detailed description
- Wait for confirmation before disclosure

### Security Best Practices:
- Never commit secrets or credentials
- Use environment variables
- Follow OWASP guidelines
- Run security scans: `make security`

## 📦 Dependencies

### Adding Dependencies:
1. Justify the need
2. Check license compatibility
3. Consider security implications
4. Update requirements.txt
5. Document usage

## 🚀 Release Process

1. All tests passing
2. Documentation updated
3. CHANGELOG updated
4. Version bumped
5. Tagged and released

## 📞 Getting Help

- Create an issue for bugs
- Start a discussion for questions
- Check existing documentation
- Review closed issues/PRs

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Project documentation

Thank you for contributing to GVisit! 🎉 