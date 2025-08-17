import json
import os
import sys
from tkinter import messagebox


# -------------------------- 初始化路径与配置 --------------------------
# 获取程序根目录（当前脚本所在目录）
ROOT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

# 配置文件目录（src/config）
CONFIG_DIR = os.path.join(ROOT_DIR, 'src', 'config')

# 处理启动参数（若传入文件路径则记录）
user_file_path = sys.argv[1] if len(sys.argv) > 1 else None

# 默认文件配置（初始值）
DEFAULT_FILE_CONFIG = {
    "Root": ROOT_DIR,
    "ConfigDirectory": os.path.join(CONFIG_DIR, 'FileConfig.json'),
    "PersonalConfig": os.path.join(CONFIG_DIR, 'PersonalConfig.json'),
    "PythonDirectory": os.path.join(ROOT_DIR, 'Environment', 'python.exe'), # 运行时环境
    # "PythonDirectory": os.path.join(ROOT_DIR, 'python.exe'), # 编译时环境
    "ICON": os.path.join(ROOT_DIR, 'src', 'static', 'logo.ico'),
    "SourceCodePath": "",
    "CodeName": "",
}

# 默认个性化配置（初始值）
DEFAULT_PERSONAL_CONFIG = {
    "fontSize": 25,
    "darkMode": True,
    "highlightSyntax": True,
    "windowTop": False,
}


# -------------------------- 配置文件操作 --------------------------
def init_file_config():
    """初始化配置文件（若不存在则创建，存在则不覆盖）"""
    try:
        # 确保配置目录存在
        os.makedirs(CONFIG_DIR, exist_ok=True)

        # 初始化文件配置（FileConfig.json）
        file_config_path = DEFAULT_FILE_CONFIG["ConfigDirectory"]
        if not os.path.exists(file_config_path):
            with open(file_config_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_FILE_CONFIG, f, ensure_ascii=False, indent=4)

        # 初始化个性化配置（PersonalConfig.json）
        personal_config_path = DEFAULT_FILE_CONFIG["PersonalConfig"]
        if not os.path.exists(personal_config_path):
            with open(personal_config_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_PERSONAL_CONFIG, f, ensure_ascii=False, indent=4)

        # 处理启动参数中的文件路径（延迟导入避免循环依赖）
        if user_file_path:
            from src.utils.FileOps import split_file_path
            split_file_path(user_file_path)

    except Exception as e:
        messagebox.showerror("配置初始化失败", f"初始化配置文件时出错：\n{str(e)}")


def read_config(file_name, key=None):
    """
    读取配置文件内容

    参数:
        file_name: 配置文件名（如"FileConfig.json"）
        key: 可选，要读取的键名，不指定则返回整个配置字典

    返回:
        配置值（key存在时）或配置字典（key不存在时），失败返回None
    """
    # 构建完整配置文件路径
    config_path = os.path.join(CONFIG_DIR, file_name)

    try:
        if not os.path.exists(config_path):
            messagebox.showerror("文件不存在", f"配置文件未找到：\n{config_path}")
            return None

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        if key is None:
            return config_data  # 返回整个配置
        else:
            return config_data.get(key)  # 返回指定键值

    except json.JSONDecodeError:
        messagebox.showerror("格式错误", f"配置文件格式无效（JSON解析失败）：\n{config_path}")
    except Exception as e:
        messagebox.showerror("读取失败", f"读取配置文件时出错：\n{str(e)}")

    return None


def update_config(file_name, key, new_value=None):
    """
    更新配置文件内容

    参数:
        file_name: 配置文件名（如"FileConfig.json"）
        key: 要更新的键名，若new_value为None则key视为完整配置字典
        new_value: 新值，若为None则直接写入key作为配置字典

    返回:
        成功返回True，失败返回False
    """
    config_path = os.path.join(CONFIG_DIR, file_name)

    try:
        if new_value is None:
            # 直接覆盖整个配置文件（key作为完整配置字典）
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(key, f, ensure_ascii=False, indent=4)
            return True

        # 部分更新（更新指定键）
        if not os.path.exists(config_path):
            messagebox.showerror("文件不存在", f"配置文件未找到：\n{config_path}")
            return False

        # 读取现有配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 更新键值
        config_data[key] = new_value

        # 写入更新后的配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

        return True

    except json.JSONDecodeError:
        messagebox.showerror("格式错误", f"配置文件格式无效（JSON解析失败）：\n{config_path}")
    except Exception as e:
        messagebox.showerror("更新失败", f"更新配置文件时出错：\n{str(e)}")

    return False