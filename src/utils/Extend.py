import os
import ast
from tkinter import messagebox
from src.utils.Config import read_config


def extend_library(directory):
    """ 遍历配置目录下所有.py文件，以文件名作为库名加载内容到directory字典 """
    try: dir_file = os.path.join(read_config("FileConfig.json", "Root"), "File")
    except Exception as e:
        print(e)
        return

    if not os.path.exists(dir_file):
        messagebox.showwarning("目录不存在", f"扩展库目录不存在: {dir_file}")
        return

    # 遍历目录中的.py文件
    for item in os.listdir(dir_file):
        item_path = os.path.join(dir_file, item)
        if os.path.isfile(item_path) and item.endswith(".py"):
            library_name = os.path.splitext(item)[0]  # 文件名作为库名
            try:
                with open(item_path, "r", encoding="utf-8") as f:
                    directory[library_name] = f.read()  # 存储文件内容
            except Exception as e:
                messagebox.showerror("加载失败", f"文件 {item} 加载出错: {str(e)}")


def extract_fun(directory):
    """ 遍历配置目录下所有.py文件，提取所有函数名并以"函数名:函数名"格式更新到directory字典 """
    try: dir_file = os.path.join(read_config("FileConfig.json", "Root"), "File") # 获取目标目录路径
    except Exception as e:
        print(e)
        return

    # 检查目录是否存在
    if not os.path.exists(dir_file):
        messagebox.showwarning("目录不存在", f"目标目录不存在: {dir_file}")
        return

    # 遍历目录中所有文件
    for item in os.listdir(dir_file):
        item_path = os.path.join(dir_file, item)

        # 只处理.py文件
        if os.path.isfile(item_path) and item.endswith(".py"):
            try:
                # 读取文件内容
                with open(item_path, "r", encoding="utf-8") as f: code = f.read()

                # 解析语法树提取函数
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    # 匹配普通函数和异步函数
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_name = node.name
                        directory[func_name] = func_name  # 按"函数名:函数名"格式更新
            except Exception as e:
                messagebox.showerror("处理失败", f"文件 {item} 处理出错: {str(e)}")
