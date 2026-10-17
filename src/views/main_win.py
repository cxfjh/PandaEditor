import os
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QKeySequence, QShortcut
from src.utils import code_proc, extend, file_ops, set_page
from src.utils.extend import paint_gradient
from src.utils.code_proc import signals as code_signals
from src.utils.config_service import get_config_service
from src.utils.file_ops import import_file, read_file_content
from src.utils.syntax_high import ChineseHighlighter
from src.views.components.custom_title_bar import CustomTitleBar
from src.views.components.event_filters import WindowFocusFilter
from src.views.components.tab_manager import TabManager
from src.views.file_tree import FileTreeView
from src.views.terminal import TerminalWidget
from src.views.components.handlers import MainWindowHandlers
from src.views.components.menus import MenuBuilder
from src.utils.set_page import reset_program, uninstall_program
from src.utils.dialog_utils import DialogUtils


class MainWindowUI:
    """主窗口用户界面类"""

    def __init__(self):
        """初始化 UI 组件引用"""
        self.highlighter = None  # 语法高亮器实例
        self.main_window = None  # 主窗口引用
        self.current_editing_file = None  # 当前编辑的文件路径
        self.has_unsaved_changes = False  # 是否有未保存的修改
        self.handlers = None  # 事件处理器
        self.init_style_func = None  # 样式初始化函数
        self._font_filter = None  # 字体事件过滤器
        self._window_focus_filter = None  # 窗口焦点事件过滤器（用于自动保存）
        self._shortcuts = []  # 全局快捷键列表
        self.tab_manager = None  # 标签页管理器
        self.tab_widget = None  # 标签页组件

    def setup_ui(self, main_window):
        """
        初始化主窗口 UI 布局和组件

        Args:
            main_window: QMainWindow 实例，主窗口对象
        """
        self.main_window = main_window
        self.handlers = MainWindowHandlers(self)  # 创建事件处理器，绑定所有菜单动作

        # 窗口基础设置
        self._setup_main_window(main_window)  # 设置窗口大小、无边框等属性
        self._setup_icon(main_window)  # 设置窗口图标

        # 菜单系统
        MenuBuilder.create_menus(main_window, self)  # 创建菜单栏和子菜单
        MenuBuilder.create_actions(main_window, self)  # 创建菜单项动作
        self._setup_central_widget(main_window)  # 创建中央部件

        # 菜单集成与翻译
        self.custom_title_bar.set_menu_bar(self.menu_bar)  # 将菜单栏嵌入自定义标题栏
        MenuBuilder.build_menu_structure(self)  # 将菜单项添加到对应菜单
        self._init_menu_states()  # 从配置恢复菜单勾选状态
        MenuBuilder.setup_translations(main_window, self)  # 设置菜单文本翻译

        # 编辑器和功能设置
        self._setup_text_edit()  # 创建默认标签页和终端回调
        self._setup_style(main_window)  # 应用主题、字体、语法高亮
        self._setup_signals_and_slots()  # 绑定所有信号与槽
        self._setup_global_shortcuts(main_window)  # 注册全局快捷键
        self._setup_auto_save()  # 设置窗口失焦自动保存
        self._init_service_parents(main_window)  # 为工具模块注入父窗口引用
        self._setup_close_event(main_window)  # 拦截关闭事件，保存状态
        QtCore.QMetaObject.connectSlotsByName(main_window)  # 启用按名称自动连接槽

    @staticmethod
    def _init_service_parents(main_window):
        """为各服务模块注入父窗口引用"""
        file_ops.set_parent_widget(main_window)  # 文件操作模块
        code_proc.set_parent_widget(main_window)  # 代码处理模块
        set_page.set_parent_widget(main_window)  # 设置页面模块
        extend.set_parent_widget(main_window)  # 扩展库模块

    @staticmethod
    def _setup_main_window(main_window):
        """设置主窗口基本属性"""
        main_window.setObjectName("MainWindow")
        main_window.resize(1500, 900)  # 默认窗口大小
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
        main_window.setSizePolicy(size_policy)

        # 隐藏原生标题栏使用自定义标题栏
        main_window.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |  # 无边框
            QtCore.Qt.WindowType.WindowSystemMenuHint |  # 系统菜单
            QtCore.Qt.WindowType.WindowMinimizeButtonHint |  # 最小化按钮
            QtCore.Qt.WindowType.WindowMaximizeButtonHint |  # 最大化按钮
            QtCore.Qt.WindowType.WindowCloseButtonHint,  # 关闭按钮
        )

    @staticmethod
    def _setup_icon(main_window):
        """设置窗口图标"""
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_config_service().get_app_config("icon_path")), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        main_window.setWindowIcon(icon)

    def _setup_central_widget(self, main_window):
        """设置中央部件及布局"""
        # 创建渐变背景容器
        self.central_widget = GradientBackgroundWidget(parent=main_window, gradient_colors=["#667eea", "#764ba2", "#f093fb"], gradient_alpha=0.85)
        self.central_widget.setObjectName("central_widget")

        # 主布局垂直排列标题栏和内容区
        main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(1, 0, 1, 0)  # 极窄边距，最大化可用空间
        main_layout.setSpacing(0)

        # 自定义标题栏
        self.custom_title_bar = CustomTitleBar(title="熊猫编辑器", parent=main_window, gradient_colors=["#667eea", "#764ba2", "#f093fb"], fg_color="#FFFFFF")
        main_layout.addWidget(self.custom_title_bar)

        # 连接标题栏按钮信号到窗口操作
        self.custom_title_bar.minimize_clicked.connect(main_window.showMinimized)
        self.custom_title_bar.maximize_clicked.connect(self._on_toggle_maximize)
        self.custom_title_bar.close_clicked.connect(main_window.close)

        # 内容区域容器
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 主分割器
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, content_widget)
        self.main_splitter.setObjectName("main_splitter")
        self.main_splitter.setStyleSheet(
            """
            QSplitter { background-color: transparent; }
            QSplitter::handle { background-color: transparent; }
            QSplitter::handle:horizontal { width: 6px; }
            """,
        )

        # 文件树面板
        self.file_tree_wrapper = QtWidgets.QWidget(self.main_splitter)
        self.file_tree_wrapper.setObjectName("file_tree_wrapper")
        self.file_tree_wrapper.setStyleSheet(
            """
            QWidget#file_tree_wrapper {
                background-color: #2b2d30; 
                border-radius: 6px;
                margin: 4px;
            }
            """,
        )
        self.file_tree_layout = QtWidgets.QVBoxLayout(self.file_tree_wrapper)
        self.file_tree_layout.setContentsMargins(4, 4, 6, 6)
        self.file_tree = FileTreeView(self.file_tree_wrapper)  # 异步加载的文件树组件
        self.file_tree.setMinimumWidth(180)
        self.file_tree_layout.addWidget(self.file_tree)
        self.main_splitter.addWidget(self.file_tree_wrapper)

        # 编辑区 + 终端
        self.right_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, self.main_splitter)
        self.right_splitter.setObjectName("right_splitter")
        self.right_splitter.setStyleSheet(
            """
            QSplitter { background-color: transparent; }
            QSplitter::handle { background-color: transparent; }
            QSplitter::handle:vertical { height: 6px; }
            """,
        )

        # 编辑器面板
        self.editor_wrapper = QtWidgets.QWidget(self.right_splitter)
        self.editor_wrapper.setObjectName("editor_wrapper")
        self.editor_wrapper.setStyleSheet(
            """
            QWidget#editor_wrapper {
                background-color: #1e1f22;  /* VS Code 风格深色背景 */
                border-radius: 6px;
                margin: 4px;
            }
            """,
        )
        self.editor_wrapper_layout = QtWidgets.QVBoxLayout(self.editor_wrapper)
        self.editor_wrapper_layout.setContentsMargins(6, 4, 6, 6)

        # 标签页组件
        self.tab_widget = QtWidgets.QTabWidget(self.editor_wrapper)
        self.tab_widget.setObjectName("tab_widget")
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                background-color: transparent;
                border: none;
            }
            """,
        )
        self.editor_wrapper_layout.addWidget(self.tab_widget)

        # 初始化标签页管理器
        self.tab_manager = TabManager(self.tab_widget, parent=main_window)
        self.tab_manager.tab_changed.connect(self.handlers.on_cursor_position_changed)  # 切换标签时更新状态栏

        # 终端面板
        self.terminal_wrapper = QtWidgets.QWidget(self.right_splitter)
        self.terminal_wrapper.setObjectName("terminal_wrapper")
        self.terminal_wrapper.setStyleSheet(
            """
            QWidget#terminal_wrapper {
                background-color: #1e1f22;
                border-radius: 6px;
                margin: 4px;
            }
            """,
        )
        self.terminal_wrapper_layout = QtWidgets.QVBoxLayout(self.terminal_wrapper)
        self.terminal_wrapper_layout.setContentsMargins(4, 4, 4, 4)
        self.terminal = TerminalWidget(self.terminal_wrapper)  # 内嵌终端组件
        self.terminal.setMinimumHeight(100)
        self.terminal.setStyleSheet(
            """
            QWidget#TerminalWidget {
                background-color: transparent;
                border: none;
            }
            """,
        )
        self.terminal.setObjectName("TerminalWidget")
        self.terminal_wrapper_layout.addWidget(self.terminal)

        # 组装分割器层次结构
        self.main_splitter.addWidget(self.right_splitter)
        self.right_splitter.addWidget(self.editor_wrapper)
        self.right_splitter.addWidget(self.terminal_wrapper)

        # 设置分割器初始比例文件树占100px，右侧占1200px
        self.main_splitter.setSizes([100, 1200])

        # 编辑器占700px终端占200px
        self.right_splitter.setSizes([700, 200])

        # 分割器手柄宽度设为1px
        self.main_splitter.setHandleWidth(1)
        self.right_splitter.setHandleWidth(1)

        # 将内容区添加到主布局
        content_layout.addWidget(self.main_splitter)
        main_layout.addWidget(content_widget, 1)  # stretch=1，占据剩余空间

        # 状态栏
        self.status_bar = main_window.statusBar()
        self.status_bar.setStyleSheet(
            """
            QStatusBar {
                background-color: #2b2d30;
                color: #A9B7C6;
                border-top: 1px solid #3c3f41;
            }
            QStatusBar QLabel {
                color: #A9B7C6;
                background-color: transparent;
            }
            """,
        )
        self.status_label = QtWidgets.QLabel()
        self.status_label.setText("Ready")
        self.status_bar.addPermanentWidget(self.status_label)  # 右侧固定显示
        main_window.setStatusBar(self.status_bar)
        main_window.setCentralWidget(self.central_widget)

        # 初始化文件树根目录
        self._init_file_tree()

    def _on_toggle_maximize(self):
        """最大化/还原窗口"""
        if self.main_window.isMaximized():
            self.main_window.showNormal()
            self.custom_title_bar.max_btn.setText("□")
            self.custom_title_bar.max_btn.setToolTip("最大化")
        else:
            self.main_window.showMaximized()
            self.custom_title_bar.max_btn.setText("❐")
            self.custom_title_bar.max_btn.setToolTip("还原")

    def _init_file_tree(self):
        """初始化文件树根目录和工作目录"""
        source_code_path = get_config_service().get_file_config("source_code_path")
        if source_code_path and os.path.isdir(source_code_path):
            self.file_tree.set_root_path(source_code_path)
            self.terminal.set_working_directory(source_code_path)

    def _setup_text_edit(self):
        """设置文本编辑区域及相关组件"""
        self.tab_manager.create_new_tab(file_path=None, content="")
        self.terminal.set_get_code_callback(lambda: self.tab_manager.get_current_editor().toPlainText() if self.tab_manager.get_current_editor() else "")

    def _setup_style(self, main_window):
        """设置编辑器样式"""

        def init_style(font_size=25, dark_mode=True, syntax_highlight=True, window_top=False):
            # 应用字体到所有标签页
            self.tab_manager.apply_font_size(font_size)

            # 应用主题到所有标签页
            self.tab_manager.apply_theme(dark_mode)

            # 设置语法高亮
            if syntax_highlight:
                current_editor = self.tab_manager.get_current_editor()
                current_file = self.tab_manager.get_current_file_path()
                if current_editor and current_file and current_file.endswith('.cn'):
                    self.highlighter = ChineseHighlighter(current_editor.document(), current_editor, dark_mode)
                    self.highlighter._current_file = current_file
                else:
                    self.highlighter = None
            else:
                self.highlighter = None

            self.tab_manager.toggle_syntax_highlight(syntax_highlight)

            self.file_tree.apply_theme(dark_mode)
            self.terminal.apply_theme(dark_mode)
            main_window.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, window_top)
            main_window.show()

        self.init_style_func = init_style

        try:
            settings = get_config_service().get_personal_config()
            if settings:
                init_style(settings['fontSize'], settings['darkMode'], settings['highlightSyntax'], settings['windowTop'])
            else:
                init_style()
        except Exception as e:
            DialogUtils.show_error(main_window, "样式配置", f"配置样式文件读取失败：\n{e}")

        # 恢复上次打开的文件和标签页
        if get_config_service().get_file_config("source_code_path") != "":
            # 尝试恢复上次的标签页
            self.tab_manager.restore_tabs_state()

            # 如果没有恢复任何标签页，则创建默认的
            if self.tab_manager.tab_widget.count() == 0:
                content = read_file_content() or ""
                source_path = get_config_service().get_file_config("source_code_path")
                code_name = get_config_service().get_file_config("code_name")
                file_ext = get_config_service().get_file_config("file_ext") or ".cn"
                if source_path and code_name:
                    file_path = os.path.normpath(os.path.join(source_path, f"{code_name}{file_ext}"))
                    if os.path.exists(file_path):
                        self.tab_manager.create_new_tab(file_path=file_path, content=content)

        # 处理启动时拖拽的文件/文件夹路径
        self._handle_launch_path()

    def _handle_launch_path(self):
        """处理启动时通过拖拽或命令行传入的文件/文件夹路径"""
        launch_path = self.main_window.property("launch_path")
        if not launch_path:
            return

        # 清理路径
        launch_path = launch_path.strip().strip('"').strip("'")

        if not os.path.exists(launch_path):
            DialogUtils.show_warning(self.main_window, "路径无效", f"找不到指定的路径：\n{launch_path}")
            return

        # 先判断是否为目录
        if os.path.isdir(launch_path):
            self._open_directory(launch_path)
        elif os.path.isfile(launch_path):
            self._open_file(launch_path)
        else:
            # 既不是文件也不是目录
            DialogUtils.show_warning(self.main_window, "路径类型未知", f"无法识别的路径类型：\n{launch_path}")

    def _open_directory(self, dir_path: str):
        """打开指定目录作为项目根目录"""
        normalized_path = os.path.normpath(dir_path)
        get_config_service().update_file_config("source_code_path", normalized_path)
        self.file_tree.set_root_path(normalized_path)
        self.terminal.set_working_directory(normalized_path)
        self.handlers.on_cursor_position_changed()

    def _open_file(self, file_path: str):
        """打开指定文件"""
        normalized_path = os.path.normpath(file_path)

        # 更新文件树的根目录为文件所在目录
        file_dir = os.path.dirname(normalized_path)
        get_config_service().update_file_config("source_code_path", file_dir)
        self.file_tree.set_root_path(file_dir)
        self.terminal.set_working_directory(file_dir)

        # 读取文件内容并创建标签页
        try:
            with open(normalized_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.tab_manager.create_new_tab(file_path=normalized_path, content=content)
            self.handlers.on_cursor_position_changed()
        except Exception as e:
            DialogUtils.show_error(self.main_window, "打开失败", f"无法打开文件：\n{normalized_path}\n错误：{e}", )

    def _setup_signals_and_slots(self):
        """设置信号与槽连接"""
        self.open_action.triggered.connect(self.handlers.on_open_directory)
        self.save_action.triggered.connect(self.handlers.on_save_file)
        self.save_as_action.triggered.connect(self.handlers.on_save_as_file)
        self.import_action.triggered.connect(import_file)
        self.find_action.triggered.connect(self.handlers.on_find_replace)
        self.run_action.triggered.connect(self.handlers.on_run_code)
        self.compile_action.triggered.connect(self.handlers.on_compile_code)
        self.website_action.triggered.connect(self.handlers.open_website)
        self.github_action.triggered.connect(self.handlers.open_github)
        self.author_github_action.triggered.connect(self.handlers.open_author_github)
        self.uninstall_action.triggered.connect(uninstall_program)
        self.reset_action.triggered.connect(reset_program)
        self.dark_mode_action.triggered.connect(self.handlers.on_dark_mode_changed)
        self.syntax_highlight_action.triggered.connect(self.handlers.on_syntax_highlight_changed)
        self.window_top_action.triggered.connect(self.handlers.on_window_top_changed)
        self.update_action.triggered.connect(self.handlers.open_website)
        self.tutorial_action.triggered.connect(self.handlers.open_tutorial)
        self.toggle_file_tree_action.toggled.connect(self.handlers.toggle_file_tree)
        self.toggle_terminal_action.toggled.connect(self.handlers.toggle_terminal)
        self.toggle_line_numbers_action.toggled.connect(self.handlers.toggle_line_numbers)
        self.pip_taobao_action.triggered.connect(self.handlers.on_pip_mirror_changed)
        self.hide_window_action.triggered.connect(self.handlers.on_hide_window_changed)
        self.admin_privilege_action.triggered.connect(self.handlers.on_admin_privilege_changed)
        self.single_file_action.triggered.connect(self.handlers.on_single_file_changed)
        self.add_data_action.triggered.connect(self.handlers.on_add_data_changed)
        self.compile_default_icon_action.triggered.connect(self.handlers.on_compile_default_icon_changed)
        self.compile_icon_action.triggered.connect(self.handlers.on_compile_icon_changed)
        self.file_tree.signals.file_selected.connect(self.handlers.on_file_tree_selected)
        code_signals.compile_log.connect(self.handlers.on_compile_log)

    def _setup_global_shortcuts(self, main_window):
        """使用 QShortcut 设置全局快捷键"""
        self._shortcuts = []

        shortcuts_map = [
            ("Ctrl+O", self.handlers.on_open_directory),
            ("Ctrl+S", self.handlers.on_save_file),
            ("Ctrl+Shift+S", self.handlers.on_save_as_file),
            ("Ctrl+I", import_file),
            ("Ctrl+F", self.handlers.on_find_replace),
            ("Ctrl+R", self.handlers.on_run_code),
            ("Ctrl+B", self.handlers.on_compile_code),
            ("Shift+Esc", self.handlers.toggle_file_tree_shortcut),
            ("Ctrl+`", self.handlers.toggle_terminal_shortcut),
        ]

        for key_seq, callback in shortcuts_map:
            shortcut = QShortcut(QKeySequence(key_seq), main_window)
            shortcut.activated.connect(callback)
            self._shortcuts.append(shortcut)

    def _init_menu_states(self):
        """初始化菜单项的选中状态"""
        self.handlers.init_menu_states()

    def _setup_auto_save(self):
        """设置自动保存功能"""
        # 自动保存由标签页管理器处理
        if self.main_window:
            self._window_focus_filter = WindowFocusFilter(self.handlers.auto_save)
            self.main_window.installEventFilter(self._window_focus_filter)

    def _setup_close_event(self, main_window):
        """设置窗口关闭事件，保存标签页状态"""
        original_close = main_window.closeEvent

        def new_close_event(event):
            self.tab_manager.save_tabs_state()
            self.handlers.auto_save()
            original_close(event)

        main_window.closeEvent = new_close_event

    def on_cursor_position_changed(self):
        """光标位置变化时的回调"""
        self.handlers.on_cursor_position_changed()


class GradientBackgroundWidget(QtWidgets.QWidget):
    """渐变背景容器"""

    def __init__(self, parent=None, gradient_colors=None, gradient_alpha=0.85):
        """
        初始化渐变背景容器
        
        Args:
            parent: 父窗口
            gradient_colors: 渐变色列表，默认 ["#667eea", "#764ba2", "#f093fb"]
            gradient_alpha: 渐变背景透明度 (0.0-1.0)，默认 0.85
        """
        super().__init__(parent)
        self._gradient_colors = gradient_colors or ["#667eea", "#764ba2", "#f093fb"]
        self._gradient_alpha = gradient_alpha

    def paintEvent(self, event):
        """绘制渐变背景"""
        paint_gradient(self, self._gradient_colors, self._gradient_alpha)
