import os
from tkinter import filedialog, messagebox
from src.utils.Config import update_config, read_config


def split_file_path(file_path):
    """ 解析文件路径，提取目录和文件名并更新配置 """
    if not file_path: return

    # 分割路径和文件名（跨平台兼容）
    file_dir, file_name = os.path.split(file_path)
    base_name, _ = os.path.splitext(file_name) # 分割文件名和扩展名

    # 更新配置（使用os.path.normpath标准化路径）
    update_config("FileConfig.json", "CodeName", base_name)
    update_config("FileConfig.json", "SourceCodePath", os.path.normpath(file_dir))


def open_file():
    """ 打开文件对话框，选择.cn文件并更新配置 """
    try:
        # 打开文件选择对话框（仅显示.cn文件）
        file_path = filedialog.askopenfilename(filetypes=[("CN Files", "*.cn")], title="打开CN文件")
        if not file_path: return  # 用户取消选择

        # 标准化路径（处理斜杠/反斜杠问题）
        normalized_path = os.path.normpath(file_path)
        split_file_path(normalized_path)
    except Exception as e: messagebox.showerror("打开文件失败", f"无法打开文件：\n{str(e)}")


def save_file(content):
    """ 保存内容到当前文件（基于配置中的路径和文件名） """
    try:
        # 从配置获取路径和文件名
        source_dir = read_config("FileConfig.json", "SourceCodePath")
        code_name = read_config("FileConfig.json", "CodeName")

        # 检查配置是否完整
        if not all([source_dir, code_name]):
            messagebox.showwarning("保存失败", "请先指定保存路径（使用另存为）")
            return

        # 构建完整文件路径
        file_path = os.path.normpath(os.path.join(source_dir, f"{code_name}.cn"))

        # 写入内容（确保目录存在）
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f: f.write(content)
    except Exception as e: messagebox.showerror("保存文件失败", f"保存失败：\n{str(e)}")


def save_as_file(content):
    """ 另存为对话框，选择新路径保存内容并更新配置 """
    try:
        # 打开另存为对话框
        file_path = filedialog.asksaveasfilename(filetypes=[("CN Files", "*.cn")], defaultextension=".cn", title="另存为CN文件")
        if not file_path:  return # 用户取消选择

        # 标准化路径
        normalized_path = os.path.normpath(file_path)
        os.makedirs(os.path.dirname(normalized_path), exist_ok=True) # 确保目录存在

        # 写入内容
        with open(normalized_path, "w", encoding="utf-8") as f: f.write(content)

        # 更新配置
        split_file_path(normalized_path)
    except Exception as e: messagebox.showerror("另存文件失败", f"另存失败：\n{str(e)}")


def read_file_content():
    """ 读取当前配置中指定的文件内容 """
    try:
        # 从配置获取路径和文件名
        source_dir = read_config("FileConfig.json", "SourceCodePath")
        code_name = read_config("FileConfig.json", "CodeName")

        # 检查配置是否完整
        if not all([source_dir, code_name]): return None
        file_path = os.path.normpath(os.path.join(source_dir, f"{code_name}.cn")) # 构建完整路径

        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 清除无效配置
            update_config("FileConfig.json", "SourceCodePath", "")
            update_config("FileConfig.json", "CodeName", "")
            return None

        # 读取内容
        with open(file_path, "r", encoding="utf-8") as f: return f.read()
    except Exception as e:
        messagebox.showerror("读取文件失败", f"无法获取文件内容：\n{str(e)}")
        return None
