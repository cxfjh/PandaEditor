import os # 导入os模块 处理文件路径
from src.utils.Config import readConfig, writeConfig, getFileConfig # 导入配置文件读写函数
from tkinter import messagebox # 弹窗库 显示提示信息
from PyQt6.QtCore import pyqtSignal, QObject # 导入PyQt6模块的核心类
from PyQt6 import QtCore, QtGui, QtWidgets  # 导入PyQt6模块的全部类


class DialogSignals(QObject): dialogClosed = pyqtSignal(object) # 定义一个信号类


# 定义一个UI类
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        self.signals = DialogSignals() # 创建信号类实例

        # 设置对话框的名称和大小
        Dialog.setObjectName("Dialog")
        Dialog.resize(344, 337)  # 设置对话框的大小
        Dialog.setFixedSize(Dialog.width(), Dialog.height()) # 禁止窗口大小调整


        # 设置主窗口的图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(getFileConfig("Root") + r'\static', 'logo.ico')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off) # 添加一个图像到图标对象中，使用"./Ui/logo.ico"路径下的图像，正常模式
        Dialog.setWindowIcon(icon) # 设置主窗口的图标
        
        # 创建垂直布局部件并设置其位置和大小
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(70, 30, 213, 211))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        
        # 创建垂直布局并设置其边距
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # 创建水平布局4
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        
        # 创建标签4并设置字体
        self.label_4 = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        
        # 创建数字选择框2并设置字体和范围
        self.spinBox_2 = QtWidgets.QSpinBox(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.spinBox_2.setFont(font)
        self.spinBox_2.setMinimum(10)
        self.spinBox_2.setMaximum(60)
        self.spinBox_2.setProperty("value", 25)
        self.spinBox_2.setObjectName("spinBox_2")
        self.horizontalLayout_4.addWidget(self.spinBox_2)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        
        # 创建水平布局6
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        
        # 创建标签6并设置字体
        self.label_6 = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        
        # 创建复选框4并设置字体和默认状态
        self.checkBox_4 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.checkBox_4.setFont(font)
        self.checkBox_4.setChecked(True)
        self.checkBox_4.setTristate(False)
        self.checkBox_4.setObjectName("checkBox_4")
        self.horizontalLayout_6.addWidget(self.checkBox_4)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        
        # 创建水平布局5
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        
        # 创建标签5并设置字体
        self.label_5 = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        
        # 创建复选框3并设置字体和默认状态
        self.checkBox_3 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.checkBox_3.setFont(font)
        self.checkBox_3.setChecked(True)
        self.checkBox_3.setTristate(False)
        self.checkBox_3.setObjectName("checkBox_3")
        self.horizontalLayout_5.addWidget(self.checkBox_3)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        
        # 创建水平布局7
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        
        # 创建标签7并设置字体
        self.label_7 = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_7.addWidget(self.label_7)
        
        # 创建复选框5并设置字体
        self.checkBox_5 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.checkBox_5.setFont(font)
        self.checkBox_5.setObjectName("checkBox_5")
        self.horizontalLayout_7.addWidget(self.checkBox_5)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        
        # 创建水平布局部件并设置其位置和大小
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(140, 260, 181, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        
        # 创建水平布局并设置其边距
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        # 创建按钮1并设置字体
        self.pushButton = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        
        # 创建按钮2并设置字体
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)

        # 重新翻译UI文本
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.setSettings() # 设置设置值

    # 重新翻译UI文本
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "设置"))
        self.label_4.setText(_translate("Dialog", "字体大小："))
        self.spinBox_2.setSuffix(_translate("Dialog", "px"))
        self.label_6.setText(_translate("Dialog", "主题风格："))
        self.checkBox_4.setText(_translate("Dialog", "暗夜模式"))
        self.label_5.setText(_translate("Dialog", "语法高亮："))
        self.checkBox_3.setText(_translate("Dialog", "高亮状态"))
        self.label_7.setText(_translate("Dialog", "窗口状态："))
        self.checkBox_5.setText(_translate("Dialog", "窗口置顶"))
        self.pushButton.setText(_translate("Dialog", "确定"))
        self.pushButton_2.setText(_translate("Dialog", "取消"))

        self.pushButton_2.clicked.connect(Dialog.reject) # 取消按钮的点击事件
        self.pushButton.clicked.connect(lambda: (self.getSettings(), Dialog.accept())) # 菜单栏的设置按钮的点击事件


    # 获取所有设置的值
    def getSettings(self):
        try:
            settings = {
                "fontSize": self.spinBox_2.value(),
                "highlightSyntax": self.checkBox_3.isChecked(),
                "darkMode": self.checkBox_4.isChecked(),
                "windowTop": self.checkBox_5.isChecked()
            }
            writeConfig("personalConfig.json", settings) # 读取json文件并写入内容
            self.signals.dialogClosed.emit(settings) # 发送信号，通知主窗口关闭设置窗口
        except: messagebox.showerror("错误", "设置失败！(6079)") # 弹出错误提示框


    # 读取json文件并设置设置值
    def setSettings(self):
        try:
            settings = readConfig("personalConfig.json") # 读取json文件

            # 设置设置值
            self.spinBox_2.setValue(settings["fontSize"])
            self.checkBox_4.setChecked(settings["darkMode"])
            self.checkBox_3.setChecked(settings["highlightSyntax"])
            self.checkBox_5.setChecked(settings["windowTop"])
        except: messagebox.showerror("错误", "设置失败！(4891)") # 弹出错误提示框

