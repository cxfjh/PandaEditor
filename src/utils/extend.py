import os
from typing import Dict, List
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from src.utils.config_service import get_config_service
from src.utils.dialog_utils import DialogUtils


def paint_gradient(widget, gradient_colors: List[str], gradient_alpha: float = 0.85) -> None:
    """
    绘制水平渐变背景
    
    Args:
        widget: Qt 控件实例，用于获取尺寸和绘制区域
        gradient_colors: 渐变色列表，如 ["#667eea", "#764ba2"]
        gradient_alpha: 透明度 (0.0-1.0)，默认 0.85
    """
    painter = QPainter(widget)  # 创建 QPainter 对象
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 启用抗锯齿渲染

    # 创建水平线性渐变
    gradient = QLinearGradient(0, 0, widget.width(), 0)
    for i, color_hex in enumerate(gradient_colors):
        color = QColor(color_hex)  # 将十六进制颜色转换为 QColor
        color.setAlphaF(gradient_alpha)  # 设置透明度
        # 计算颜色位置
        gradient.setColorAt(i / max(len(gradient_colors) - 1, 1), color)

    painter.fillRect(widget.rect(), gradient)  # 用渐变填充控件矩形区域
    painter.end()  # 结束绘制


# 全局父窗口引用，用于对话框的模态显示
_parent_widget = None


def set_parent_widget(widget) -> None:
    """
    设置父窗口引用

    Args:
        widget: 主窗口部件引用
    """
    global _parent_widget
    _parent_widget = widget


def _get_file_dir() -> str:
    """
    获取扩展库目录路径

    Returns:
        扩展库目录的完整路径，若配置缺失或目录不存在则返回空字符串
    """
    root_path = get_config_service().get_app_config("root_dir")  # 获取程序根目录
    if not root_path: return ""
    file_dir = os.path.join(root_path, "File")  # 构建扩展库目录路径
    if not os.path.isdir(file_dir):
        if _parent_widget is not None:
            DialogUtils.show_warning(_parent_widget, "目录不存在", f"扩展库目录不存在：\n{file_dir}")
        return ""
    return file_dir


def _iter_py_files(file_dir: str):
    """
    遍历目录下所有 .py 文件

    Args:
        file_dir: 要遍历的目录路径
        
    Yields:
        元组 (文件名, 文件完整路径)
    """
    for filename in os.listdir(file_dir):  # 列出目录下所有文件
        if filename.endswith(".py"):  # 只处理 .py 文件
            yield filename, os.path.join(file_dir, filename)  # 返回文件名和完整路径


def extend_library(directory: Dict) -> None:
    """
    加载扩展库文件内容

    Args:
        directory: 用于存储扩展库内容的字典，将被原地修改
    """
    file_dir = _get_file_dir()  # 获取扩展库目录路径
    if not file_dir: return
    for filename, file_path in _iter_py_files(file_dir):  # 遍历所有 .py 文件
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lib_name = os.path.splitext(filename)[0]  # 获取文件名
                directory[lib_name] = f.read()  # 将文件内容存入字典
        except Exception as e:
            DialogUtils.show_error(_parent_widget, "加载失败", f"文件 {filename} 加载失败：\n{e}")
