from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("connect")
def handlConnection():
    print("socket connected")

@socketio.on('draw')
def handle_draw(data):
    emit('draw', data, broadcast=True)

@socketio.on('stopDrawing')
def handle_stop_drawing():
    socketio.emit('stopDrawing')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=60000)
