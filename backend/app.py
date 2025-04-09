from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import random
from data.config import Config
from data.db import db
from data.models import User, Chat, Message as ChatMessage
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)


def send_email(to_email, subject, body):
    msg = Message(
        subject=subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to_email],
        body=body
    )
    mail.send(msg)

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

    verification_code = "".join(str(random.randint(0, 9)) for _ in range(6))
    verification_codes[email] = verification_code
    send_email(email, "Verification Code", f"Your code: {verification_code}")

    new_user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered. Check your email for the verification code."}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Login successful!", "user_id": user.id}), 200
    return jsonify({"error": "Invalid credentials"}), 401

