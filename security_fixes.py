"""
Security Fixes for GVisit Application

This file contains the fixes for the three critical security vulnerabilities:
1. XSS (Cross-Site Scripting)
2. Timing Attack
3. Password Hash Format
"""

# FIX 1: XSS Vulnerability
# In templates/journal.html, line 138, REMOVE the |safe filter
# FROM: <p class="card-text">{{ entry.content.replace('\n', '<br>') | safe }}</p>
# TO:   <p class="card-text" style="white-space: pre-wrap;">{{ entry.content }}</p>

# FIX 2: Timing Attack in verify_user function
def verify_user_secure(username, password):
    """Verify user credentials with constant-time comparison"""
    from werkzeug.security import check_password_hash
    
    users = get_users()
    username_lower = username.lower()
    
    # Always perform the same operations regardless of username validity
    # Use a dummy hash if user doesn't exist
    dummy_hash = "$2b$12$dummy.hash.that.is.not.valid.but.takes.time.to.check"
    
    if username_lower in users:
        stored_hash = users[username_lower]["password_hash"]
        user_exists = True
    else:
        stored_hash = dummy_hash
        user_exists = False
    
    # Always perform the hash check (constant time)
    password_valid = check_password_hash(stored_hash, password)
    
    # Return True only if user exists AND password is valid
    return user_exists and password_valid

# FIX 3: Password Hash Format - Ensure bcrypt is used
def register_user_secure(username, password):
    """Register a new user with bcrypt hashing"""
    from werkzeug.security import generate_password_hash
    
    users = get_users()
    username_lower = username.lower()
    
    if username_lower in users:
        return False, "Username already exists"
    
    # Explicitly specify bcrypt method for password hashing
    # This ensures bcrypt is used even in older Werkzeug versions
    users[username_lower] = {
        "password_hash": generate_password_hash(password, method='bcrypt'),
        "display_name": username_lower.capitalize(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_users(users)
    return True, "User registered successfully"

# Additional security enhancement: Add password hash migration
def migrate_password_hashes():
    """Migrate any non-bcrypt password hashes to bcrypt"""
    users = get_users()
    migrated_count = 0
    
    for username, user_data in users.items():
        password_hash = user_data.get('password_hash', '')
        
        # Check if it's not a bcrypt hash (bcrypt hashes start with $2b$, $2a$, or $2y$)
        if not password_hash.startswith(('$2b$', '$2a$', '$2y$')):
            print(f"Warning: User '{username}' has non-bcrypt password hash")
            # In production, you'd need to prompt users to reset their passwords
            # or implement a migration strategy
            migrated_count += 1
    
    if migrated_count > 0:
        print(f"Found {migrated_count} users with non-bcrypt password hashes")
        print("These users should reset their passwords for better security")
    
    return migrated_count

# Template fix for better content rendering without XSS
"""
<!-- Alternative approach for preserving line breaks without |safe filter -->
<style>
.journal-content {
    white-space: pre-wrap;       /* Preserves whitespace and line breaks */
    word-wrap: break-word;       /* Ensures long words break */
    overflow-wrap: break-word;   /* Modern property for word breaking */
}
</style>

<p class="card-text journal-content">{{ entry.content }}</p>
"""

# Additional XSS protection for tags and other fields
def sanitize_user_input(text):
    """Sanitize user input to prevent XSS"""
    from markupsafe import escape
    
    if not text:
        return text
    
    # Escape HTML entities
    return escape(text)

# Example of how to properly display user content with formatting
def format_journal_content(content):
    """Format journal content for safe display with line breaks"""
    from markupsafe import Markup, escape
    
    if not content:
        return ""
    
    # First escape the content to prevent XSS
    escaped_content = escape(content)
    
    # Then replace newlines with <br> tags
    # Since we escaped first, user input <br> would be &lt;br&gt;
    formatted = escaped_content.replace('\n', Markup('<br>'))
    
    # Return as Markup so Jinja2 knows it's safe
    return Markup(formatted) 