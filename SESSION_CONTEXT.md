# GVisit Project Context - Session Summary

## 🚀 Project Overview
**GVisit**: A Flask web application with password-protected PowerPoint presentations and a journaling system with user authentication, tags, and AWS integration.

## 📍 Current State (As of this session)

### Features Implemented
1. **PowerPoint Section**
   - Password-protected presentations (password: `GVISIT`)
   - Two presentations: ppt1 (Your Visit) and ppt2 (Restaurants)
   - Secure file download functionality

2. **Journal Application**
   - User registration/login (case-insensitive usernames)
   - Create, Read, Update, Delete journal entries
   - Tag system for categorizing entries
   - "Remember me for 30 days" functionality
   - User isolation (users can only see/edit their own entries)
   - Edit history tracking with timestamps

3. **AWS Integration**
   - S3 bucket configured for backups
   - DynamoDB table ready (but not actively used)
   - Backup/restore functionality in place

### Technical Stack
- **Backend**: Python 3.9.6, Flask 2.3.3
- **Frontend**: Bootstrap 5 (dark theme)
- **Data Storage**: JSON files (journal_entries.json, users.json)
- **Authentication**: Werkzeug password hashing (pbkdf2:sha256)
- **Testing**: pytest with 85% code coverage
- **Server**: Runs on port 5002

## 🔒 Security Status

### ✅ Fixed Vulnerabilities
1. **XSS in Journal Content**: Removed `| safe` filter from templates
2. **Timing Attack in Login**: Implemented constant-time password comparison
3. **Password Storage**: Using secure hashing (pbkdf2:sha256)

### ❌ Remaining Security Issues
1. **Information Leak**: Error messages reveal whether journal entries exist for other users
2. **Tag XSS**: Tags containing HTML/JavaScript are not properly escaped
3. **No CSRF Protection**: Forms lack CSRF tokens
4. **No Rate Limiting**: Brute force attacks possible

## 📊 Testing & Coverage
- **Total Tests**: 74 (71 passing, 3 failing)
- **Code Coverage**: 85% (280/331 statements)
- **Test Files**:
  - `tests/test_app.py` - Original tests
  - `tests/test_journal_features.py` - Journal feature tests
  - `tests/test_security.py` - Basic security tests
  - `tests/test_gvisit_security.py` - Comprehensive security tests

## 🌿 Git Workflow
- **Main Branch**: Production-ready code
- **Dev Branch**: Integration branch for testing
- **Feature Branches**: `feature/*` for new development
- **Current Branch**: dev (contains all latest features)

## 📁 Key Files & Locations
```
/Users/alexpayne/code/GVisitStuff/
├── app.py                    # Main Flask application
├── templates/               # HTML templates
│   ├── journal.html        # Main journal page
│   ├── edit_journal.html   # Edit entry page
│   └── ...
├── static/                  # CSS, JS, PowerPoints
│   └── ppts/               # PowerPoint files
├── tests/                   # All test files
├── journal_entries.json     # Journal data
├── users.json              # User data
└── requirements.txt        # Python dependencies
```

## 🔧 Next Session Tasks

### High Priority
1. **Fix Information Leak**
   - Change error message in `/journal/edit/<id>` to generic "Entry not found"
   - Remove any permission-specific error messages

2. **Fix Tag XSS**
   - Ensure all tag content is HTML-escaped in templates
   - Add validation to prevent HTML in tags

3. **Add CSRF Protection**
   - Implement Flask-WTF for CSRF tokens
   - Add tokens to all forms

### Medium Priority
1. **Rate Limiting**
   - Install Flask-Limiter
   - Add limits to login/registration endpoints

2. **Security Headers**
   - Add Flask-Talisman for security headers
   - Configure CSP, HSTS, X-Frame-Options

3. **Input Validation**
   - Add length limits to all form fields
   - Validate username format (alphanumeric only?)

### Low Priority
1. **AWS Active Use**
   - Implement automatic backups to S3
   - Consider moving to DynamoDB for data storage

2. **Two-Factor Authentication**
   - Add optional 2FA for users
   - Email or TOTP-based

3. **Audit Logging**
   - Log security events
   - Track failed login attempts

## 🎯 For Presentation Work
When you're ready to work on presentations:
1. PowerPoint files are in `static/ppts/`
2. Current presentations:
   - `ppt1.pptx` - "Your Visit to Seattle"
   - `ppt2.pptx` - "Seattle Restaurant Recommendations"
3. To update: Replace files in `static/ppts/` directory
4. No code changes needed unless adding new presentations

## 💡 Quick Commands
```bash
# Start the app
cd /Users/alexpayne/code/GVisitStuff
python3 app.py

# Run tests
python3 -m pytest

# Check coverage
python3 -m pytest --cov=app --cov-report=term-missing

# Git workflow
git checkout dev
git pull origin dev
git checkout -b feature/your-feature
# ... make changes ...
git add .
git commit -m "feat: your feature"
git push origin feature/your-feature
```

## 🔐 Important Passwords/Info
- PowerPoint Password: `GVISIT`
- Default test users: Check `users.json`
- App runs on: http://127.0.0.1:5002

## 📚 Documentation Created This Session
1. `DEEP_DIVE_SECURITY_VULNERABILITIES.md` - Detailed security explanations
2. `REAL_WORLD_ATTACK_SCENARIOS.md` - Attack scenarios and impacts
3. `SECURITY_TESTING_SUMMARY.md` - Testing progress and findings
4. `.github/TESTING_STRATEGY.md` - Comprehensive testing approach
5. `.github/TEST_DRIVEN_DEVELOPMENT.md` - TDD guidelines

---

**Session Achievement**: Increased code coverage from 26% to 85% by implementing comprehensive security testing! 🎉 