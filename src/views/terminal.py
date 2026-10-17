import os
from typing import Callable, Optional
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget
from src.utils.config_service import get_config_service
from src.views.components.handlers import is_current_file_cn
from src.utils.code_proc import parse_code


# 终端深色主题样式常量
_TERMINAL_BG = "#1e1f22"
_TERMINAL_FG = "#A9B7C6"
_TERMINAL_INPUT_BG = "#2b2d30"
_TERMINAL_BORDER = "#3c3f41"

# 终端输出最大行数限制
_MAX_OUTPUT_LINES = 5000

# 命令分发映射表
_COMMAND_HANDLERS = {
    "help": "_show_help",
    "cls": "_clear_screen",
    "pwd": "_show_pwd",
    "run": "_run_code",
    "ls": "_list_all_packages",
}


class TerminalWidget(QWidget):
    """终端组件"""

    def __init__(self, parent=None):
        """
        初始化终端组件
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        self.setObjectName("TerminalWidget")

        # 核心组件和状态变量
        self._process = QProcess(self)  # 子进程管理器
        self._current_dir = os.getcwd()  # 当前工作目录
        self._command_history: list[str] = []  # 命令历史记录列表
        self._history_index: int = -1  # 当前浏览的历史记录索引
        self._running_code = False  # 标记是否正在运行Python代码
        self._get_code_callback: Optional[Callable[[], str]] = None  # 回调函数用于从编辑器获取当前代码

        # 初始化UI和进程
        self._setup_ui()
        self._setup_process()

    def _setup_ui(self):
        """初始化终端 UI 布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # 极窄边距
        layout.setSpacing(0)  # 无间距

        # 输出区域
        self._output = QPlainTextEdit(self)
        self._output.setReadOnly(True)  # 只读，不允许用户直接编辑输出
        self._output.setFont(QFont("Cascadia Code", 10))
        self._output.setStyleSheet(f"QPlainTextEdit {{ background-color: {_TERMINAL_BG}; " f"color: {_TERMINAL_FG}; border: none; border-top: 1px solid {_TERMINAL_BORDER}; }}")
        self._output.setUndoRedoEnabled(False)  # 禁用撤销/重做
        self._output.setMaximumBlockCount(_MAX_OUTPUT_LINES)  # 限制最大行数，防止内存溢出

        # 输入行容器
        input_container = QWidget(self)
        input_container.setStyleSheet(f"QWidget {{ background-color: {_TERMINAL_INPUT_BG}; }}", )
        input_container.setFixedHeight(30)  # 固定高度
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(4, 2, 4, 2)
        input_layout.setSpacing(0)

        # 输入行
        self._input = _TerminalLineEdit(self)
        self._input.setFont(QFont("Cascadia Code", 10))
        self._input.setStyleSheet(f"QLineEdit {{ background-color: {_TERMINAL_INPUT_BG}; " f"color: {_TERMINAL_FG}; border: none; }}", )
        self._input.setPlaceholderText("输入命令后按 Enter 执行...")
        self._input.returnPressed.connect(self._on_submit)  # 回车键触发命令执行

        # 组装布局
        input_layout.addWidget(self._input)
        layout.addWidget(self._output)
        layout.addWidget(input_container)

        # 显示欢迎信息
        self._append_output("> 熊猫编辑器终端")
        self._append_output("> 输入 help 查看可用命令\n")

    def _setup_process(self):
        """初始化子进程配置"""
        self._process.setWorkingDirectory(self._current_dir)  # 设置初始工作目录
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)  # 合并标准输出和标准错误
        self._process.readyReadStandardOutput.connect(self._on_ready_read)  # 标准输出就绪信号
        self._process.readyReadStandardError.connect(self._on_ready_read)  # 标准错误就绪信号
        self._process.finished.connect(self._on_process_finished)  # 进程结束信号
        self._process.errorOccurred.connect(self._on_process_error)  # 进程错误信号

    def apply_theme(self, dark_mode: bool):
        """
        应用主题样式
        
        Args:
            dark_mode: True=深色主题，False=浅色主题
        """
        if dark_mode:
            bg, fg, input_bg, border_color = _TERMINAL_BG, _TERMINAL_FG, _TERMINAL_INPUT_BG, _TERMINAL_BORDER
        else:
            bg, fg, input_bg, border_color = "#FFFFFF", "#000000", "#F0F0F0", "#D1D5DB"

        self.setStyleSheet(f"QWidget#TerminalWidget {{ background-color: {bg}; border: 1px solid {border_color}; }}")
        self._output.setStyleSheet(f"QPlainTextEdit {{ background-color: {bg}; color: {fg}; border: none; border-top: 1px solid {border_color}; }}")
        self._input.setStyleSheet(f"QLineEdit {{ background-color: {input_bg}; color: {fg}; border: none; }}")

    def _append_output(self, text: str):
        """追加输出文本"""
        self._output.appendPlainText(text)

    def append_output(self, text: str):
        """追加输出文本"""
        self._append_output(text)

    def _on_submit(self):
        """处理用户提交命令"""
        command = self._input.text()
        self._input.clear()

        # 如果正在运行代码将输入发送给进程
        if self._running_code:
            self._process.write(command.encode("utf-8") + b"\n")  # 发送输入+换行符
            self._append_output(command)  # 回显用户输入
            return

        # 命令模式下空输入直接返回
        if not command.strip():
            return

        # 显示命令回显
        self._append_output(f"> {command.strip()}")

        # 记录命令历史
        self._command_history.append(command.strip())
        self._history_index = len(self._command_history)  # 索引指向最新位置
        self._execute_command(command.strip())

    def _execute_command(self, command: str):
        """
        执行命令
        
        Args:
            command: 用户输入的命令字符串
        """
        cmd_lower = command.lower()

        # 精确匹配内部命令
        if cmd_lower in _COMMAND_HANDLERS:
            getattr(self, _COMMAND_HANDLERS[cmd_lower])()  # 动态调用对应方法
            return

        # 前缀匹配带参数的命令
        if cmd_lower.startswith("cd "):
            self._change_directory(command[3:].strip())  # 提取路径参数
            return
        if cmd_lower.startswith("add "):
            self._install_package(command[4:].strip())  # 提取包名参数
            return
        if cmd_lower.startswith("del "):
            self._uninstall_package(command[4:].strip())  # 提取包名参数
            return

        # 外部命令
        self._process.start("cmd.exe", ["/c", command])  # /c 表示执行后关闭

    def _clear_screen(self):
        """清空终端"""
        self._output.clear()

    def _show_pwd(self):
        """显示当前目录"""
        self._append_output(self._current_dir)

    def _show_help(self):
        """显示帮助信息"""
        help_text = (
            "\n内部命令:\n"
            "  help             - 显示此帮助信息 (help)\n"
            "  cls              - 清空终端 (cls)\n"
            "  cd <path>        - 切换目录 (cd d:\\)\n"
            "  pwd              - 显示当前目录 (pwd)\n"
            "  run              - 运行当前代码 (run)\n"
            "  add <package>    - 安装库 (add requests)\n"
            "  del <package>    - 卸载库 (del requests)\n"
            "  ls               - 列出所有的库 (ls)\n\n"
            "\n外部命令:\n"
            "  支持执行系统命令 (如 dir, echo, pause 等)\n"
        )
        self._append_output(help_text)

    def set_get_code_callback(self, callback):
        """设置获取代码的回调函数"""
        self._get_code_callback = callback

    def _get_python_dir(self):
        """获取 Python 目录未配置时输出错误信息"""
        python_dir = get_config_service().get_app_config("python_path")
        if not python_dir:
            self._append_output("错误: 未配置Python路径")
        return python_dir

    def _install_package(self, package_name: str):
        """
        安装Python库
        
        Args:
            package_name: 要安装的库名称
        """
        if not package_name:
            self._append_output("错误: 请指定要安装的库名称")
            self._append_output("用法: add <库名>")
            return

        python_dir = self._get_python_dir()
        if not python_dir:
            return

        # 构建 pip 命令参数
        pip_args = ["-m", "pip", "install", package_name]

        # 检查是否配置了淘宝镜像源
        mirror = get_config_service().get_personal_config("pipMirror")
        if mirror == "taobao":
            pip_args.extend(["-i", "https://mirrors.aliyun.com/pypi/simple/"])

        self._append_output(f"正在安装 {package_name}...")
        self._process.start(python_dir, pip_args)

    def _uninstall_package(self, package_name: str):
        """卸载Python库"""
        if not package_name:
            self._append_output("错误: 请指定要卸载的库名称")
            self._append_output("用法: del <库名>")
            return

        python_dir = self._get_python_dir()
        if not python_dir:
            return

        self._append_output(f"正在卸载 {package_name}...")
        self._process.start(python_dir, ["-m", "pip", "uninstall", "-y", package_name])

    def _list_all_packages(self):
        """列出所有已安装的Python库"""
        python_dir = self._get_python_dir()
        if not python_dir:
            return

        self._append_output("正在获取已安装的库列表...")
        self._process.start(python_dir, ["-m", "pip", "list"])

    def _run_code(self):
        """运行解析后的 Python 代码文件"""
        if not self._get_code_callback:
            self._append_output("错误: 未设置代码回调，无法运行！")
            return

        # 检查当前文件是否为 .cn 格式
        if not is_current_file_cn():
            self._append_output("错误: 只能运行 .cn 格式的中文代码文件！")
            return

        # 通过回调获取编辑器中的代码内容
        code_text = self._get_code_callback()
        if not code_text:
            self._append_output("错误: 代码为空！")
            return

        # 解析中文代码为 Python 代码
        if not parse_code(code_text):
            self._append_output("错误: 代码解析失败！")
            return

        # 获取运行所需的配置
        python_dir = get_config_service().get_app_config("python_path")
        source_code_path = get_config_service().get_file_config("source_code_path")
        code_name = get_config_service().get_file_config("code_name")

        # 验证必要配置是否完整
        if not all([python_dir, source_code_path, code_name]):
            self._append_output("错误: 缺少必要配置，无法运行代码！")
            return

        # 构建代码文件路径
        code_path = os.path.join(source_code_path, f"{code_name}.py")
        if not os.path.isfile(code_path):
            self._append_output(f"错误: 代码文件不存在：\n{code_path}")
            return

        # 标记为运行状态启动 Python 进程
        self._running_code = True
        self._append_output(f"正在运行: {code_path}\n")
        self._process.start(python_dir, ["-u", code_path])

    def set_working_directory(self, path: str):
        """设置工作目录"""
        if os.path.isdir(path):
            self._current_dir = path
            self._process.setWorkingDirectory(path)

    def _change_directory(self, path: str):
        """
        切换工作目录
        
        Args:
            path: 目标目录路径
        """
        if not path:
            self._append_output(self._current_dir)  # 无参数时显示当前目录
            return

        # 处理路径：绝对路径直接使用，相对路径基于当前目录拼接
        new_dir = os.path.normpath(path if os.path.isabs(path) else os.path.join(self._current_dir, path))
        if os.path.isdir(new_dir):
            self._current_dir = new_dir
            self._process.setWorkingDirectory(new_dir)  # 更新进程工作目录
            self._append_output(f"已切换到: {new_dir}")
        else:
            self._append_output(f"目录不存在: {path}")

    @staticmethod
    def _decode_process_data(raw_data) -> str:
        """
        解码进程输出数据
        
        Args:
            raw_data: QProcess 输出的原始字节数据
            
        Returns:
            解码后的字符串
        """
        data = bytes(raw_data.data())
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("gbk", errors="ignore")  # 忽略无法解码的字符

    def _on_ready_read(self):
        """进程输出就绪时调用"""
        raw_data = self._process.readAllStandardOutput()
        if not raw_data.isEmpty():
            self._append_output(self._decode_process_data(raw_data).rstrip())  # 去除末尾空白

    def _on_process_finished(self, exit_code: int):
        """
        进程结束时调用
        
        Args:
            exit_code: 进程退出码（0=成功，非0=失败）
        """
        self._running_code = False  # 重置运行状态
        if exit_code != 0:
            # 非零退出码，读取并显示错误信息
            raw_error = self._process.readAllStandardError()
            if not raw_error.isEmpty():
                error_text = self._decode_process_data(raw_error)
                if error_text:
                    self._append_output(f"错误: {error_text.rstrip()}")
        else:
            # 正常退出
            self._append_output("\n> 执行完毕\n")

    def _on_process_error(self, error):
        """
        进程发生错误时调用
        
        Args:
            error: QProcess.Error 枚举值
        """
        self._running_code = False
        self._append_output(f"\n进程错误: {error}")

    def get_history_prev(self) -> str | None:
        """
        获取上一条历史命令
        
        Returns:
            上一条命令文本，如果没有更多历史则返回 None
        """
        if not self._command_history:
            return None
        if self._history_index > 0:
            self._history_index -= 1  # 索引向前移动
        return self._command_history[self._history_index]

    def get_history_next(self) -> str | None:
        """
        获取下一条历史命令
        
        Returns:
            下一条命令文本，如果已是最新位置则返回空字符串
        """
        if not self._command_history:
            return None
        if self._history_index < len(self._command_history) - 1:
            self._history_index += 1  # 索引向后移动
            return self._command_history[self._history_index]
        self._history_index = len(self._command_history)  # 重置到最新位置
        return ""  # 返回空字符串表示清除输入框


class _TerminalLineEdit(QLineEdit):
    """终端输入框"""

    def __init__(self, terminal: TerminalWidget):
        """
        初始化终端输入框

        Args:
            terminal: 关联的 TerminalWidget 实例
        """
        super().__init__()
        self._terminal = terminal

    def keyPressEvent(self, event):
        """
        拦截键盘事件，处理上下键浏览历史
        
        Args:
            event: 键盘事件对象
        """
        key = event.key()

        # 上箭头键获取上一条历史命令
        if key == Qt.Key.Key_Up:
            history = self._terminal.get_history_prev()
            if history is not None:
                self.setText(history)  # 填充到输入框
            return

        # 下箭头键获取下一条历史命令
        if key == Qt.Key.Key_Down:
            history = self._terminal.get_history_next()
            if history is not None:
                self.setText(history)  # 填充到输入框
            return

        # 其他按键交给父类处理
        super().keyPressEvent(event)
