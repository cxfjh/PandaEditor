import os
import psutil
import shutil
import subprocess
from tkinter import messagebox
from src.utils.Config import read_config, init_file_config


def reset_program():
    """
    重置程序配置，删除配置目录后重新初始化并重启程序
    """
    try:
        # 获取配置目录路径
        config_dir = os.path.join(read_config('FileConfig.json', 'Root'), "src", "config")
        # 询问用户是否确认重置
        if messagebox.askquestion('重置程序', '确定要重置程序吗？') == 'yes':
            # 删除配置目录（若存在）
            if os.path.exists(config_dir):
                shutil.rmtree(config_dir)

            messagebox.showinfo('重置程序', '重置程序成功，请重新启动程序！')

            # 重新初始化配置文件
            init_file_config()

            # 重启程序
            restart_program()
    except Exception as e:
        messagebox.showerror('重置程序', f'重置程序失败，错误信息：{str(e)}，请检查配置文件，或使用管理员身份运行程序！')


def uninstall_program():
    """
    卸载程序，调用卸载程序执行卸载操作后重启
    """
    try:
        # 询问用户是否确认卸载
        if messagebox.askquestion('卸载程序', '确定要卸载程序吗？') == 'yes':
            # 获取卸载程序路径
            uninstaller_path = os.path.join(read_config('FileConfig.json', 'Root'), 'uninst.exe')

            # 执行卸载程序
            subprocess.run(uninstaller_path, check=True)

            # 重启程序（实际卸载后可能不需要，这里逻辑可根据实际情况调整）
            restart_program()
    except Exception as e:
        messagebox.showerror( '重置程序', f'重置程序失败，错误信息：{str(e)}，请检查配置文件，或使用管理员身份运行程序！')


def restart_program():
    """
    重启当前程序，通过结束当前进程实现
    """
    current_pid = psutil.Process().pid
    # 遍历进程，找到当前进程并结束
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['pid'] == current_pid:
            proc.kill()
