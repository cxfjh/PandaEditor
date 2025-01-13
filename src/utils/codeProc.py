import os
import re
import shutil
import threading
import subprocess
from tkinter import messagebox
from src.utils.Config import readConfig
from src.module.StandardLibrary import Grammar, Symbols


# 全局变量，用于存储配置信息
envPath = ""
exePath = ""
codePath = ""
Character = {
    "“": '"',
    "”": '"',
}


# 初始化配置信息
def init():
    global envPath, exePath, codePath
    envPath = readConfig("FileConfig.json", "PythonDirectory")
    exePath = os.path.join(readConfig("FileConfig.json", "SourceCodePath"), readConfig("FileConfig.json", "CodeName"))
    codePath = exePath + ".py"


# 保护被引用的部分
def protectParts(string):
    protected_parts = re.findall(r'“([^”]*)”', string)
    placeholders = {}
    for i, part in enumerate(protected_parts):
        placeholder = f'__PROTECTED_{i}__'
        placeholders[placeholder] = part
        string = string.replace(f'“{part}”', placeholder)
    return string, placeholders


# 还原被保护的部分
def restoreParts(string, placeholders):
    for placeholder, part in placeholders.items():
        string = string.replace(placeholder, f'“{part}”')
    return string


# 解析代码
def parseCode(string):
    try:
        init()
        string, placeholders = protectParts(string)
        pattern = r'(?<![\w\u4e00-\u9fff])(' + '|'.join(map(re.escape, Grammar.keys())) + r')(?![\w\u4e00-\u9fff])'
        result = re.sub(pattern, lambda match: Grammar[match.group(0)], string)
        result = re.sub('|'.join(map(re.escape, Symbols.keys())), lambda match: Symbols[match.group(0)], result)
        result = restoreParts(result, placeholders)
        result = re.sub('|'.join(map(re.escape, Character.keys())), lambda match: Character[match.group(0)], result)

        os.makedirs(os.path.dirname(codePath), exist_ok=True)
        with open(codePath, 'w', encoding='utf-8') as f: f.write(result)
    except Exception as e: messagebox.showerror("代码解析", "解析代码时发生错误！")


def runThread():
    try: 
        scriptDir = os.path.dirname(codePath)
        subprocess.run([envPath, codePath], cwd=scriptDir)
    except subprocess.CalledProcessError as e: messagebox.showerror("代码运行", "线程运行代码时发生错误！")


# 运行代码
def runCode(textCode):
    try:
        parseCode(textCode)
        threading.Thread(target=runThread).start()
    except: messagebox.showerror("代码运行", "运行代码时发生错误！")


def compileThread():
    try:
        if readConfig("FileConfig.json", "CodeName")[-2:] == "-w": subprocess.run([envPath, "-m", "PyInstaller", "-F", "-w", "--distpath=" + exePath,  "-i", "./src/static/logo.ico", codePath], check=True)
        else: subprocess.run([envPath, "-m", "PyInstaller", "-F", "--distpath=" + exePath,  "-i", "./src/static/logo.ico", codePath], check=True)
        messagebox.showinfo("编译代码", "编译完成！")
        os.startfile(exePath)
        deleteGarbage()
    except: messagebox.showerror("代码编译", "线程编译代码时发生错误！")


# 编译代码
def compileCode(textCode):
    try:
        parseCode(textCode)
        threading.Thread(target=compileThread).start()
        messagebox.showinfo("编译代码", "正在编译代码，请勿重复操作！")
    except Exception as e: messagebox.showerror("代码编译", "编译代码时发生错误！")


# 删除垃圾文件
def deleteGarbage():
    try:
        rootPath = readConfig("FileConfig.json", "Root")
        targetPath = os.path.join(rootPath, "build")
        for filename in os.listdir(rootPath):
            if filename.endswith('.spec'):
                filePath = os.path.join(rootPath, filename)
                os.remove(filePath)
        shutil.rmtree(targetPath)
    except: pass   
