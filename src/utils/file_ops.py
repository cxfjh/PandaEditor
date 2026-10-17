import os
import shutil
from typing import Optional
from src.utils.config_service import get_config_service
from src.utils.dialog_utils import DialogUtils
from PySide6.QtWidgets import QFileDialog


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


def _get_current_file_path() -> Optional[str]:
    """
    获取当前配置中的文件路径

    Returns:
        规范化的文件完整路径，若配置不完整则返回 None
    """
    source_dir = get_config_service().get_file_config("source_code_path")  # 源码目录
    code_name = get_config_service().get_file_config("code_name")  # 文件名
    file_ext = get_config_service().get_file_config("file_ext") or ".cn"  # 扩展名
    if not all([source_dir, code_name]): return None  # 配置不完整，返回 None
    return os.path.normpath(os.path.join(source_dir, f"{code_name}{file_ext}"))  # 拼接并规范化路径


def split_file_path(file_path: Optional[str]) -> None:
    """
    解析文件路径，更新目录、文件名和扩展名配置

    Args:
        file_path: 文件完整路径，为 None 时不执行任何操作
    """
    if not file_path: return
    file_dir, file_name = os.path.split(file_path)  # 拆分目录和文件名
    base_name, file_ext = os.path.splitext(file_name)  # 拆分文件名和扩展名
    get_config_service().update_file_config("code_name", base_name)  # 更新文件名配置
    get_config_service().update_file_config("source_code_path", os.path.normpath(file_dir))  # 更新目录配置
    get_config_service().update_file_config("file_ext", file_ext)  # 更新扩展名配置


def open_directory() -> Optional[str]:
    """
    打开目录选择对话框

    Returns:
        选中的目录路径，若用户取消或发生错误则返回 None
    """
    try:
        dir_path = QFileDialog.getExistingDirectory(_parent_widget, "打开目录")  # 弹出目录选择对话框
        if dir_path:
            normalized_path = os.path.normpath(dir_path)  # 规范化路径
            get_config_service().update_file_config("source_code_path", normalized_path)  # 更新配置
            return normalized_path
    except Exception as e:
        DialogUtils.show_error(_parent_widget, "打开失败", f"无法打开目录：\n{e}")
    return None


def save_file(content: str, file_path: Optional[str] = None) -> Optional[str]:
    """
    保存到当前配置的文件或指定路径
    
    Args:
        content: 要保存的文件内容
        file_path: 可选的文件路径，如果提供则保存到该路径
        
    Returns:
        保存的文件路径，失败则返回 None
    """
    try:
        if not file_path:
            file_path = _get_current_file_path()  # 从配置获取当前文件路径
            if not file_path:
                DialogUtils.show_warning(_parent_widget, "保存失败", "请先使用【另存为】指定保存路径")
                return None
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # 创建目录
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)  # 写入文件内容
        return file_path
    except Exception as e:
        DialogUtils.show_error(_parent_widget, "保存失败", f"保存文件出错：\n{e}")
        return None


def save_as_file(content: str) -> Optional[str]:
    """
    另存为新文件并更新配置

    Args:
        content: 要保存的文件内容
        
    Returns:
        保存的文件路径，用户取消则返回 None
    """
    try:
        # 弹出另存为对话框
        file_path = DialogUtils.save_file_dialog(_parent_widget, "另存为 CN 文件", "CN 文件 (*.cn)")
        if not file_path:
            return None

        normalized_path = os.path.normpath(file_path)  # 规范化路径

        # 如果用户没有输入 .cn 后缀，自动添加
        if not normalized_path.endswith('.cn'):
            normalized_path += '.cn'

        os.makedirs(os.path.dirname(normalized_path), exist_ok=True)  # 创建目录
        with open(normalized_path, "w", encoding="utf-8") as f:
            f.write(content)  # 写入文件内容
        split_file_path(normalized_path)  # 更新配置
        return normalized_path
    except Exception as e:
        DialogUtils.show_error(_parent_widget, "另存失败", f"无法保存文件：\n{e}")
        return None


def read_file_content() -> Optional[str]:
    """
    读取当前配置文件内容

    Returns:
        文件内容字符串，若文件不存在或读取失败则返回 None
    """
    try:
        file_path = _get_current_file_path()  # 从配置获取当前文件路径
        if not file_path or not os.path.isfile(file_path):
            # 文件不存在，清空相关配置
            get_config_service().update_file_config("source_code_path", "")
            get_config_service().update_file_config("code_name", "")
            return None
        with open(file_path, "r", encoding="utf-8") as f: return f.read()  # 读取文件内容
    except Exception as e:
        DialogUtils.show_error(_parent_widget, "读取失败", f"无法读取文件内容：\n{e}")
        return None


def import_file() -> None:
    """导入 .py 扩展文件到 /File 目录"""
    try:
        file_path = DialogUtils.open_file_dialog(_parent_widget, "导入 PY 扩展文件", "Python 文件 (*.py)")  # 弹出文件选择对话框
        if not file_path: return
        src_path = os.path.normpath(file_path)  # 规范化源文件路径
        if not os.path.isfile(src_path):
            DialogUtils.show_error(_parent_widget, "导入失败", "文件不存在")
            return
        root = get_config_service().get_app_config("root_dir")  # 获取程序根目录
        target_dir = os.path.join(root, "File")  # 构建目标目录路径
        os.makedirs(target_dir, exist_ok=True)  # 创建目标目录（若不存在）
        file_name = os.path.basename(src_path)  # 获取文件名
        target_path = os.path.join(target_dir, file_name)  # 构建目标文件路径
        shutil.copyfile(src_path, target_path)  # 复制文件到目标目录
        DialogUtils.show_info(_parent_widget, "导入成功", f"文件已导入：\n{target_path}\n重启生效")
    except Exception as e:
        DialogUtils.show_error(_parent_widget, "导入失败", f"无法导入文件：\n{e}")
