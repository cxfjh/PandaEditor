import os
import psutil
import shutil
import subprocess
from tkinter import messagebox
from src.utils.Config import readConfig, initFileConfig


# 重置程序
def resetProgram():
    try:
        delPath = os.path.join(readConfig('FileConfig.json', 'Root'), "src", "config")
        if messagebox.askyesno('重置程序', '确定要重置程序吗？重置后将重新启动程序！'):
            if os.path.exists(delPath): shutil.rmtree(delPath)
            messagebox.showinfo('重置程序', '重置程序成功，请重新启动程序！')
            initFileConfig()
            restartProgram()
    except Exception as e: messagebox.showerror('重置程序', '重置程序失败，请检查配置文件，或使用管理员身份运行程序！')


# 卸载程序
def uninstallProgram():
    try:
        if messagebox.askyesno('卸载程序', '确定要卸载程序吗？'):
            uninst_path = os.path.join(os.path.dirname(readConfig('FileConfig.json', 'Root')), 'uninst.exe')
            subprocess.run(uninst_path, check=True)
            restartProgram()
    except Exception as e: messagebox.showerror('卸载程序', '卸载程序失败，请检查程序目录，或使用管理员身份运行程序！')


# 重启程序
def restartProgram():
    currentPid = psutil.Process().pid
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['pid'] == currentPid:
            proc.kill()
