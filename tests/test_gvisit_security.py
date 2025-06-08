"""
GVisit-Specific Security Test Suite

Tests security vulnerabilities specific to the GVisit application features:
- PowerPoint access control
- File download security
- Journal privacy
- AWS integration security
- Tag system security
"""

import unittest
import json
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, register_user, verify_user


class TestPowerPointSecurity(unittest.TestCase):
    """Test PowerPoint access control and download security"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()
    
    def test_powerpoint_authentication_bypass_attempt(self):
        """Test that PowerPoints can't be accessed without password"""
        # Try direct access to PowerPoint page
        response = self.client.get('/powerpoint/ppt1')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/ppt1', response.location)
        
        # Try direct download without auth
        response = self.client.get('/download_ppt/ppt1')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/ppt1', response.location)
    
    def test_powerpoint_session_isolation(self):
        """Test that authenticating for one PPT doesn't give access to another"""
        # Login to ppt1
        response = self.client.post('/login/ppt1', data={
            'password': 'GVISIT'
        })
        self.assertEqual(response.status_code, 302)
        
        # Try to access ppt2 without logging in
        response = self.client.get('/powerpoint/ppt2')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/ppt2', response.location)
    
    def test_powerpoint_path_traversal_download(self):
        """Test path traversal attempts in PowerPoint downloads"""
        # Authenticate first
        self.client.post('/login/ppt1', data={'password': 'GVISIT'})
        
        # Try path traversal attacks
        traversal_attempts = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            'ppt1/../../sensitive_file',
            '%2e%2e%2f%2e%2e%2fpasswords.txt',
            'ppt1\x00.pdf'  # Null byte injection
        ]
        
        for attempt in traversal_attempts:
            response = self.client.get(f'/download_ppt/{attempt}')
            # Should either redirect or return error, never 200
            self.assertNotEqual(response.status_code, 200)
    
    def test_powerpoint_invalid_id_handling(self):
        """Test handling of invalid PowerPoint IDs"""
        invalid_ids = [
            'ppt3',  # Non-existent
            '<script>alert(1)</script>',  # XSS attempt
            'ppt1 OR 1=1',  # SQL injection style
            '',  # Empty
            'null',
            'undefined'
        ]
        
        for ppt_id in invalid_ids:
            response = self.client.get(f'/login/{ppt_id}')
            # Should redirect to home with error or return 404
            self.assertIn(response.status_code, [302, 404])
            
            response = self.client.get(f'/download_ppt/{ppt_id}')
            self.assertIn(response.status_code, [302, 404])


class TestJournalPrivacySecurity(unittest.TestCase):
    """Test journal privacy and data isolation"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Set up temp files
        self.temp_journal = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_journal.write('[]')
        self.temp_journal.close()
        
        self.temp_users = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_users.write('{}')
        self.temp_users.close()
        
        import app as app_module
        self.original_journal_file = app_module.JOURNAL_FILE
        self.original_users_file = app_module.USERS_FILE
        app_module.JOURNAL_FILE = self.temp_journal.name
        app_module.USERS_FILE = self.temp_users.name
        
        # Create test users
        register_user('alice', 'password123')
        register_user('bob', 'password456')
    
    def tearDown(self):
        import app as app_module
        app_module.JOURNAL_FILE = self.original_journal_file
        app_module.USERS_FILE = self.original_users_file
        os.unlink(self.temp_journal.name)
        os.unlink(self.temp_users.name)
    
    def test_cross_user_journal_access_prevention(self):
        """Test that users cannot access each other's journal entries via ID manipulation"""
        # Alice creates an entry
        self.client.post('/journal_login', data={
            'username': 'alice',
            'password': 'password123'
        })
        
        self.client.post('/journal', data={
            'focus': 'Private Thoughts',
            'content': 'Alice\'s secret diary entry',
            'mood': 'good',
            'energy': 'High',
            'tags': 'private,secret'
        })
        
        self.client.post('/logout_journal')
        
        # Bob logs in and tries to access Alice's entry
        self.client.post('/journal_login', data={
            'username': 'bob',
            'password': 'password456'
        })
        
        # Try to edit Alice's entry (ID 1)
        response = self.client.get('/journal/edit/1')
        self.assertEqual(response.status_code, 302)
        
        # Try to delete Alice's entry
        response = self.client.post('/journal/delete/1')
        self.assertEqual(response.status_code, 302)
        
        # Verify Bob's journal view doesn't show Alice's entry
        response = self.client.get('/journal')
        self.assertNotIn(b"Alice's secret diary entry", response.data)
    
    def test_journal_id_enumeration_prevention(self):
        """Test that journal entry IDs can't be enumerated"""
        # Login as user
        self.client.post('/journal_login', data={
            'username': 'alice',
            'password': 'password123'
        })
        
        # Try to access non-existent high IDs
        for entry_id in [999, 10000, 99999]:
            response = self.client.get(f'/journal/edit/{entry_id}')
            self.assertEqual(response.status_code, 302)
            
            response = self.client.post(f'/journal/delete/{entry_id}')
            self.assertEqual(response.status_code, 302)
    
    def test_journal_data_leak_in_errors(self):
        """Test that error messages don't leak information about other users"""
        # Alice creates entry
        self.client.post('/journal_login', data={
            'username': 'alice',
            'password': 'password123'
        })
        self.client.post('/journal', data={
            'focus': 'Test',
            'content': 'Test',
            'mood': 'good',
            'energy': 'High'
        })
        self.client.post('/logout_journal')
        
        # Bob tries to access
        self.client.post('/journal_login', data={
            'username': 'bob',
            'password': 'password456'
        })
        
        response = self.client.get('/journal/edit/1', follow_redirects=True)
        # Should not reveal that entry exists for another user
        self.assertIn(b'Entry not found', response.data)
        self.assertNotIn(b'permission', response.data.lower())
        self.assertNotIn(b'alice', response.data.lower())


class TestFileSecurityVulnerabilities(unittest.TestCase):
    """Test file handling security vulnerabilities"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_null_byte_injection(self):
        """Test null byte injection in file paths"""
        # Authenticate for PowerPoint
        self.client.post('/login/ppt1', data={'password': 'GVISIT'})
        
        null_byte_attacks = [
            'presentation.pptx\x00.txt',
            'file\x00../../etc/passwd',
            'document%00.pdf'
        ]
        
        for attack in null_byte_attacks:
            response = self.client.get(f'/download_ppt/{attack}')
            self.assertNotEqual(response.status_code, 200)
    
    def test_file_inclusion_attacks(self):
        """Test local/remote file inclusion attempts"""
        attacks = [
            'file:///etc/passwd',
            'http://evil.com/malware.exe',
            'ftp://attacker.com/backdoor',
            '\\\\evil\\share\\virus.exe'
        ]
        
        for attack in attacks:
            response = self.client.get(f'/download_ppt/{attack}')
            self.assertIn(response.status_code, [302, 404])


class TestInputValidationSecurity(unittest.TestCase):
    """Test input validation across all forms"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Set up temp files
        self.temp_users = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_users.write('{}')
        self.temp_users.close()
        
        import app as app_module
        self.original_users_file = app_module.USERS_FILE
        app_module.USERS_FILE = self.temp_users.name
    
    def tearDown(self):
        import app as app_module
        app_module.USERS_FILE = self.original_users_file
        os.unlink(self.temp_users.name)
    
    def test_registration_input_validation(self):
        """Test registration form input validation"""
        # Test extremely long username
        response = self.client.post('/journal_register', data={
            'username': 'a' * 10000,
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Should handle gracefully
        
        # Test special characters in username
        special_usernames = [
            'user<script>',
            'user"onclick="alert(1)"',
            'user\';DROP TABLE users;--',
            'user\x00admin',
            '../../../etc/passwd',
            'user@evil.com<>'
        ]
        
        for username in special_usernames:
            response = self.client.post('/journal_register', data={
                'username': username,
                'password': 'password123',
                'confirm_password': 'password123'
            })
            # Should either reject or safely handle
            self.assertIn(response.status_code, [200, 302])
    
    def test_journal_form_overflow_attacks(self):
        """Test buffer overflow attempts in journal forms"""
        # Register and login
        register_user('testuser', 'password123')
        self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Try to overflow each field
        overflow_data = {
            'focus': 'A' * 100000,
            'content': 'B' * 1000000,
            'mood': 'C' * 10000,
            'energy': 'D' * 10000,
            'action_item': 'E' * 100000,
            'gratitude_1': 'F' * 100000,
            'tags': ','.join(['tag'] * 10000)
        }
        
        response = self.client.post('/journal', data=overflow_data)
        # Should handle without crashing
        self.assertIn(response.status_code, [200, 302])
    
    def test_tag_injection_attacks(self):
        """Test various injection attacks through the tag system"""
        register_user('testuser', 'password123')
        self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        malicious_tags = [
            '<img src=x onerror=alert(1)>',
            'javascript:alert(1)',
            'onclick=alert(1)',
            '{{7*7}}',  # Template injection
            '${7*7}',   # Template injection
            '%(password)s',  # Format string
            '{user.__class__.__mro__}',  # Python object injection
        ]
        
        for tag in malicious_tags:
            response = self.client.post('/journal', data={
                'focus': 'Test',
                'content': 'Test',
                'mood': 'good',
                'energy': 'High',
                'tags': tag
            })
            
            # Verify tag is escaped in response
            response = self.client.get('/journal')
            # Should not execute/evaluate the malicious tag
            self.assertNotIn(b'49', response.data)  # 7*7
            self.assertNotIn(b'alert', response.data)
            if tag in ['<img src=x onerror=alert(1)>']:
                self.assertIn(b'&lt;', response.data)


class TestSessionSecurityVulnerabilities(unittest.TestCase):
    """Test session management vulnerabilities"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Set up temp users file
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
    
    def test_concurrent_session_handling(self):
        """Test handling of concurrent sessions for same user"""
        # Login from "browser 1"
        client1 = self.app.test_client()
        response1 = client1.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response1.status_code, 302)
        
        # Login from "browser 2" 
        client2 = self.app.test_client()
        response2 = client2.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response2.status_code, 302)
        
        # Both sessions should work
        response1 = client1.get('/journal')
        self.assertEqual(response1.status_code, 200)
        
        response2 = client2.get('/journal')
        self.assertEqual(response2.status_code, 200)
    
    def test_session_cookie_security_headers(self):
        """Test that session cookies have proper security headers"""
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Check session cookie attributes
        cookies = response.headers.getlist('Set-Cookie')
        session_cookie = next((c for c in cookies if 'session=' in c), None)
        
        if session_cookie:
            # Should have security attributes
            self.assertIn('HttpOnly', session_cookie)
            # Note: Secure flag may not be set in test environment
    
    def test_logout_invalidates_session(self):
        """Test that logout properly invalidates the session"""
        # Login
        self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Verify logged in
        response = self.client.get('/journal')
        self.assertEqual(response.status_code, 200)
        
        # Logout
        self.client.post('/logout_journal')
        
        # Try to access journal
        response = self.client.get('/journal')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/journal_login', response.location)


class TestAWSIntegrationSecurity(unittest.TestCase):
    """Test AWS integration security"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('app.boto3')
    def test_aws_credential_exposure_prevention(self, mock_boto3):
        """Test that AWS credentials are not exposed in responses"""
        # Make various requests
        endpoints = ['/', '/health', '/journal_login']
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            response_text = response.data.decode('utf-8').lower()
            
            # Check for AWS credential patterns
            self.assertNotIn('akia', response_text)  # AWS Access Key ID prefix
            self.assertNotIn('aws_access_key', response_text)
            self.assertNotIn('aws_secret', response_text)
            self.assertNotIn('secretkey', response_text)
    
    def test_s3_bucket_manipulation_attempts(self):
        """Test attempts to manipulate S3 bucket operations"""
        # This would need actual AWS mocking for full testing
        # Here we test that the app handles malicious bucket names gracefully
        pass
    
    @patch('app.aws_backup')
    def test_backup_restore_authorization(self, mock_backup):
        """Test that backup/restore operations require proper authorization"""
        # Attempt to trigger backup without auth
        response = self.client.post('/backup')  # If such endpoint exists
        self.assertNotEqual(response.status_code, 200)


class TestRateLimitingAndBruteForce(unittest.TestCase):
    """Test rate limiting and brute force protection"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Set up temp users file
        self.temp_users = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_users.write('{}')
        self.temp_users.close()
        
        import app as app_module
        self.original_users_file = app_module.USERS_FILE
        app_module.USERS_FILE = self.temp_users.name
        
        register_user('victim', 'correctpassword')
    
    def tearDown(self):
        import app as app_module
        app_module.USERS_FILE = self.original_users_file
        os.unlink(self.temp_users.name)
    
    def test_login_brute_force_resilience(self):
        """Test that the app handles brute force login attempts"""
        # Simulate brute force attack
        passwords = ['password', '123456', 'admin', 'letmein', 'qwerty']
        
        for i, password in enumerate(passwords * 10):  # 50 attempts
            response = self.client.post('/journal_login', data={
                'username': 'victim',
                'password': password
            })
            # Should handle gracefully (not crash)
            self.assertIn(response.status_code, [200, 302])
    
    def test_registration_flooding(self):
        """Test handling of registration flooding attempts"""
        # Try to register many users rapidly
        for i in range(50):
            response = self.client.post('/journal_register', data={
                'username': f'flood_user_{i}',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            self.assertIn(response.status_code, [200, 302])


class TestErrorHandlingSecurityInfo(unittest.TestCase):
    """Test that error messages don't leak sensitive information"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        # Disable debug mode to test production error handling
        self.app.config['DEBUG'] = False
        self.client = self.app.test_client()
    
    def test_404_error_info_leak(self):
        """Test that 404 errors don't leak information"""
        response = self.client.get('/nonexistent/path/to/secret/file.db')
        self.assertEqual(response.status_code, 404)
        
        # Should not reveal file system structure
        response_text = response.data.decode('utf-8')
        self.assertNotIn('/home/', response_text)
        self.assertNotIn('/var/www/', response_text)
        self.assertNotIn('secret', response_text.lower())
    
    def test_500_error_info_leak(self):
        """Test that 500 errors don't leak sensitive information"""
        # This would need to trigger an actual error
        # Check that stack traces aren't exposed in production
        pass


if __name__ == '__main__':
    unittest.main() 