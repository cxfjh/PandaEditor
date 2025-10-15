import os
import re
import shutil
import threading
import subprocess
from tkinter import messagebox
from src.utils.Config import read_config
from src.module.StandardLibrary import Grammar, Symbols


# 字符映射（中文符号转Python符号）
CHARACTER_MAPPING = {"“": '"',  "”": '"'}

# 匹配语法关键词（带边界，避免部分匹配）
GRAMMAR_PATTERN = re.compile(r'(?<![\w\u4e00-\u9fff])(' + '|'.join(map(re.escape, Grammar.keys())) + r')(?![\w\u4e00-\u9fff])')

# 匹配符号
SYMBOLS_PATTERN = re.compile('|'.join(map(re.escape, Symbols.keys())))

# 匹配需要替换的字符
CHARACTER_PATTERN = re.compile('|'.join(map(re.escape, CHARACTER_MAPPING.keys())))


def _get_config():
    """获取配置信息（替代全局变量，避免状态混乱）"""
    python_dir = read_config("FileConfig.json", "PythonDirectory") # Python路径
    source_code_path = read_config("FileConfig.json", "SourceCodePath") # 源代码路径
    code_name = read_config("FileConfig.json", "CodeName") # 代码名称
    icon_path = read_config("FileConfig.json", "ICON")  # 从配置读取图标路径，避免硬编码
    exe_path = os.path.join(source_code_path, code_name) if (source_code_path and code_name) else ""
    code_path = f"{exe_path}.py" if exe_path else ""

    return {
        "python_dir": python_dir,
        "exe_path": exe_path,
        "code_path": code_path,
        "icon_path": icon_path,
        "code_name": code_name
    }


def _protect_parts(code_str):
    """保护“”包裹的内容（用占位符替换，避免解析干扰）"""
    protected_parts = re.findall(r'“([^”]*)”', code_str)
    placeholders = {}
    for i, part in enumerate(protected_parts):
        placeholder = f'__PROTECTED_{i}__'
        placeholders[placeholder] = part
        code_str = code_str.replace(f'“{part}”', placeholder)
    return code_str, placeholders


def _restore_parts(code_str, placeholders):
    """还原被保护的内容（将占位符替换回原始内容）"""
    for placeholder, part in placeholders.items(): code_str = code_str.replace(placeholder, f'“{part}”')
    return code_str


def parse_code(code_str):
    """ 解析代码（替换中文关键词、符号为Python语法） """
    try:
        config = _get_config()
        # 检查配置完整性
        if not all([config["python_dir"], config["code_path"]]):
            messagebox.showerror("配置错误", "请先指定文件路径（打开或保存文件）")
            return False

        # 替换语法关键词（使用预编译正则）
        protected_str, placeholders = _protect_parts(code_str) # 保护特殊部分
        parsed_str = GRAMMAR_PATTERN.sub(lambda m: Grammar[m.group(0)], protected_str) # 替换语法关键词（使用预编译正则）
        parsed_str = SYMBOLS_PATTERN.sub(lambda m: Symbols[m.group(0)], parsed_str) # 替换符号（使用预编译正则）
        parsed_str = _restore_parts(parsed_str, placeholders) # 还原保护部分
        parsed_str = CHARACTER_PATTERN.sub(lambda m: CHARACTER_MAPPING[m.group(0)], parsed_str) # 替换中文特殊字符（使用预编译正则）

        # 写入Python文件
        os.makedirs(os.path.dirname(config["code_path"]), exist_ok=True)
        with open(config["code_path"], 'w', encoding='utf-8') as f: f.write(parsed_str)

        return True
    except Exception as e:
        messagebox.showerror("代码解析失败", f"解析错误：\n{str(e)}")
        return False


def _run_thread():
    """运行代码的线程函数（内部处理，含详细错误反馈）"""
    try:
        config = _get_config()
        if not os.path.exists(config["code_path"]):
            messagebox.showerror("文件不存在", f"代码文件未找到：\n{config['code_path']}")
            return

        # 执行代码（捕获输出，便于调试）
        subprocess.run([config["python_dir"], config["code_path"]], cwd=os.path.dirname(config["code_path"]))
    except Exception as e:
        messagebox.showerror("线程运行失败", f"运行时错误：\n{str(e)}")


def run_code(text_code):
    """运行代码入口（解析成功后启动线程）"""
    if parse_code(text_code):  # 解析成功才启动线程
        try:
            # 启动守护线程（避免程序退出后残留）
            thread = threading.Thread(target=_run_thread, daemon=True)
            thread.start()
        except Exception as e:
            messagebox.showerror("线程启动失败", f"无法启动运行线程：\n{str(e)}")


def _compile_thread():
    """编译代码的线程函数（内部处理，分步构建命令）"""
    try:
        config = _get_config()
        if not all([config["python_dir"], config["code_path"], config["icon_path"]]):
            messagebox.showerror("配置错误", "缺少必要配置（路径或图标）")
            return

        # 构建PyInstaller基础命令
        cmd = [
            config["python_dir"], "-m", "PyInstaller",
            "-F",  # 单文件打包
            f"--distpath={config['exe_path']}",
            f"-i{config['icon_path']}",  # 图标路径（从配置读取）
            config["code_path"]
        ]

        # 若代码名以"-w"结尾，添加无控制台参数
        if config["code_name"].endswith("-w"): cmd.insert(3, "-w")  # 插入到"-F"之后

        # 执行编译命令（捕获输出）
        subprocess.run(cmd)

        # 编译成功后提示并打开目录
        messagebox.showinfo("编译完成", "代码已成功编译！")
        os.startfile(config["exe_path"])

        # 清理临时文件
        _delete_garbage(config["python_dir"])
    except subprocess.CalledProcessError as e:
        messagebox.showerror("编译命令失败", f"编译出错：\n{e.stderr}")
    except Exception as e:
        messagebox.showerror("编译线程失败", f"编译时错误：\n{str(e)}")


def compile_code(text_code):
    """编译代码入口（解析成功后启动线程）"""
    if parse_code(text_code):  # 解析成功才启动线程
        try:
            thread = threading.Thread(target=_compile_thread, daemon=True)
            thread.start()
            messagebox.showinfo("编译中", "正在编译代码，请等待...\n（请勿重复操作）")
        except Exception as e:
            messagebox.showerror("线程启动失败", f"无法启动编译线程：\n{str(e)}")


def _delete_garbage(root_dir):
    """清理编译生成的临时文件（build目录和.spec文件）"""
    try:
        # 从Python路径推导根目录（或直接从配置读取）
        root_path = os.path.dirname(root_dir)  # 适配路径结构

        # 清理build目录
        build_dir = os.path.join(root_path, "build")
        if os.path.exists(build_dir) and os.path.isdir(build_dir): shutil.rmtree(build_dir, ignore_errors=True)

        # 清理.spec文件
        for filename in os.listdir(root_path):
            if filename.endswith('.spec'):
                spec_file = os.path.join(root_path, filename)
                if os.path.isfile(spec_file): os.remove(spec_file)
    except Exception as e:
        messagebox.showerror("临时文件", f"清理临时文件失败：{str(e)}")
