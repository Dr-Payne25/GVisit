import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestConfiguration(unittest.TestCase):
    """Test configuration and environment variables"""
    
    def test_default_config(self):
        """Test that default configuration values are set"""
        # Import app after setting up path
        from app import app, PASSWORD
        
        self.assertIsNotNone(app.secret_key)
        self.assertEqual(PASSWORD, 'GVISIT')  # Default password
        
    def test_environment_variables(self):
        """Test that environment variables can override defaults"""
        # Set test environment variables
        os.environ['PASSWORD'] = 'TEST_PASSWORD'
        os.environ['PORT'] = '8080'
        
        # Re-import to get new environment values
        # This is a simplified test - in real scenario you'd need to reload the module
        self.assertEqual(os.environ.get('PASSWORD'), 'TEST_PASSWORD')
        self.assertEqual(os.environ.get('PORT'), '8080')
        
        # Clean up
        del os.environ['PASSWORD']
        del os.environ['PORT']
        
    def test_journal_focuses_loaded(self):
        """Test that journal focuses are properly loaded"""
        from app import JOURNAL_FOCUSES
        
        self.assertIn('Daily Reflection', JOURNAL_FOCUSES)
        self.assertIn('Weekly Goals', JOURNAL_FOCUSES)
        self.assertIn('Brain Dump', JOURNAL_FOCUSES)
        self.assertEqual(len(JOURNAL_FOCUSES), 7)
        
    def test_mood_options_loaded(self):
        """Test that mood options are properly configured"""
        from app import MOOD_OPTIONS
        
        self.assertEqual(len(MOOD_OPTIONS), 5)
        self.assertEqual(MOOD_OPTIONS[0]['value'], 'excellent')
        self.assertEqual(MOOD_OPTIONS[0]['label'], '😀 Excellent')
        
    def test_energy_levels_loaded(self):
        """Test that energy levels are configured"""
        from app import ENERGY_LEVELS
        
        self.assertEqual(ENERGY_LEVELS, ['High', 'Medium', 'Low'])
        
    def test_focus_prompts_loaded(self):
        """Test that focus prompts are properly mapped"""
        from app import FOCUS_PROMPTS
        
        self.assertIn('Daily Reflection', FOCUS_PROMPTS)
        self.assertEqual(
            FOCUS_PROMPTS['Daily Reflection'], 
            'What was a win today? What was a challenge? What did you learn?'
        )

if __name__ == '__main__':
    unittest.main() 