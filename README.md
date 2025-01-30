# Server

Server是一个使用Flask框架和Socket.IO库的Python web应用，允许用户发送剪贴板内容到指定的设备（如智能电视）。主要功能包括：

1. 使用Flask框架创建web应用，并集成Socket.IO库来处理实时通信。
2. 应用包含一个路由`/`，用于渲染index.html页面，并显示已注册的设备列表。
3. 提供`/send_clipboard`路由，允许用户通过POST请求发送剪贴板内容到指定设备。
4. 使用Socket.IO处理设备连接、注册和断开连接事件，并更新设备列表。

如需更详细的文档或说明，请参考项目的其他文档和代码。


# client

项目简介。

## 功能

- **跨平台剪贴板同步**：在不同设备和操作系统之间同步剪贴板内容。
- **快速访问剪贴板历史**：通过一个界面快速访问和复制剪贴板历史记录。
- **自定义快捷键**：为常用操作设置自定义快捷键，提高效率。

## 安装

请按照以下步骤安装和运行项目：

1. 克隆仓库：
   ```
   git clone https://github.com/shnulaa/clipboard-sync.git
   ```

2. 进入项目目录：
   ```
   cd yourproject
   ```

3. 获取依赖：
   ```
   flutter pub get
   ```

4. 运行项目：
   ```
   flutter run
   ```

## 使用说明

在这里简要描述如何使用项目。

## 贡献

欢迎贡献！请阅读[贡献指南](https://github.com/yourusername/yourproject/blob/main/CONTRIBUTING.md)。

## 许可证

项目遵循[许可证名称]许可。


