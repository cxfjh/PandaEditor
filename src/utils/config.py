textCode = """
账号 等于 “fjh”
密码 等于 “123”

循环 真的：
	用户输入的账号 等于 输入（“请输入账号：”）
	用户输入的密码 等于 输入（“请输入密码：”）

	如果 用户输入的账号 全等 账号 并且 用户输入的密码 全等 密码：
		输出（“登录成功”）
		中断
	否则：
		输出（“登录失败”）
"""

import json # 导入json模块 处理配置文件
import os # 导入os模块 处理文件路径
from tkinter import messagebox # 导入tkinter模块 显示错误信息


# 文件配置
fileConfig = {
    "Root": os.getcwd() + r'\src', # 根目录
    "ConfigDirectory": os.getcwd() + r'\src\config', # 配置文件目录
    "FileDirectory": os.getcwd() + r'\src\config', # 操作文件目录
    "SaveDirectory": os.getcwd() + r'\src\config\源代码', # 保存目录
    "TextFilePath": os.getcwd() + r'\src\config\Code.cn', # 文本文件路径
    "CodeFilePath": os.getcwd() + r'\src\config\Code.py', # 代码文件路径
    "PythonDirectory": os.getcwd() + r'\Python.exe', # Python目录
    "TextFileName": "Code.cn", # 操作源文件名
    "CodeFileName": "Code.py", # 输出代码文件名
    "TextCode": textCode, # 文本代码
}


# 个性化配置
personalConfig = {
    "fontSize": 25, # 字体大小
    "darkMode": True, # 黑夜模式
    "highlightSyntax": True, # 语法高亮
    "windowTop": False, # 窗口置顶
}


# 初始化JSON文件
def initFileConfig():
    try:
        directory = fileConfig["FileDirectory"]  # 存放配置文件的目录
        filePath = os.path.join(directory, 'fileConfig.json')  # 文件配置路径
        personalPath = os.path.join(directory, 'personalConfig.json')  # 样式配置路径
        if isConfigFileExists(filePath, personalPath): return # 如果配置文件不存在，则初始化配置文件
        os.makedirs(directory, exist_ok=True)  # 创建目录，exist_ok=True 表示如果目录已存在不会抛出异常
        with open(filePath, 'w', encoding='utf-8') as f: json.dump(fileConfig, f, ensure_ascii=False)  # 直接使用 json.dump 写入空 JSON 文件
        with open(personalPath, 'w', encoding='utf-8') as f: json.dump(personalConfig, f, ensure_ascii=False)  # 直接使用 json.dump 写入空 JSON 文件
        with open(fileConfig["TextFilePath"], 'w', encoding='utf-8') as f: f.write(fileConfig["TextCode"]) # 写入文本代码文件
        with open(fileConfig["CodeFilePath"], 'w', encoding='utf-8') as f: f.write("") # 写入空代码文件
    except: messagebox.showerror("错误", "初始化配置文件失败！(4842)") # 显示错误信息


# 判断配置文件是否存在
def isConfigFileExists(filePath, personalPath):
    try:
        if not os.path.exists(filePath) or not os.path.exists(personalPath): return False # 如果配置文件不存在，返回False
        TextFilePath = getFileConfig('TextFilePath') # 读取文本文件路径
        if not os.path.exists(TextFilePath): # 判断文本文件是否存在
            with open(filePath, 'w', encoding='utf-8') as f: json.dump(fileConfig, f, ensure_ascii=False)  # 直接使用 json.dump 写入空 JSON 文件
        return True
    except: messagebox.showerror("错误", "配置文件不存在！(2448)") # 显示错误信息


# 写入JSON文件
def writeFileConfig():
    try:
        directory = os.path.join(os.getcwd(), 'fileConfig')  # 设置目录
        filePath = os.path.join(directory, 'fileConfig.json')  # 设置文件路径
        os.makedirs(directory, exist_ok=True)  # 创建目录，exist_ok=True 表示如果目录已存在不会抛出异常
        with open(filePath, 'w', encoding='utf-8') as f: f.write("") # 清空json文件
        with open(filePath, 'w', encoding='utf-8') as f: json.dump(fileConfig, f, ensure_ascii=False)  # 直接使用 json.dump 写入空 JSON 文件
        with open(directory + r'\Code.cn', 'w', encoding='utf-8') as f: f.write(fileConfig["TextCode"]) # 写入文本代码文件
        with open(directory + r'\Code.py', 'w', encoding='utf-8') as f: f.write("") # 写入空代码文件
    except: messagebox.showerror("错误", "写入配置文件失败！(7909)") # 显示错误信息


# 读取JSON文件
def readConfig(fileName):
    try:
        with open(os.path.join(fileConfig["FileDirectory"], fileName), 'r', encoding='utf-8') as f: return json.load(f) # 读取JSON文件
    except: messagebox.showerror("错误", "读取配置文件失败！(3070)") # 显示错误信息


# 修改JSON文件
def writeConfig(fileName, jsonData):
    try:
        with open(os.path.join(fileConfig["FileDirectory"], fileName), 'w', encoding='utf-8') as f: f.write(json.dumps(jsonData, ensure_ascii=False)) # 写入JSON文件
    except: messagebox.showerror("错误", "写入配置文件失败！(3684)") # 显示错误信息


# 修改fileConfig配置
def setFileConfig(key, value):
    try:
        jsonData = readConfig("fileConfig.json") # 读取JSON文件
        jsonData[key] = value # 修改配置
        with open(os.path.join(fileConfig["FileDirectory"], "fileConfig.json"), 'w', encoding='utf-8') as f: f.write(json.dumps(jsonData, ensure_ascii=False)) # 写入JSON文件
    except: messagebox.showerror("错误", "修改配置文件失败！(3509)") # 显示错误信息


# 获取fileConfig配置
def getFileConfig(key): 
    try: return readConfig("fileConfig.json")[key] # 获取配置
    except: messagebox.showerror("错误", "获取配置文件失败！(2135)") # 显示错误信息


# 修改personalConfig配置
def setPersonalConfig(key, value):
    try:
        jsonData = readConfig("personalConfig.json") # 读取JSON文件
        jsonData[key] = value # 修改配置
        with open(os.path.join(fileConfig["FileDirectory"], "personalConfig.json"), 'w', encoding='utf-8') as f: f.write(json.dumps(jsonData, ensure_ascii=False)) # 写入JSON文件
    except: messagebox.showerror("错误", "修改个性化配置文件失败！(9859)") # 显示错误信息


# 获取personalConfig配置
def getPersonalConfig(key): 
    try: return readConfig("personalConfig.json")[key] # 获取配置
    except: messagebox.showerror("错误", "获取个性化配置文件失败！(5116)") # 显示错误信息
