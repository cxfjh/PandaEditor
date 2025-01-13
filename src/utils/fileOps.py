import os
from tkinter import filedialog, messagebox
from src.utils.Config import updateConfig, readConfig


# 处理文件路径
def splitFilePath(filePath):
    if not filePath: return
    path, filename = os.path.split(filePath)
    name, _ = os.path.splitext(filename)
    updateConfig("FileConfig.json", "CodeName", os.path.join(name))
    updateConfig("FileConfig.json", "SourceCodePath", os.path.join(path))


# 打开文件
def openFile():
    try:
        filePath = filedialog.askopenfilename(filetypes=[("CN Files", "*.cn")]).replace('/', '\\')
        if not filePath: return
        splitFilePath(filePath)
    except Exception as e: messagebox.showerror("打开文件", "打开文件失败！")


# 保存文件
def saveFile(content):
    try:
        filePath = os.path.join(readConfig("FileConfig.json", "SourceCodePath"), readConfig("FileConfig.json", "CodeName")) + ".cn"
        with open(filePath, "w", encoding="utf-8") as fileHandle: fileHandle.write(content)
    except Exception as e: messagebox.showerror("保存文件", "保存文件失败！")


# 另存文件
def saveAsFile(content):
    try:
        filePath = filedialog.asksaveasfilename(filetypes=[("CN Files", "*.cn")], defaultextension=".cn")
        if not filePath: return
        with open(filePath, "w", encoding="utf-8") as fileHandle: fileHandle.write(content)
        splitFilePath(filePath)
    except Exception as e: messagebox.showerror("另存文件", "另存文件失败！")


# 读取文件内容
def readFileContent():
    try:
        filePath = readConfig("FileConfig.json", "SourceCodePath") + "\\" + readConfig("FileConfig.json", "CodeName") + ".cn"
        if not os.path.exists(filePath):
            updateConfig("FileConfig.json", "SourceCodePath", "")
            updateConfig("FileConfig.json", "CodeName", "")
            return None
        with open(filePath, "r", encoding="utf-8") as fileHandle: return fileHandle.read()
    except Exception as e:
        messagebox.showerror("获取内容", "获取文件内容失败！")
        return None
