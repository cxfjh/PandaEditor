import os
from typing import Optional
from PySide6 import QtCore
from src.utils.code_proc import compile_code, run_code
from src.utils.config_service import get_config_service
from src.utils.file_ops import open_directory, save_as_file, save_file
from PySide6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
from src.utils.dialog_utils import DialogUtils
from src.utils.syntax_high import ChineseHighlighter
from src.utils.syntax_hint import SyntaxHintManager


# 共享的当前文件路径变量
_current_file_path: Optional[str] = None


def get_current_file_path() -> Optional[str]:
    """获取当前文件路径"""
    return _current_file_path


def set_current_file_path(path: Optional[str]) -> None:
    """设置当前文件路径"""
    global _current_file_path
    _current_file_path = path


def is_current_file_cn() -> bool:
    """检查当前文件是否为 .cn 格式"""
    return _current_file_path is not None and _current_file_path.endswith('.cn')


class MainWindowHandlers:
    """主窗口事件处理类"""

    def __init__(self, ui):
        """
        初始化事件处理器
        
        Args:
            ui: MainWindowUI 实例
        """
        self.ui = ui

    def on_cursor_position_changed(self):
        """光标位置变化时，更新状态栏的行号和文件信息"""
        current_editor = self.ui.tab_manager.get_current_editor()
        if not current_editor:
            return

        # 计算当前光标所在行号
        cursor = current_editor.textCursor()
        cursor_position = cursor.position()
        cursor_block = current_editor.document().findBlock(cursor_position)
        cursor_line_number = cursor_block.blockNumber() + 1  # 行号从 1 开始
        file_path = self.ui.tab_manager.get_current_file_path() or "未命名"

        # 更新共享文件路径变量
        actual_path = self.ui.tab_manager.get_current_file_path()
        set_current_file_path(actual_path)

        # 更新状态栏显示
        spaces = ' ' * 10
        self.ui.status_label.setText(f"行号: {cursor_line_number}{spaces}文件: {file_path}{spaces}版本: v0.1.0")

    def on_open_directory(self):
        """处理打开目录操作"""
        dir_path = open_directory()
        if dir_path:
            try:
                # 更新文件树根目录和工作目录到打开的目录
                self.ui.file_tree.set_root_path(dir_path)
                self.ui.terminal.set_working_directory(dir_path)
                self.on_cursor_position_changed()
            except Exception as e:
                DialogUtils.show_error(self.ui.main_window, "打开失败", f"无法打开目录:\n{e}")

    def on_save_file(self):
        """处理保存文件操作"""
        current_file_path = self.ui.tab_manager.get_current_file_path()
        if current_file_path:
            try:
                current_editor = self.ui.tab_manager.get_current_editor()
                if not current_editor:
                    return
                content = current_editor.toPlainText()
                result = save_file(content, current_file_path)
                if result:
                    self.ui.tab_manager.mark_current_tab_modified(False)  # 清除修改标记
            except Exception as e:
                DialogUtils.show_error(self.ui.main_window, "保存失败", f"保存文件出错：\n{e}")
        else:
            # 未命名的文件，自动弹出另存为对话框
            self.on_save_as_file()

    def on_save_as_file(self):
        """处理另存为文件操作"""
        current_editor = self.ui.tab_manager.get_current_editor()
        if current_editor:
            result = save_as_file(current_editor.toPlainText())
            if result:
                # 更新标签页文件路径
                self.ui.tab_manager.set_current_file_path(result)
                self.ui.tab_manager.mark_current_tab_modified(False)

                # 更新文件树根目录和工作目录到保存文件的目录
                file_dir = os.path.dirname(result)
                self.ui.file_tree.set_root_path(file_dir)
                self.ui.terminal.set_working_directory(file_dir)

                # 如果是 .cn 文件且没有语法高亮器，创建语法高亮器
                if result.endswith('.cn'):
                    tab_data = self.ui.tab_manager.get_current_tab_data()
                    if tab_data and not tab_data.highlighter:
                        tab_data.highlighter = ChineseHighlighter(current_editor.document(), current_editor, self.ui.tab_manager.dark_mode)
                        tab_data.highlighter._current_file = result

                    # 创建语法补全管理器
                    if tab_data and not tab_data.syntax_hint:
                        tab_data.syntax_hint = SyntaxHintManager(current_editor, dark_mode=self.ui.tab_manager.dark_mode)
                        tab_data.syntax_hint.set_current_file(result)

    def on_find_replace(self):
        """处理查找和替换操作"""
        tab_data = self.ui.tab_manager.get_current_tab_data()
        if tab_data and tab_data.find_replace_dialog:
            tab_data.find_replace_dialog.show()
            tab_data.find_replace_dialog.raise_()
            tab_data.find_replace_dialog.activateWindow()

    def on_run_code(self):
        """处理运行代码操作"""
        if not is_current_file_cn():
            DialogUtils.show_error(self.ui.main_window, "运行失败", "只能运行 .cn 格式的中文代码文件")
            return

        if not self._save_current_file():
            return

        current_editor = self.ui.tab_manager.get_current_editor()
        if current_editor:
            # 直接传递文件路径，不修改全局配置
            run_code(current_editor.toPlainText(), _current_file_path)

    def on_compile_code(self):
        """处理编译代码操作"""
        if not is_current_file_cn():
            DialogUtils.show_error(self.ui.main_window, "编译失败", "只能编译 .cn 格式的中文代码文件")
            return

        if not self._save_current_file():
            return

        current_editor = self.ui.tab_manager.get_current_editor()
        if current_editor:
            # 直接传递文件路径，不修改全局配置
            compile_code(current_editor.toPlainText(), _current_file_path)

    def _save_current_file(self) -> bool:
        """保存当前文件，成功返回 True，失败返回 False"""
        current_file_path = self.ui.tab_manager.get_current_file_path()
        if not current_file_path:
            return False

        try:
            current_editor = self.ui.tab_manager.get_current_editor()
            if not current_editor:
                return False
            content = current_editor.toPlainText()
            with open(current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            DialogUtils.show_error(self.ui.main_window, "保存失败", f"保存文件出错：\n{e}")
            return False

    def on_compile_log(self, log: str):
        """处理编译日志输出"""
        self.ui.terminal.append_output(log)

    @staticmethod
    def open_website():
        """打开官方网站"""
        os.startfile('https://cxfjh.github.io')

    @staticmethod
    def open_github():
        """打开 GitHub 开源地址"""
        os.startfile('https://github.com/cxfjh/panda-editor')

    @staticmethod
    def open_author_github():
        """打开作者 GitHub 主页"""
        os.startfile('https://github.com/cxfjh')

    @staticmethod
    def open_tutorial():
        """打开使用教程"""
        os.startfile('https://github.com/cxfjh/panda-editor/blob/main/docs/USAGE.md')

    def toggle_file_tree(self, checked: bool):
        """
        切换文件窗口显示状态
        
        Args:
            checked: True=显示，False=隐藏
        """
        self.ui.file_tree.setVisible(checked)
        if checked:
            self.ui.main_splitter.setSizes([200, 1200])  # 显示时设置宽度比例
        else:
            self.ui.main_splitter.setSizes([0, 1200])  # 隐藏时宽度为 0

    def toggle_terminal(self, checked: bool):
        """
        切换终端窗口显示状态
        
        Args:
            checked: True=显示，False=隐藏
        """
        self.ui.terminal.setVisible(checked)
        if checked:
            self.ui.right_splitter.setSizes([700, 200])  # 显示时设置高度比例
        else:
            self.ui.right_splitter.setSizes([900, 0])  # 隐藏时高度为 0

    def toggle_line_numbers(self, checked: bool):
        """
        切换行号显示状态
        
        Args:
            checked: True=显示行号，False=隐藏行号
        """
        self.ui.tab_manager.toggle_line_numbers(checked)

    def toggle_file_tree_shortcut(self):
        """快捷键切换文件窗口"""
        current = self.ui.toggle_file_tree_action.isChecked()
        self.ui.toggle_file_tree_action.setChecked(not current)
        self.toggle_file_tree(not current)

    def toggle_terminal_shortcut(self):
        """快捷键切换终端窗口"""
        current = self.ui.toggle_terminal_action.isChecked()
        self.ui.toggle_terminal_action.setChecked(not current)
        self.toggle_terminal(not current)

    def init_menu_states(self):
        """初始化菜单项的选中状态，从配置读取"""
        try:
            settings = get_config_service().get_personal_config()
            if settings:
                # 读取并应用各项配置
                self.ui.dark_mode_action.setChecked(settings.get('darkMode', True))
                self.ui.syntax_highlight_action.setChecked(settings.get('highlightSyntax', True))
                self.ui.window_top_action.setChecked(settings.get('windowTop', False))
                pip_mirror = settings.get('pipMirror', 'taobao')
                self.ui.pip_taobao_action.setChecked(pip_mirror == 'taobao')
                self.ui.hide_window_action.setChecked(settings.get('hideWindow', False))
                self.ui.admin_privilege_action.setChecked(settings.get('adminPrivilege', False))
                self.ui.single_file_action.setChecked(settings.get('singleFileMode', True))
                use_default_icon = settings.get('useDefaultCompileIcon', True)
                self.ui.compile_default_icon_action.setChecked(use_default_icon)
                self.ui.compile_icon_action.setEnabled(not use_default_icon)  # 使用默认图标时禁用自定义选项
        except Exception as e:
            print(f"初始化菜单项选中状态时出错: {e}")

    def on_pip_mirror_changed(self):
        """切换 pip 源设置"""
        is_taobao = self.ui.pip_taobao_action.isChecked()
        get_config_service().update_personal_config("pipMirror", "taobao" if is_taobao else "default")

    def on_hide_window_changed(self):
        """切换编译时隐藏窗口设置"""
        hide = self.ui.hide_window_action.isChecked()
        get_config_service().update_personal_config("hideWindow", hide)

    def on_admin_privilege_changed(self):
        """切换编译时管理员权限设置"""
        admin = self.ui.admin_privilege_action.isChecked()
        get_config_service().update_personal_config("adminPrivilege", admin)

    def on_single_file_changed(self):
        """切换编译单文件模式设置"""
        single_file = self.ui.single_file_action.isChecked()
        get_config_service().update_personal_config("singleFileMode", single_file)

    def on_add_data_changed(self):
        """设置编译时导入的资源文件/目录"""
        try:
            # 获取已添加的资源路径
            existing_paths = get_config_service().get_personal_config("addDataPaths") or []

            # 创建资源管理对话框
            dialog = QDialog(self.ui.main_window)
            dialog.setWindowTitle("管理编译资源")
            dialog.setMinimumWidth(500)
            layout = QVBoxLayout(dialog)

            # 列表显示已添加的资源
            list_widget = QListWidget()
            for path in existing_paths:
                list_widget.addItem(path)
            layout.addWidget(list_widget)

            # 按钮区域
            btn_layout = QHBoxLayout()

            add_file_btn = QPushButton("添加文件")
            add_folder_btn = QPushButton("添加文件夹")
            remove_btn = QPushButton("移除选中")
            clear_btn = QPushButton("清空全部")
            ok_btn = QPushButton("确定")

            btn_layout.addWidget(add_file_btn)
            btn_layout.addWidget(add_folder_btn)
            btn_layout.addWidget(remove_btn)
            btn_layout.addWidget(clear_btn)
            btn_layout.addStretch()
            btn_layout.addWidget(ok_btn)
            layout.addLayout(btn_layout)

            def add_file():
                """添加文件到资源列表"""
                paths, _ = QFileDialog.getOpenFileNames(dialog, "选择资源文件")
                for paths in paths:
                    paths = os.path.normpath(paths)
                    if paths not in existing_paths:
                        existing_paths.append(paths)
                        list_widget.addItem(paths)

            def add_folder():
                """添加文件夹到资源列表"""
                folder = QFileDialog.getExistingDirectory(dialog, "选择资源文件夹")
                if folder:
                    folder = os.path.normpath(folder)
                    if folder not in existing_paths:
                        existing_paths.append(folder)
                        list_widget.addItem(folder)

            def remove_selected():
                """移除选中的资源"""
                for item in list_widget.selectedItems():
                    paths = item.text()
                    if paths in existing_paths:
                        existing_paths.remove(paths)
                    list_widget.takeItem(list_widget.row(item))

            def clear_all():
                """清空所有资源"""
                list_widget.clear()
                existing_paths.clear()

            # 连接按钮信号
            add_file_btn.clicked.connect(add_file)
            add_folder_btn.clicked.connect(add_folder)
            remove_btn.clicked.connect(remove_selected)
            clear_btn.clicked.connect(clear_all)
            ok_btn.clicked.connect(dialog.accept)

            # 用户点击确定后保存配置
            if dialog.exec() == QDialog.Accepted:  # type: ignore
                get_config_service().update_personal_config("addDataPaths", existing_paths)
                if existing_paths:
                    DialogUtils.show_info(self.ui.main_window, "资源已添加", f"已添加 {len(existing_paths)} 个资源路径\n编译时将自动打包这些资源")
        except Exception as e:
            DialogUtils.show_error(self.ui.main_window, "设置失败", f"无法管理资源路径：\n{e}")

    def on_compile_default_icon_changed(self):
        """切换编译默认图标设置"""
        use_default = self.ui.compile_default_icon_action.isChecked()
        get_config_service().update_personal_config("useDefaultCompileIcon", use_default)
        # 如果切换为使用默认图标，禁用自定义图标菜单
        self.ui.compile_icon_action.setEnabled(not use_default)

    def on_compile_icon_changed(self):
        """设置编译时使用的图标"""
        try:
            icon_path = QFileDialog.getOpenFileName(self.ui.main_window, "选择编译图标", "", "图标文件 (*.ico);;所有文件 (*)")[0]
            if icon_path:
                import os
                icon_path = os.path.normpath(icon_path)
                get_config_service().update_personal_config("compileIconPath", icon_path)
                DialogUtils.show_info(self.ui.main_window, "图标已设置", f"编译图标已设置为：\n{icon_path}\n\n编译时将使用此图标")
        except Exception as e:
            DialogUtils.show_error(self.ui.main_window, "设置失败", f"无法设置编译图标：\n{e}")

    def on_dark_mode_changed(self):
        """切换深色模式"""
        dark_mode = self.ui.dark_mode_action.isChecked()
        get_config_service().update_personal_config("darkMode", dark_mode)

        # 使用标签页管理器应用主题
        self.ui.tab_manager.apply_theme(dark_mode)

        # 更新终端和文件树主题
        self.ui.terminal.apply_theme(dark_mode)
        self.ui.file_tree.apply_theme(dark_mode)

        # 更新语法提示主题
        tab_data = self.ui.tab_manager.get_current_tab_data()
        if tab_data and tab_data.syntax_hint:
            tab_data.syntax_hint.update_theme(dark_mode)

    def on_syntax_highlight_changed(self):
        """切换语法高亮"""
        highlight = self.ui.syntax_highlight_action.isChecked()
        get_config_service().update_personal_config("highlightSyntax", highlight)

        # 使用标签页管理器切换语法高亮
        self.ui.tab_manager.toggle_syntax_highlight(highlight)

    def on_window_top_changed(self):
        """切换窗口置顶"""
        window_top = self.ui.window_top_action.isChecked()
        get_config_service().update_personal_config("windowTop", window_top)
        main_window = self.ui.central_widget.window()
        if main_window:
            main_window.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, window_top)
            main_window.show()

    def on_text_changed(self):
        """文本内容变化时的回调"""
        self.ui.tab_manager.mark_current_tab_modified(True)

    def auto_save(self):
        """自动保存当前文件"""
        current_file_path = self.ui.tab_manager.get_current_file_path()
        if not current_file_path:
            return

        if not self.ui.tab_manager.is_current_tab_modified():
            return

        try:
            current_editor = self.ui.tab_manager.get_current_editor()
            if not current_editor:
                return
            content = current_editor.toPlainText()
            with open(current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.ui.tab_manager.mark_current_tab_modified(False)
        except Exception as e:
            print(f"自动保存失败: {e}")

    def on_file_tree_selected(self, file_path: str):
        """
        处理文件树双击事件，打开选中的文件
        
        Args:
            file_path: 双击选中的文件完整路径
        """
        self.auto_save()  # 先保存当前文件

        try:
            # 直接从磁盘读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查文件是否已经在标签页中打开
            for index in range(self.ui.tab_manager.tab_widget.count()):
                tab_data = self.ui.tab_manager.tab_data_map.get(index)
                if tab_data and tab_data.file_path == file_path:
                    # 文件已打开，切换到该标签页
                    self.ui.tab_manager.tab_widget.setCurrentIndex(index)
                    # 重新加载最新内容
                    if tab_data.editor:
                        tab_data.editor.setPlainText(content)
                        tab_data.has_unsaved_changes = False
                    # 更新配置
                    file_dir, file_name = os.path.split(file_path)
                    base_name, file_ext = os.path.splitext(file_name)
                    get_config_service().update_file_config("code_name", base_name)
                    get_config_service().update_file_config("file_ext", file_ext)
                    return

            # 文件未打开，创建新标签页
            self.ui.tab_manager.create_new_tab(file_path=file_path, content=content)

            # 更新文件名和扩展名配置
            file_dir, file_name = os.path.split(file_path)
            base_name, file_ext = os.path.splitext(file_name)
            get_config_service().update_file_config("code_name", base_name)
            get_config_service().update_file_config("file_ext", file_ext)

            # 更新语法补全的当前文件
            tab_data = self.ui.tab_manager.get_current_tab_data()
            if tab_data and tab_data.syntax_hint:
                tab_data.syntax_hint.set_current_file(file_path)

            # 更新终端工作目录
            self.ui.terminal.set_working_directory(file_dir)

            # 更新状态栏
            self.on_cursor_position_changed()
        except Exception as e:
            DialogUtils.show_error(self.ui.main_window, "打开失败", f"无法打开文件:\n{e}")
