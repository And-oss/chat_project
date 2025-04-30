"""
Flask application for chat system with real-time messaging capabilities.
This module contains the application logic, including routes for user registration, 
login, chat functionality, and handling real-time messaging using SocketIO.
"""
import random
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from data.config import Config
from data.db import db
from data.models import User, Chat, Message as ChatMessage

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)
socketio = SocketIO(app, cors_allowed_origins="*")

verification_codes = {}

@app.errorhandler(400)
def bad_request(_):
    """Handle bad request errors."""
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(_):
    """Handle not found errors."""
    return jsonify({"error": "Not found"}), 404

def send_email(to_email, subject, body):
    """Send an email with the specified subject and body."""
    msg = Message(
        subject=subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to_email],
        body=body
    )
    mail.send(msg)

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration."""
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    verification_code = "".join(str(random.randint(0, 9)) for _ in range(6))
    verification_codes[email] = verification_code
    send_email(email, "Verification Code", f"Your code: {verification_code}")

    new_user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered. Check your email for the verification code."}), 201

@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Login successful!", "user_id": user.id}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/search_user_by_id/<int:user_id>', methods=['GET'])
def search_user_by_id(user_id):
    """Search for a user by their ID."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user.id, "username": user.username}), 200

@app.route('/search_users', methods=['GET'])
def search_users():
    """Search for users by username."""
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username parameter is required"}), 400

    users = User.query.filter(User.username.ilike(f'%{username}%')).all()

    users_data = [{"id": user.id, "username": user.username} for user in users]

    return jsonify(users_data), 200

@app.route('/get_chats/<int:user_id>', methods=['GET'])
def get_chats(user_id):
    """Get a list of chats for a specific user."""
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

@app.route('/get_messages/<int:chat_id>', methods=['GET'])
def get_messages(chat_id):
    """Get messages for a specific chat."""
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.timestamp).all()
    messages_data = [{
        "id": message.id,
        "sender_id": message.sender_id,
        "content": message.content,
        "timestamp": message.timestamp.isoformat()
    } for message in messages]

    return jsonify(messages_data), 200

@app.route('/get_user_profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get a user's profile."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email
    }), 200


@app.route('/create_personal_chat', methods=['POST', 'OPTIONS'])
def create_personal_chat():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    user1_id = data.get('user_id')
    user2_id = data.get('participant_id')

    if not user1_id or not user2_id:
        return jsonify({"error": "Both user_id and participant_id are required"}), 400

    # Check if both users exist
    user1 = User.query.get(user1_id)
    user2 = User.query.get(user2_id)
    
    if not user1 or not user2:
        return jsonify({"error": "One or both users not found"}), 404

    # Check if a personal chat already exists between these users
    existing_chat = Chat.query.filter(
        Chat.is_group == False,
        Chat.participants.any(id=user1_id),
        Chat.participants.any(id=user2_id)
    ).first()

    if existing_chat:
        response_data = {
            "message": "Chat already exists",
            "chat": {
                "id": existing_chat.id,
                "name": existing_chat.name,
                "is_group": existing_chat.is_group,
                "participants": [{"id": p.id, "username": p.username} for p in existing_chat.participants]
            }
        }
        print("Existing chat found, returning:", response_data)
        return jsonify(response_data), 200

    chat_name = f"{user1.username} {user2.username}"
    new_chat = Chat(name=chat_name, is_group=False)
    new_chat.participants.extend([user1, user2])
    
    db.session.add(new_chat)
    db.session.commit()

    response_data = {
        "message": "Personal chat created successfully",
        "chat": {
            "id": new_chat.id,
            "name": new_chat.name,
            "is_group": new_chat.is_group,
            "participants": [{"id": p.id, "username": p.username} for p in new_chat.participants]
        }
    }
    return jsonify(response_data), 201

@socketio.on('send_message')
def handle_send_message(json):
    """Handle sending a message in a chat."""
    chat_id = json.get('chat_id')
    user_id = json.get('user_id')
    text = json.get('text')

    if not chat_id or not user_id or not text:
        emit('error', {'message': 'Missing required fields'})
        return

    user = User.query.get(user_id)
    chat = Chat.query.get(chat_id)
    if not user or not chat:
        emit('error', {'message': 'Invalid user or chat'})
        return

    new_message = ChatMessage(content=text, sender_id=user_id, chat_id=chat_id)
    db.session.add(new_message)
    db.session.commit()

    join_room(str(chat_id))
    emit('receive_message', {
        'chat_id': chat_id,
        'sender_id': user_id,
        'text': text,
        'username': user.username,
        'timestamp': new_message.timestamp.isoformat()
    }, room=str(chat_id))

# Chat call handler section
@socketio.on('accept_call')
def handle_accept_call(data):
    """Handle accepting a call in a chat."""
    chat_id = data.get('chat_id')
    user_id = data.get('user_id')

    if not chat_id or not user_id:
        emit('error', {'message': 'Missing chat_id or user_id'})
        return

    join_room(str(chat_id))

    emit('call_accepted', {
        'chat_id': chat_id,
        'user_id': user_id
    }, room=str(chat_id))

@socketio.on('decline_call')
def handle_decline_call(data):
    """Handle declining a call in a chat."""
    chat_id = data.get('chat_id')
    user_id = data.get('user_id')

    if not chat_id or not user_id:
        emit('error', {'message': 'Missing chat_id or user_id'})
        return

    emit('call_declined', {
        'chat_id': chat_id,
        'user_id': user_id
    }, room=str(chat_id))

@socketio.on('end_call')
def handle_end_call(data):
    """Handle ending a call in a chat."""
    chat_id = data.get('chat_id')
    user_id = data.get('user_id')

    if not chat_id or not user_id:
        emit('error', {'message': 'Missing chat_id or user_id'})
        return

    emit('call_ended', {
        'chat_id': chat_id,
        'user_id': user_id
    }, room=str(chat_id))