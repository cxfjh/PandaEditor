import os
import shutil
import subprocess
import ctypes
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QMenu, QInputDialog, QMessageBox
from PySide6.QtCore import Signal, QObject, QThread, Qt
from PySide6.QtGui import QAction


# 需要过滤的大型目录
_IGNORED_DIRS = {
    '.git', '.svn', '.hg',
    '__pycache__', '.pytest_cache', '.mypy_cache', '.eggs',
    'node_modules', 'bower_components',
    '.venv', 'venv', 'env', '.tox',
    'dist', 'build', '.idea', '.vscode',
}


def _set_dark_title_bar(widget):
    """
    设置窗口标题栏为深色模式
    
    Args:
        widget: Qt 窗口部件
    """
    try:
        hwnd = int(widget.winId())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))  # type: ignore
    except Exception as e:
        print("设置深色模式失败:", str(e))
        try:
            hwnd = int(widget.winId())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int), )  # type: ignore
        except Exception as e:
            print("设置深色模式失败:", str(e))


def _should_ignore(name: str) -> bool:
    """
    判断是否应该忽略该目录/文件

    Args:
        name: 目录或文件名
        
    Returns:
        bool: True 表示应该忽略，False 表示应该显示
    """
    if name.startswith('.'): return True  # 隐藏文件/目录
    if name in _IGNORED_DIRS: return True  # 已知的大型目录
    if name.endswith('.egg-info'): return True  # Python 包信息目录
    return False


class DirectoryLoader(QThread):
    """
    异步目录加载线程

    Attributes:
        finished: 加载完成信号，携带父节点和子节点数据列表 [(name, path, is_dir), ...]
    """
    finished = Signal(object, list)

    def __init__(self, parent_item, parent_path):
        """
        初始化加载器

        Args:
            parent_item: 父树节点对象（QTreeWidgetItem）
            parent_path: 要扫描的目录路径
        """
        super().__init__()
        self._parent_item = parent_item
        self._parent_path = parent_path

    def run(self):
        """执行目录扫描"""
        dirs = []
        files = []
        try:
            if not os.path.isdir(self._parent_path):
                self.finished.emit(self._parent_item, [])
                return

            # 遍历目录内容
            for name in os.listdir(self._parent_path):
                if _should_ignore(name):
                    continue
                full_path = os.path.join(self._parent_path, name)
                if os.path.isdir(full_path):
                    dirs.append((name, full_path, True))
                else:
                    files.append((name, full_path, False))
        except (PermissionError, Exception) as e:
            print("目录目录扫描失败:", str(e))

        # 先文件夹后文件按名称字母排序
        dirs.sort(key=lambda x: x[0].lower())
        files.sort(key=lambda x: x[0].lower())
        self.finished.emit(self._parent_item, dirs + files)  # 发送结果到主线程


class FileTreeSignals(QObject):
    """文件树信号类"""
    file_selected = Signal(str)  # 文件路径


class FileTreeView(QWidget):
    """文件树视图组件"""

    # 文件类型 emoji 映射表
    _FILE_ICONS = {
        '.cn': '🐼',
        '.py': '🐍', '.pyw': '🐍',
        '.txt': '📄', '.md': '📝', '.json': '📋',
        '.yaml': '⚙️', '.yml': '⚙️', '.ini': '⚙️', '.toml': '⚙️', '.cfg': '⚙️', '.conf': '⚙️',
        '.csv': '📊', '.log': '📜', '.sh': '🐚', '.bat': '🐚', '.ps1': '🐚',
        '.ico': '🖼️', '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.bmp': '🖼️', '.webp': '🖼️', '.svg': '🎨',
        '.js': '🟨', '.ts': '🔷', '.html': '🌐', '.htm': '🌐', '.css': '🎨', '.xml': '📋',
        '.c': '🔹', '.cpp': '🔹', '.h': '🔹', '.hpp': '🔹', '.java': '☕', '.go': '🐹', '.rs': '🦀',
        '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦', '.gz': '📦', '.bz2': '📦',
        '.pdf': '📕', '.docx': '📘', '.doc': '📘', '.xlsx': '📗', '.xls': '📗', '.pptx': '📙', '.ppt': '📙',
        '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.mp4': '🎬', '.mkv': '🎬', '.avi': '🎬', '.ttf': '🔤', '.otf': '🔤',
    }

    _FOLDER_ICON = '📁'
    _DEFAULT_FILE_ICON = '📃'

    def __init__(self, parent=None):
        """
        初始化文件树视图

        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        self.signals = FileTreeSignals()  # 信号对象，用于发出文件选中事件
        self._root_path = ""  # 当前根目录路径
        self._loader = None  # 异步加载器引用
        self._dark_mode = True  # 默认深色主题
        self._setup_ui()

    def _setup_ui(self):
        """初始化 UI 布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 3, 0, 1)  # 极窄边距
        self.setStyleSheet("""QWidget#FileTreeView { background-color: #2b2d30; border: 1px solid #3c3f41; } """)
        self.setObjectName("FileTreeView")

        # 创建树形控件
        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)  # 隐藏表头
        self.tree.setAnimated(True)  # 启用展开/折叠动画
        self.tree.setIndentation(20)  # 缩进 20px
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # 启用自定义右键菜单

        # 连接信号
        self.tree.customContextMenuRequested.connect(self._on_context_menu)  # 右键菜单
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)  # 双击打开文件
        self.tree.itemExpanded.connect(self._on_item_expanded)  # 节点展开时加载子节点

        # 应用深色主题样式
        self.tree.setStyleSheet(
            """
                        QTreeWidget {
                            background-color: #2b2d30;
                            color: #A9B7C6;
                            border: none;
                        }
                        QTreeWidget::viewport {
                            background-color: #2b2d30;
                        }
                        QTreeWidget::item {
                            padding: 4px;
                        }
                        QTreeWidget::item:hover {
                            background-color: #323438;
                        }
                        QTreeWidget::item:selected {
                            background-color: #214283;
                        }
                    """,
        )

        layout.addWidget(self.tree)

    def apply_theme(self, dark_mode: bool):
        """
        应用主题样式

        Args:
            dark_mode: True 为暗夜模式，False 为浅色模式
        """
        if dark_mode:
            bg = "#2b2d30"
            fg = "#A9B7C6"
            hover_bg = "#323438"
            selected_bg = "#214283"
            border_color = "#3c3f41"
        else:
            bg = "#F0F0F0"
            fg = "#000000"
            hover_bg = "#E4E7EB"
            selected_bg = "#B4D7FF"
            border_color = "#D1D5DB"

        self._dark_mode = dark_mode
        self.setStyleSheet(
            f"""
            QWidget#FileTreeView {{ 
                background-color: {bg}; 
                border: 1px solid {border_color}; 
            }}
            QInputDialog {{
                background-color: #2b2d30;
                color: #A9B7C6;
            }}
            QInputDialog QLabel {{
                color: #A9B7C6;
            }}
            QInputDialog QLineEdit {{
                background-color: #323438;
                color: #A9B7C6;
                border: 1px solid #3c3f41;
                padding: 4px;
                border-radius: 3px;
            }}
            QInputDialog QPushButton {{
                background-color: #3c3f41;
                color: #A9B7C6;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }}
            QInputDialog QPushButton:hover {{
                background-color: #323438;
            }}
            QMessageBox {{
                background-color: #2b2d30;
                color: #A9B7C6;
            }}
            QMessageBox QLabel {{
                color: #A9B7C6;
            }}
            QMessageBox QPushButton {{
                background-color: #3c3f41;
                color: #A9B7C6;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #323438;
            }}
        """,
        )
        self.tree.setStyleSheet(
            f"""
            QTreeWidget {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-right: 1px solid {border_color};
            }}
            QTreeWidget::viewport {{
                background-color: {bg};
            }}
            QTreeWidget::item {{
                padding: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {hover_bg};
            }}
            QTreeWidget::item:selected {{
                background-color: {selected_bg};
            }}
        """,
        )

    def set_root_path(self, path: str):
        """
        设置根目录路径并初始化文件树
        
        Args:
            path: 根目录的完整路径
        """
        if not os.path.isdir(path): return
        self._root_path = path
        self.tree.clear()  # 清空现有树结构

        # 创建根节点
        root_name = os.path.basename(path) or path
        root_item = QTreeWidgetItem(self.tree, [root_name])
        root_item.setData(0, 0x0100, path)  # 存储路径数据
        root_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)  # 显示展开箭头
        self._load_children_async(root_item, path)  # 异步加载子节点

    def _load_children_async(self, parent_item, parent_path):
        """
        异步加载子节点
        
        Args:
            parent_item: 父树节点对象
            parent_path: 要加载的目录路径
        """
        # 如果已有加载器在运行，等待其完成
        if self._loader and self._loader.isRunning():
            self._loader.wait()

        # 创建新的加载器并启动
        self._loader = DirectoryLoader(parent_item, parent_path)
        self._loader.finished.connect(self._on_loader_finished, Qt.ConnectionType.UniqueConnection)
        self._loader.start()

    def _on_loader_finished(self, parent_item, children_data):
        """
        加载完成回调
        
        Args:
            parent_item: 父树节点
            children_data: 子节点数据列表 [(name, path, is_dir), ...]
        """
        for name, full_path, is_dir in children_data:
            child = QTreeWidgetItem(parent_item, [name])
            child.setData(0, 0x0100, full_path)  # 存储路径
            if is_dir:
                child.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                child.setText(0, f"{self._FOLDER_ICON} {name}")
            else:
                ext = os.path.splitext(name)[1].lower()
                icon = self._FILE_ICONS.get(ext, self._DEFAULT_FILE_ICON)  # type: ignore
                child.setText(0, f"{icon} {name}")

        self.tree.viewport().update()  # 刷新视图

    def _on_item_expanded(self, item: QTreeWidgetItem):
        """
        节点展开时加载子节点
        
        Args:
            item: 被展开的树节点
        """
        path = item.data(0, 0x0100)
        if not path or not os.path.isdir(path): return
        item.takeChildren()  # 清除占位子节点
        self._load_children_async(item, path)  # 异步加载真实子节点

    def _on_item_double_clicked(self, item: QTreeWidgetItem):
        """
        双击节点时发出文件选中信号
        
        Args:
            item: 被双击的树节点
        """
        path = item.data(0, 0x0100)
        if path and os.path.isfile(path):
            self.signals.file_selected.emit(path)  # 发出文件选中信号

    def _on_context_menu(self, pos):
        """
        右键菜单

        Args:
            pos: 鼠标点击位置
        """
        item = self.tree.itemAt(pos)
        if not item: return

        path = item.data(0, 0x0100)
        if not path: return

        # 类型断言
        assert isinstance(path, str)
        dir_path = path if os.path.isdir(path) else os.path.dirname(path)
        assert isinstance(dir_path, str)

        # 创建右键菜单
        menu = QMenu(self)
        if self._dark_mode:
            menu_bg = "#3c3f41"
            menu_fg = "#A9B7C6"
            menu_border = "#515356"
            menu_selected = "#214283"
            menu_separator = "#515356"
        else:
            menu_bg = "#FFFFFF"
            menu_fg = "#000000"
            menu_border = "#D1D5DB"
            menu_selected = "#B4D7FF"
            menu_separator = "#D1D5DB"
        menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: {menu_bg};
                color: {menu_fg};
                border: 1px solid {menu_border};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
                margin: 2px 4px;
            }}
            QMenu::item:selected {{
                background-color: {menu_selected};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {menu_separator};
                margin: 4px 8px;
            }}
            """,
        )

        # 新建文件
        new_file_action = QAction("新建文件", menu)
        new_file_action.triggered.connect(lambda: self._new_file(dir_path))
        menu.addAction(new_file_action)

        # 新建文件夹
        new_folder_action = QAction("新建文件夹", menu)
        new_folder_action.triggered.connect(lambda: self._new_folder(dir_path))
        menu.addAction(new_folder_action)
        menu.addSeparator()

        # 重命名
        rename_action = QAction("重命名", menu)
        rename_action.triggered.connect(lambda: self._rename_item(item, path))  # type: ignore[arg-type]
        menu.addAction(rename_action)

        # 删除
        delete_action = QAction("删除", menu)
        delete_action.triggered.connect(lambda: self._delete_item(item, path))  # type: ignore[arg-type]
        menu.addAction(delete_action)
        menu.addSeparator()

        # 在资源管理器中打开
        if os.path.exists(path):
            explorer_action = QAction("在资源管理器中打开", menu)
            explorer_action.triggered.connect(lambda: self._open_in_explorer(path))
            menu.addAction(explorer_action)
            menu.addSeparator()

        # 刷新
        refresh_action = QAction("刷新", menu)
        refresh_action.triggered.connect(lambda: self._refresh())
        menu.addAction(refresh_action)

        menu.exec(self.tree.mapToGlobal(pos))  # 在鼠标位置显示菜单

    def _show_input_dialog(self, title, label, default_text=""):
        """
        显示输入对话框
        
        Args:
            title: 对话框标题
            label: 提示文本
            default_text: 默认输入值
            
        Returns:
            用户输入的文本，如果取消则返回 None
        """
        dialog = QInputDialog(self)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextValue(default_text)
        _set_dark_title_bar(dialog)  # 应用深色标题栏
        ok = dialog.exec()
        return dialog.textValue().strip() if ok else None

    def _new_file(self, dir_path: str):
        """
        新建文件
        
        Args:
            dir_path: 文件所在目录路径
        """
        name = self._show_input_dialog("新建文件", "请输入文件名:")
        if not name:
            return
        file_path = os.path.join(dir_path, name)
        if os.path.exists(file_path):
            QMessageBox.warning(self, "警告", f"文件已存在:\n{file_path}")
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')  # 创建空文件
            self._refresh_parent(dir_path)  # 刷新父目录
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建文件失败:\n{e}")

    def _new_folder(self, dir_path: str):
        """新建文件夹"""
        name = self._show_input_dialog("新建文件夹", "请输入文件夹名:")
        if not name:
            return
        folder_path = os.path.join(dir_path, name)
        if os.path.exists(folder_path):
            QMessageBox.warning(self, "警告", f"文件夹已存在:\n{folder_path}")
            return
        try:
            os.makedirs(folder_path, exist_ok=True)
            self._refresh_parent(dir_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建文件夹失败:\n{e}")

    def _rename_item(self, item: QTreeWidgetItem, old_path: str):
        """重命名文件或文件夹"""
        old_name = os.path.basename(old_path)
        new_name = self._show_input_dialog("重命名", "请输入新名称:", old_name)
        if not new_name or new_name == old_name:
            return
        new_path = os.path.join(os.path.dirname(old_path), new_name)  # type: ignore
        if os.path.exists(new_path):
            QMessageBox.warning(self, "警告", f"已存在同名文件/文件夹:\n{new_path}")
            return
        try:
            os.rename(old_path, new_path)
            item.setText(0, new_name)  # type: ignore
            item.setData(0, 0x0100, new_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重命名失败:\n{e}")

    def _delete_item(self, item: QTreeWidgetItem, path: str):
        """
        删除文件或文件夹
        
        Args:
            item: 树节点对象
            path: 要删除的文件/文件夹路径
        """
        name = os.path.basename(path)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {'文件夹' if os.path.isdir(path) else '文件'} 吗?\n{name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            # 删除文件系统内容
            if os.path.isdir(path):
                shutil.rmtree(path)  # 递归删除目录
            else:
                os.remove(path)  # 删除文件

            # 从树控件中移除节点
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                self.tree.invisibleRootItem().removeChild(item)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败:\n{e}")

    def _open_in_explorer(self, path: str):
        """
        在资源管理器中打开文件或文件夹

        Args:
            path: 文件或文件夹路径
        """
        try:
            if os.path.isfile(path):
                # 打开文件所在目录并选中文件
                subprocess.Popen(f'explorer /select,"{path}"')
            else:
                # 打开文件夹
                os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开资源管理器失败:\n{e}")

    def _refresh_parent(self, dir_path: str):
        """
        刷新父目录（新建/重命名/删除后调用）
        
        Args:
            dir_path: 要刷新的目录路径
        """

        # 递归查找对应路径的树节点
        def find_item_by_path(item, path):
            item_path = item.data(0, 0x0100)
            if item_path == path:
                return item
            for i in range(item.childCount()):
                result = find_item_by_path(item.child(i), path)
                if result:
                    return result
            return None

        root_item = self.tree.topLevelItem(0)
        if not root_item:
            return

        parent_item = find_item_by_path(root_item, dir_path)
        if not parent_item:
            return

        # 清除所有子节点并重新加载
        parent_item.takeChildren()
        parent_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
        self._load_children_async(parent_item, dir_path)

    def _refresh(self):
        """刷新整个文件树"""
        if not self._root_path: return
        self.tree.clear()
        root_name = os.path.basename(self._root_path) or self._root_path
        root_item = QTreeWidgetItem(self.tree, [root_name])
        root_item.setData(0, 0x0100, self._root_path)
        root_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
        self._load_children_async(root_item, self._root_path)
