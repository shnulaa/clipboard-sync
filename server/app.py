from flask import Flask, render_template, request
import socketio
import eventlet
import sqlite3
import os

# 设置 async_mode
async_mode = 'eventlet'

app = Flask(__name__)
sio = socketio.Server(cors_allowed_origins='*', async_mode=async_mode)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# 初始化数据库
def init_db():
    os.makedirs('server/db', exist_ok=True)
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tv_clients
                 (id TEXT PRIMARY KEY, name TEXT, sid TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS send_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tv_id TEXT, tv_name TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/static/socket.io/socket.io.js')
def serve_socketio_js():
    return app.send_static_file('socket.io.js')

tv_clients = {}

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    c.execute("SELECT tv_id, tv_name, content, timestamp FROM send_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?", (per_page, offset))
    logs = c.fetchall()
    c.execute("SELECT COUNT(*) FROM send_logs")
    total_logs = c.fetchone()[0]
    conn.close()
    total_pages = (total_logs + per_page - 1) // per_page
    return render_template('index.html', tv_clients=tv_clients, logs=logs, page=page, total_pages=total_pages)

@app.route('/get_logs', methods=['GET'])
def get_logs():
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    c.execute("SELECT tv_id, tv_name, content, timestamp FROM send_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?", (per_page, offset))
    logs = c.fetchall()
    c.execute("SELECT COUNT(*) FROM send_logs")
    total_logs = c.fetchone()[0]
    conn.close()
    total_pages = (total_logs + per_page - 1) // per_page
    return {"logs": logs, "page": page, "total_pages": total_pages}

@app.route('/send_clipboard', methods=['POST'])
def send_clipboard():
    content = request.form['content']
    tv_id = request.form['tv_id']
    if tv_id in tv_clients:
        tv_name = tv_clients[tv_id]['name']
        conn = sqlite3.connect('server/db/clipboard_sync.db')
        c = conn.cursor()
        c.execute("INSERT INTO send_logs (tv_id, tv_name, content) VALUES (?, ?, ?)", (tv_id, tv_name, content))
        conn.commit()
        c.execute("SELECT tv_id, tv_name, content, timestamp FROM send_logs ORDER BY timestamp DESC LIMIT 10")
        logs = c.fetchall()
        c.execute("SELECT COUNT(*) FROM send_logs")
        total_logs = c.fetchone()[0]
        conn.close()
        total_pages = (total_logs + 10 - 1) // 10
        sio.emit('clipboard_data', {'content': content}, to=tv_clients[tv_id]['sid'])
        sio.emit('update_logs', {"logs": logs, "page": 1, "total_pages": total_pages})
        return {"status": "success", "message": "成功发送消息"}, 200
    return {"status": "error", "message": "未找到指定设备"}, 404

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    c.execute("DELETE FROM send_logs")
    conn.commit()
    conn.close()
    sio.emit('update_logs', [])
    return {"status": "success", "message": "日志已清空"}, 200

@sio.on('connect')
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.on('register_tv')
def register_tv(sid, data):
    tv_id = data['id']
    tv_name = data['name']
    tv_clients[tv_id] = {'name': tv_name, 'sid': sid}
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO tv_clients (id, name, sid, status) VALUES (?, ?, ?, ?)", (tv_id, tv_name, sid, 'online'))
    conn.commit()
    conn.close()
    print(f"Registered TV: {tv_id} ({tv_name})")
    sio.emit('device_update', {'action': 'add', 'tv_id': tv_id, 'tv_name': tv_name, 'name': tv_name})

@sio.on('disconnect')
def disconnect(sid):
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    for tv_id, client_info in list(tv_clients.items()):
         if client_info['sid'] == sid:
            del tv_clients[tv_id]
            c.execute("UPDATE tv_clients SET status=? WHERE id=?", ('offline', tv_id))
            conn.commit()
            print(f"Client disconnected: {sid} tv_id={tv_id}")
            sio.emit('device_update', {'action': 'remove', 'tv_id': tv_id, 'tv_name': client_info['name'], 'name': client_info['name']})
            break
    conn.close()

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)