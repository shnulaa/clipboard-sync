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
      _addMessage('收到剪贴板数据：${data['content']}');
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
    _addMessage("已同步剪贴板：$text");
  }

  void _addMessage(String message) {
    setState(() {
      _messages.add(message);
    });
  }

  @override
  void dispose() {
    socket.disconnect();
    socket.dispose();
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
