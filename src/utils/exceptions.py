import sys
import traceback
import logging
from typing import Optional
from PySide6.QtWidgets import QMessageBox, QWidget


# 配置日志记录器
logger = logging.getLogger("PandaEditor")


class PandaEditorException(Exception):
    """基础异常类"""

    def __init__(self, message: str, detail: Optional[str] = None):
        """
        初始化异常实例
        
        Args:
            message: 简短的错误消息（用于对话框主文本）
            detail: 详细的错误信息（用于对话框详细信息区域）
        """
        self.message = message  # 简短错误消息
        self.detail = detail  # 详细错误信息
        super().__init__(message)


class ConfigException(PandaEditorException):
    """配置相关异常"""
    pass


class GlobalExceptionHandler:
    """
    全局异常处理器
    
    Attributes:
        parent_widget: 父窗口引用，用于展示模态对话框
    """

    def __init__(self, parent_widget: Optional[QWidget] = None):
        """
        初始化全局异常处理器
        
        Args:
            parent_widget: 父窗口引用（可选），用于展示模态对话框
        """
        self.parent_widget = parent_widget

    def handle_exception(self, exc_type, exc_value, exc_tb) -> None:
        """
        统一异常处理入口
        
        Args:
            exc_type: 异常类型（如 ValueError、TypeError）
            exc_value: 异常实例（包含错误消息）
            exc_tb: 异常追踪信息（堆栈追踪对象）
        """
        # 忽略 KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)  # 使用默认异常钩子
            return

        # 格式化异常详情
        error_detail = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        error_message = str(exc_value)  # 提取异常消息

        # 写入日志
        logger.error(f"未捕获异常: {exc_type.__name__}\n{error_detail}")

        # 展示错误对话框
        self._show_error_dialog(exc_type.__name__, error_message, error_detail)

    def _show_error_dialog(self, error_type: str, message: str, detail: str) -> None:
        """
        展示错误对话框
        
        Args:
            error_type: 异常类型名称（如 ValueError）
            message: 简短错误消息
            detail: 详细错误信息（堆栈追踪）
        """
        if self.parent_widget:
            # 有父窗口，展示模态错误对话框
            msg_box = QMessageBox(self.parent_widget)
            msg_box.setIcon(QMessageBox.Icon.Critical)  # 设置图标为严重错误
            msg_box.setWindowTitle("程序错误")
            msg_box.setText(f"<b>{error_type}</b>")  # 主文本显示异常类型（加粗）
            msg_box.setInformativeText(message)  # 提示文本显示简短消息
            msg_box.setDetailedText(detail)  # 详细信息显示堆栈追踪
            msg_box.exec()  # 显示对话框（模态）
        else:
            # 无父窗口时回退到控制台输出
            print(f"[ERROR] {error_type}: {message}\n{detail}", file=sys.stderr)


def install_global_exception_handler(parent_widget: Optional[QWidget] = None) -> GlobalExceptionHandler:
    """
    安装全局异常处理器

    Args:
        parent_widget: 父窗口引用（可选），用于展示模态对话框
        
    Returns:
        GlobalExceptionHandler: 异常处理器实例
    """
    handler = GlobalExceptionHandler(parent_widget)
    sys.excepthook = handler.handle_exception  # 替换默认异常钩子
    return handler
