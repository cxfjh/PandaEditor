import os
import shutil
import subprocess
from src.utils.config_service import get_config_service
from src.utils.dialog_utils import DialogUtils


# 全局父窗口引用，用于对话框的模态显示
_parent_widget = None


def set_parent_widget(widget) -> None:
    """
    设置父窗口引用
    
    用途：
    - 为对话框提供模态显示的父窗口
    - 确保对话框始终在主窗口之上显示
    
    Args:
        widget: 主窗口部件引用
    """
    global _parent_widget
    _parent_widget = widget


def _get_root_path() -> str:
    """
    获取程序根目录

    Returns:
        程序根目录的完整路径，若配置缺失则返回空字符串
    """
    root = get_config_service().get_app_config("root_dir")
    if not root:
        DialogUtils.show_error(_parent_widget, "错误", "未获取到程序根目录！")
        return ""
    return root


def reset_program() -> None:
    """重置程序到初始状态"""
    root = _get_root_path()
    if not root: return
    if not DialogUtils.ask_question(_parent_widget, "重置程序", "确定要重置程序吗？"): return

    config_dir = os.path.join(root, "src", "config")  # 配置目录路径
    try:
        if os.path.exists(config_dir):
            shutil.rmtree(config_dir)  # 删除配置目录
        get_config_service().init_config()  # 重新初始化配置
        DialogUtils.show_info(_parent_widget, "重置成功", "程序已重置，即将重启！")
        restart_program()  # 重启程序
    except Exception as e:
        DialogUtils.show_error(_parent_widget, "重置失败", f"错误信息：{str(e)}\n\n请尝试使用管理员身份运行！")


def uninstall_program() -> None:
    """调用卸载程序执行卸载"""
    root = _get_root_path()
    if not root: return
    if not DialogUtils.ask_question(_parent_widget, "卸载程序", "确定要卸载程序吗？"): return

    try:
        uninstaller = os.path.join(root, "uninst.exe")  # 卸载程序路径
        if not os.path.exists(uninstaller):
            DialogUtils.show_error(_parent_widget, "卸载失败", "未找到卸载程序：uninst.exe")
            return
        subprocess.run(uninstaller, check=True)  # 执行卸载程序
    except Exception as e:
        DialogUtils.show_error(_parent_widget, "卸载失败", f"错误信息：{str(e)}\n\n请尝试使用管理员身份运行！")


def restart_program() -> None:
    """关闭当前进程"""
    os.kill(os.getpid(), 9)
