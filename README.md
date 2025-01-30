# 跨平台剪贴板同步

在不同设备和操作系统之间同步剪贴板内容。

## Server

Server是一个使用Flask框架和Socket.IO库的Python web应用，允许用户发送剪贴板内容到指定的设备（如智能电视）。主要功能包括：

1. 使用Flask框架创建web应用，并集成Socket.IO库来处理实时通信。
2. 应用包含一个路由`/`，用于渲染index.html页面，并显示已注册的设备列表。
3. 提供`/send_clipboard`路由，允许用户通过POST请求发送剪贴板内容到指定设备。
4. 使用Socket.IO处理设备连接、注册和断开连接事件，并更新设备列表。

### 安装和运行

请按照以下步骤安装和运行Server：

1. 克隆仓库：
   ```sh
   git clone https://github.com/shnulaa/clipboard-sync.git
   ```

2. 进入Server目录：
   ```sh
   cd clipboard-sync/server
   ```

3. 安装依赖：
   ```sh
   pip install -r requirements.txt
   ```

4. 运行Server：
   ```sh
   python app.py
   ```

## Client

Client是一个跨平台的应用程序，允许用户在不同设备和操作系统之间同步剪贴板内容。主要功能包括：

- **跨平台剪贴板同步**：在不同设备和操作系统之间同步剪贴板内容。
- **快速访问剪贴板历史**：通过一个界面快速访问和复制剪贴板历史记录。
- **自定义快捷键**：为常用操作设置自定义快捷键，提高效率。

### 安装和运行

请按照以下步骤安装和运行Client：

1. 克隆仓库：
   ```sh
   git clone https://github.com/shnulaa/clipboard-sync.git
   ```

2. 进入Client目录：
   ```sh
   cd clipboard-sync/client
   ```

3. 获取依赖：
   ```sh
   flutter pub get
   ```

4. 运行Client：
   ```sh
   flutter run
   ```

## 使用说明

在这里简要描述如何使用项目。

## 贡献

欢迎贡献！请阅读[贡献指南](https://github.com/yourusername/yourproject/blob/main/CONTRIBUTING.md)。

## 许可证

项目遵循[许可证名称]许可。


