from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QEvent
from PySide6.QtGui import QInputMethodEvent


class LineNumberArea(QtWidgets.QWidget):
    """行号区域控件 - 自定义行号显示组件"""

    def __init__(self, editor):
        """
        初始化行号区域
        
        Args:
            editor: CodeEditor 实例，关联的代码编辑器
        """
        super().__init__(editor)  # 设置编辑器为父控件
        self._editor = editor

    def sizeHint(self):
        """
        返回行号区域的建议大小
        
        Returns:
            QSize: 行号区域的建议大小（宽度根据行号计算，高度为 0 表示自适应）
        """
        return QtCore.QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        """
        绘制事件 - 当行号区域需要重绘时触发
        
        Args:
            event: QPaintEvent 实例，包含需要重绘的区域
        """
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    """自定义代码编辑器 - 增强型代码编辑组件"""

    def __init__(self, parent=None, dark_mode=True):
        """
        初始化代码编辑器
        
        Args:
            parent: 父窗口部件
            dark_mode: 是否使用深色模式，默认为 True
        """
        super().__init__(parent)
        self._dark_mode = dark_mode
        self._line_number_area = LineNumberArea(self)
        self._show_line_numbers = True

        # 连接信号到槽
        self.blockCountChanged.connect(self.update_line_number_area_width)  # 行数变化时更新宽度
        self.updateRequest.connect(self.update_line_number_area)  # 视图更新时重绘行号
        self.cursorPositionChanged.connect(self.highlight_current_line)  # 光标移动时高亮当前行

        # 初始化行号区域和当前行高亮
        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # 安装输入法事件过滤器
        self.installEventFilter(self)

    def line_number_area_width(self):
        """
        计算行号区域的宽度
        
        Returns:
            int: 行号区域宽度（像素），如果不显示行号则返回 0
        """
        if not self._show_line_numbers:
            return 0
        digits = 1
        max_num = max(1, self.blockCount())  # 最大行号
        while max_num >= 10:
            max_num //= 10
            digits += 1  # 计算位数
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits  # 3px 边距 + 数字宽度 * 位数
        return space

    def update_line_number_area_width(self, _):
        """
        更新行号区域宽度
        
        Args:
            _: 未使用的参数（信号传递的块数量）
        """
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """
        更新行号区域显示
        
        Args:
            rect: QRect, 需要更新的区域
            dy: int, 垂直滚动距离（>0 表示向下滚动）
        """
        if dy:
            self._line_number_area.scroll(0, dy)  # 滚动时平移行号区域
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())  # 重绘指定区域

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)  # 视口完全变化时重新计算宽度

    def resizeEvent(self, event):
        """
        调整大小事件 - 编辑器尺寸变化时同步行号区域尺寸
        
        Args:
            event: QResizeEvent 实例
        """
        super().resizeEvent(event)
        cr = self.contentsRect()  # 获取内容区域
        self._line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """
        绘制行号区域 - 核心绘制逻辑
        
        Args:
            event: QPaintEvent 实例，包含需要重绘的区域
        """
        if not self._show_line_numbers:
            return

        painter = QtGui.QPainter(self._line_number_area)

        # 绘制行号区域背景
        bg_color = "#252526" if self._dark_mode else "#F3F3F3"
        painter.fillRect(event.rect(), QtGui.QColor(bg_color))

        # 获取第一个可见块
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # 预计算颜色
        current_line_color = "#C6C6C6" if self._dark_mode else "#000000"  # 当前行行号颜色
        normal_line_color = "#858585" if self._dark_mode else "#6E6E6E"  # 普通行号颜色
        current_block_num = self.textCursor().blockNumber()  # 当前光标所在行号

        # 遍历所有可见块并绘制行号
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)  # 行号从 1 开始
                pen_color = current_line_color if block_number == current_block_num else normal_line_color
                painter.setPen(QtGui.QColor(pen_color))
                painter.drawText(0, top, self._line_number_area.width() - 5, self.fontMetrics().height(), QtCore.Qt.AlignmentFlag.AlignRight, number)  # type: ignore

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()  # type: ignore
            block_number += 1

    def highlight_current_line(self):
        """高亮显示当前行"""
        extra_selections = []

        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()

            # 根据主题设置高亮颜色
            if self._dark_mode:
                line_color = QtGui.QColor("#2A2D2E")  # 深色模式行高亮色
            else:
                line_color = QtGui.QColor("#E8E8E8")  # 浅色模式行高亮色

            # 设置高亮范围为当前行
            selection.format.setBackground(line_color)  # type: ignore
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)  # type: ignore
            selection.cursor = self.textCursor()  # type: ignore
            selection.cursor.clearSelection()  # 清除选中状态，仅高亮背景
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def set_dark_mode(self, dark_mode: bool):
        """
        设置深色模式 - 切换编辑器主题
        
        Args:
            dark_mode: True 为深色模式，False 为浅色模式
        """
        self._dark_mode = dark_mode
        self.highlight_current_line()  # 重新高亮当前行
        self._line_number_area.update()  # 重绘行号区域

    def set_show_line_numbers(self, show):
        """
        设置是否显示行号
        
        Args:
            show: bool, True 显示行号，False 隐藏行号
        """
        self._show_line_numbers = show
        self.update_line_number_area_width(0)  # 重新计算宽度
        self._line_number_area.setVisible(show)  # 显示/隐藏行号区域

    def eventFilter(self, obj, event):
        """
        事件过滤器 - 拦截中文输入法事件，处理中文括号自动补全
        
        Args:
            obj: QObject 实例，事件目标对象
            event: QEvent 实例，包含事件类型和详细信息
            
        Returns:
            bool: 如果事件已被处理则返回 True，否则返回父类实现的结果
        """
        # 拦截输入法事件
        if obj is self and event.type() == QEvent.Type.InputMethod:
            if isinstance(event, QInputMethodEvent):
                commit = event.commitString()  # 获取输入法提交的字符
                # 检查是否为中文括号
                if commit and commit in ('（', '【', '《', '“', '”', "‘", "’"):
                    self._handle_chinese_bracket_completion(commit)
                    return True  # 事件已处理，阻止默认行为
        return super().eventFilter(obj, event)

    def _handle_chinese_bracket_completion(self, commit_str: str):
        """
        处理中文输入法提交的括号字符补全
        
        Args:
            commit_str: 输入法提交的括号字符
        """
        bracket_map = { '（': '）', '【': '】', '《': '》', '“': '”', "‘": "’", "’": "’", "”": "”" }
        close_bracket = bracket_map.get(commit_str)
        if close_bracket:
            cursor = self.textCursor()
            cursor.insertText(commit_str + close_bracket)  # 插入开括号+闭括号
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left)  # 光标左移一位
            self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        """
        按键事件处理 - 拦截键盘输入，实现特殊功能
        
        Args:
            event: QKeyEvent 实例
        """
        # Tab 键处理
        if event.key() == QtCore.Qt.Key.Key_Tab:
            if event.modifiers() == QtCore.Qt.KeyboardModifier.NoModifier:
                self.insertPlainText("    ")  # 插入 4 个空格
                return

        # Ctrl+/ 切换注释
        if event.key() == QtCore.Qt.Key.Key_Slash and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self._toggle_comment()
            return

        # 英文键盘括号补全
        if event.key() in (
                QtCore.Qt.Key.Key_ParenLeft, QtCore.Qt.Key.Key_BraceLeft,
                QtCore.Qt.Key.Key_BracketLeft, QtCore.Qt.Key.Key_QuoteDbl,
                QtCore.Qt.Key.Key_Apostrophe,
        ):
            if self._handle_english_bracket_completion(event):
                return

        super().keyPressEvent(event)  # 其他键交给默认处理

    def _handle_english_bracket_completion(self, event):
        """
        处理英文键盘括号补全
        
        Args:
            event: QKeyEvent 实例
            
        Returns:
            bool: True 表示已处理括号补全，False 表示不是括号键
        """
        bracket_map = {
            QtCore.Qt.Key.Key_ParenLeft: ('(', ')'),
            QtCore.Qt.Key.Key_BraceLeft: ('{', '}'),
            QtCore.Qt.Key.Key_BracketLeft: ('[', ']'),
            QtCore.Qt.Key.Key_QuoteDbl: ('"', '"'),
            QtCore.Qt.Key.Key_Apostrophe: ("'", "'"),
        }

        brackets = bracket_map.get(event.key())
        if brackets:
            cursor = self.textCursor()
            cursor.insertText(brackets[0] + brackets[1])  # 插入开括号+闭括号
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left)  # 光标左移一位
            self.setTextCursor(cursor)
            return True
        return False

    def _toggle_comment(self):
        """切换注释/取消注释 (Ctrl+/)"""
        cursor = self.textCursor()

        # 处理选中区域：多行注释/取消注释
        if cursor.hasSelection():
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()

            cursor.setPosition(start_pos)
            start_block = cursor.block()
            cursor.setPosition(end_pos)
            end_block = cursor.block()

            start_block_num = start_block.blockNumber()
            end_block_num = end_block.blockNumber()

            # 收集选中区域的文本
            document = self.document()
            lines = []
            for i in range(start_block_num, end_block_num + 1):
                block = document.findBlockByNumber(i)
                lines.append(block.text())

            # 判断是否所有非空行都已注释
            all_commented = all(line.lstrip().startswith('#') for line in lines if line.strip())

            # 生成新文本：取消注释或添加注释
            new_lines = []
            if all_commented:
                # 取消注释：删除第一个 # 及其后的一个空格
                for line in lines:
                    if line.lstrip().startswith('#'):
                        idx = line.index('#')
                        new_lines.append(line[:idx] + line[idx + 1:])
                    else:
                        new_lines.append(line)
            else:
                # 添加注释：在缩进后插入 #
                for line in lines:
                    if line.strip():
                        stripped = line.lstrip()
                        indent = len(line) - len(stripped)
                        new_lines.append(line[:indent] + '#' + line[indent:])
                    else:
                        new_lines.append(line)  # 空行保持不变

            # 批量替换文本
            cursor.beginEditBlock()
            cursor.setPosition(start_block.position())
            for i, line in enumerate(new_lines):
                if i > 0:
                    cursor.movePosition(QtGui.QTextCursor.MoveOperation.Down)
                    cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                cursor.select(QtGui.QTextCursor.SelectionType.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.insertText(line)
            cursor.endEditBlock()
        else:
            # 单行注释/取消注释
            block = cursor.block()
            text = block.text()

            if text.lstrip().startswith('#'):
                # 取消注释
                idx = text.index('#')
                new_text = text[:idx] + text[idx + 1:]
            else:
                # 添加注释
                stripped = text.lstrip()
                indent = len(text) - len(stripped)
                new_text = text[:indent] + '#' + text[indent:]

            cursor.select(QtGui.QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(new_text)

        self.setTextCursor(cursor)
