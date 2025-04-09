import unittest
from app import app, socketio, db, User, Chat, ChatMessage  # Import your app and models

class ChatAppTests(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['MAIL_SUPPRESS_SEND'] = True
        with app.app_context():
            db.create_all()

        self.client = app.test_client()
        self.socket_client = socketio.test_client(app, flask_test_client=self.client)

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

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
        # First register a user
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })

        # Now try to login
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

    def test_create_chat(self):
        # Register and login user
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        user_data = response.get_json()

        # Create a chat
        response = self.client.post('/create_chat', json={
            'name': 'Test Chat',
            'is_group': False,
            'participants': [user_data['user_id']]
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Chat created successfully')

    def test_create_chat_invalid_participants(self):
        # Register and login user
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        user_data = response.get_json()


        response = self.client.post('/create_chat', json={
            'name': 'Invalid Chat',
            'is_group': False,
            'participants': [9999]  # Non-existent user ID
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid participants')

    def test_get_chat_users(self):
        # Register and login user
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        user_data = response.get_json()

        # Create a chat
        self.client.post('/create_chat', json={
            'name': 'Test Chat',
            'is_group': False,
            'participants': [user_data['user_id']]
        })

        # Get the chat users
        chat_id = 1  # Assuming chat ID is 1
        response = self.client.get(f'/get_chat_users/{chat_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]['username'], 'testuser')

    def test_send_message(self):
        self.client.post('/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        user_data = response.get_json()

        # Создаём чат
        self.client.post('/create_chat', json={
            'name': 'Test Chat',
            'is_group': False,
            'participants': [user_data['user_id']]
        })


        chat_id = 1
        message_data = {
            'chat_id': chat_id,
            'user_id': user_data['user_id'],
            'text': 'Hello, world!'
        }

        self.socket_client.emit('send_message', message_data)

        received = self.socket_client.get_received()

        self.assertGreater(len(received), 0)
        message = received[0]['args'][0]
        self.assertEqual(message['text'], 'Hello, world!')
        self.assertEqual(message['username'], 'testuser')

    def test_send_message_invalid_user(self):
        chat_id = 1
        message_data = {
            'chat_id': chat_id,
            'user_id': 999,
            'text': 'Hello, world!'
        }

        self.socket_client.emit('send_message', message_data)

        received = self.socket_client.get_received()

        self.assertGreater(len(received), 0)
        error_message = received[0]['args'][0]
        self.assertEqual(error_message['message'], 'Invalid user or chat')

if __name__ == '__main__':
    unittest.main()