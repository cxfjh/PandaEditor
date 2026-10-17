from typing import List, Optional, Set, cast
from PySide6.QtCore import QEvent, QObject, QStringListModel, QThread, QTimer, Qt, Signal
from PySide6.QtGui import QInputMethodEvent, QKeyEvent, QTextCursor
from PySide6.QtWidgets import QCompleter, QPlainTextEdit
from src.module.builtin_map import builtin
from src.module.keyword_map import keyword
from src.module.lib_map import lib
from src.module.stdlib_map import stdlib
from src.module.method_map import method


class FilterWorker(QObject):
    """后台过滤线程"""
    resultReady = Signal(list, str)  # 信号：匹配结果列表, 当前前缀

    def __init__(self, all_items: List[str]):
        """
        初始化过滤工作器
        
        Args:
            all_items: 所有候选词列表（完整词库）
        """
        super().__init__()
        self.all_items = all_items
        self._last_prefix = ""  # 上一次过滤的前缀

    def filter_items(self, prefix: str):
        """
        执行过滤逻辑 - 根据前缀匹配候选词
        
        Args:
            prefix: 用户输入的前缀字符串
        """
        if not prefix:
            self.resultReady.emit([], prefix)  # 空前缀返回空列表
            return
        if prefix == self._last_prefix: return  # 相同前缀不重复过滤
        self._last_prefix = prefix
        prefix_lower = prefix.lower()
        matched = [item for item in self.all_items if prefix_lower in item.lower()]  # 包含匹配
        self.resultReady.emit(matched, prefix)  # 发射结果到主线程


class SyntaxCompleter(QCompleter):
    """自定义补全器 - 增强型代码补全弹出框"""

    def __init__(self, parent=None, dark_mode=True):
        """
        初始化自定义补全器
        
        Args:
            parent: 父控件
            dark_mode: 是否使用深色模式，默认为 True
        """
        super().__init__(parent)
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)  # 弹出式补全模式
        self.setFilterMode(Qt.MatchFlag.MatchContains)  # 包含匹配（非前缀匹配）
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # 不区分大小写
        self._dark_mode = dark_mode

        # 获取弹出框并应用主题样式
        popup = self.popup()
        assert popup is not None
        self._apply_theme(popup, dark_mode)

    @staticmethod
    def _apply_theme(popup, dark_mode: bool):
        """
        应用主题样式到补全弹出框
        
        Args:
            popup: QListView 实例（补全弹出框）
            dark_mode: True 为深色主题，False 为浅色主题
        """
        if dark_mode:
            # 深色主题
            popup.setStyleSheet(
                """
                QListView {
                    background-color: #3c3f41;  
                    color: #A9B7C6; 
                    border: 1px solid #515356;  
                    border-radius: 6px; 
                    padding: 4px;
                    min-width: 180px;
                    max-height: 420px;
                    font-size: 16px;
                    outline: 0;
                }
                QListView::item { padding: 6px 12px; border-radius: 4px; margin: 2px 0; }
                QListView::item:selected { background-color: #214283; color: #A9B7C6; } 
                QListView::item:hover:not(:selected) { background-color: #4e5254; }
                QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
                QScrollBar::handle:vertical { background: #515356; border-radius: 4px; min-height: 20px; }
                QScrollBar::handle:vertical:hover { background: #636669; }
                QScrollBar::addLine:vertical, QScrollBar::subLine:vertical { height: 0; }  
                """,
            )
        else:
            # 浅色主题
            popup.setStyleSheet(
                """
                QListView {
                    background-color: #FFFFFF;  
                    color: #000000; 
                    border: 1px solid #D1D5DB;  
                    border-radius: 6px;
                    padding: 4px;
                    min-width: 180px;
                    max-height: 420px;
                    font-size: 16px;
                    outline: 0;
                }
                QListView::item { padding: 6px 12px; border-radius: 4px; margin: 2px 0; }
                QListView::item:selected { background-color: #B4D7FF; color: #000000; }  
                QListView::item:hover:not(:selected) { background-color: #E4E7EB; } 
                QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
                QScrollBar::handle:vertical { background: #D1D5DB; border-radius: 4px; min-height: 20px; }
                QScrollBar::handle:vertical:hover { background: #9CA3AF; }
                QScrollBar::addLine:vertical, QScrollBar::subLine:vertical { height: 0; }  
                """,
            )

    def update_theme(self, dark_mode: bool):
        """
        更新补全弹出框主题
        
        Args:
            dark_mode: True 为深色主题，False 为浅色主题
        """
        self._dark_mode = dark_mode
        popup = self.popup()
        if popup:
            self._apply_theme(popup, dark_mode)


class SyntaxHintManager(QObject):
    """语法提示管理器 - 代码自动补全核心管理器"""

    def __init__(self, text_edit: QPlainTextEdit, dark_mode=True):
        """
        初始化语法提示管理器
        
        Args:
            text_edit: QPlainTextEdit 实例，需要补全功能的编辑器
            dark_mode: 是否使用深色模式，默认为 True
        """
        super().__init__(parent=text_edit)
        self.text_edit = text_edit
        self._dark_mode = dark_mode
        if not self.text_edit: return

        # 创建自定义补全器
        self.completer = SyntaxCompleter(text_edit, dark_mode)
        self.completer.setWidget(text_edit)  # 设置补全器关联的控件
        self.completer.activated.connect(self.insert_completion)  # 连接补全选中信号
        popup = self.completer.popup()
        assert popup is not None
        popup.installEventFilter(self)  # 安装事件过滤器

        # 防抖计时器
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)  # 单次触发
        self._debounce_timer.setInterval(150)  # 150ms 延迟
        self._debounce_timer.timeout.connect(self._do_request_completion)  # 超时后请求补全

        # 监听编辑器输入事件
        self.text_edit.installEventFilter(self)

        # 定义触发字符集
        self.base_trigger: Set[str] = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789")  # 字母数字下划线
        self.chinese_punctuation: Set[str] = set('，。、；：？！"\'""（）【】《》@*')  # 中文标点

        # 缓存
        self._current_file: Optional[str] = None  # 当前文件路径
        self._popup_min_width: Optional[int] = None  # 补全框最小宽度

        # 初始化候选数据
        self._init_completion_data()

    def _init_completion_data(self):
        """一次性加载补全数据，并开启后台线程"""
        items = set()
        items.update(keyword.keys())  # 关键字
        items.update(builtin.keys())  # 内置函数
        items.update(method.keys())  # 方法
        items.update(lib.keys())  # 库
        items.update(stdlib.keys())  # 标准库

        # 排序并去重
        all_items = sorted(items, key=lambda x: (-len(x), x))
        self.all_items = all_items

        # 启动后台线程
        self._thread = QThread()
        self.worker = FilterWorker(all_items)
        self.worker.moveToThread(self._thread)  # 将工作器移到线程
        self.worker.resultReady.connect(self._update_completion)  # 连接结果信号
        self._thread.start()

    def cleanup(self):
        """清理资源 - 安全退出后台线程"""
        if hasattr(self, '_thread') and self._thread.isRunning():
            self._thread.quit()  # 请求退出线程
            self._thread.wait()  # 等待线程退出

    def _get_current_word(self) -> str:
        """
        获取光标前的当前单词

        Returns:
            str: 光标前的单词字符串
        """
        cursor = self.text_edit.textCursor()
        block_text = cursor.block().text()[:cursor.positionInBlock()]  # 当前行光标前的文本
        chars = []
        for char in reversed(block_text):
            # 判断是否为有效字符
            if char in self.base_trigger or '\u4e00' <= char <= '\u9fff' or char in self.chinese_punctuation:
                chars.append(char)
            else:
                break
        return "".join(reversed(chars))  # 反转回原顺序

    def insert_completion(self, completion: str):
        """
        插入补全内容到编辑器
        
        Args:
            completion: 补全候选词
        """
        if not completion: return
        cursor = self.text_edit.textCursor()
        word = self._get_current_word()
        if word == completion: return  # 已完整输入，无需补全
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, len(word))  # 选中当前单词
        cursor.insertText(completion)  # 替换为补全内容
        self.text_edit.setTextCursor(cursor)

    def show_completion(self):
        """触发防抖计时器"""
        self._debounce_timer.start(200)

    def _do_request_completion(self):
        """请求后台线程过滤数据 - 获取当前前缀并发送过滤请求"""
        prefix = self._get_current_word()
        self.worker.filter_items(prefix)

    def _update_completion(self, matched: List[str], prefix: str):
        """
        主线程更新 UI 显示补全结果

        Args:
            matched: 匹配结果列表（来自后台线程）
            prefix: 当前前缀
        """
        if not prefix:
            popup = self.completer.popup()
            assert popup is not None
            popup.hide()  # 空前缀隐藏补全框
            return
        if prefix != self._get_current_word(): return  # 前缀已变化，忽略过期结果

        # 更新模型
        model = QStringListModel(matched, self.completer)
        self.completer.setModel(model)
        self.completer.setCompletionPrefix(prefix)

        # 定位补全框
        rect = self.text_edit.cursorRect()
        rect.translate(0, self.text_edit.fontMetrics().height() * 2)

        # 只计算一次补全框宽度
        if self._popup_min_width is None:
            popup = self.completer.popup()
            assert popup is not None
            self._popup_min_width = max(200, popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width())

        rect.setWidth(self._popup_min_width or rect.width())
        self.completer.complete(rect)  # 显示补全框

    def set_current_file(self, file_path: Optional[str]) -> None:
        """
        设置当前文件路径，用于判断是否为 .cn 文件
        
        Args:
            file_path: 当前编辑的文件路径
        """
        self._current_file = file_path

    def _should_complete(self) -> bool:
        """
        检查是否应该启用补全

        Returns:
            bool: True 表示启用补全，False 表示禁用
        """
        if not self._current_file:
            return True  # 无文件路径时默认启用
        return self._current_file.endswith('.cn')  # 仅 .cn 文件启用

    def eventFilter(self, obj, event):
        """
        事件过滤器 - 拦截键盘/输入事件触发补全

        Args:
            obj: QObject 实例，事件目标对象
            event: QEvent 实例，包含事件类型和详细信息
            
        Returns:
            bool: True 表示事件已处理，False 表示继续传递
        """
        # 回车选中补全
        if obj == self.completer.popup() and event.type() == QEvent.Type.KeyPress:
            key_event = cast(QKeyEvent, event)
            if key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter:
                popup = self.completer.popup()
                assert popup is not None
                current_row = popup.currentIndex().row()
                if current_row >= 0:
                    # 有选中项，插入选中项
                    model = self.completer.model()
                    index = model.index(current_row, 0)
                    if index.isValid():
                        current_completion = model.data(index)
                        if current_completion:
                            self.insert_completion(current_completion)
                            popup.hide()
                else:
                    # 无选中项，插入当前补全前缀
                    current_completion = self.completer.currentCompletion()
                    if current_completion:
                        self.insert_completion(current_completion)
                        popup.hide()
                return True  # 事件已处理

        # 非文本编辑器事件，直接传递给父类
        if obj is not self.text_edit: return super().eventFilter(obj, event)
        et = event.type()

        # 中文输入法事件
        if et == QEvent.Type.InputMethod and isinstance(event, QInputMethodEvent):
            if event.preeditString() or event.commitString():  # 有预编辑或提交字符串
                if self._should_complete():
                    self.show_completion()  # 触发防抖补全
            return False  # 不拦截，继续传递

        # 按键释放事件
        if et == QEvent.Type.KeyRelease and isinstance(event, QKeyEvent):
            key = event.key()
            # 排除特殊键
            if key in (
                    Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab,
                    Qt.Key.Key_Backspace, Qt.Key.Key_Delete,
                    Qt.Key.Key_Left, Qt.Key.Key_Right,
                    Qt.Key.Key_Up, Qt.Key.Key_Down,
                    Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt,
            ):
                return False  # 特殊键不触发补全
            if self._should_complete():
                self.show_completion()  # 触发防抖补全
            return False  # 不拦截，继续传递

        # 输入法查询事件
        if et == QEvent.Type.InputMethodQuery:
            if self._should_complete():
                self.show_completion()  # 触发防抖补全
            return False  # 不拦截，继续传递

        return super().eventFilter(obj, event)

    def update_theme(self, dark_mode: bool):
        """
        更新补全器主题
        
        Args:
            dark_mode: True 为深色主题，False 为浅色主题
        """
        self._dark_mode = dark_mode
        self.completer.update_theme(dark_mode)  # 同步更新补全弹出框主题

    def __del__(self):
        """析构函数 - 确保资源被正确释放"""
        try:
            self.cleanup()  # 安全退出后台线程
        except Exception as e:
            print(f"语法提示器析构时出错: {e}")
