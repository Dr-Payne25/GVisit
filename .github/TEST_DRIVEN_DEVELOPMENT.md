# Test-Driven Development (TDD) Guide for GVisit

## 🎯 The TDD Cycle

1. **RED** - Write a failing test
2. **GREEN** - Write minimal code to pass the test
3. **REFACTOR** - Improve the code while keeping tests green

## 📋 TDD Workflow for New Features

### Step 1: Write Security Tests FIRST

Before implementing ANY feature, write tests for:
- Authentication requirements
- Authorization boundaries
- Input validation
- XSS prevention
- CSRF protection

### Step 2: Write Feature Tests

```python
# Example: Before adding a "favorite entries" feature

def test_user_can_favorite_entry():
    """Test that users can mark entries as favorites"""
    # This test will FAIL initially - that's good!
    login_user('testuser', 'password')
    
    # Create an entry
    entry_id = create_journal_entry("Test content")
    
    # Favorite the entry
    response = client.post(f'/journal/favorite/{entry_id}')
    assert response.status_code == 200
    
    # Verify it's marked as favorite
    entries = get_journal_entries()
    assert entries[0]['is_favorite'] == True

def test_user_cannot_favorite_others_entries():
    """Security test - users can't favorite other users' entries"""
    # Create entry as user1
    login_user('user1', 'password1')
    entry_id = create_journal_entry("User1 content")
    logout()
    
    # Try to favorite as user2
    login_user('user2', 'password2')
    response = client.post(f'/journal/favorite/{entry_id}')
    assert response.status_code == 404  # Entry not found for this user

def test_favorite_requires_authentication():
    """Security test - must be logged in to favorite"""
    response = client.post('/journal/favorite/1')
    assert response.status_code == 302  # Redirect to login
```

### Step 3: Implement Minimal Code

```python
# app.py - Add only what's needed to pass tests
@app.route('/journal/favorite/<int:entry_id>', methods=['POST'])
@journal_login_required
def favorite_entry(entry_id):
    username = session.get('journal_user')
    entries = get_journal_entries()
    
    # Find entry belonging to current user
    for entry in entries:
        if entry['id'] == entry_id and entry['username'] == username:
            entry['is_favorite'] = True
            save_journal_entries(entries)
            return jsonify({'success': True})
    
    return jsonify({'error': 'Entry not found'}), 404
```

### Step 4: Write Edge Case Tests

```python
def test_favorite_idempotency():
    """Test that favoriting twice doesn't break anything"""
    login_user('testuser', 'password')
    entry_id = create_journal_entry("Test")
    
    # Favorite twice
    client.post(f'/journal/favorite/{entry_id}')
    response = client.post(f'/journal/favorite/{entry_id}')
    
    assert response.status_code == 200
    entries = get_journal_entries()
    assert entries[0]['is_favorite'] == True

def test_favorite_with_xss_attempt():
    """Security test - XSS in favorite request"""
    login_user('testuser', 'password')
    
    # Try XSS in entry_id
    response = client.post('/journal/favorite/<script>alert("xss")</script>')
    assert response.status_code == 404
    assert b'<script>' not in response.data
```

## 🔒 Security Test Templates

### XSS Prevention Test Template

```python
def test_xss_prevention_in_[feature]():
    """Test XSS prevention in [feature name]"""
    xss_payloads = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        'javascript:alert("XSS")',
        '<svg onload=alert(1)>'
    ]
    
    for payload in xss_payloads:
        # Submit payload
        response = submit_with_payload(payload)
        
        # Verify it's escaped in output
        assert payload not in response.data.decode()
        assert '&lt;script&gt;' in response.data.decode()
```

### Authentication Test Template

```python
def test_[feature]_requires_authentication():
    """Test that [feature] requires login"""
    # Ensure logged out
    client.post('/logout_journal')
    
    # Try to access feature
    response = client.get('/[feature_endpoint]')
    assert response.status_code == 302
    assert '/journal_login' in response.location
```

### Authorization Test Template

```python
def test_[feature]_authorization_boundaries():
    """Test that users can only access their own [resources]"""
    # Create resource as user1
    login_user('user1', 'password1')
    resource_id = create_resource()
    logout()
    
    # Try to access as user2
    login_user('user2', 'password2')
    response = access_resource(resource_id)
    assert response.status_code == 404
```

## 📊 Coverage Requirements

### Before Merging ANY PR:

1. **New Features**: Must have ≥ 90% test coverage
2. **Bug Fixes**: Must include regression tests
3. **Security Features**: Must have 100% test coverage
4. **Overall Project**: Must maintain ≥ 85% coverage

### Running Coverage Checks:

```bash
# Check coverage for new code
python3 -m pytest tests/test_new_feature.py --cov=app --cov-report=term-missing

# Ensure no coverage regression
python3 -m pytest --cov=app --cov-fail-under=85
```

## 🚀 Real-World TDD Example

Let's walk through adding a "search journal entries" feature:

### 1. Write Security Tests First

```python
# tests/test_search.py
def test_search_requires_authentication():
    response = client.get('/journal/search?q=test')
    assert response.status_code == 302

def test_search_only_returns_own_entries():
    # User1 creates entry
    login_user('user1', 'password1')
    create_entry('Secret user1 data')
    logout()
    
    # User2 searches
    login_user('user2', 'password2')
    response = client.get('/journal/search?q=secret')
    assert b'Secret user1 data' not in response.data

def test_search_prevents_xss():
    login_user('test', 'pass')
    response = client.get('/journal/search?q=<script>alert(1)</script>')
    assert b'<script>' not in response.data
```

### 2. Write Feature Tests

```python
def test_search_by_content():
    login_user('test', 'pass')
    create_entry('Python programming tips')
    create_entry('JavaScript best practices')
    
    response = client.get('/journal/search?q=python')
    assert b'Python programming tips' in response.data
    assert b'JavaScript best practices' not in response.data

def test_search_by_tags():
    login_user('test', 'pass')
    create_entry('Content 1', tags='work,python')
    create_entry('Content 2', tags='personal,javascript')
    
    response = client.get('/journal/search?q=tag:python')
    assert b'Content 1' in response.data
    assert b'Content 2' not in response.data

def test_search_empty_query():
    login_user('test', 'pass')
    response = client.get('/journal/search?q=')
    assert response.status_code == 400
    assert b'Query cannot be empty' in response.data
```

### 3. Run Tests (They Should Fail)

```bash
python3 -m pytest tests/test_search.py -v
# All tests should FAIL - this is expected!
```

### 4. Implement Feature

Only NOW do we write the actual code:

```python
@app.route('/journal/search')
@journal_login_required
def search_entries():
    query = request.args.get('q', '').strip()
    
    if not query:
        return "Query cannot be empty", 400
    
    # Escape query for display
    safe_query = escape(query)
    
    username = session.get('journal_user')
    entries = get_journal_entries()
    
    # Filter entries
    results = []
    for entry in entries:
        if entry['username'] != username:
            continue
            
        if query.startswith('tag:'):
            tag_search = query[4:].lower()
            if tag_search in [t.lower() for t in entry.get('tags', [])]:
                results.append(entry)
        else:
            if query.lower() in entry['content'].lower():
                results.append(entry)
    
    return render_template('search_results.html', 
                         results=results, 
                         query=safe_query)
```

### 5. Run Tests Again

```bash
python3 -m pytest tests/test_search.py -v
# All tests should now PASS!
```

### 6. Check Coverage

```bash
python3 -m pytest tests/test_search.py --cov=app --cov-report=term-missing
# Aim for 100% coverage of the new code
```

## 🎓 TDD Best Practices

1. **Write Tests First** - Always, no exceptions
2. **One Test, One Assertion** - Keep tests focused
3. **Test Names Describe Behavior** - `test_user_can_...`, `test_system_prevents_...`
4. **Fast Tests** - Use mocks for external services
5. **Independent Tests** - Each test sets up its own data
6. **Security First** - Write security tests before feature tests

## 🔄 Continuous Integration

Add to `.github/workflows/test.yml`:

```yaml
- name: Run tests with coverage
  run: |
    python -m pytest --cov=app --cov-fail-under=85
    
- name: Security test suite
  run: |
    python -m pytest tests/test_security.py -v
    
- name: Check for XSS vulnerabilities
  run: |
    python -m pytest -k "xss" -v
```

## 📝 Commit Message Format

When doing TDD:

```
test: add tests for journal search feature

- Add authentication requirement tests
- Add search functionality tests  
- Add XSS prevention tests
- Add authorization boundary tests
```

Then:

```
feat: implement journal search functionality

- Add /journal/search endpoint
- Support content and tag search
- Ensure user isolation
- Prevent XSS attacks

All tests passing (16/16)
```

## 🚨 Emergency Protocol

If you find a security vulnerability through testing:

1. **Don't commit the vulnerable code**
2. **Write a failing test that exposes the issue**
3. **Fix the vulnerability**
4. **Ensure the test passes**
5. **Add more related security tests**
6. **Document in SECURITY.md**

Remember: **A failing test is better than a security hole!** 