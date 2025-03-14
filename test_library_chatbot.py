import unittest
from server import app  
from faq_search_rag import query_faq_pinecone

class TestLibraryChatbot(unittest.TestCase):
    
    def setUp(self):
        """Set up the test client and any necessary test data."""
        self.client = app.test_client()
        self.client.testing = True

    def test_new_session_creation(self):
        """Test if a new session is created successfully."""
        response = self.client.post('/new_session', json={"session_name": "test_session"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Session 'test_session' created successfully.", response.get_data(as_text=True))

    def test_existing_session(self):
        """Test that an existing session returns the correct response."""
        self.client.post('/new_session', json={"session_name": "existing_session"})
        response = self.client.get('/sessions')
        self.assertEqual(response.status_code, 200)
        self.assertIn("existing_session", response.get_data(as_text=True))

    def test_sentiment_analysis_positive(self):
        """Test sentiment analysis for a positive message."""
        sentiment = "I love this library!"
        response = self.client.post('/chat', json={
            "session_name": "test_session", 
            "message": sentiment
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("positive", response.json.get('response').lower())

    def test_sentiment_analysis_negative(self):
        """Test sentiment analysis for a negative message."""
        sentiment = "I am really frustrated with the service."
        response = self.client.post('/chat', json={
            "session_name": "test_session", 
            "message": sentiment
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("escalate", response.json.get('response').lower())

    def test_faq_query(self):
        """Test FAQ query handling through Pinecone."""
        query = "What are the library hours?"
        response = query_faq_pinecone(query)
        self.assertIn("hours", response.lower())

    def test_invalid_session(self):
        """Test if the system handles invalid session gracefully."""
        response = self.client.post('/chat', json={
            "session_name": "non_existing_session", 
            "message": "Hello"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid session", response.json.get('error'))

    def test_appointment_handling(self):
        """Test appointment handling with mock data."""
        appointment_request = "I'd like to book an appointment for 2 PM tomorrow to discuss my membership."
        response = self.client.post('/chat', json={
            "session_name": "test_session", 
            "message": appointment_request
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("appointment has been confirmed", response.json.get('response').lower())

    def test_app_error_handling(self):
        """Test if app handles errors gracefully."""
        response = self.client.post('/chat', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json.get('error'))

    def tearDown(self):
        """Clean up after each test if necessary."""
        pass

if __name__ == "__main__":
    unittest.main()
