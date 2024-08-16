import os  # 导入系统库 处理文件路径
from src.utils.config import getFileConfig, setFileConfig  # 导入配置文件读写函数
from tkinter import filedialog, messagebox  # 导入文件选择框和弹窗提示库
from src.views.mainWin import setFilePath # 导入 UI 类


# 分割文件路径和文件名
def splitFilePath(filePath):
    path, filename = os.path.split(filePath)  # 分割文件路径和文件名
    setFileConfig("FileDirectory", path)  # 更新配置文件
    setFileConfig("TextFileName", filename)  # 更新配置文件
    setFileConfig("TextFilePath", filePath)  # 更新配置文件
    setFilePath()  # 更新主窗口文件路径


# 打开文件函数
def openFile():
    try:
        filePath = filedialog.askopenfilename(filetypes=[("*", "*.cn")]).replace('/', '\\') # 选择文件
        if not filePath: return  # 未选择文件
        splitFilePath(filePath)  # 分割文件路径和文件名
    except: messagebox.showerror("错误", "打开文件失败！(2128)") # 弹窗提示错误信息


# 保存文件函数
def saveFile(content):
    try:
        with open(getFileConfig("TextFilePath"), "w", encoding="utf-8") as fileHandle: fileHandle.write(content)
    except: messagebox.showerror("错误", "保存文件失败！(5814)") # 弹窗提示错误信息


# 另存文件函数
def saveAsFile(content):
    try:
        filePath = filedialog.asksaveasfilename(filetypes=[("*", "*.cn")], defaultextension=".cn")  # 选择另存文件路径
        if not filePath: return  # 未选择文件路径
        with open(filePath, "w", encoding="utf-8") as fileHandle: fileHandle.write(content)  # 另存文件内容
        splitFilePath(filePath)  # 分割文件路径和文件名
    except: messagebox.showerror("错误", "另存文件失败！(5220)") # 弹窗提示错误信息


# 获取文本代码
def getText():
    try:
        with open(getFileConfig("TextFilePath"), "r", encoding="utf-8") as fileHandle: return fileHandle.read()  # 读取文本代码
    except: messagebox.showerror("错误", "获取文本失败！(2049)") # 弹窗提示错误信息
