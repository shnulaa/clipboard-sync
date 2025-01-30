from flask import Flask, render_template, request
import socketio
import eventlet

app = Flask(__name__)
sio = socketio.Server(cors_allowed_origins='*')
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

@app.route('/static/socket.io/socket.io.js')
def serve_socketio_js():
    return app.send_static_file('socket.io.js')

tv_clients = {}

@app.route('/')
def index():
    return render_template('index.html', tv_clients=tv_clients)

@app.route('/send_clipboard', methods=['POST'])
def send_clipboard():
    content = request.form['content']
    tv_id = request.form['tv_id']
    if tv_id in tv_clients:
      sio.emit('clipboard_data', {'content': content}, to=tv_clients[tv_id]['sid'])
      return {"status": "success", "message": "成功发送消息"}, 200
    return {"status": "error", "message": "未找到指定设备"}, 404

@sio.on('connect')
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.on('register_tv')
def register_tv(sid, data):
    tv_id = data['id']
    tv_name = data['name']
    tv_clients[tv_id] = {'name': tv_name, 'sid': sid}
    print(f"Registered TV: {tv_id} ({tv_name})")
    sio.emit('device_update', {'action': 'add', 'tv_id': tv_id, 'tv_name': tv_name, 'name': tv_name})

@sio.on('disconnect')
def disconnect(sid):
    for tv_id, client_info in list(tv_clients.items()):
         if client_info['sid'] == sid:
            del tv_clients[tv_id]
            print(f"Client disconnected: {sid} tv_id={tv_id}")
            sio.emit('device_update', {'action': 'remove', 'tv_id': tv_id, 'tv_name': client_info['name'], 'name': client_info['name']})
            break


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)