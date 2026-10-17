import hashlib
import os
import re
import shutil
import subprocess
import threading
from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal
from src.module.grammar import grammar, symbols
from src.utils.config_service import get_config_service
from src.utils.dialog_utils import DialogUtils


# 全局父窗口引用用于对话框的模态显示
_parent_widget = None

# 解析结果缓存
_PARSE_CACHE: Dict[str, str] = { }
_CACHE_MAX_SIZE = 100  # 最大缓存条目数
_CACHE_ENABLED = True  # 是否启用缓存


class _DialogSignals(QObject):
    """跨线程弹窗信号类，用于子线程向主线程发送弹窗请求，避免跨线程 UI 操作导致崩溃"""
    error = Signal(str, str, str)
    compile_finished = Signal(bool, str)
    compile_log = Signal(str)  # 编译日志输出信号


# 全局信号实例
signals = _DialogSignals()


def _on_error(title: str, msg: str, detail: str) -> None:
    """
    错误弹窗槽函数

    Args:
        title: 弹窗标题
        msg: 错误消息
        detail: 详细错误信息
    """
    DialogUtils.show_error(_parent_widget, title, msg, detail)


# 初始化信号槽连接
signals.error.connect(_on_error)


def set_parent_widget(widget) -> None:
    """
    设置父窗口引用

    Args:
        widget: 主窗口部件引用
    """
    global _parent_widget
    _parent_widget = widget


# 预编译正则表达式
CHARACTER_MAPPING: Dict[str, str] = { "\u201c": '"', "\u201d": '"' }
GRAMMAR_PATTERN = re.compile(fr'(?<![\w\u4e00-\u9fff])({"|".join(map(re.escape, grammar.keys()))})(?![\w\u4e00-\u9fff])')
SYMBOLS_PATTERN = re.compile('|'.join(map(re.escape, symbols.keys())))

# 预编译引号保护正则
_QUOTE_PROTECT_PATTERN = re.compile(r'[\u201c\u201d]([^\u201c\u201d]*)[\u201c\u201d]')
_QUOTE_RESTORE_PATTERN = re.compile(r'__PROTECTED_\d+__')

# 预编译注释检查
_COMMENT_PREFIX = '#'

# 引号保护/还原的占位符计数器
_protect_idx = 0
_protect_placeholders: Dict[str, str] = { }


def _protect_quote_match(match) -> str:
    """保护中文引号内容的回调函数"""
    global _protect_idx
    placeholder = f"__PROTECTED_{_protect_idx}__"
    _protect_placeholders[placeholder] = match.group(1)
    _protect_idx += 1
    return placeholder


def _restore_quote_match(match) -> str:
    """还原中文引号内容的回调函数"""
    placeholder = match.group(0)
    return f"\u201c{_protect_placeholders.get(placeholder, '')}\u201d"


def _reset_protect_state():
    """重置引号保护状态"""
    global _protect_idx
    _protect_idx = 0
    _protect_placeholders.clear()


def _get_code_hash(code: str) -> str:
    """
    生成代码内容的哈希值
    
    Args:
        code: 代码内容字符串
        
    Returns:
        MD5 哈希值字符串
    """
    return hashlib.md5(code.encode('utf-8')).hexdigest()


def _process_line_fast(line: str) -> str:
    """
    快速处理单行代码
    
    Args:
        line: 单行代码
        
    Returns:
        处理后的代码行
    """
    # 空行或纯空白行直接返回
    if not line or line.isspace():
        return line

    # 注释行直接返回
    stripped = line.lstrip()
    if stripped.startswith(_COMMENT_PREFIX):
        return line

    # 不包含中文引号的行跳过保护/还原步骤
    has_chinese_quotes = '\u201c' in line or '\u201d' in line

    if has_chinese_quotes:
        # 需要保护引号内容
        _reset_protect_state()
        protected_str = _QUOTE_PROTECT_PATTERN.sub(_protect_quote_match, line)
        parsed_str = GRAMMAR_PATTERN.sub(lambda m: grammar[m.group(0)], protected_str)
        parsed_str = SYMBOLS_PATTERN.sub(lambda m: symbols[m.group(0)], parsed_str)

        # 还原引号内容
        parsed_str = _QUOTE_RESTORE_PATTERN.sub(_restore_quote_match, parsed_str)
    else:
        # 无需保护引号，直接替换
        parsed_str = GRAMMAR_PATTERN.sub(lambda m: grammar[m.group(0)], line)
        parsed_str = SYMBOLS_PATTERN.sub(lambda m: symbols[m.group(0)], parsed_str)

    # 字符映射替换
    if '\u201c' in parsed_str or '\u201d' in parsed_str:
        parsed_str = parsed_str.replace('\u201c', '"').replace('\u201d', '"')

    return parsed_str


def _get_config() -> Optional[dict]:
    """
    从配置文件读取路径信息

    Returns:
        包含路径信息的字典，若配置不完整则返回 None。
        字典结构：
            - python_dir: Python 解释器路径
            - source_code_path: 源代码目录
            - exe_path: 可执行文件路径不含扩展名
            - code_path: 生成的 Python 代码文件路径.py
            - icon_path: 应用图标路径
            - code_name: 代码文件名
            - root: 项目根目录
    """
    try:
        root = get_config_service().get_app_config("root_dir")
        python_dir = get_config_service().get_app_config("python_path")
        source_code_path = get_config_service().get_file_config("source_code_path")
        code_name = get_config_service().get_file_config("code_name")
        icon_path = get_config_service().get_app_config("icon_path")

        # 校验必要配置项是否完整
        if not all([python_dir, source_code_path, code_name, root]): return None
        exe_path = os.path.join(source_code_path, code_name)
        code_path = f"{exe_path}.py"

        # 返回配置信息
        return {
            "python_dir": python_dir,
            "source_code_path": source_code_path,
            "exe_path": exe_path,
            "code_path": code_path,
            "icon_path": icon_path,
            "code_name": code_name,
            "root": root,
        }
    except Exception as e:
        print(f"配置读取异常: {e}")
        return None


def parse_code(code_str: str, file_path: Optional[str] = None) -> bool:
    """
    中文代码到 Python 代码的解析转换

    Args:
        code_str: 中文代码字符串
        file_path: 当前 .cn 文件路径（可选，如果不提供则从配置读取）

    Returns:
        转换是否成功
    """
    try:
        # 读取配置信息
        config = _get_config()
        if not config:
            DialogUtils.show_error(_parent_widget, "配置错误", "请先正确配置文件路径！")
            return False

        # 如果提供了文件路径，使用它来覆盖配置中的路径
        if file_path:
            file_dir, file_name = os.path.split(file_path)
            base_name, _ = os.path.splitext(file_name)
            config["source_code_path"] = file_dir
            config["code_name"] = base_name
            config["exe_path"] = os.path.join(file_dir, base_name)
            config["code_path"] = f"{config['exe_path']}.py"

        # 确保输出目录存在
        os.makedirs(os.path.dirname(config["code_path"]), exist_ok=True)  # type: ignore

        # 检查缓存
        code_hash = _get_code_hash(code_str) if _CACHE_ENABLED else None
        if code_hash and code_hash in _PARSE_CACHE:
            parsed_str = _PARSE_CACHE[code_hash]
            with open(config["code_path"], "w", encoding="utf-8") as f:
                f.write(parsed_str)
            return True

        # 按行分割，优化处理流程
        lines = code_str.split('\n')
        processed_lines = []

        # 使用快速路径处理每行
        for line in lines:
            processed_lines.append(_process_line_fast(line))

        # 合并所有行
        parsed_str = '\n'.join(processed_lines)

        # 写入缓存
        if code_hash:
            # LRU 策略：缓存满时删除一半旧条目
            if len(_PARSE_CACHE) >= _CACHE_MAX_SIZE:
                keys_to_remove = list(_PARSE_CACHE.keys())[:_CACHE_MAX_SIZE // 2]
                for key in keys_to_remove:
                    del _PARSE_CACHE[key]
            _PARSE_CACHE[code_hash] = parsed_str

        # 写入 Python 文件
        with open(config["code_path"], "w", encoding="utf-8") as f:
            f.write(parsed_str)
        return True
    except Exception as e:
        DialogUtils.show_error(_parent_widget, "代码解析失败", f"解析异常：\n{str(e)}")
        return False


_compile_file_path: Optional[str] = None  # 编译时使用的文件路径
_run_file_path: Optional[str] = None  # 运行时使用的文件路径


def _run_thread() -> None:
    """执行 Python 代码的线程任务"""
    config = _get_config()

    # 如果运行时指定了文件路径，使用它来覆盖配置中的路径
    global _run_file_path
    if _run_file_path:
        file_dir, file_name = os.path.split(_run_file_path)
        base_name, _ = os.path.splitext(file_name)
        config["source_code_path"] = file_dir  # type: ignore
        config["code_name"] = base_name  # type: ignore
        config["exe_path"] = os.path.join(file_dir, base_name)  # type: ignore
        config["code_path"] = f"{config['exe_path']}.py"  # type: ignore
        _run_file_path = None  # 使用后清空

    # 校验必要配置项是否完整
    if not config or not os.path.exists(config["code_path"]):
        signals.error.emit("错误", "代码文件不存在，请先保存！", "")
        return

    try:
        # 执行 Python 代码
        subprocess.run([config["python_dir"], config["code_path"]], cwd=config["source_code_path"])
    except subprocess.CalledProcessError as e:
        signals.error.emit("运行错误", f"代码执行失败：\n{e.stderr}", "")
    except Exception as e:
        signals.error.emit("运行异常", f"运行失败：\n{str(e)}", "")


def run_code(text_code: str, file_path: Optional[str] = None) -> None:
    """
    运行代码入口函数

    Args:
        text_code: 中文代码文本
        file_path: 当前 .cn 文件路径（可选）
    """
    global _run_file_path
    _run_file_path = file_path
    if parse_code(text_code, file_path):
        thread = threading.Thread(target=_run_thread, daemon=True)
        thread.start()


def _compile_thread() -> None:
    """PyInstaller 打包线程任务"""
    config = _get_config()
    if not config:
        signals.error.emit("配置错误", "缺少必要配置，无法编译！", "")
        return

    # 如果编译时指定了文件路径，使用它来覆盖配置中的路径
    global _compile_file_path
    if _compile_file_path:
        file_dir, file_name = os.path.split(_compile_file_path)
        base_name, _ = os.path.splitext(file_name)
        config["source_code_path"] = file_dir
        config["code_name"] = base_name
        config["exe_path"] = os.path.join(file_dir, base_name)
        config["code_path"] = f"{config['exe_path']}.py"
        _compile_file_path = None  # 使用后清空

    # 检查同级目录是否有 icon.ico
    code_dir = os.path.dirname(config["code_path"])
    local_icon = os.path.join(code_dir, "icon.ico")  # type: ignore[arg-type]

    # 从配置读取编译图标设置
    use_default_icon = get_config_service().get_personal_config("useDefaultCompileIcon")

    if use_default_icon:
        # 使用默认图标：优先项目目录下的 icon.ico，其次配置中的 icon_path
        icon_path = local_icon if os.path.isfile(local_icon) else config.get("icon_path")
    else:
        # 使用自定义图标
        custom_icon = get_config_service().get_personal_config("compileIconPath")
        if custom_icon and os.path.isfile(custom_icon):
            icon_path = custom_icon
        elif os.path.isfile(local_icon):
            icon_path = local_icon
        else:
            icon_path = config.get("icon_path")

    # 从配置读取编译选项
    hide_window = get_config_service().get_personal_config("hideWindow")
    admin_privilege = get_config_service().get_personal_config("adminPrivilege")
    single_file = get_config_service().get_personal_config("singleFileMode")

    try:
        # 获取输出名称
        base_name = os.path.splitext(os.path.basename(config["code_path"]))[0]

        # 构建 PyInstaller 命令
        cmd = [
            config["python_dir"], "-m", "PyInstaller",
            "-F" if single_file else "-D",  # 单文件模式 / 目录模式
            f"--name={base_name}",  # 指定输出名称
            f"--distpath={config['source_code_path']}",  # 输出目录
            "--log-level=INFO",  # 输出详细日志
        ]

        # 添加图标
        if icon_path and os.path.isfile(icon_path):
            cmd.append(f"-i{icon_path}")

        # 如果配置了隐藏窗口添加-w参数
        if hide_window:
            cmd.append("-w")

        # 如果需要管理员权限，添加--uac-admin参数
        if admin_privilege:
            cmd.append("--uac-admin")

        # 添加资源文件/目录
        add_data_paths = get_config_service().get_personal_config("addDataPaths") or []
        for data_path in add_data_paths:
            if os.path.exists(data_path):
                target_dir = os.path.basename(data_path)
                cmd.append(f"--add-data={data_path}{os.pathsep}{target_dir}")

        cmd.append(config["code_path"])  # 入口文件

        # 执行打包
        process = subprocess.Popen(
            cmd,
            cwd=config["source_code_path"],
        )

        # 等待进程完成
        process.wait()

        if process.returncode == 0:
            # 目录模式（-D）需要将输出从子目录移动到源码目录
            if not single_file:
                dist_subdir = os.path.join(config['source_code_path'], base_name)
                if os.path.isdir(dist_subdir):
                    # 将 _internal 和 exe 移动到源码目录
                    for item in os.listdir(dist_subdir):
                        src_item = os.path.join(dist_subdir, item)
                        dst_item = os.path.join(config['source_code_path'], item)
                        if os.path.exists(dst_item):
                            if os.path.isdir(dst_item):
                                shutil.rmtree(dst_item)
                            else:
                                os.remove(dst_item)
                        shutil.move(src_item, dst_item)
                    # 删除空的子目录
                    shutil.rmtree(dist_subdir)

            # 打开编译输出目录
            subprocess.Popen(f'explorer "{config["source_code_path"]}"')

            # 清理临时文件
            _clean_build_files(config['source_code_path'])
            signals.compile_finished.emit(True, "")
        else:
            signals.compile_finished.emit(False, f"编译失败（退出码: {process.returncode}）")

    except subprocess.CalledProcessError:
        signals.compile_finished.emit(False, "PyInstaller 执行出错，请检查依赖与代码！")
    except Exception as e:
        signals.compile_finished.emit(False, f"打包失败：\n{str(e)}")


# 编译时使用的文件路径
_compile_file_path: Optional[str] = None  # type: ignore


def compile_code(text_code: str, file_path: Optional[str] = None) -> None:
    """
    编译代码入口函数

    Args:
        text_code: 中文代码文本
        file_path: 当前 .cn 文件路径（可选）
    """
    global _compile_file_path
    _compile_file_path = file_path
    if parse_code(text_code, file_path):
        thread = threading.Thread(target=_compile_thread, daemon=True)
        thread.start()


def _clean_build_files(work_dir: str) -> None:
    """
    清理 PyInstaller 生成的临时文件

    Args:
        work_dir: 项目工作目录
    """
    try:
        # 删除 build 目录
        build_path = os.path.join(work_dir, "build")
        if os.path.isdir(build_path): shutil.rmtree(build_path)

        # 删除 .spec 文件
        for file in os.listdir(work_dir):
            if file.endswith(".spec"):
                spec_path = os.path.join(work_dir, file)
                if os.path.isfile(spec_path): os.remove(spec_path)
    except Exception as e:
        signals.error.emit("清理异常", f"清理临时文件失败：\n{str(e)}", "")
