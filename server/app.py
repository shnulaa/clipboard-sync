# 导入所需的库
from flask import Flask, render_template, request
import socketio
import eventlet
import sqlite3
import os

# 设置 WebSocket 的异步模式为 eventlet
async_mode = 'eventlet'

# 初始化 Flask 应用和 SocketIO 服务器
app = Flask(__name__)
# 创建 SocketIO 服务器实例，允许跨域访问
sio = socketio.Server(cors_allowed_origins='*', async_mode=async_mode)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# 初始化数据库函数
def init_db():
    """
    初始化数据库，创建必要的表：
    - tv_clients: 存储电视客户端信息
    - send_logs: 存储剪贴板发送记录
    """
    # 确保数据库目录存在
    os.makedirs('server/db', exist_ok=True)
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    
    # 创建电视客户端表
    c.execute('''CREATE TABLE IF NOT EXISTS tv_clients
                 (id TEXT PRIMARY KEY, name TEXT, sid TEXT, status TEXT)''')
    
    # 创建发送日志表
    c.execute('''CREATE TABLE IF NOT EXISTS send_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tv_id TEXT, tv_name TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# 启动时初始化数据库
init_db()

# 提供 socket.io 客户端库的静态文件
@app.route('/static/socket.io/socket.io.js')
def serve_socketio_js():
    """提供Socket.IO客户端JavaScript库"""
    return app.send_static_file('socket.io.js')

# 存储在线电视客户端信息的字典
tv_clients = {}

# 主页路由，显示客户端列表和发送日志
@app.route('/')
def index():
    """
    处理主页请求，支持分页显示日志
    - page: 当前页码（默认1）
    - per_page: 每页显示的日志数量
    """
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    # 查询分页日志数据
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    c.execute("SELECT tv_id, tv_name, content, timestamp FROM send_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?", (per_page, offset))
    logs = c.fetchall()
    
    # 获取总日志数用于分页计算
    c.execute("SELECT COUNT(*) FROM send_logs")
    total_logs = c.fetchone()[0]
    conn.close()
    
    total_pages = (total_logs + per_page - 1) // per_page
    return render_template('index.html', tv_clients=tv_clients, logs=logs, page=page, total_pages=total_pages)

# 获取日志的 API 接口
@app.route('/get_logs', methods=['GET'])
def get_logs():
    """
    获取分页的日志数据
    - 返回JSON格式的日志数据和分页信息
    """
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

# 发送剪贴板内容的 API 接口
@app.route('/send_clipboard', methods=['POST'])
def send_clipboard():
    """
    接收并转发剪贴板内容到指定的电视客户端
    - 验证目标设备是否存在
    - 记录发送日志
    - 通知目标设备接收剪贴板内容
    - 广播日志更新消息给所有客户端
    """
    content = request.form['content']
    tv_id = request.form['tv_id']
    
    if tv_id in tv_clients:
        tv_name = tv_clients[tv_id]['name']
        
        # 记录发送日志
        conn = sqlite3.connect('server/db/clipboard_sync.db')
        c = conn.cursor()
        c.execute("INSERT INTO send_logs (tv_id, tv_name, content) VALUES (?, ?, ?)", (tv_id, tv_name, content))
        conn.commit()
        
        # 获取最新日志数据
        c.execute("SELECT tv_id, tv_name, content, timestamp FROM send_logs ORDER BY timestamp DESC LIMIT 10")
        logs = c.fetchall()
        
        c.execute("SELECT COUNT(*) FROM send_logs")
        total_logs = c.fetchone()[0]
        conn.close()
        
        total_pages = (total_logs + 10 - 1) // 10
        
        # 通知目标设备接收剪贴板内容
        sio.emit('clipboard_data', {'content': content}, to=tv_clients[tv_id]['sid'])
        
        # 广播日志更新消息
        sio.emit('update_logs', {"logs": logs, "page": 1, "total_pages": total_pages})
        
        return {"status": "success", "message": "成功发送消息"}, 200
    
    return {"status": "error", "message": "未找到指定设备"}, 404

# 清空日志的 API 接口
@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    """
    清空所有发送日志记录
    - 删除数据库中的所有日志记录
    - 通知所有客户端日志已清空
    """
    conn = sqlite3.connect('server/db/clipboard_sync.db')
    c = conn.cursor()
    c.execute("DELETE FROM send_logs")
    conn.commit()
    conn.close()
    
    # 通知所有客户端日志已清空
    sio.emit('update_logs', [])
    return {"status": "success", "message": "日志已清空"}, 200

# Socket.IO 事件：客户端连接
@sio.on('connect')
def connect(sid, environ):
    """
    处理新的 WebSocket 连接
    - 打印连接信息
    """
    print(f"Client connected: {sid}")

# Socket.IO 事件：注册电视客户端
@sio.on('register_tv')
def register_tv(sid, data):
    """
    处理电视客户端的注册请求
    - 保存客户端信息到内存和数据库
    - 广播设备更新消息
    """
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

# Socket.IO 事件：客户端断开连接
@sio.on('disconnect')
def disconnect(sid):
    """
    处理客户端断开连接
    - 更新客户端状态为离线
    - 从内存中移除客户端信息
    - 通知其他客户端设备已断开
    """
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

# 主程序入口
if __name__ == '__main__':
    """
    启动应用程序
    - 使用eventlet WSGI服务器监听所有网络接口的5000端口
    """
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)