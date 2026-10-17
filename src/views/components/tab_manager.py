import os
from typing import Dict, Optional
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFont
from src.utils.config_service import get_config_service
from src.views.components.editor import CodeEditor
from src.views.components.find_replace import FindReplaceDialog
from src.views.components.event_filters import FontSizeFilter
from src.utils.syntax_hint import SyntaxHintManager
from src.utils.syntax_high import ChineseHighlighter
from src.utils.dialog_utils import DialogUtils


class TabData:
    """单个标签页的数据容器"""

    def __init__(self, file_path: Optional[str] = None):
        """
        初始化标签页数据
        
        Args:
            file_path: 文件路径（None 表示新建未命名文件）
        """
        self.file_path = file_path  # 文件完整路径
        self.has_unsaved_changes = False  # 是否有未保存的修改
        self.editor: Optional[CodeEditor] = None  # 代码编辑器实例
        self.highlighter: Optional[ChineseHighlighter] = None  # 语法高亮器
        self.syntax_hint = None  # 语法补全管理器
        self.find_replace_dialog: Optional[FindReplaceDialog] = None  # 查找替换对话框
        self.font_filter = None  # 字体大小事件过滤器


class TabManager(QtCore.QObject):
    """标签页管理器"""

    # 信号定义
    tab_changed = QtCore.Signal()  # 标签页切换或光标位置变化时触发
    tab_count_changed = QtCore.Signal(int)  # 标签页数量变化时触发

    def __init__(self, tab_widget: QtWidgets.QTabWidget, parent=None):
        """
        初始化标签页管理器
        
        Args:
            tab_widget: QTabWidget 实例（UI 标签页组件）
            parent: 父对象
        """
        super().__init__(parent)
        self.tab_widget = tab_widget
        self.tab_data_map: Dict[int, TabData] = { }  # 标签索引 -> TabData 映射表
        self._dark_mode = True  # 默认深色主题
        self._font_size = 25  # 默认字体大小
        self._syntax_highlight = True  # 默认启用语法高亮
        self._max_tabs = 12  # 最大标签页数量限制

        # 设置标签页样式
        self._setup_tab_style()

        # 连接信号
        self.tab_widget.currentChanged.connect(self._on_tab_changed)  # 标签切换信号
        self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)  # 关闭标签信号

    @property
    def dark_mode(self) -> bool:
        """获取当前是否为深色模式"""
        return self._dark_mode

    def _setup_tab_style(self):
        """设置标签页样式"""
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #2b2d30;
                color: #A9B7C6;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e1f22;
                border-bottom: 2px solid #569CDE;
            }
            QTabBar::tab:hover {
                background-color: #3c3f41;
            }
            """,
        )
        self.tab_widget.setTabsClosable(True)  # 显示关闭按钮
        self.tab_widget.setMovable(True)  # 允许拖拽排序

    def create_new_tab(self, file_path: Optional[str] = None, content: str = "") -> int:
        """
        创建新标签页
        
        Args:
            file_path: 文件路径（可选，None 表示新建未命名文件）
            content: 初始内容（默认空字符串）
            
        Returns:
            新标签页的索引
        """
        # 检查文件是否已经打开
        if file_path:
            for index, tab_data in self.tab_data_map.items():
                if tab_data.file_path == file_path:
                    self.tab_widget.setCurrentIndex(index)  # 切换到已打开的标签页
                    return index

        # 如果标签页数量达到上限，关闭第一个标签页
        while self.tab_widget.count() >= self._max_tabs:
            self._on_tab_close_requested(0)

        # 创建代码编辑器实例
        editor = CodeEditor(parent=self.tab_widget, dark_mode=self._dark_mode)
        editor.setFont(QFont("Sarasa Mono SC", self._font_size))  # 更纱黑体
        editor.setPlainText(content)
        editor.setTabChangesFocus(False)  # Tab 键不切换焦点
        editor.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)  # 禁用自动换行

        # 设置编辑器样式（确保初始颜色正确）
        if self._dark_mode:
            editor.setStyleSheet("background-color: #1e1f22; color: #A9B7C6; selection-background-color: #214283;")
        else:
            editor.setStyleSheet("background-color: #FFFFFF; color: #000000; selection-background-color: #B4D7FF;")

        # 创建标签页数据容器
        tab_data = TabData(file_path)
        tab_data.editor = editor

        # 安装字体大小过滤器
        font_filter = FontSizeFilter(editor)
        editor.installEventFilter(font_filter)
        tab_data.font_filter = font_filter

        # 只为 .cn 文件创建语法高亮器
        is_cn_file = file_path and file_path.endswith('.cn')
        if self._syntax_highlight and is_cn_file:
            tab_data.highlighter = ChineseHighlighter(editor.document(), editor, self._dark_mode)
            tab_data.highlighter._current_file = file_path

        # 创建查找替换对话框
        tab_data.find_replace_dialog = FindReplaceDialog(editor, parent=self.tab_widget, dark_mode=self._dark_mode)

        # 为 .cn 文件创建语法补全管理器
        if is_cn_file:
            tab_data.syntax_hint = SyntaxHintManager(editor, dark_mode=self._dark_mode)
            tab_data.syntax_hint.set_current_file(file_path)

        # 添加标签页到 UI 组件
        tab_name = self._get_tab_name(file_path)
        tab_index = self.tab_widget.addTab(editor, tab_name)
        self.tab_data_map[tab_index] = tab_data  # 建立索引到数据的映射

        # 设置当前标签页为新创建的
        self.tab_widget.setCurrentIndex(tab_index)

        # 连接编辑器信号
        editor.cursorPositionChanged.connect(self._on_cursor_position_changed)  # 光标移动
        editor.textChanged.connect(self._on_text_changed)  # 文本修改

        self.tab_count_changed.emit(self.tab_widget.count())  # 发出数量变化信号
        return tab_index

    def get_current_tab_data(self) -> Optional[TabData]:
        """获取当前标签页数据"""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return None
        return self.tab_data_map.get(current_index)

    def get_current_editor(self) -> Optional[CodeEditor]:
        """获取当前标签页的编辑器"""
        tab_data = self.get_current_tab_data()
        if tab_data:
            return tab_data.editor
        return None

    def get_current_file_path(self) -> Optional[str]:
        """获取当前标签页的文件路径"""
        tab_data = self.get_current_tab_data()
        if tab_data:
            return tab_data.file_path
        return None

    def set_current_file_path(self, file_path: str):
        """设置当前标签页的文件路径"""
        tab_data = self.get_current_tab_data()
        if tab_data:
            tab_data.file_path = file_path
            self._update_tab_title(self.tab_widget.currentIndex())

    def mark_current_tab_modified(self, modified: bool = True):
        """标记当前标签页为已修改"""
        tab_data = self.get_current_tab_data()
        if tab_data:
            tab_data.has_unsaved_changes = modified
            self._update_tab_title(self.tab_widget.currentIndex())

    def is_current_tab_modified(self) -> bool:
        """检查当前标签页是否有未保存的修改"""
        tab_data = self.get_current_tab_data()
        if tab_data:
            return tab_data.has_unsaved_changes
        return False

    def close_tab(self, index: int) -> bool:
        """
        关闭指定标签页

        Args:
            index: 标签页索引
            
        Returns:
            是否成功关闭（用户取消则返回 False）
        """
        if index < 0 or index >= self.tab_widget.count():
            return False

        tab_data = self.tab_data_map.get(index)
        if tab_data and tab_data.has_unsaved_changes:
            # 弹出保存提示对话框
            reply = QtWidgets.QMessageBox.question(
                self.tab_widget,
                "保存文件",
                f"文件 '{self._get_tab_name(tab_data.file_path)}' 尚未保存，是否保存？",
                QtWidgets.QMessageBox.StandardButton.Save |
                QtWidgets.QMessageBox.StandardButton.Discard |
                QtWidgets.QMessageBox.StandardButton.Cancel,
            )

            if reply == QtWidgets.QMessageBox.StandardButton.Save:
                if not self._save_tab(index):  # 保存失败则取消关闭
                    return False
            elif reply == QtWidgets.QMessageBox.StandardButton.Cancel:
                return False  # 用户取消操作

        # 从 UI 中移除标签页
        self.tab_widget.removeTab(index)
        if index in self.tab_data_map:
            del self.tab_data_map[index]

        # 重新映射索引
        self._remap_tab_data()

        self.tab_count_changed.emit(self.tab_widget.count())
        return True

    def close_all_tabs(self):
        """关闭所有标签页"""
        while self.tab_widget.count() > 0:
            if not self.close_tab(0):
                break

    def apply_theme(self, dark_mode: bool):
        """
        应用主题到所有标签页
        
        Args:
            dark_mode: True=深色主题，False=浅色主题
        """
        self._dark_mode = dark_mode
        for tab_data in self.tab_data_map.values():
            if tab_data.editor:
                tab_data.editor.set_dark_mode(dark_mode)  # 更新编辑器内部主题状态
                if dark_mode:
                    tab_data.editor.setStyleSheet("background-color: #1e1f22; color: #A9B7C6; selection-background-color: #214283;")
                else:
                    tab_data.editor.setStyleSheet("background-color: #FFFFFF; color: #000000; selection-background-color: #B4D7FF;")

            if tab_data.highlighter:
                tab_data.highlighter.update_theme(dark_mode)  # 更新语法高亮主题

    def apply_font_size(self, font_size: int):
        """应用字体大小到所有标签页"""
        self._font_size = font_size
        for tab_data in self.tab_data_map.values():
            if tab_data.editor:
                tab_data.editor.setFont(QFont("Sarasa Mono SC", font_size))

    def toggle_syntax_highlight(self, enable: bool):
        """
        切换语法高亮
        
        Args:
            enable: True=启用，False=禁用
        """
        self._syntax_highlight = enable
        for tab_data in self.tab_data_map.values():
            if tab_data.editor and tab_data.file_path and tab_data.file_path.endswith('.cn'):
                if enable and not tab_data.highlighter:
                    # 启用高亮：创建新的语法高亮器
                    tab_data.highlighter = ChineseHighlighter(tab_data.editor.document(), tab_data.editor, self._dark_mode)
                    tab_data.highlighter._current_file = tab_data.file_path
                elif not enable and tab_data.highlighter:
                    # 禁用高亮：断开文档关联并销毁高亮器
                    tab_data.highlighter.setDocument(None)
                    tab_data.highlighter = None

    def toggle_line_numbers(self, show: bool):
        """切换行号显示"""
        for tab_data in self.tab_data_map.values():
            if tab_data.editor:
                tab_data.editor.set_show_line_numbers(show)

    def save_tabs_state(self):
        """保存当前标签页状态到配置"""
        tabs_info = []
        for index in range(self.tab_widget.count()):
            tab_data = self.tab_data_map.get(index)
            if tab_data:
                # 读取当前编辑器内容
                content = ""
                if tab_data.editor:
                    content = tab_data.editor.toPlainText()

                tabs_info.append(
                    {
                        "file_path": tab_data.file_path or "",
                        "content": content,
                        "has_unsaved": tab_data.has_unsaved_changes,
                    },
                )

        # 保存到会话配置
        get_config_service().update_session_config("last_tabs", tabs_info)
        get_config_service().update_session_config("last_active_tab", self.tab_widget.currentIndex())

    def restore_tabs_state(self):
        """从配置恢复上次打开的标签页"""
        tabs_info = get_config_service().get_session_config("last_tabs") or []
        last_active_tab = get_config_service().get_session_config("last_active_tab") or 0

        if not tabs_info:
            return

        # 清空现有标签页和数据映射
        self.tab_widget.clear()
        self.tab_data_map.clear()

        # 逐个恢复标签页
        for tab_info in tabs_info:
            file_path = tab_info.get("file_path") or None
            content = tab_info.get("content", "")

            # 如果有文件路径且文件存在，优先读取文件内容
            if file_path and os.path.exists(file_path):  # type: ignore
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:  # type: ignore
                        content = f.read()
                except Exception as e:
                    print(f"读取文件 {file_path} 失败：{e}")

            self.create_new_tab(file_path=file_path, content=content)  # type: ignore

        # 恢复上次激活的标签页
        if 0 <= last_active_tab < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(last_active_tab)

    def _on_tab_changed(self):
        """标签页切换时的回调"""
        tab_data = self.get_current_tab_data()
        if tab_data and tab_data.file_path:
            file_dir, file_name = os.path.split(tab_data.file_path)
            base_name, file_ext = os.path.splitext(file_name)
            get_config_service().update_file_config("code_name", base_name)
            get_config_service().update_file_config("file_ext", file_ext)

        self.tab_changed.emit()

    def _on_tab_close_requested(self, index: int):
        """
        关闭标签页请求
        
        Args:
            index: 要关闭的标签页索引
        """
        self.close_tab(index)

    def _on_cursor_position_changed(self):
        """光标位置变化时发出信号"""
        self.tab_changed.emit()

    def _on_text_changed(self):
        """文本内容变化时标记为已修改"""
        self.mark_current_tab_modified(True)

    def _save_tab(self, index: int) -> bool:
        """
        保存指定标签页到文件
        
        Args:
            index: 标签页索引
            
        Returns:
            是否保存成功
        """
        tab_data = self.tab_data_map.get(index)
        if not tab_data or not tab_data.editor:
            return False

        if not tab_data.file_path:
            return False  # 未命名文件无法保存

        try:
            content = tab_data.editor.toPlainText()
            with open(tab_data.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            tab_data.has_unsaved_changes = False  # 清除修改标记
            self._update_tab_title(index)  # 更新标题
            return True
        except Exception as e:
            DialogUtils.show_error(self.tab_widget, "保存失败", f"保存文件出错：\n{e}")
            return False

    def _update_tab_title(self, index: int):
        """
        更新标签页标题
        
        Args:
            index: 标签页索引
        """
        tab_data = self.tab_data_map.get(index)
        if tab_data:
            tab_name = self._get_tab_name(tab_data.file_path)
            if tab_data.has_unsaved_changes:
                tab_name += " *"  # 未保存文件添加 * 标记
            self.tab_widget.setTabText(index, tab_name)

    @staticmethod
    def _get_tab_name(file_path: Optional[str]) -> str:
        """
        获取标签页名称
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件名或"未命名"
        """
        if not file_path:
            return "未命名"
        return os.path.basename(file_path)

    def _remap_tab_data(self):
        """重新映射标签页数据"""
        new_map = { }
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            # 查找与该编辑器组件对应的 TabData
            for old_index, tab_data in self.tab_data_map.items():
                if tab_data.editor == widget:
                    new_map[i] = tab_data
                    break
        self.tab_data_map = new_map
