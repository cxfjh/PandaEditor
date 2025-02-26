import os
import keyboard
from tkinter import messagebox
from PyQt6 import QtCore, QtGui, QtWidgets 
from src.utils.SyntaxHigh import ChineseHighlighter 
from src.utils.CodeProc import runCode, compileCode 
from src.utils.Config import readConfig
from src.views.SetWin import Ui_Dialog, DialogSignals
from src.utils.SetPage import resetProgram, uninstallProgram
from src.utils.FileOps import openFile, readFileContent, saveFile, saveAsFile, splitFilePath


# 定义主窗口类
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow") # 设置主窗口的对象名
        MainWindow.resize(1500, 900) # 设置主窗口的初始大小为 800x600

        # 创建一个大小策略对象，并设置为可扩展的大小策略
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)  # 水平拉伸因子设为0
        sizePolicy.setVerticalStretch(0)    # 垂直拉伸因子设为0
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())  # 根据高度是否可以基于宽度进行调整
        MainWindow.setSizePolicy(sizePolicy)  # 设置主窗口的大小策略

        # 创建一个图标对象
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(readConfig("FileConfig.json", "ICON")), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off) # 添加一个图像到图标对象中，使用"./Ui/logo.ico"路径下的图像，正常模式
        MainWindow.setWindowIcon(icon) # 设置主窗口的图标

        # 将Ui_Dialog其设为MainWindow的子部件
        self.setWin = QtWidgets.QDialog()
        self.setWin.ui = Ui_Dialog()
        self.setWin.ui.setupUi(self.setWin)
        self.setWin.setWindowTitle("设置")
        self.setWin.setWindowIcon(icon)
        self.setWin.hide()

        self.signals = DialogSignals() # 创建信号实例
        self.setWin.ui.signals.dialogClosed.connect(self.changeStyle) # 将设置窗口的信号连接到主窗口的槽函数

        # 创建一个中心窗口部件对象，并将其设为MainWindow的子部件
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget) # 创建一个水平布局的部件，作为self.centralwidget的子部件
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(50, 20, 691, 521)) # 设置该部件在self.centralwidget中的位置和大小
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        
        # 创建一个水平布局管理器，将其与self.horizontalLayoutWidget关联
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)  # 设置水平布局的外边距为0
        self.horizontalLayout.setObjectName("horizontalLayout")

        # 创建状态栏
        self.statusbar = MainWindow.statusBar()
        self.statusLabel = QtWidgets.QLabel() # 创建一个状态栏标签
        self.statusLabel.setText("Ready")  # 设置初始文本
        self.statusbar.addPermanentWidget(self.statusLabel)  # 添加到状态栏的永久部件区域
        MainWindow.setStatusBar(self.statusbar) # 设置MainWindow的状态栏为self.statusbar

        
        # 创建一个多行文本编辑框，作为self.horizontalLayoutWidget的子部件
        self.plainTextEdit = QtWidgets.QPlainTextEdit(parent=self.horizontalLayoutWidget)
        self.plainTextEdit.cursorPositionChanged.connect(self.onCursorPositionChanged) # 连接光标位置改变的信号到槽函数

        # 设置文本框的背景颜色和字体大小和字体颜色
        def iniStyle(fontSize = 25, bgColor = True, fontColor = True, windowStaysOnTop = False):
            font = QtGui.QFont() # 创建一个字体对象，并设置字体书法和大小
            font.setFamily("楷体")  # 设置字体书法为楷体
            font.setPointSize(fontSize)  # 设置字体大小为25
            self.plainTextEdit.setFont(font) # 将设置好的字体应用于self.plainTextEdit 
            if fontColor: self.highlighter = ChineseHighlighter(self.plainTextEdit.document()) # 创建一个语法高亮对象，并将其与self.plainTextEdit关联
            else: self.highlighter = None # 不使用语法高亮
            if bgColor: self.plainTextEdit.setStyleSheet("background-color: #1f1f1f; color: #cccccc;") # 设置文本框的背景颜色为黑色，字体颜色为白色
            else: self.plainTextEdit.setStyleSheet("background-color: #ffffff; color: #0d0d10;") # 设置文本框的背景颜色为白色，字体颜色为黑色
            MainWindow.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, windowStaysOnTop)  # 设置窗口置顶
            MainWindow.show() # 显示主窗口
        self.iniStyle = iniStyle # 将iniStyle函数设为self.iniStyle

        # 读取配置文件
        if readConfig("PersonalConfig.json"): 
            try:
                settings = readConfig("PersonalConfig.json")
                iniStyle(settings['fontSize'], settings['darkMode'], settings['highlightSyntax'], settings['windowTop'])
            except: messagebox.showerror("样式配置", "配置样式文件读取失败，请检查配置文件内容。")
        else: iniStyle()
        
        self.plainTextEdit.setTabChangesFocus(True) # 设置按下Tab键时切换焦点
        self.plainTextEdit.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)  # 设置文本换行模式为不换行
        self.plainTextEdit.setTabStopDistance(60.0) # 设置Tab键的停止距离为60.0像素
        self.plainTextEdit.setObjectName("plainTextEdit") # 设置多行文本编辑框的对象名
        self.horizontalLayout.addWidget(self.plainTextEdit) # 将self.plainTextEdit添加到self.horizontalLayout中

        # 创建一个垂直布局管理器，将其与self.centralwidget关联
        self.centralLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralLayout.addWidget(self.horizontalLayoutWidget) # 将self.horizontalLayoutWidget添加到self.centralLayout中
        MainWindow.setCentralWidget(self.centralwidget) # 设置MainWindow的中心部件为self.centralwidget

        # 创建一个菜单栏部件，作为MainWindow的子部件
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21)) # 设置菜单栏的位置和大小
        self.menubar.setObjectName("menubar") # 设置菜单栏的对象名

        # 创建多个菜单部件，作为self.menubar的子部件
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_3.setObjectName("menu_3")
        self.menu_4 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_4.setObjectName("menu_4")
        self.menu_6 = QtWidgets.QMenu(parent=self.menu_4)
        self.menu_6.setObjectName("menu_6")
        self.menu_5 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_5.setObjectName("menu_5")
        MainWindow.setMenuBar(self.menubar)

        # 创建多个操作部件，作为MainWindow的子部件
        self.action = QtGui.QAction(parent=MainWindow)
        self.action.setObjectName("action")
        self.action_2 = QtGui.QAction(parent=MainWindow)
        self.action_2.setObjectName("action_2")
        self.action_3 = QtGui.QAction(parent=MainWindow)
        self.action_3.setObjectName("action_3")
        self.action_4 = QtGui.QAction(parent=MainWindow)
        self.action_4.setObjectName("action_4")
        self.action_5 = QtGui.QAction(parent=MainWindow)
        self.action_5.setObjectName("action_5")
        self.action_6 = QtGui.QAction(parent=MainWindow)
        self.action_6.setObjectName("action_6")
        self.action_7 = QtGui.QAction(parent=MainWindow)
        self.action_7.setObjectName("action_7")
        self.action_8 = QtGui.QAction(parent=MainWindow)
        self.action_8.setObjectName("action_8")
        self.action2449579731_qq_com = QtGui.QAction(parent=MainWindow)
        self.action2449579731_qq_com.setObjectName("action2449579731_qq_com")
        self.action_10 = QtGui.QAction(parent=MainWindow)
        self.action_10.setCheckable(False)
        self.action_10.setChecked(False)
        self.action_10.setObjectName("action_10")
        self.action_12 = QtGui.QAction(parent=MainWindow)
        self.action_12.setObjectName("action_12")
        self.action_13 = QtGui.QAction(parent=MainWindow)
        self.action_13.setObjectName("action_13")
        self.action_14 = QtGui.QAction(parent=MainWindow)
        self.action_14.setObjectName("action_14")

        # 将操作部件添加到对应的菜单部件中
        self.menu.addAction(self.action)
        self.menu.addAction(self.action_2)
        self.menu.addAction(self.action_3)
        self.menu_2.addAction(self.action_4)
        self.menu_2.addAction(self.action_5)
        self.menu_3.addAction(self.action_6)
        self.menu_3.addAction(self.action_7)
        self.menu_6.addAction(self.action2449579731_qq_com)
        self.menu_4.addAction(self.action_8)
        self.menu_4.addAction(self.menu_6.menuAction())
        self.menu_5.addAction(self.action_10)
        self.menu_5.addSeparator()
        self.menu_5.addAction(self.action_12)
        self.menu_5.addAction(self.action_13)
        self.menu_5.addAction(self.action_14)

        # 将菜单部件的menuAction()（动作）添加到菜单栏中
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())
        self.menubar.addAction(self.menu_4.menuAction())
        self.menubar.addAction(self.menu_5.menuAction())

        # 连接信号和槽，关联界面翻译和其他功能的实现
        self.retranslateUi(MainWindow)  # 调用界面翻译函数
        QtCore.QMetaObject.connectSlotsByName(MainWindow)  # 使用元对象连接机制，连接MainWindow中的槽函数


    # 定义槽函数更改文本框的背景颜色和字体颜色
    def changeStyle(self, message): self.iniStyle(message['fontSize'], message['darkMode'], message['highlightSyntax'], message['windowTop'])


    # 定义槽函数获取光标所在的行数
    def onCursorPositionChanged(self):
        # 获取光标的当前位置（索引）
        cursor = self.plainTextEdit.textCursor()
        cursorPosition = cursor.position()
        
        # 获取光标所在的行数
        cursorBlock = self.plainTextEdit.document().findBlock(cursorPosition)
        cursorLineNumber = cursorBlock.blockNumber() + 1  # 行号从0开始，+1转换为从1开始

        self.statusLabel.setText(f"行号: {cursorLineNumber}    文件：{readConfig('FileConfig.json', 'SourceCodePath')}/{readConfig('FileConfig.json', 'CodeName')}.cn     版本: v2.0.1") # 修改状态栏的文本


    # 定义界面
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate  # 定义一个翻译函数
        MainWindow.setWindowTitle(_translate("MainWindow", "熊猫编辑器"))  # 设置主窗口的标题

        # 设置各个菜单项的显示文本
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.menu_2.setTitle(_translate("MainWindow", "代码"))
        self.menu_3.setTitle(_translate("MainWindow", "关于"))
        self.menu_4.setTitle(_translate("MainWindow", "帮助"))
        self.menu_6.setTitle(_translate("MainWindow", "联系作者"))
        self.menu_5.setTitle(_translate("MainWindow", "设置"))
        self.action.setText(_translate("MainWindow", "打开文件  Ctrl+O"))
        self.action_2.setText(_translate("MainWindow", "保存文件  Ctrl+S"))
        self.action_3.setText(_translate("MainWindow", "另存文件  Ctrl+Shift+S"))
        self.action_4.setText(_translate("MainWindow", "运行代码  Ctrl+R"))
        self.action_5.setText(_translate("MainWindow", "编译代码  Ctrl+B"))
        self.action_6.setText(_translate("MainWindow", "官方网站"))
        self.action_7.setText(_translate("MainWindow", "开源地址"))
        self.action_8.setText(_translate("MainWindow", "使用教程"))
        self.action2449579731_qq_com.setText(_translate("MainWindow", "2449579731@qq.com"))
        self.action_10.setText(_translate("MainWindow", "视图设置"))
        self.action_12.setText(_translate("MainWindow", "更新程序  Ctrl+U"))
        self.action_13.setText(_translate("MainWindow", "卸载程序  Ctrl+Shift+U"))
        self.action_14.setText(_translate("MainWindow", "重置程序  Ctrl+Shift+R"))

        if readConfig("FileConfig.json", "SourceCodePath") != "": self.plainTextEdit.setPlainText(readFileContent())

        # 绑定信号和槽，关联菜单项的点击事件和功能实现
        self.action.triggered.connect(lambda: (openFile(), self.plainTextEdit.setPlainText(readFileContent()))) # 绑定打开文件操作
        self.action_2.triggered.connect(lambda: saveFile(self.plainTextEdit.toPlainText()))  # 绑定保存文件操作
        self.action_3.triggered.connect(lambda: saveAsFile(self.plainTextEdit.toPlainText()))  # 绑定另存文件操作
        self.action_4.triggered.connect(lambda: (runCode(self.plainTextEdit.toPlainText()), saveFile(self.plainTextEdit.toPlainText())))  # 绑定运行代码操作
        self.action_5.triggered.connect(lambda: (compileCode(self.plainTextEdit.toPlainText()), saveFile(self.plainTextEdit.toPlainText())))  # 绑定编译代码操作
        self.action_6.triggered.connect(lambda: os.startfile('https://cxfjh.github.io/PandaEditorHub/'))  # 绑定官方网站操作
        self.action_7.triggered.connect(lambda: os.startfile('https://github.com/cxfjh/PandaEditor'))  # 绑定开源地址操作
        self.action_13.triggered.connect(uninstallProgram)  # 绑定卸载程序操作
        self.action_14.triggered.connect(resetProgram)  # 绑定重置程序操作
        self.action_10.triggered.connect(self.setWin.show)  # 绑定视图设置操作
        self.action_12.triggered.connect(lambda: os.startfile('https://cxfjh.github.io/PandaEditorHub/'))  # 绑定更新程序操作
        self.action_8.triggered.connect(lambda: os.startfile('https://github.com/cxfjh/PandaEditor/blob/main/docs/USAGE.md'))  # 绑定使用教程操作

        # 快捷键设置
        keyboard.add_hotkey('Ctrl+O', lambda: (openFile(), self.plainTextEdit.setPlainText(readFileContent())))  # 绑定Ctrl+O快捷键打开文件
        keyboard.add_hotkey('ctrl+S', lambda: saveFile(self.plainTextEdit.toPlainText()))  # 绑定Ctrl+S快捷键保存文件
        keyboard.add_hotkey('Ctrl+Shift+S', lambda: saveAsFile(self.plainTextEdit.toPlainText()))  # 绑定Ctrl+Shift+S快捷键另存文件
        keyboard.add_hotkey('Ctrl+R', lambda: (runCode(self.plainTextEdit.toPlainText()), saveFile(self.plainTextEdit.toPlainText())))  # 绑定Ctrl+R快捷键运行代码
        keyboard.add_hotkey('Ctrl+B', lambda: (compileCode(self.plainTextEdit.toPlainText()), saveFile(self.plainTextEdit.toPlainText())))  # 绑定Ctrl+B快捷键编译代码
        keyboard.add_hotkey('Ctrl+Shift+U', uninstallProgram)  # 绑定Ctrl+Shift+U快捷键卸载程序
        keyboard.add_hotkey('Ctrl+Shift+R', resetProgram)  # 绑定Ctrl+Shift+R快捷键重置程序
        keyboard.add_hotkey('Ctrl+U', lambda: os.startfile('https://cxfjh.github.io/PandaEditorHub/'))  # 绑定Ctrl+U快捷键更新程序
