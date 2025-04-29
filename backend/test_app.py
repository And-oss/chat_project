import unittest
import os
import sys

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import app, socketio, db
from data.models import User, Chat, Message as ChatMessage

class ChatAppTests(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        app.config['MAIL_SUPPRESS_SEND'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()

        self.client = app.test_client()
        self.socket_client = socketio.test_client(app, flask_test_client=self.client)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
        self.app_context.pop()

    def test_register(self):
        response = self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User registered. Check your email for the verification code.')

    def test_register_missing_fields(self):
        response = self.client.post('/register', json={
            'email': 'test@example.com',
            'username': ''
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing required fields')

    def test_login(self):
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })

        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Login successful!')

    def test_login_invalid_credentials(self):
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid credentials')

    def test_get_user_profile(self):

        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        

        login_response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        user_data = login_response.get_json()
        user_id = user_data['user_id']
        

        response = self.client.get(f'/get_user_profile/{user_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')

    def test_search_user_by_id(self):
        # Register a user
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Login to get user_id
        login_response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        user_data = login_response.get_json()
        user_id = user_data['user_id']
        
        # Search for user by ID
        response = self.client.get(f'/search_user_by_id/{user_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], user_id)
        self.assertEqual(data['username'], 'testuser')

    def test_search_users(self):
        # Register a user
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Search for users by username
        response = self.client.get('/search_users?username=test')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'testuser')

    def test_get_chats_empty(self):
        # Register a user
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Login to get user_id
        login_response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        user_data = login_response.get_json()
        user_id = user_data['user_id']
        
        # Get chats for user (should be empty)
        response = self.client.get(f'/get_chats/{user_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)

    def test_socket_connection(self):
        # Test that socket connection works
        self.assertTrue(self.socket_client.is_connected())
        
    def test_error_handler(self):
        # Test 404 error handler
        response = self.client.get('/nonexistent_route')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'Not found')

if __name__ == '__main__':
    unittest.main()