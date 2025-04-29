from app import app, socketio, db

"""
This module runs the application, initializes the database, and starts the server with SocketIO support.
"""

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)