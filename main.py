# main.py
import sys
import threading
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtCore import QStringListModel, QSortFilterProxyModel, Qt
from ui_form import Ui_Dialog
from tcpclient import TcpClient
from commands import *
import json


class SignalBus(QObject):
    log_signal = pyqtSignal(str)


class MainApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.signal_bus = SignalBus()
        self.signal_bus.log_signal.connect(self.append_log)

        # 初始化 TCP 客户端
        self.client = TcpClient("192.168.2.127", 8888)
        if not self.client.connect():
            self.append_log("[!] 无法连接服务器")
        else:
            self.append_log("[+] 成功连接服务器")

        # 绑定按钮事件
        self.ui.clear_logs_button.clicked.connect(self.ui.textBrowser_log.clear)
        #self.ui.textEdit_lua.textChanged.connect(self.on_text_changed)
        self.ui.refresh_class_button.clicked.connect(self.refresh_classes)
        self.ui.plainTextEdit_filterClassName.textChanged.connect(self.on_filterClass_text_changed)
        self.ui.plainTextEdit_filterMethodname.textChanged.connect(self.on_filterMethod_text_changed)

        # 初始化 model 并绑定到 listView
        self.model = QStringListModel()
        self.filter_proxy = QSortFilterProxyModel()
        self.filter_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)  # 忽略大小写
        self.filter_proxy.setSourceModel(self.model)

        # 设置 listView 显示代理模型（而不是原始 model）
        self.ui.listView_classmethod.setModel(self.filter_proxy)
        self.ui.classnameorg_model = self.model

        # 监听消息接收线程
        self.start_recv_thread()

    def on_filterClass_text_changed(self,text):
        self.filter_proxy.setFilterFixedString(text)

    def on_filterMethod_text_changed(self,text):
        pass
    
    def refresh_classes(self):
        data = {"command": REFRESH_ALL_CLASS}
        self.client.send(json.dumps(data))
        self.append_log(f"[>] 发送指令: {json.dumps(data)}")

    def send_lua_code(self):
        content = self.ui.textEdit_lua.toPlainText().strip()
        if content:
            self.client.send(content)
            self.append_log(f"[>] 发送: {content}")
            self.ui.textEdit_lua.clear()

    def append_log(self, text: str):
        self.ui.textBrowser_log.append(text)

    def start_recv_thread(self):
        def recv_loop():
            while True:
                try:
                    messages = self.client.receive()
                    for msg in messages:
                        #self.signal_bus.log_signal.emit(f"[<] 收到: {msg}")
                        message_handler(self.ui, json.loads(msg))
                except Exception as e:
                    self.signal_bus.log_signal.emit(f"[!] 接收异常: {e}")
                    break

        t = threading.Thread(target=recv_loop, daemon=True)
        t.start()

    def closeEvent(self, event):
        self.client.close()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
