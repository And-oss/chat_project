"""
Application runner module.
This module runs the application, initializes the database, and starts the server with SocketIO support.
"""

from app import app, socketio, db

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)