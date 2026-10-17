from PySide6 import QtGui, QtWidgets
import re


class FindReplaceDialog(QtWidgets.QDialog):
    """查找和替换对话框"""

    def __init__(self, editor, parent=None, dark_mode=True):
        """
        初始化查找替换对话框
        
        Args:
            editor: 代码编辑器实例（CodeEditor）
            parent: 父组件（通常是标签页组件）
            dark_mode: 是否使用深色主题
        """
        super().__init__(parent)
        self._editor = editor
        self._dark_mode = dark_mode
        self._setup_ui()

    def _setup_ui(self):
        """设置对话框界面"""
        self.setWindowTitle("查找和替换")
        self.setModal(False)  # 非模态对话框
        self.resize(400, 150)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)

        # 查找行布局
        find_layout = QtWidgets.QHBoxLayout()
        self.find_label = QtWidgets.QLabel("查找:")
        self.find_input = QtWidgets.QLineEdit()
        self.find_input.returnPressed.connect(self._find_next)  # 回车键查找下一个
        find_layout.addWidget(self.find_label)
        find_layout.addWidget(self.find_input, 1)  # 拉伸因子为 1

        self.find_prev_btn = QtWidgets.QPushButton("上一个")
        self.find_prev_btn.clicked.connect(self._find_previous)
        find_layout.addWidget(self.find_prev_btn)

        self.find_next_btn = QtWidgets.QPushButton("下一个")
        self.find_next_btn.clicked.connect(self._find_next)
        find_layout.addWidget(self.find_next_btn)

        layout.addLayout(find_layout)

        # 替换行布局
        replace_layout = QtWidgets.QHBoxLayout()
        self.replace_label = QtWidgets.QLabel("替换:")
        self.replace_input = QtWidgets.QLineEdit()
        self.replace_input.returnPressed.connect(self._replace)  # 回车键替换
        replace_layout.addWidget(self.replace_label)
        replace_layout.addWidget(self.replace_input, 1)

        self.replace_btn = QtWidgets.QPushButton("替换")
        self.replace_btn.clicked.connect(self._replace)
        replace_layout.addWidget(self.replace_btn)

        self.replace_all_btn = QtWidgets.QPushButton("全部替换")
        self.replace_all_btn.clicked.connect(self._replace_all)
        replace_layout.addWidget(self.replace_all_btn)

        layout.addLayout(replace_layout)

        # 选项行布局
        options_layout = QtWidgets.QHBoxLayout()
        self.case_sensitive = QtWidgets.QCheckBox("区分大小写")
        options_layout.addWidget(self.case_sensitive)

        self.use_regex = QtWidgets.QCheckBox("正则表达式")
        options_layout.addWidget(self.use_regex)

        options_layout.addStretch()  # 弹性空间，将关闭按钮推到右侧

        self.close_btn = QtWidgets.QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        options_layout.addWidget(self.close_btn)

        layout.addLayout(options_layout)

        # 状态标签（显示查找/替换结果）
        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)

        # 设置深色模式样式
        if self._dark_mode:
            self.setStyleSheet(
                """
                QDialog { background-color: #1E1E1E; color: #CCCCCC; }
                QLabel { color: #CCCCCC; }
                QComboBox, QLineEdit { background-color: #2D2D2D; color: #CCCCCC; border: 1px solid #3E3E3E; padding: 3px; }
                QPushButton { background-color: #0E639C; color: white; border: none; padding: 5px 10px; }
                QPushButton:hover { background-color: #1177BB; }
                QCheckBox { color: #CCCCCC; }
            """,
            )

    def showEvent(self, event):
        """对话框显示时的事件处理"""
        super().showEvent(event)
        cursor = self._editor.textCursor()
        if cursor.hasSelection():
            self.find_input.setText(cursor.selectedText())  # 使用选中文本作为查找内容
        self.find_input.selectAll()  # 全选输入框文本，方便用户修改
        self.find_input.setFocus()  # 聚焦输入框

    def _find_next(self):
        """查找下一个匹配项"""
        self._find(forward=True)

    def _find_previous(self):
        """查找上一个匹配项"""
        self._find(forward=False)

    def _find(self, forward=True):
        """
        执行查找
        
        Args:
            forward: True=向后查找，False=向前查找
        """
        find_text = self.find_input.text()
        if not find_text:
            self.status_label.setText("请输入查找内容")
            return

        if self.use_regex.isChecked():
            # 使用正则表达式查找
            self._find_regex(find_text, forward)
        else:
            # 使用 Qt 内置查找方法
            flags = QtGui.QTextDocument.FindFlag.FindBackward if not forward else QtGui.QTextDocument.FindFlag(0)
            if self.case_sensitive.isChecked():
                flags = flags | QtGui.QTextDocument.FindFlag.FindCaseSensitively  # 叠加区分大小写标志

            found = self._editor.find(find_text, flags)
            if found:
                self.status_label.setText("已找到")
            else:
                # 未找到，尝试循环查找
                cursor = self._editor.textCursor()
                if forward:
                    cursor.movePosition(QtGui.QTextCursor.MoveOperation.Start)  # 移到文档开头
                else:
                    cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)  # 移到文档结尾
                self._editor.setTextCursor(cursor)

                found = self._editor.find(find_text, flags)
                if found:
                    self.status_label.setText("已找到（从文档开头/结尾重新开始）")
                else:
                    self.status_label.setText("未找到")

    def _find_regex(self, pattern: str, forward: bool):
        """
        使用正则表达式查找
        
        Args:
            pattern: 正则表达式模式
            forward: True=向后查找，False=向前查找
        """
        try:
            flags = 0 if self.case_sensitive.isChecked() else re.IGNORECASE
            regex = re.compile(pattern, flags)
        except re.error as e:
            self.status_label.setText(f"正则表达式错误: {e}")
            return

        cursor = self._editor.textCursor()
        document = self._editor.document()
        total_blocks = document.blockCount()  # 总行数
        current_block_num = cursor.block().blockNumber()  # 当前行号

        # 先从当前位置搜索
        search_order = range(current_block_num + 1, total_blocks) if forward else range(current_block_num - 1, -1, -1)
        if self._search_blocks(regex, document, search_order, cursor):
            self.status_label.setText("已找到")
            return

        # 未找到从头/尾继续搜索
        search_order = range(0, total_blocks) if forward else range(total_blocks - 1, -1, -1)
        if self._search_blocks(regex, document, search_order, cursor):
            self.status_label.setText("已找到（从文档开头/结尾重新开始）")
            return

        self.status_label.setText("未找到")

    def _search_blocks(self, regex, document, search_order, cursor):
        """
        在指定行范围内搜索正则匹配
        
        Args:
            regex: 编译后的正则表达式对象
            document: QTextDocument 实例
            search_order: 要搜索的行号范围（range 对象）
            cursor: 文本游标（用于选中匹配文本）
            
        Returns:
            True=找到匹配，False=未找到
        """
        for block_num in search_order:
            block = document.findBlockByNumber(block_num)
            text = block.text()
            match = regex.search(text)
            if match:
                # 找到匹配，设置游标选中匹配文本
                cursor.setPosition(block.position() + match.start())
                cursor.setPosition(block.position() + match.end(), QtGui.QTextCursor.MoveMode.KeepAnchor)
                self._editor.setTextCursor(cursor)
                self._editor.ensureCursorVisible()  # 滚动到可见区域
                return True
        return False

    def _replace(self):
        """替换当前匹配项"""
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()

        if not find_text:
            self.status_label.setText("请输入查找内容")
            return

        if self.use_regex.isChecked():
            # 使用正则替换
            self._replace_regex(find_text, replace_text)
        else:
            # 普通文本替换
            cursor = self._editor.textCursor()
            if cursor.hasSelection() and cursor.selectedText() == find_text:
                cursor.insertText(replace_text)  # 替换选中文本
                self._editor.setTextCursor(cursor)
                self.status_label.setText("已替换")
                self._find_next()  # 自动查找下一个
            else:
                self.status_label.setText("当前选中的不是查找内容，请先查找")

    def _replace_regex(self, pattern: str, replace_text: str):
        """
        使用正则表达式替换当前匹配项
        
        Args:
            pattern: 正则表达式模式
            replace_text: 替换文本
        """
        try:
            flags: int = 0 if self.case_sensitive.isChecked() else re.IGNORECASE
            regex = re.compile(pattern, flags)
        except re.error as e:
            self.status_label.setText(f"正则表达式错误: {e}")
            return

        cursor = self._editor.textCursor()
        # 检查选中文本是否完全匹配正则表达式
        if cursor.hasSelection() and regex.fullmatch(cursor.selectedText()):
            new_text = regex.sub(replace_text, cursor.selectedText())
            cursor.insertText(new_text)
            self._editor.setTextCursor(cursor)
            self.status_label.setText("已替换")
            self._find_next()  # 自动查找下一个
        else:
            self.status_label.setText("当前选中的不是查找内容，请先查找")

    def _replace_all(self):
        """全部替换"""
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()

        if not find_text:
            self.status_label.setText("请输入查找内容")
            return

        # 获取整个文档文本
        document = self._editor.document()
        full_text = document.toPlainText()

        # 执行替换
        flags = 0
        if not self.case_sensitive.isChecked():
            flags = re.IGNORECASE

        # 转义查找文本中的正则特殊字符
        escaped_find = re.escape(find_text)
        regex = re.compile(escaped_find, flags)  # type: ignore
        new_text, count = regex.subn(replace_text, full_text)

        if count == 0:
            self.status_label.setText("未找到匹配项")
            return

        # 批量更新文档
        cursor = self._editor.textCursor()
        cursor.beginEditBlock()  # 开始编辑块
        cursor.select(QtGui.QTextCursor.SelectionType.Document)  # 选中整个文档
        cursor.insertText(new_text)  # 替换为新文本
        cursor.endEditBlock()  # 结束编辑块

        self.status_label.setText(f"已替换 {count} 处")
