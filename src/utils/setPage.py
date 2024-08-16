import os # 导入os模块 处理文件和目录
import psutil # 导入psutil模块 处理进程
import shutil # 导入shutil模块 处理文件和目录
import subprocess # 导入subprocess模块 运行外部程序
from tkinter import messagebox # 弹窗库 处理弹窗
from src.utils.config import getFileConfig, initFileConfig # 处理操作配置文件


# 重置程序
def resetProgram():
    try:
        delPath = getFileConfig('ConfigDirectory') # 获取配置文件路径
        if messagebox.askyesno('提示', '确定要重置程序吗？重置后将重新启动程序！'): # 弹窗确认删除配置文件
            if os.path.exists(delPath): shutil.rmtree(delPath) # 删除文件夹
            messagebox.showinfo('提示', '重置程序成功，请重新启动程序！') # 弹窗提示删除成功
            initFileConfig() # 初始化配置文件
            for proc in psutil.process_iter(['pid', 'name']): # 循环遍历进程
                if proc.info['pid'] == psutil.Process().pid: proc.kill() # 杀死当前进程
    except: messagebox.showerror('错误', '重置程序失败，请检查配置文件，或使用管理员身份运行程序！(8380)') # 弹窗提示删除失败


# 卸载程序
def uninstallProgram():
    try: 
        if messagebox.askyesno('提示', '确定要卸载程序吗？'):
            subprocess.run(os.path.dirname(getFileConfig("Root")) + r'\uninst.exe', check=True)
            for proc in psutil.process_iter(['pid', 'name']): # 循环遍历进程
                if proc.info['pid'] == psutil.Process().pid: proc.kill() # 杀死当前进程
    except: messagebox.showerror('错误', '卸载程序失败，请检查程序目录，或使用管理员身份运行程序！(9674)') # 弹窗提示卸载失败


