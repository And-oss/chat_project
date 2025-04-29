"""
Database models for users, chats, and messages.
"""

from .db import db

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
    
    def __repr__(self):
        """Return string representation of User."""
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary representation."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class Chat(db.Model):
    """Model representing a chat (private or group)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_group = db.Column(db.Boolean, default=False)
    participants = db.relationship('User', secondary=chat_participants, backref='chats')
    
    def __repr__(self):
        """Return string representation of Chat."""
        return f'<Chat {self.name}>'
    
    def to_dict(self):
        """Convert chat to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'is_group': self.is_group
        }

class Message(db.Model):
    """Model representing a message sent in a chat"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        """Return string representation of Message."""
        return f'<Message {self.id}>'
    
    def to_dict(self):
        """Convert message to dictionary representation."""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'chat_id': self.chat_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }