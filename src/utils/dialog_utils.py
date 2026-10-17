from typing import Optional
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget


class DialogUtils:
    """对话框工具类"""

    @staticmethod
    def _show_message_box(parent: Optional[QWidget], icon: QMessageBox.Icon, title: str, message: str, detail: str = "") -> None:
        """
        展示消息对话框

        Args:
            parent: 父窗口
            icon: 消息图标
            title: 对话框标题
            message: 消息内容
            detail: 详细信息
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if detail:
            msg_box.setDetailedText(detail)
        msg_box.exec()

    @staticmethod
    def show_error(parent: Optional[QWidget], title: str, message: str, detail: str = "") -> None:
        """
        展示错误对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 错误信息
            detail: 详细信息
        """
        DialogUtils._show_message_box(parent, QMessageBox.Icon.Critical, title, message, detail)

    @staticmethod
    def show_warning(parent: Optional[QWidget], title: str, message: str) -> None:
        """
        展示警告对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 警告信息
        """
        DialogUtils._show_message_box(parent, QMessageBox.Icon.Warning, title, message)

    @staticmethod
    def show_info(parent: Optional[QWidget], title: str, message: str) -> None:
        """
        展示信息对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 提示信息
        """
        DialogUtils._show_message_box(parent, QMessageBox.Icon.Information, title, message)

    @staticmethod
    def ask_question(parent: Optional[QWidget], title: str, message: str) -> bool:
        """
        展示确认对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 确认信息

        Returns:
            bool: 用户确认返回 True，取消返回 False
        """
        result = QMessageBox.question(
            parent, title, message,  # type: ignore
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes

    @staticmethod
    def _file_dialog(parent: Optional[QWidget], title: str, file_filter: str, directory: str, save: bool) -> str:
        """
        文件选择对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            file_filter: 文件过滤器
            directory: 默认目录
            save: True 为保存对话框，False 为打开对话框

        Returns:
            str: 选中的文件路径，取消返回空字符串
        """
        if save:
            file_path, _ = QFileDialog.getSaveFileName(parent, title, directory, file_filter)
        else:
            file_path, _ = QFileDialog.getOpenFileName(parent, title, directory, file_filter)
        return file_path or ""

    @staticmethod
    def open_file_dialog(parent: Optional[QWidget], title: str, file_filter: str, directory: str = "") -> str:
        """
        打开文件选择对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            file_filter: 文件过滤器
            directory: 默认目录

        Returns:
            str: 选中的文件路径，取消返回空字符串
        """
        return DialogUtils._file_dialog(parent, title, file_filter, directory, save=False)

    @staticmethod
    def save_file_dialog(parent: Optional[QWidget], title: str, file_filter: str, directory: str = "") -> str:
        """
        保存文件对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            file_filter: 文件过滤器
            directory: 默认目录

        Returns:
            str: 保存路径，取消返回空字符串
        """
        return DialogUtils._file_dialog(parent, title, file_filter, directory, save=True)
