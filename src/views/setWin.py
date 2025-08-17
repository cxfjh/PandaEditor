from tkinter import messagebox

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, QObject
from src.utils.Config import read_config, update_config


class DialogSignals(QObject):
    """设置对话框信号类，用于跨窗口和主窗口传递设置变更数据"""
    # 定义信号，对话框关闭时发射，携带设置字典数据
    dialogClosed = Signal(object)


class SettingsDialogUI:
    """设置对话框UI类，负责配置界面的展示和设置数据的处理"""

    def __init__(self):
        """初始化设置对话框的UI组件和信号实例"""
        self.vertical_layout_widget = None  # 主垂直布局容器
        self.vertical_layout = None  # 主垂直布局管理器
        self.font_size_layout = None  # 字体大小大小布局
        self.font_size_label = None  # 字体大小标签
        self.font_size_spinbox = None  # 字体大小调节框
        self.theme_layout = None  # 主题布局
        self.theme_label = None  # 主题标签
        self.dark_mode_checkbox = None  # 暗夜模式复选框
        self.syntax_highlight_layout = None  # 语法高亮布局
        self.syntax_highlight_label = None  # 语法高亮标签
        self.syntax_highlight_checkbox = None  # 语法高亮复选框
        self.window_top_layout = None  # 窗口置顶布局
        self.window_top_label = None  # 窗口置顶标签
        self.window_top_checkbox = None  # 窗口置顶复选框
        self.button_layout_widget = None  # 按钮布局容器
        self.button_layout = None  # 按钮布局管理器
        self.confirm_button = None  # 确定按钮
        self.cancel_button = None  # 取消按钮

        # 创建信号实例，用于向主窗口发送设置数据
        self.signals = DialogSignals()


    def setup_ui(self, dialog):
        """
        构建设置对话框的完整UI布局
        :param dialog: 对话框实例（父窗口）
        """
        # 设置对话框基本属性
        dialog.setObjectName("SettingsDialog")
        dialog.resize(344, 337)
        dialog.setFixedSize(dialog.width(), dialog.height())  # 固定窗口大小，防止用户调整

        # 设置对话框图标（从配置文件读取图标路径）
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(read_config("FileConfig.json", "ICON")), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        dialog.setWindowIcon(icon)

        # 初始化设置相关的控件（字体、主题等）
        self._init_settings_controls(dialog)

        # 初始化底部操作按钮（确定、取消）
        self._init_action_buttons(dialog)

        # 设置界面文本（支持国际化翻译）
        self._setup_translations(dialog)
        # 自动连接信号槽（根据对象名称匹配）
        QtCore.QMetaObject.connectSlotsByName(dialog)

        # 从配置文件加载已保存的设置，初始化控件状态
        self._load_settings_from_config()


    def _init_settings_controls(self, dialog):
        """初始化所有设置项的控件（字体大小、主题等）"""
        # 创建主垂直布局容器（放置所有设置项）
        self.vertical_layout_widget = QtWidgets.QWidget(parent=dialog)
        self.vertical_layout_widget.setGeometry(QtCore.QRect(70, 30, 213, 211))  # 固定位置和大小
        self.vertical_layout_widget.setObjectName("verticalLayoutWidget")

        # 创建垂直布局管理器（管理设置项的排列）
        self.vertical_layout = QtWidgets.QVBoxLayout(self.vertical_layout_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)  # 消除内边距，紧凑布局
        self.vertical_layout.setObjectName("verticalLayout")

        # 依次初始化各个设置项
        self._init_font_size_setting()  # 字体大小设置
        self._init_theme_setting()  # 主题风格设置
        self._init_syntax_highlight_setting()  # 语法高亮设置
        self._init_window_top_setting()  # 窗口置顶设置


    def _init_font_size_setting(self):
        """初始化字体大小设置项（标签+调节框）"""
        # 创建水平布局（一行显示标签和调节框）
        self.font_size_layout = QtWidgets.QHBoxLayout()
        self.font_size_layout.setObjectName("fontSizeLayout")

        # 字体大小标签
        self.font_size_label = QtWidgets.QLabel(parent=self.vertical_layout_widget)
        self._set_font(self.font_size_label)  # 应用统一字体样式
        self.font_size_label.setObjectName("fontSizeLabel")
        self.font_size_layout.addWidget(self.font_size_label)

        # 字体大小调节框（SpinBox）
        self.font_size_spinbox = QtWidgets.QSpinBox(parent=self.vertical_layout_widget)
        self._set_font(self.font_size_spinbox)
        self.font_size_spinbox.setMinimum(10)  # 最小字体10px
        self.font_size_spinbox.setMaximum(60)  # 最大字体60px
        self.font_size_spinbox.setProperty("value", 25)  # 默认25px
        self.font_size_spinbox.setObjectName("fontSizeSpinBox")
        self.font_size_layout.addWidget(self.font_size_spinbox)

        # 将字体大小布局添加到主垂直布局
        self.vertical_layout.addLayout(self.font_size_layout)


    def _init_theme_setting(self):
        """初始化主题风格设置项（标签+暗夜模式复选框）"""
        self.theme_layout = QtWidgets.QHBoxLayout()
        self.theme_layout.setObjectName("themeLayout")

        self.theme_label = QtWidgets.QLabel(parent=self.vertical_layout_widget)
        self._set_font(self.theme_label)
        self.theme_label.setObjectName("themeLabel")
        self.theme_layout.addWidget(self.theme_label)

        # 暗夜模式复选框（默认勾选）
        self.dark_mode_checkbox = QtWidgets.QCheckBox(parent=self.vertical_layout_widget)
        self._set_font(self.dark_mode_checkbox)
        self.dark_mode_checkbox.setChecked(True)  # 默认启用暗夜模式
        self.dark_mode_checkbox.setTristate(False)  # 禁用三态（只支持勾选/未勾选）
        self.dark_mode_checkbox.setObjectName("darkModeCheckBox")
        self.theme_layout.addWidget(self.dark_mode_checkbox)

        self.vertical_layout.addLayout(self.theme_layout)


    def _init_syntax_highlight_setting(self):
        """初始化语法高亮设置项（标签+复选框）"""
        self.syntax_highlight_layout = QtWidgets.QHBoxLayout()
        self.syntax_highlight_layout.setObjectName("syntaxHighlightLayout")

        self.syntax_highlight_label = QtWidgets.QLabel(parent=self.vertical_layout_widget)
        self._set_font(self.syntax_highlight_label)
        self.syntax_highlight_label.setObjectName("syntaxHighlightLabel")
        self.syntax_highlight_layout.addWidget(self.syntax_highlight_label)

        # 语法高亮复选框（默认勾选）
        self.syntax_highlight_checkbox = QtWidgets.QCheckBox(parent=self.vertical_layout_widget)
        self._set_font(self.syntax_highlight_checkbox)
        self.syntax_highlight_checkbox.setChecked(True)  # 默认启用语法高亮
        self.syntax_highlight_checkbox.setTristate(False)
        self.syntax_highlight_checkbox.setObjectName("syntaxHighlightCheckBox")
        self.syntax_highlight_layout.addWidget(self.syntax_highlight_checkbox)

        self.vertical_layout.addLayout(self.syntax_highlight_layout)


    def _init_window_top_setting(self):
        """初始化窗口置顶设置项（标签+复选框）"""
        self.window_top_layout = QtWidgets.QHBoxLayout()
        self.window_top_layout.setObjectName("windowTopLayout")

        self.window_top_label = QtWidgets.QLabel(parent=self.vertical_layout_widget)
        self._set_font(self.window_top_label)
        self.window_top_label.setObjectName("windowTopLabel")
        self.window_top_layout.addWidget(self.window_top_label)

        # 窗口置顶复选框（默认不勾选）
        self.window_top_checkbox = QtWidgets.QCheckBox(parent=self.vertical_layout_widget)
        self._set_font(self.window_top_checkbox)
        self.window_top_checkbox.setObjectName("windowTopCheckBox")  # 默认不置顶
        self.window_top_layout.addWidget(self.window_top_checkbox)

        self.vertical_layout.addLayout(self.window_top_layout)


    def _init_action_buttons(self, dialog):
        """初始化底部操作按钮（确定和取消）"""
        # 按钮布局容器
        self.button_layout_widget = QtWidgets.QWidget(parent=dialog)
        self.button_layout_widget.setGeometry(QtCore.QRect(140, 260, 181, 41))  # 固定位置
        self.button_layout_widget.setObjectName("buttonLayoutWidget")

        # 按钮水平布局（并排显示确定和取消）
        self.button_layout = QtWidgets.QHBoxLayout(self.button_layout_widget)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setObjectName("buttonLayout")

        # 确定按钮
        self.confirm_button = QtWidgets.QPushButton(parent=self.button_layout_widget)
        self._set_font(self.confirm_button)
        self.confirm_button.setObjectName("confirmButton")
        self.button_layout.addWidget(self.confirm_button)

        # 取消按钮
        self.cancel_button = QtWidgets.QPushButton(parent=self.button_layout_widget)
        self._set_font(self.cancel_button)
        self.cancel_button.setObjectName("cancelButton")
        self.button_layout.addWidget(self.cancel_button)


    @staticmethod
    def _set_font(widget):
        """为所有控件设置统一的字体样式（楷体，14px）"""
        font = QtGui.QFont()
        font.setFamily("楷体")  # 使用楷体，适合中文显示
        font.setPointSize(14)  # 字体大小14px
        widget.setFont(font)


    def _setup_translations(self, dialog):
        """设置界面所有文本（支持国际化翻译）"""
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("Dialog", "设置"))  # 窗口标题

        # 各个设置项的文本
        self.font_size_label.setText(_translate("Dialog", "字体大小："))
        self.font_size_spinbox.setSuffix(_translate("Dialog", "px"))  # 单位显示
        self.theme_label.setText(_translate("Dialog", "主题风格："))
        self.dark_mode_checkbox.setText(_translate("Dialog", "暗夜模式"))
        self.syntax_highlight_label.setText(_translate("Dialog", "语法高亮："))
        self.syntax_highlight_checkbox.setText(_translate("Dialog", "高亮状态"))
        self.window_top_label.setText(_translate("Dialog", "窗口状态："))
        self.window_top_checkbox.setText(_translate("Dialog", "窗口置顶"))

        # 按钮文本
        self.confirm_button.setText(_translate("Dialog", "确定"))
        self.cancel_button.setText(_translate("Dialog", "取消"))

        # 绑定按钮事件
        self.cancel_button.clicked.connect(dialog.reject)  # 取消按钮：关闭对话框（不保存）
        # 确定按钮：保存设置到配置文件 + 关闭对话框
        self.confirm_button.clicked.connect(lambda: (self._save_settings_to_config(), dialog.accept()))


    def _save_settings_to_config(self):
        """将当前设置项的状态保存到配置文件，并发射信号通知主窗口更新"""
        try:
            # 收集当前所有设置项的状态
            current_settings = {
                "fontSize": self.font_size_spinbox.value(),  # 字体大小
                "highlightSyntax": self.syntax_highlight_checkbox.isChecked(),  # 语法高亮状态
                "darkMode": self.dark_mode_checkbox.isChecked(),  # 暗夜模式状态
                "windowTop": self.window_top_checkbox.isChecked()  # 窗口置顶状态
            }
            # 保存到配置文件
            update_config("PersonalConfig.json", current_settings)
            # 发射信号，通知主窗口应用新设置
            self.signals.dialogClosed.emit(current_settings)
        except Exception as e:
            messagebox.showerror("设置保存", f"保存设置失败: {str(e)}")


    def _load_settings_from_config(self):
        """从配置文件加载已保存的设置，初始化控件状态"""
        try:
            # 读取配置文件中的设置
            saved_settings = read_config("PersonalConfig.json")
            if saved_settings:  # 如果配置存在
                # 同步到各个控件
                self.font_size_spinbox.setValue(saved_settings["fontSize"])
                self.dark_mode_checkbox.setChecked(saved_settings["darkMode"])
                self.syntax_highlight_checkbox.setChecked(saved_settings["highlightSyntax"])
                self.window_top_checkbox.setChecked(saved_settings["windowTop"])
        except Exception as e:
            messagebox.showerror("设置加载", f"加载设置失败: {str(e)}")
