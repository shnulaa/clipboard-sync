import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/services.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Clipboard Sync TV',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  late IO.Socket socket;
  String _deviceId = '';
  String _deviceName = '';
  final List<String> _messages = []; // 显示消息
  final ScrollController _scrollController = ScrollController(); // 添加滚动控制器

  @override
  void initState() {
    super.initState();
    _fetchDeviceInfo();
  }

  Future<void> _fetchDeviceInfo() async {
    DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();
    AndroidDeviceInfo androidInfo = await deviceInfo.androidInfo;
    setState(() {
      _deviceId = androidInfo.id;
      _deviceName = androidInfo.model;
    });
    _connectToServer();
  }

  void _connectToServer() {
    socket = IO.io(
        'http://192.168.50.224:5000', // TODO: 修改为你服务器的 IP 地址
        IO.OptionBuilder().setTransports(['websocket']).build());

    socket.onConnect((_) {
      print('TV客户端已连接');
      _addMessage('TV客户端已连接');
      socket.emit(
          'register_tv', {'id': _deviceId, 'name': _deviceName}); // 发送注册信息
    });

    socket.on('clipboard_data', (data) {
      print('收到剪贴板数据：$data');
      _addMessage('收到服务端数据：${data['content']}，已经同步到剪贴板');
      _setClipboardData(data['content']);
    });

    socket.onDisconnect((_) {
      print('TV客户端断开连接');
      _addMessage('TV客户端断开连接');
    });

    socket.onError((data) => print('连接错误：$data'));
  }

  Future<void> _setClipboardData(String text) async {
    Clipboard.setData(ClipboardData(text: text));
    _addMessage("收到服务端数据：$text，已经同步到剪贴板");
  }

  void _addMessage(String message) {
    setState(() {
      _messages.add(message);
    });
    _scrollToBottom(); // 添加滚动到底部的方法调用
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    socket.disconnect();
    socket.dispose();
    _scrollController.dispose(); // 释放滚动控制器
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Clipboard Sync TV')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('TV Device ID: $_deviceId'),
            Text('TV Device Name: $_deviceName'),
            Expanded(
                child: ListView.builder(
              controller: _scrollController, // 设置滚动控制器
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return ListTile(title: Text(_messages[index]));
              },
            ))
          ],
        ),
      ),
    );
  }
}
