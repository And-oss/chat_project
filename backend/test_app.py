import unittest
import json
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Create a test app
app = Flask(__name__)

# Check if we're running in CI/CD environment
is_ci = os.environ.get('CI', False)

# Set up database URI based on environment
if is_ci:
    # In CI environment, use the environment variables for database configuration
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
else:
    # In local environment, use in-memory SQLite for simplicity and isolation
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

# Common configurations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['MAIL_SUPPRESS_SEND'] = True  # Don't actually send emails during testing

# Initialize database
db = SQLAlchemy(app)

# Define models for testing that match your real models
chat_participants = db.Table(
    'chat_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True)
)

class User(db.Model):
    """Model representing a user"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(2048), nullable=False)

class Chat(db.Model):
    """Model representing a chat (private or group)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_group = db.Column(db.Boolean, default=False)
    participants = db.relationship('User', secondary=chat_participants, backref='chats')

class Message(db.Model):
    """Model representing a message sent in a chat"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create mock implementations of app routes for testing
socketio = SocketIO(app)

# Mock verification codes for testing
verification_codes = {}

# Register route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
        
    # Mock verification code
    verification_codes[email] = "123456"
    
    new_user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered. Check your email for the verification code."}), 201

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Login successful!", "user_id": user.id}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# Search user route
@app.route('/search_user_by_id/<int:user_id>', methods=['GET'])
def search_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user.id, "username": user.username}), 200

# Search users route
@app.route('/search_users', methods=['GET'])
def search_users():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username parameter is required"}), 400

    users = User.query.filter(User.username.ilike(f'%{username}%')).all()
    users_data = [{"id": user.id, "username": user.username} for user in users]

    return jsonify(users_data), 200

# Get chats route
@app.route('/get_chats/<int:user_id>', methods=['GET'])
def get_chats(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    chats = Chat.query.filter(Chat.participants.any(id=user_id)).all()
    chats_data = [{
        "id": chat.id,
        "name": chat.name,
        "is_group": chat.is_group,
        "participants": [{"id": participant.id, "username": participant.username} for participant in chat.participants]
    } for chat in chats]

    return jsonify(chats_data), 200

# Get messages route
@app.route('/get_messages/<int:chat_id>', methods=['GET'])
def get_messages(chat_id):
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    messages_data = [{
        "id": message.id,
        "sender_id": message.sender_id,
        "content": message.content,
        "timestamp": message.timestamp.isoformat() if message.timestamp else None
    } for message in messages]

    return jsonify(messages_data), 200

# Get user profile route
@app.route('/get_user_profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email
    }), 200

# Error handler
@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found"}), 404

# Socket.IO event handlers
@socketio.on('send_message')
def handle_send_message(json_data):
    pass  # Mock implementation for testing

@socketio.on('accept_call')
def handle_accept_call(data):
    pass  # Mock implementation for testing

@socketio.on('decline_call')
def handle_decline_call(data):
    pass  # Mock implementation for testing

@socketio.on('end_call')
def handle_end_call(data):
    pass  # Mock implementation for testing

# Setup test class
class ChatAppTests(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = app
        self.client = app.test_client()
        
        # Create a new database for each test
        try:
            with app.app_context():
                db.create_all()
                
                # Create test users for multiple tests
                test_user1 = User(
                    username='testuser1', 
                    email='test1@example.com',
                    password=generate_password_hash('password123')
                )
                test_user2 = User(
                    username='testuser2', 
                    email='test2@example.com',
                    password=generate_password_hash('password123')
                )
                test_user3 = User(
                    username='otheruser', 
                    email='other@example.com',
                    password=generate_password_hash('password123')
                )
                
                db.session.add_all([test_user1, test_user2, test_user3])
                db.session.commit()
                
                # Create test chats
                private_chat = Chat(name='Private Chat', is_group=False)
                private_chat.participants.append(test_user1)
                private_chat.participants.append(test_user2)
                
                group_chat = Chat(name='Group Chat', is_group=True)
                group_chat.participants.append(test_user1)
                group_chat.participants.append(test_user2)
                group_chat.participants.append(test_user3)
                
                db.session.add_all([private_chat, group_chat])
                db.session.commit()
                
                # Add some test messages
                message1 = Message(
                    sender_id=test_user1.id,
                    chat_id=private_chat.id,
                    content='Hello from user1'
                )
                message2 = Message(
                    sender_id=test_user2.id,
                    chat_id=private_chat.id,
                    content='Hello back from user2'
                )
                message3 = Message(
                    sender_id=test_user1.id,
                    chat_id=group_chat.id,
                    content='Hello everyone'
                )
                
                db.session.add_all([message1, message2, message3])
                db.session.commit()
        except Exception as e:
            print(f"Error setting up test database: {e}")
            # We still want to fail the test, not silently catch errors
            raise

    def tearDown(self):
        """Clean up after each test"""
        try:
            with app.app_context():
                db.session.remove()
                db.drop_all()
        except Exception as e:
            print(f"Error tearing down test database: {e}")

    def test_register(self):
        """Test user registration functionality"""
        response = self.client.post('/register', json={
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password123'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', data)
        self.assertIn('verification code', data['message'].lower())
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'newuser@example.com')

    def test_register_missing_fields(self):
        """Test registration with missing fields"""
        response = self.client.post('/register', json={
            'email': 'incomplete@example.com',
            'username': ''  # Missing username
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing required fields')

    def test_register_duplicate_email(self):
        """Test registration with an already registered email"""
        response = self.client.post('/register', json={
            'email': 'test1@example.com',  # Already exists
            'username': 'newuser',
            'password': 'password123'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Email already registered')

    def test_login(self):
        """Test user login with valid credentials"""
        response = self.client.post('/login', json={
            'username': 'testuser1',
            'password': 'password123'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertIn('user_id', data)
        self.assertEqual(data['message'], 'Login successful!')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/login', json={
            'username': 'testuser1',
            'password': 'wrongpassword'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid credentials')

    def test_search_user_by_id(self):
        """Test searching for a user by ID"""
        with app.app_context():
            user = User.query.filter_by(username='testuser1').first()
            user_id = user.id
        
        response = self.client.get(f'/search_user_by_id/{user_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], 'testuser1')
        self.assertEqual(data['id'], user_id)

    def test_search_user_by_id_not_found(self):
        """Test searching for a non-existent user ID"""
        response = self.client.get('/search_user_by_id/9999')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    def test_search_users(self):
        """Test searching for users by username substring"""
        response = self.client.get('/search_users?username=test')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)  # Should find testuser1 and testuser2
        usernames = [user['username'] for user in data]
        self.assertIn('testuser1', usernames)
        self.assertIn('testuser2', usernames)

    def test_search_users_no_matches(self):
        """Test searching for users with no matches"""
        response = self.client.get('/search_users?username=nonexistentuser')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)  # Should be empty list

    def test_search_users_missing_parameter(self):
        """Test searching for users without providing the username parameter"""
        response = self.client.get('/search_users')
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Username parameter is required')

    def test_get_chats(self):
        """Test retrieving a user's chats"""
        with app.app_context():
            user = User.query.filter_by(username='testuser1').first()
            user_id = user.id
        
        response = self.client.get(f'/get_chats/{user_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)  # User should be in two chats
        
        # Check that both private and group chats are returned
        chat_names = [chat['name'] for chat in data]
        self.assertIn('Private Chat', chat_names)
        self.assertIn('Group Chat', chat_names)
        
        # Verify the group chat has the correct is_group flag
        for chat in data:
            if chat['name'] == 'Group Chat':
                self.assertTrue(chat['is_group'])
            if chat['name'] == 'Private Chat':
                self.assertFalse(chat['is_group'])

    def test_get_chats_user_not_found(self):
        """Test retrieving chats for a non-existent user"""
        response = self.client.get('/get_chats/9999')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    def test_get_messages(self):
        """Test retrieving messages for a chat"""
        with app.app_context():
            chat = Chat.query.filter_by(name='Private Chat').first()
            chat_id = chat.id
        
        response = self.client.get(f'/get_messages/{chat_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)  # Private chat should have 2 messages
        
        # Check message contents
        messages = [msg['content'] for msg in data]
        self.assertIn('Hello from user1', messages)
        self.assertIn('Hello back from user2', messages)

    def test_get_messages_chat_not_found(self):
        """Test retrieving messages for a non-existent chat"""
        response = self.client.get('/get_messages/9999')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Chat not found')

    def test_get_user_profile(self):
        """Test retrieving a user's profile"""
        with app.app_context():
            user = User.query.filter_by(username='testuser1').first()
            user_id = user.id
        
        response = self.client.get(f'/get_user_profile/{user_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], 'testuser1')
        self.assertEqual(data['email'], 'test1@example.com')

    def test_get_user_profile_not_found(self):
        """Test retrieving a profile for a non-existent user"""
        response = self.client.get('/get_user_profile/9999')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    def test_error_handler_not_found(self):
        """Test 404 error handler"""
        response = self.client.get('/nonexistent_route')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'Not found')

    def test_socketio_structure(self):
        """
        Test that the SocketIO structure is correctly defined.
        This is a simple verification that the app has SocketIO events defined.
        """
        # Test that SocketIO is correctly initialized
        self.assertTrue(hasattr(socketio, 'on_event'))
        
        # Check that our socket event functions are defined
        self.assertTrue(callable(handle_send_message))
        self.assertTrue(callable(handle_accept_call))
        self.assertTrue(callable(handle_decline_call))
        self.assertTrue(callable(handle_end_call))

if __name__ == '__main__':
    unittest.main()