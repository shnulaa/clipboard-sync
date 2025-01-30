# Clipboard Sync TV

Clipboard Sync TV是一个Flutter应用，用于将剪贴板数据从移动设备同步到TV设备。应用通过WebSocket与服务器通信，接收剪贴板更新并显示在TV屏幕上。

## 功能特性

- 实时同步剪贴板数据
- 支持多种设备平台
- 简单易用的用户界面
- 高效的WebSocket通信

## 技术栈

- Flutter：用于构建跨平台应用
- WebSocket：用于实时通信
- Dart：编程语言

## 编译指南

要编译Clipboard Sync TV，请按照以下步骤操作：

1. 确保你已经安装了Flutter SDK和所有依赖项。
2. 打开终端，导航到项目目录。
3. 运行`flutter pub get`来获取所有依赖项。
4. 根据你的目标平台，运行以下命令之一：

   - 对于Android：`flutter run --release`在连接的Android设备或模拟器上运行应用。
   - 对于iOS：`flutter run --release`在连接的iOS设备或模拟器上运行应用。
   - 对于Web：`flutter run -d chrome --release`在Chrome浏览器中运行应用。
   - 对于Linux、macOS和Windows，你可能需要查看Flutter文档以获取特定平台的编译指南。

## 配置指南

请注意，你可能需要根据你的服务器IP地址和配置修改`lib/main.dart`中的相关代码。具体步骤如下：

1. 打开`lib/main.dart`文件。
2. 找到WebSocket服务器地址配置部分。
3. 将默认的服务器地址替换为你的服务器IP地址。

```dart
// lib/main.dart
// ...existing code...
const String serverAddress = 'ws://your-server-ip:port';
// ...existing code...
```

## 运行截图

以下是应用运行时的截图：

![Screenshot1](screenshots/screenshot1.png)
![Screenshot2](screenshots/screenshot2.png)

## 贡献指南

如果你想为Clipboard Sync TV做出贡献，请遵循以下步骤：

1. Fork此仓库。
2. 创建一个新的分支：`git checkout -b feature-branch`
3. 提交你的更改：`git commit -am 'Add new feature'`
4. 推送到分支：`git push origin feature-branch`
5. 创建一个Pull Request

## 许可证

此项目使用MIT许可证。有关更多信息，请参阅LICENSE文件。
