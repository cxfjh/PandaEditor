import os # 系统库 处理文件和目录
import re # 正则表达式库 处理字符串
import shutil # 文件管理库 复制、移动、删除文件
import threading # 多线程库 运行代码
import subprocess # 子进程库 运行命令
from tkinter import messagebox # 弹窗库 显示提示信息
from src.utils.config import getFileConfig # 导入JSON库 读取配置文件
from src.views.mainWin import setMistake # 导入主窗口函数 显示错误信息
from src.StandardLibrary.StandardLibrary import Grammar, Symbols  # 导入标准库


# 解析中文字符代码
def parseCode(string):
    try:
        protectedParts = re.compile(r'“.*?”').findall(string) # 保护被 “ ” 包裹的部分
        tempPlaceholders = {f'__PROTECTED_{i}__': part for i, part in enumerate(protectedParts)} # 替换保护部分为临时占位符
        for placeholder, part in tempPlaceholders.items(): string = string.replace(part, placeholder) # 保护被 “ ” 包裹的部分

        pattern = r'(?<![\w\u4e00-\u9fff])(' + '|'.join(map(re.escape, Grammar.keys())) + r')(?![\w\u4e00-\u9fff])' # 匹配关键字
        result = re.compile(pattern).sub(lambda match: Grammar[match.group(0)], string) # 替换关键字
        
        for placeholder, part in tempPlaceholders.items(): result = result.replace(placeholder, part) # 恢复保护部分
        replacementPattern = re.compile('|'.join(map(re.escape, Symbols.keys()))) # 匹配符号
        result = replacementPattern.sub(lambda match: Symbols[match.group(0)], result) # 替换符号

        with open(getFileConfig("CodeFilePath"), 'w', encoding='utf-8') as f: f.write(result) # 保存临时文件

        checkCode() # 语法检查
    except: messagebox.showerror("代码解析", "解析代码时发生错误！(3468)")


# 语法检查
def checkCode():
    try:
        result = subprocess.run([getFileConfig("PythonDirectory"), '-m', 'flake8', getFileConfig("CodeFilePath")], capture_output=True, text=True, encoding='utf-8') 
        if result.returncode != 0: 
            e = "、".join(re.findall(r'Code\.py:(\d+)', result.stdout))
            mistake = f'在第{e}行代码中发生了错误!'
            setMistake(mistake)
            messagebox.showerror("代码检查", mistake) # 弹窗提示检查失败
        else: setMistake(None) # 显示无错误
    except: messagebox.showerror("代码检查", "检查代码时发生错误！(5678)") # 弹窗提示检查失败


# 运行代码的线程函数
def runThread(): 
    try:  subprocess.run([getFileConfig("PythonDirectory"), getFileConfig("CodeFilePath")])
    except: messagebox.showerror("代码运行", "运行代码时发生错误！(2850)") # 弹窗提示运行失败


# 运行代码
def runCode(textCode):
    try:
        parseCode(textCode) # 解析代码
        threading.Thread(target=runThread).start() # 启动线程
    except: messagebox.showerror("代码运行", "运行代码时发生错误！(8533)") # 弹窗提示运行失败


# 编译代码的线程函数
def compileThread(): 
    try:
        destinationFolder = getFileConfig("FileDirectory") + r"\\源代码\\" + os.path.splitext(getFileConfig("TextFileName"))[0] # 储存目录
        command = [
            getFileConfig("PythonDirectory"), "-m", "PyInstaller", "-F",
            "--distpath", destinationFolder,
            "-i", "./src/static/logo.ico",
            getFileConfig("CodeFilePath"),
        ]  # 组装命令
        subprocess.run(command) # 运行编译命令
        messagebox.showinfo("编译提示", "编译完成！") # 弹窗提示编译成功
        organizeFiles(destinationFolder) # 整理文件
    except: messagebox.showerror("代码编译", "编译代码时发生错误！(9921)") # 弹窗提示编译失败


# 编译代码
def compileCode(textCode):
    try:
        parseCode(textCode) # 解析代码
        threading.Thread(target=compileThread).start() # 启动线程
        messagebox.showinfo("编译提示", "正在编译代码，请勿重复操作！") # 弹窗提示编译中 
    except: messagebox.showerror("代码编译", "编译代码时发生错误！(1194)")  #  # 弹窗提示编译失败


# 整理文件
def organizeFiles(destinationFolder):
    try:
        newFile = destinationFolder + r"\\" + os.path.splitext(getFileConfig("TextFileName"))[0] + ".exe" # 新文件名
        oldFile = destinationFolder + r"\\Code.exe" # 旧文件名
        if os.path.exists(newFile) and newFile != oldFile: os.remove(newFile) # 删除旧文件
        if newFile != oldFile: os.rename(oldFile, newFile) # 重命名文件
        os.startfile(destinationFolder) # 打开编译后的源代码目录
        os.remove(os.path.dirname(getFileConfig("Root")) + r"\\Code.spec") # 删除临时文件
        shutil.rmtree(os.path.dirname(getFileConfig("Root")) + r"\\build") # 删除临时文件夹
    except: messagebox.showerror("代码整理", "整理文件时发生错误！(7025)") # 弹窗提示整理失败

