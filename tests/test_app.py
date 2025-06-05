import unittest
import json
import os
import tempfile
from datetime import datetime
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, add_journal_entry, get_journal_entries

class TestGVisitApp(unittest.TestCase):
    """Test suite for GVisit Flask application"""
    
    def setUp(self):
        """Set up test client and temporary files"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()
        
        # Create a temporary file for journal entries
        self.temp_journal = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_journal.write('[]')
        self.temp_journal.close()
        
        # Override the journal file path
        import app as app_module
        self.original_journal_file = app_module.JOURNAL_FILE
        app_module.JOURNAL_FILE = self.temp_journal.name
        
    def tearDown(self):
        """Clean up temporary files"""
        import app as app_module
        app_module.JOURNAL_FILE = self.original_journal_file
        os.unlink(self.temp_journal.name)
        
    def test_home_page(self):
        """Test that home page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Your New Website!', response.data)
        self.assertIn(b'Presentations', response.data)
        self.assertIn(b'Quick Journal', response.data)
        
    def test_journal_page_loads(self):
        """Test that journal page loads successfully"""
        response = self.client.get('/journal')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Digital Journal', response.data)
        self.assertIn(b'New Entry', response.data)
        
    def test_login_page_ppt1(self):
        """Test that login page for presentation 1 loads"""
        response = self.client.get('/login/ppt1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password Required', response.data)
        self.assertIn(b'Presentation 1', response.data)
        
    def test_login_page_ppt2(self):
        """Test that login page for presentation 2 loads"""
        response = self.client.get('/login/ppt2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password Required', response.data)
        self.assertIn(b'Presentation 2', response.data)
        
    def test_invalid_presentation_id(self):
        """Test that invalid presentation ID redirects to home"""
        response = self.client.get('/login/invalid', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid presentation ID', response.data)
        
    def test_presentation_requires_password(self):
        """Test that presentations require password"""
        response = self.client.get('/powerpoint/ppt1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You need to enter the password', response.data)
        
    def test_correct_password_login(self):
        """Test login with correct password"""
        response = self.client.post('/login/ppt1', 
                                    data={'password': 'GVISIT'}, 
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Access Granted', response.data)
        self.assertIn(b'presentation1.pptx', response.data)
        
    def test_incorrect_password_login(self):
        """Test login with incorrect password"""
        response = self.client.post('/login/ppt1', 
                                    data={'password': 'wrong'}, 
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect password', response.data)
        
    def test_add_journal_entry(self):
        """Test adding a journal entry"""
        entry_data = {
            'focus': 'Daily Reflection',
            'content': 'Test journal entry content',
            'mood': 'good',
            'energy': 'Medium',
            'gratitude_1': 'Grateful for tests',
            'gratitude_2': 'Grateful for Flask',
            'gratitude_3': '',
            'action_item': 'Write more tests'
        }
        
        response = self.client.post('/journal', 
                                    data=entry_data, 
                                    follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Journal entry added successfully!', response.data)
        self.assertIn(b'Test journal entry content', response.data)
        
    def test_journal_entry_validation(self):
        """Test journal entry validation"""
        # Missing required fields
        entry_data = {
            'focus': 'Daily Reflection',
            'content': '',  # Empty content
            'mood': 'good',
            'energy': 'Medium'
        }
        
        response = self.client.post('/journal', 
                                    data=entry_data, 
                                    follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please fill in all required fields', response.data)
        
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('aws_backup', data)
        self.assertIn('dynamodb', data)
        
    def test_secure_download_without_auth(self):
        """Test that download requires authentication"""
        response = self.client.get('/download_ppt/ppt1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You need to enter the password', response.data)
        
    def test_static_css_loads(self):
        """Test that static CSS file loads"""
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Custom styles to supplement Bootstrap', response.data)


class TestJournalFunctions(unittest.TestCase):
    """Test journal-specific functions"""
    
    def setUp(self):
        """Set up temporary journal file"""
        self.temp_journal = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_journal.write('[]')
        self.temp_journal.close()
        
        import app as app_module
        self.original_journal_file = app_module.JOURNAL_FILE
        app_module.JOURNAL_FILE = self.temp_journal.name
        
    def tearDown(self):
        """Clean up"""
        import app as app_module
        app_module.JOURNAL_FILE = self.original_journal_file
        os.unlink(self.temp_journal.name)
        
    def test_get_empty_journal_entries(self):
        """Test getting entries from empty journal"""
        entries = get_journal_entries()
        self.assertEqual(entries, [])
        
    def test_add_and_get_journal_entry(self):
        """Test adding and retrieving journal entries"""
        entry_data = {
            'focus': 'Test Focus',
            'content': 'Test Content',
            'mood': 'excellent',
            'energy': 'High',
            'gratitude': ['Test 1', 'Test 2'],
            'action_item': 'Test Action'
        }
        
        add_journal_entry(entry_data)
        entries = get_journal_entries()
        
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['focus'], 'Test Focus')
        self.assertEqual(entries[0]['content'], 'Test Content')
        self.assertEqual(entries[0]['mood'], 'excellent')
        self.assertEqual(entries[0]['energy'], 'High')
        self.assertEqual(len(entries[0]['gratitude']), 2)
        

if __name__ == '__main__':
    unittest.main() 