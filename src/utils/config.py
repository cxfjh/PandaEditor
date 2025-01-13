import json
import os
import sys
from tkinter import messagebox


# 程序启动参数
userPath = None
if len(sys.argv) > 1: 
    userPath = sys.argv[1]
    os.chdir(os.path.dirname(sys.argv[0]))


# 配置文件目录
configFilePath = os.path.join(os.getcwd(), 'src', 'config')


# 文件配置
FileConfig = {
    "Root": os.getcwd(),
    "ConfigDirectory": os.path.join(configFilePath, 'FileConfig.json'),
    "PersonalConfig": os.path.join(configFilePath, 'PersonalConfig.json'),
    "PythonDirectory": os.path.join(os.getcwd(), 'Python.exe'), 
    "ICON": os.path.join(os.getcwd(), 'src', "static", "logo.ico"),
    "SourceCodePath": "",
    "CodeName": "",
}


# 个性化配置
PersonalConfig = {
    "fontSize": 25,
    "darkMode": True,
    "highlightSyntax": True,
    "windowTop": False,
}


# 初始化JSON文件
def initFileConfig():
    try:
        if not os.path.exists(configFilePath):
            os.makedirs(configFilePath, exist_ok=True)
            with open(FileConfig["ConfigDirectory"], 'w', encoding='utf-8') as f: json.dump(FileConfig, f, ensure_ascii=False, indent=4)
            with open(FileConfig["PersonalConfig"], 'w', encoding='utf-8') as f: json.dump(PersonalConfig, f, ensure_ascii=False, indent=4)
  
        from src.utils.FileOps import splitFilePath
        splitFilePath(userPath)
    except Exception as e: messagebox.showerror("初始化", "初始化配置文件失败！")


# 读取JSON文件
def readConfig(filePath, key = None):
    fullFilePath = os.path.join(configFilePath, filePath)
    try:
        if key == None:
            with open(fullFilePath, 'r', encoding='utf-8') as f: return json.load(f)
        else:
            with open(fullFilePath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(key)
    except FileNotFoundError: messagebox.showerror("错误", f"配置文件未找到: {fullFilePath}")
    except json.JSONDecodeError: messagebox.showerror("错误", f"配置文件格式错误: {fullFilePath}")
    except Exception as e: messagebox.showerror("读取配置", "读取配置文件失败！")
    return None


# 修改JSON文件
def updateConfig(filePath, key, newValue = None):
    fullFilePath = os.path.join(configFilePath, filePath)
    try:
        if newValue == None:
            with open(fullFilePath, 'w', encoding='utf-8') as f:  json.dump(key, f, ensure_ascii=False, indent=4)
            return True
        with open(fullFilePath, 'r', encoding='utf-8') as f: data = json.load(f)
        data[key] = newValue
        with open(fullFilePath, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except FileNotFoundError: messagebox.showerror("修改配置", "文件未找到")
    except json.JSONDecodeError: messagebox.showerror("修改配置", "文件格式错误")
    except Exception as e: messagebox.showerror("修改配置", "更新配置文件失败！")
    return False


