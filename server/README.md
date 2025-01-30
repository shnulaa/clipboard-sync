# 剪贴板同步项目

## 项目概述
基于Python Flask框架和Socket.IO实现的跨设备剪贴板同步解决方案，支持将PC端的剪贴板内容实时推送到智能电视等设备。采用客户端-服务器架构，包含以下核心组件：

### 技术栈
- **后端框架**: Flask 2.0 + Flask-SocketIO 5.3
- **前端库**: 
  - Bootstrap 5.1.3
  - FontAwesome 6.0.0
  - Socket.IO Client 4.7.4
- **通信协议**: WebSocket (通过Socket.IO实现)

## 功能特性
### 后端功能
1. 设备注册管理
   - 自动识别新设备连接
   - 设备UUID生成与验证
   - 心跳检测机制

2. 剪贴板同步
   - 支持文本/HTML内容传输
   - 内容加密传输（AES-256）
   - 多设备广播支持

3. API接口
   - `/send_clipboard` POST接口
   - `/devices` 设备列表查询接口
   - `/health` 服务健康检查

### 前端功能
1. 设备管理界面
   - 实时设备状态显示
   - 设备连接/断开通知
   - 剪贴板历史记录查看

2. 交互功能
   - 一键复制/粘贴
   - 剪贴板内容格式自动识别
   - 多语言支持（中/英）

## 项目结构
```
.
├── app.py                 # 主应用入口
├── requirements.txt       # 依赖清单
├── static/                # 静态资源
│   ├── lib/               # 第三方库
│   └── css/               # 自定义样式
└── templates/             # 前端模板
    └── index.html         # 主界面模板
```

## 环境准备
### 系统要求
- Python 3.8+
- pip 20.3+
- 现代浏览器（Chrome 90+/Firefox 88+）

## 安装与运行
### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置设置
创建 `.env` 文件配置环境变量：
```ini
# 服务端口设置
SERVER_PORT=5000
SOCKETIO_PORT=5001

# 安全配置
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_aes256_key
```

### 3. 启动服务
```bash
# 开发模式（热重载）
python app.py --debug

# 生产模式
python app.py --prod
```

### 4. 访问应用
浏览器打开：http://localhost:5000

## 高级配置
### Docker部署
```bash
docker build -t clipboard-sync .
docker run -p 5000:5000 -p 5001:5001 clipboard-sync
```

### 调试模式
```bash
# 启用调试控制台
python app.py --debug --console
```

## 注意事项
1. 首次运行时会自动生成设备认证证书（保存在certs/目录）
2. 生产环境建议配置Nginx反向代理
3. 跨设备访问需确保网络策略开放相关端口