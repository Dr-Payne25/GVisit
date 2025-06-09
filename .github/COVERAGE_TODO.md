# Coverage Improvement TODO

Current Coverage: **84%** (326 statements, 51 missed)
Target Coverage: **85%** (need to cover 4 more lines minimum)

## 🚨 High Priority - Security Vulnerabilities to Fix

### 1. XSS Vulnerability (CRITICAL)
- [ ] Fix HTML escaping in journal entries
- [ ] Use `Markup` and `escape` from Flask properly
- [ ] Add template filters for safe HTML rendering

### 2. Timing Attack
- [ ] Add constant-time comparison for login
- [ ] Use `bcrypt.checkpw()` for all password comparisons
- [ ] Ensure same response time for invalid usernames

### 3. Password Hash Format
- [ ] Verify all passwords use bcrypt format ($2b$...)
- [ ] Add migration for any legacy passwords

## 📊 Coverage Gaps to Fill (Lines Not Covered)

### AWS Integration (lines 40-53)
```python
# Need to mock:
- boto3.client('s3')
- boto3.client('dynamodb')
- AWS credential validation
```

### DynamoDB Operations (lines 121-137, 143-144)
```python
# Test cases needed:
- test_backup_to_dynamodb()
- test_restore_from_dynamodb()
- test_dynamodb_connection_failure()
```

### Error Handlers (lines 268-276, 310-314)
```python
# Test cases needed:
- test_404_error_page()
- test_500_error_page()
- test_presentation_not_found()
- test_download_file_not_found()
```

### Utility Functions (lines 521-528)
```python
# Test cases needed:
- test_check_aws_configured()
- test_check_aws_not_configured()
```

## 🎯 Quick Wins (Easy Coverage Gains)

1. **Test AWS Configuration Check** (+8 lines)
   ```python
   def test_check_aws_configured():
       # Mock boto3 with credentials
       assert check_aws_configured() == True
   
   def test_check_aws_not_configured():
       # Mock boto3 without credentials
       assert check_aws_configured() == False
   ```

2. **Test Error Pages** (+9 lines)
   ```python
   def test_404_error():
       response = client.get('/nonexistent')
       assert response.status_code == 404
       assert b'Page not found' in response.data
   ```

3. **Test Production Config** (+2 lines)
   ```python
   def test_production_server_config():
       # Mock environment for production
       assert app.config['DEBUG'] == False
   ```

## 📝 Test Files to Create/Update

1. `tests/test_aws_integration.py` - Mock AWS services
2. `tests/test_error_handlers.py` - Test all error scenarios
3. `tests/test_utils.py` - Test utility functions

## 🚀 Action Plan

### Immediate (Fix Security Issues First):
1. [ ] Fix XSS vulnerability in templates
2. [ ] Fix timing attack in login
3. [ ] Verify password hash format

### Today (Reach 85% Coverage):
1. [ ] Add AWS configuration tests
2. [ ] Add error handler tests
3. [ ] Run `pytest --cov-fail-under=85` to verify

### This Week:
1. [ ] Reach 90% coverage
2. [ ] Add integration tests for AWS
3. [ ] Add performance benchmarks

## 🧪 Commands to Run

```bash
# Check current coverage
python3 -m pytest --cov=app --cov-report=term-missing

# Run security tests
python3 -m pytest tests/test_security.py -v

# Generate HTML report
python3 -m pytest --cov=app --cov-report=html
open htmlcov/index.html

# Fail if under 85%
python3 -m pytest --cov=app --cov-fail-under=85
```

## 📈 Coverage Tracking

| Date | Coverage | Tests | Security Issues |
|------|----------|-------|-----------------|
| Dec 8 | 83% | 36 | Unknown |
| Dec 8 | 84% | 52 | 3 Critical |
| Target | 85%+ | 60+ | 0 | 