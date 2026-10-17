from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from src.utils.extend import paint_gradient


class CustomTitleBar(QWidget):
    """自定义标题栏组件"""

    minimize_clicked = Signal()  # 最小化信号
    maximize_clicked = Signal()  # 最大化/还原信号
    close_clicked = Signal()  # 关闭信号

    def __init__(self, title="熊猫编辑器", parent=None, gradient_colors=None, fg_color="#FFFFFF", gradient_alpha=0.85):
        """
        初始化自定义标题栏
        
        Args:
            title: 窗口标题
            parent: 父窗口
            gradient_colors: 渐变色列表，如 ["#667eea", "#764ba2"]（不含 alpha）
            fg_color: 文字颜色
            gradient_alpha: 渐变背景透明度 (0.0-1.0)，默认 0.85
        """
        super().__init__(parent)
        self._drag_pos = None  # 拖拽偏移量
        self._gradient_colors = gradient_colors or ["#667eea", "#764ba2"]  # 默认渐变色
        self._fg_color = fg_color
        self._gradient_alpha = gradient_alpha
        self._is_maximized = False  # 最大化状态
        self._menu_bar = None  # 菜单栏引用

        # 启用半透明背景融合效果
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)  # 禁用系统默认背景
        self.setAutoFillBackground(False)  # 禁用自动填充背景
        self._setup_ui(title)

    def _setup_ui(self, title):
        """初始化 UI 布局"""
        self.setFixedHeight(40)  # 固定标题栏高度
        self.setObjectName("CustomTitleBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 无边距
        layout.setSpacing(0)  # 无间距

        # 标题标签
        self.title_label = _DraggableWidget()  # 使用可拖拽容器包裹标题
        self.title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {self._fg_color};
                font-size: 13px;
                font-weight: bold;
                padding-left: 12px;
                background: transparent;
            }}
        """,
        )
        # 添加标签文字
        title_label_inner = QLabel(title)
        title_label_inner.setStyleSheet(
            f"""
            QLabel {{
                color: {self._fg_color};
                font-size: 13px;
                font-weight: bold;
                padding-left: 12px;
                background: transparent;
            }}
        """,
        )
        title_label_inner.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)  # 垂直居中，左对齐
        title_layout = QHBoxLayout(self.title_label)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.addWidget(title_label_inner)
        layout.addWidget(self.title_label, 0)  # stretch=0，固定大小

        # 菜单栏容器
        self.menu_container = QWidget()
        self.menu_container.setStyleSheet("background: transparent;")  # 透明背景
        self.menu_layout = QHBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(8, 2, 0, 0)
        self.menu_layout.setSpacing(0)
        layout.addWidget(self.menu_container, 0)  # stretch=0，固定大小

        # 空白拖拽区域
        self.drag_area = _DraggableWidget()
        self.drag_area.setStyleSheet("background: transparent;")
        layout.addWidget(self.drag_area, 1)  # stretch=1，占据剩余空间

        # 最小化按钮
        self.min_btn = QPushButton("─")
        self._setup_button_style(self.min_btn)
        self.min_btn.setToolTip("最小化")
        self.min_btn.clicked.connect(self.minimize_clicked.emit)  # 连接最小化信号
        layout.addWidget(self.min_btn)

        # 最大化/还原按钮
        self.max_btn = QPushButton("□")
        self._setup_button_style(self.max_btn)
        self.max_btn.setToolTip("最大化")
        self.max_btn.clicked.connect(self._on_maximize)  # 连接内部处理方法
        layout.addWidget(self.max_btn)

        # 关闭按钮
        self.close_btn = QPushButton("✕")
        self._setup_button_style(self.close_btn, is_close=True)  # 关闭按钮特殊样式
        self.close_btn.setToolTip("关闭")
        self.close_btn.clicked.connect(self.close_clicked.emit)  # 连接关闭信号
        layout.addWidget(self.close_btn)

    def _setup_button_style(self, btn, is_close=False):
        """
        设置按钮样式
        
        Args:
            btn: QPushButton 实例
            is_close: 是否为关闭按钮（关闭按钮悬停时为红色）
        """
        hover_color = "#E81123" if is_close else "rgba(255, 255, 255, 0.2)"  # 关闭按钮悬停红色，其他按钮半透明白色
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent; 
                border: none;
                color: {self._fg_color};
                font-size: 16px;
                font-weight: bold;
                min-width: 45px;
                max-width: 45px;
                min-height: 40px;
                max-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};  
            }}
        """,
        )

    def set_menu_bar(self, menu_bar):
        """
        设置菜单栏 - 将菜单栏集成到标题栏中
        
        Args:
            menu_bar: QMenuBar 实例
        """
        self._menu_bar = menu_bar
        # 设置菜单栏透明背景
        menu_bar.setStyleSheet(
            """
            QMenuBar {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                padding: 0;
                spacing: 0;
            }
            QMenuBar::item {
                padding: 8px 12px;
                background-color: transparent;
                border-radius: 4px;
                margin: 2px 4px;
                color: #FFFFFF;
            }
            QMenuBar::item:selected {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QMenuBar::item:pressed {
                background-color: rgba(255, 255, 255, 0.3);  
            }
            QMenu {
                background-color: #2b2d30;
                color: #A9B7C6;
                border: 1px solid #3c3f41;
                border-radius: 6px;
                padding: 4px 0;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QMenu::item:selected {
                background-color: #214283;
            }
            QMenu::separator {
                height: 1px;
                background-color: #515356;
                margin: 4px 8px;
            }
            """,
        )
        self.menu_layout.addWidget(menu_bar)  # 将菜单栏添加到标题栏布局中

    def _on_maximize(self):
        """最大化/还原按钮点击处理"""
        self._is_maximized = not self._is_maximized  # 切换状态
        self.max_btn.setText("❐" if self._is_maximized else "□")  # 更新图标
        self.max_btn.setToolTip("还原" if self._is_maximized else "最大化")  # 更新提示
        self.maximize_clicked.emit()  # 发射信号

    def set_title(self, title):
        """
        设置标题文字
        
        Args:
            title: 新标题文字
        """
        inner_label = self.title_label.layout().itemAt(0).widget()  # type: ignore
        if isinstance(inner_label, QLabel):
            inner_label.setText(title)

    def mouseDoubleClickEvent(self, event):
        """
        双击标题栏最大化/还原
        
        Args:
            event: QMouseEvent 实例
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_maximize()

    def mousePressEvent(self, event):
        """
        鼠标按下事件 - 用于拖拽窗口
        
        Args:
            event: QMouseEvent 实例
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击在按钮上
            child = self.childAt(event.pos())
            if child and isinstance(child, QPushButton):
                return  # 点击在按钮上，不拖拽

            # 计算偏移量 = 鼠标全局位置 - 窗口左上角位置
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件 - 用于拖拽窗口

        Args:
            event: QMouseEvent 实例
        """
        if hasattr(self, '_drag_pos') and self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)  # 移动窗口
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件 - 清除拖拽状态
        
        Args:
            event: QMouseEvent 实例
        """
        if hasattr(self, '_drag_pos'):
            self._drag_pos = None  # 清除偏移量
        event.accept()

    def paintEvent(self, event):
        """
        绘制半透明渐变背景

        Args:
            event: QPaintEvent 实例
        """
        paint_gradient(self, self._gradient_colors, self._gradient_alpha)


class _DraggableWidget(QWidget):
    """支持拖拽的空白容器"""

    def __init__(self, parent=None):
        """
        初始化可拖拽容器
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        self._drag_pos = None  # 拖拽偏移量

    def mousePressEvent(self, event):
        """
        鼠标按下事件 - 用于拖拽窗口
        
        Args:
            event: QMouseEvent 实例
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击在按钮上
            child = self.childAt(event.pos())
            if child and isinstance(child, QPushButton):
                return  # 点击在按钮上，不拖拽

            # 计算偏移量 = 鼠标全局位置 - 窗口左上角位置
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件 - 用于拖拽窗口
        
        Args:
            event: QMouseEvent 实例
        """
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)  # 移动窗口
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件 - 清除拖拽状态
        
        Args:
            event: QMouseEvent 实例
        """
        self._drag_pos = None  # 清除偏移量
        event.accept()
