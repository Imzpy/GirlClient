# main.py
import sys
import threading
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtCore import QStringListModel, QSortFilterProxyModel, Qt, QModelIndex
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.Qsci import QsciScintilla, QsciLexerLua
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
        self.client = TcpClient("192.168.2.169", 8888) #192.168.2.127
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
        self.cmodel = QStringListModel()
        self.filter_proxy = QSortFilterProxyModel()
        self.filter_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)  # 忽略大小写
        self.filter_proxy.setSourceModel(self.cmodel)

        self.ui.listView_classmethod.clicked.connect(self.on_classname_clicked)
        self.ui.listView_classmethod.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置 listView 显示代理模型（而不是原始 model）
        self.ui.listView_classmethod.setModel(self.filter_proxy)
        self.ui.classnameorg_model = self.cmodel

        self.mmodel = QStringListModel()
        self.mfilter_proxy = QSortFilterProxyModel()
        self.mfilter_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)  # 忽略大小写
        self.mfilter_proxy.setSourceModel(self.mmodel)
        self.mfilter_proxy.setSourceModel(self.mmodel)
        self.ui.listView_methods.clicked.connect(self.on_methodname_clicked)
        self.ui.listView_methods.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置 listView 显示代理模型（而不是原始 model）
        self.ui.listView_methods.setModel(self.mfilter_proxy)
        self.ui.methodsorg_model = self.mmodel

        self.setup_lua_editor()

        # 监听消息接收线程
        self.start_recv_thread()

    def on_filterClass_text_changed(self,text):
        self.filter_proxy.setFilterFixedString(text)

    def on_filterMethod_text_changed(self,text):
        self.mfilter_proxy.setFilterFixedString(text)
    
    def refresh_classes(self):
        data = {COMMAND: REFRESH_ALL_CLASS}
        self.client.send(json.dumps(data))
        self.append_log(f"[>] 发送指令: {json.dumps(data)}")

    def on_classname_clicked(self, index: QModelIndex):
        source_index = self.filter_proxy.mapToSource(index)
        text = self.cmodel.data(source_index, Qt.DisplayRole)
        data = {COMMAND: REFRESH_ALL_METHODS, CLASSNAME:text}
        self.client.send(json.dumps(data))
        self.ui.textBrowser_log.append("[Log] 获取类" + text + "的方法.")
        self.append_log(f"[>] 发送指令: {json.dumps(data)}")

    def on_methodname_clicked(self, index: QModelIndex):
        source_index = self.mfilter_proxy.mapToSource(index)
        text = self.mmodel.data(source_index, Qt.DisplayRole)
        self.ui.tip_methodname.setText('方法名:' + text)
        self.ui.tip_methodname.setToolTip('方法名:' + text)

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
    def setup_lua_editor(self):
        parent = self.ui.textEdit_lua.parent()
        layout = parent.layout()

        self.editor = QsciScintilla()
        self.editor.setLexer(QsciLexerLua())
        self.editor.setUtf8(True)
        self.editor.setMarginsFont(self.editor.font())
        self.editor.setMarginWidth(0, "0000")
        self.editor.setMarginLineNumbers(0, True)
        self.editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.editor.setAutoIndent(True)
        self.editor.setIndentationsUseTabs(False)
        self.editor.setTabWidth(4)
        self.editor.setIndentationWidth(4)

        # 保留原控件的尺寸策略和限制
        self.editor.setSizePolicy(self.ui.textEdit_lua.sizePolicy())
        self.editor.setMinimumSize(self.ui.textEdit_lua.minimumSize())
        self.editor.setMaximumSize(self.ui.textEdit_lua.maximumSize())
        self.editor.setMarginWidth(0, "000")
        self.editor.setWrapMode(QsciScintilla.WrapNone)  # 不自动换行
        self.editor.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTH, 1)  # 减少初始宽度估算
        self.editor.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTHTRACKING, True)  # 自适应宽度

        self.editor.linesChanged.connect(self._update_margin_width)

        # 替换旧控件
        layout.replaceWidget(self.ui.textEdit_lua, self.editor)
        self.ui.textEdit_lua.deleteLater()
        self.ui.textEdit_lua = self.editor
    def _update_margin_width(self):
        line_count = self.editor.lines()
        digits = max(2, len(str(line_count)))
        width = self.editor.fontMetrics().width("9" * (digits + 1))
        self.editor.setMarginWidth(0, width)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
