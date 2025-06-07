import unittest
import json
import os
import tempfile
from datetime import datetime
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, register_user, verify_user, generate_remember_token, verify_remember_token
from werkzeug.security import generate_password_hash

class TestJournalAuthentication(unittest.TestCase):
    """Test suite for journal authentication features"""
    
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
        
    def tearDown(self):
        """Clean up temporary files"""
        import app as app_module
        app_module.JOURNAL_FILE = self.original_journal_file
        app_module.USERS_FILE = self.original_users_file
        os.unlink(self.temp_journal.name)
        os.unlink(self.temp_users.name)
        
    def test_journal_requires_login(self):
        """Test that journal page requires authentication"""
        response = self.client.get('/journal', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access your journal', response.data)
        self.assertIn(b'Journal Login', response.data)
        
    def test_user_registration(self):
        """Test user registration functionality"""
        # Test successful registration
        response = self.client.post('/journal_register', data={
            'username': 'testuser',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User registered successfully', response.data)
        self.assertIn(b'Digital Journal', response.data)  # Should redirect to journal
        
    def test_registration_validation(self):
        """Test registration form validation"""
        # Test short username
        response = self.client.post('/journal_register', data={
            'username': 'ab',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Username must be at least 3 characters long', response.data)
        
        # Test short password
        response = self.client.post('/journal_register', data={
            'username': 'testuser',
            'password': '12345',
            'confirm_password': '12345'
        }, follow_redirects=True)
        self.assertIn(b'Password must be at least 6 characters long', response.data)
        
        # Test password mismatch
        response = self.client.post('/journal_register', data={
            'username': 'testuser',
            'password': 'password123',
            'confirm_password': 'password456'
        }, follow_redirects=True)
        self.assertIn(b'Passwords do not match', response.data)
        
    def test_user_login(self):
        """Test user login functionality"""
        # First register a user
        register_user('testuser', 'password123')
        
        # Test successful login
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Testuser!', response.data)
        self.assertIn(b'Digital Journal', response.data)
        
    def test_login_case_insensitive(self):
        """Test that login is case-insensitive for usernames"""
        register_user('TestUser', 'password123')
        
        # Login with different case
        response = self.client.post('/journal_login', data={
            'username': 'testuser',  # lowercase
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Testuser!', response.data)
        
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        register_user('testuser', 'password123')
        
        # Wrong password
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertIn(b'Invalid username or password', response.data)
        
        # Non-existent user
        response = self.client.post('/journal_login', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertIn(b'Invalid username or password', response.data)
        
    def test_logout(self):
        """Test logout functionality"""
        # Login first
        register_user('testuser', 'password123')
        self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Logout
        response = self.client.post('/logout_journal', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out successfully', response.data)
        
        # Try to access journal after logout
        response = self.client.get('/journal', follow_redirects=True)
        self.assertIn(b'Please log in to access your journal', response.data)


class TestJournalCRUDFeatures(unittest.TestCase):
    """Test suite for journal CRUD features"""
    
    def setUp(self):
        """Set up test client and create test user"""
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
        
        # Register and login a test user
        register_user('testuser', 'password123')
        self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
    def tearDown(self):
        """Clean up temporary files"""
        import app as app_module
        app_module.JOURNAL_FILE = self.original_journal_file
        app_module.USERS_FILE = self.original_users_file
        os.unlink(self.temp_journal.name)
        os.unlink(self.temp_users.name)
        
    def test_add_journal_entry_with_tags(self):
        """Test adding a journal entry with tags"""
        response = self.client.post('/journal', data={
            'focus': 'Daily Reflection',
            'content': 'Test content with tags',
            'mood': 'good',
            'energy': 'Medium',
            'gratitude_1': 'Test gratitude',
            'action_item': 'Test action',
            'tags': 'work, personal, health'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Journal entry added successfully!', response.data)
        self.assertIn(b'work', response.data)
        self.assertIn(b'personal', response.data)
        self.assertIn(b'health', response.data)
        
    def test_edit_journal_entry(self):
        """Test editing a journal entry"""
        # First add an entry
        self.client.post('/journal', data={
            'focus': 'Daily Reflection',
            'content': 'Original content',
            'mood': 'good',
            'energy': 'Medium',
            'gratitude_1': 'Original gratitude',
            'action_item': 'Original action',
            'tags': 'original'
        })
        
        # Edit the entry
        response = self.client.post('/journal/edit/1', data={
            'focus': 'Weekly Goals',
            'content': 'Edited content',
            'mood': 'excellent',
            'energy': 'High',
            'gratitude_1': 'Edited gratitude',
            'action_item': 'Edited action',
            'tags': 'edited, updated'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Entry updated successfully!', response.data)
        self.assertIn(b'Edited content', response.data)
        self.assertIn(b'edited', response.data)
        self.assertIn(b'updated', response.data)
        
    def test_edit_nonexistent_entry(self):
        """Test editing a non-existent entry"""
        response = self.client.get('/journal/edit/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Entry not found', response.data)
        
    def test_delete_journal_entry(self):
        """Test deleting a journal entry"""
        # First add an entry
        self.client.post('/journal', data={
            'focus': 'Daily Reflection',
            'content': 'To be deleted',
            'mood': 'good',
            'energy': 'Medium'
        })
        
        # Delete the entry
        response = self.client.post('/journal/delete/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Entry deleted successfully!', response.data)
        self.assertNotIn(b'To be deleted', response.data)
        
    def test_delete_nonexistent_entry(self):
        """Test deleting a non-existent entry"""
        response = self.client.post('/journal/delete/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Entry not found', response.data)
        
    def test_user_isolation(self):
        """Test that users can only see/edit/delete their own entries"""
        # Add entry as testuser
        self.client.post('/journal', data={
            'focus': 'Daily Reflection',
            'content': 'TestUser entry',
            'mood': 'good',
            'energy': 'Medium'
        })
        
        # Logout and login as different user
        self.client.post('/logout_journal')
        register_user('otheruser', 'password456')
        self.client.post('/journal_login', data={
            'username': 'otheruser',
            'password': 'password456'
        })
        
        # Should not see testuser's entry
        response = self.client.get('/journal')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'TestUser entry', response.data)
        
        # Should not be able to edit testuser's entry
        response = self.client.get('/journal/edit/1', follow_redirects=True)
        self.assertIn(b'Entry not found', response.data)
        
        # Should not be able to delete testuser's entry
        response = self.client.post('/journal/delete/1', follow_redirects=True)
        self.assertIn(b'Entry not found', response.data)


class TestRememberMeFeature(unittest.TestCase):
    """Test suite for remember me functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Create temporary files
        self.temp_users = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_users.write('{}')
        self.temp_users.close()
        
        # Override file paths
        import app as app_module
        self.original_users_file = app_module.USERS_FILE
        app_module.USERS_FILE = self.temp_users.name
        
        # Register a test user
        register_user('testuser', 'password123')
        
    def tearDown(self):
        """Clean up"""
        import app as app_module
        app_module.USERS_FILE = self.original_users_file
        os.unlink(self.temp_users.name)
        
    def test_remember_me_token_generation(self):
        """Test remember me token generation and verification"""
        # Generate token
        token = generate_remember_token('testuser')
        self.assertIsNotNone(token)
        
        # Verify valid token
        username = verify_remember_token(token)
        self.assertEqual(username, 'testuser')
        
        # Test invalid token
        invalid_username = verify_remember_token('invalid-token')
        self.assertIsNone(invalid_username)
        
    def test_login_with_remember_me(self):
        """Test login with remember me checkbox"""
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123',
            'remember_me': '1'
        }, follow_redirects=False)
        
        # Check that remember_token cookie is set
        cookies = response.headers.getlist('Set-Cookie')
        remember_cookie_set = any('remember_token=' in cookie and 'Max-Age=2592000' in cookie 
                                  for cookie in cookies)
        self.assertTrue(remember_cookie_set)
        
    def test_login_without_remember_me(self):
        """Test login without remember me checkbox"""
        response = self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123'
            # remember_me not included
        }, follow_redirects=False)
        
        # Check that remember_token cookie is NOT set
        cookies = response.headers.getlist('Set-Cookie')
        remember_cookie_set = any('remember_token=' in cookie for cookie in cookies)
        self.assertFalse(remember_cookie_set)
        
    def test_logout_clears_remember_token(self):
        """Test that logout clears the remember token"""
        # Login with remember me
        self.client.post('/journal_login', data={
            'username': 'testuser',
            'password': 'password123',
            'remember_me': '1'
        })
        
        # Logout
        response = self.client.post('/logout_journal', follow_redirects=False)
        
        # Check that remember_token is cleared (expires=0)
        cookies = response.headers.getlist('Set-Cookie')
        remember_cleared = any('remember_token=' in cookie and 'expires' in cookie.lower() 
                               for cookie in cookies)
        self.assertTrue(remember_cleared)


if __name__ == '__main__':
    unittest.main() 