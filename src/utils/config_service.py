import json
import os
import sys
import threading
from typing import Any, Dict, Optional
from src.utils.exceptions import ConfigException


# 程序根目录
ROOT_DIR: str = os.path.abspath(os.path.dirname(sys.argv[0]))

# 配置目录
CONFIG_DIR: str = os.path.join(ROOT_DIR, "src", "config")

# 默认应用配置
DEFAULT_APP_CONFIG: Dict[str, Any] = {
    "root_dir": ROOT_DIR,
    "python_path": os.path.join(ROOT_DIR, "python.exe"),
    "icon_path": os.path.join(ROOT_DIR, "src", "static", "logo.ico"),
}

# 默认文件配置
DEFAULT_FILE_CONFIG: Dict[str, Any] = {
    "source_code_path": "",
    "code_name": "",
    "file_ext": ".cn",
}

# 默认会话配置
DEFAULT_SESSION_CONFIG: Dict[str, Any] = {
    "last_tabs": [],
    "last_active_tab": 0,
}

# 默认个性化配置
DEFAULT_PERSONAL_CONFIG: Dict[str, Any] = {
    "fontSize": 20,
    "darkMode": True,
    "highlightSyntax": True,
    "windowTop": False,
    "pipMirror": "taobao",
    "hideWindow": False,
    "adminPrivilege": False,
    "compileIconPath": "",
    "useDefaultCompileIcon": True,
    "singleFileMode": True,
    "addDataPaths": [],
}


class ConfigService:
    """
    配置服务单例类

    Attributes:
        _cache: 配置缓存字典，格式为 {文件名: 配置字典}
        _initialized: 初始化状态标志
    """
    _instance: Optional["ConfigService"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._initialized = None

    def __new__(cls) -> "ConfigService":
        """
        单例模式实现

        Returns:
            ConfigService 单例实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = { }
                    cls._instance._initialized = False
        assert cls._instance is not None
        return cls._instance

    def init_config(self) -> None:
        """
        初始化配置文件

        Raises:
            ConfigException: 配置初始化失败时抛出
        """
        if self._initialized:
            return

        try:
            # 创建配置目录
            os.makedirs(CONFIG_DIR, exist_ok=True)

            # 获取默认配置文件路径
            app_config_path = os.path.join(CONFIG_DIR, "AppConfig.json")
            file_config_path = os.path.join(CONFIG_DIR, "FileConfig.json")
            session_config_path = os.path.join(CONFIG_DIR, "SessionConfig.json")
            personal_config_path = os.path.join(CONFIG_DIR, "PersonalConfig.json")

            # 创建默认配置文件
            if not os.path.exists(app_config_path): self._write_json(app_config_path, DEFAULT_APP_CONFIG)
            if not os.path.exists(file_config_path): self._write_json(file_config_path, DEFAULT_FILE_CONFIG)
            if not os.path.exists(session_config_path): self._write_json(session_config_path, DEFAULT_SESSION_CONFIG)
            if not os.path.exists(personal_config_path): self._write_json(personal_config_path, DEFAULT_PERSONAL_CONFIG)

            # 编译环境下使用内置 Python
            if not hasattr(sys.modules.get("__main__"), "__compiled__"):
                DEFAULT_APP_CONFIG["python_path"] = os.path.join(ROOT_DIR, "Environment", "python.exe")
                self.update_app_config("python_path", DEFAULT_APP_CONFIG["python_path"])

            # 加载配置到缓存
            self._load_from_file("AppConfig.json")
            self._load_from_file("FileConfig.json")
            self._load_from_file("SessionConfig.json")
            self._load_from_file("PersonalConfig.json")

            # 处理启动传入的文件/文件夹
            launch_path_handled = False
            if len(sys.argv) > 1:
                launch_path = sys.argv[1]
                if os.path.isdir(launch_path):
                    # 拖拽的是文件夹，直接设置为源码路径
                    self.update_file_config("source_code_path", os.path.normpath(launch_path))
                    self.update_file_config("code_name", "")
                    launch_path_handled = True
                elif os.path.isfile(launch_path):
                    # 拖拽的是文件，解析文件路径
                    from src.utils.file_ops import split_file_path
                    split_file_path(launch_path)
                    launch_path_handled = True

            # 自动创建默认 code.cn 文件
            if not launch_path_handled:
                code_name = self.get_file_config("code_name")
                if not code_name:
                    code_dir = os.path.join(ROOT_DIR, "code")
                    code_file = os.path.join(code_dir, "code.cn")
                    os.makedirs(code_dir, exist_ok=True)

                    # 判断文件是否存在 并且 文件有内容，有内容就跳过写入
                    if not (os.path.exists(code_file) and os.path.getsize(code_file) > 0):
                        with open(code_file, "w", encoding="utf-8") as f:
                            f.write('输出*（“你好，世界”）')

                    self.update_file_config("code_name", "code")
                    self.update_file_config("source_code_path", code_dir)

            # 标记为已初始化
            self._initialized = True
        except Exception as e:
            raise ConfigException("配置初始化失败", str(e)) from e

    def read_config(self, file_name: str, key: Optional[str] = None) -> Any:
        """
        从缓存读取配置
        
        Args:
            file_name: 配置文件名
            key: 配置键名，为 None 时返回整个配置字典

        Returns:
            配置值或配置字典，若不存在则返回 None
        """
        config = self._cache.get(file_name)
        if config is None:
            self._load_from_file(file_name)
            config = self._cache.get(file_name)
        if config is None: return None
        assert isinstance(config, dict)
        if key is None: return dict(config)
        return config.get(key)

    def update_config(self, file_name: str, key: str, value: Any) -> bool:
        """
        更新配置

        Args:
            file_name: 配置文件名
            key: 要更新的键名
            value: 新值

        Returns:
            更新是否成功

        Raises:
            ConfigException: 配置更新失败时抛出
        """
        config_path = os.path.join(CONFIG_DIR, file_name)

        try:
            # 确保缓存中存在该配置
            if file_name not in self._cache:
                self._load_from_file(file_name)
                if file_name not in self._cache: self._cache[file_name] = { }

            # 更新键值
            self._cache[file_name][key] = value

            # 持久化到文件
            self._write_json(config_path, self._cache[file_name])
            return True
        except Exception as e:
            raise ConfigException("配置更新失败", str(e)) from e

    def _load_from_file(self, file_name: str) -> None:
        """
        从文件加载配置到缓存

        Args:
            file_name: 配置文件名

        Raises:
            ConfigException: JSON 格式损坏或读取失败时抛出
        """
        config_path = os.path.join(CONFIG_DIR, file_name)
        if not os.path.exists(config_path): return
        try:
            with open(config_path, "r", encoding="utf-8") as f: self._cache[file_name] = json.load(f)
        except json.JSONDecodeError:
            raise ConfigException("JSON 格式损坏", config_path)
        except Exception as e:
            raise ConfigException("读取配置失败", str(e)) from e

    @staticmethod
    def _write_json(path: str, data: Any) -> None:
        """
        写入 JSON 配置文件

        Args:
            path: 文件完整路径
            data: 要写入的数据
        """
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

    def get_app_config(self, key: Optional[str] = None) -> Any:
        """
        获取应用配置

        Args:
            key: 配置键名，为 None 时返回整个配置字典

        Returns:
            配置值或配置字典
        """
        return self.read_config("AppConfig.json", key)

    def get_file_config(self, key: Optional[str] = None) -> Any:
        """
        获取文件配置

        Args:
            key: 配置键名，为 None 时返回整个配置字典

        Returns:
            配置值或配置字典
        """
        return self.read_config("FileConfig.json", key)

    def get_session_config(self, key: Optional[str] = None) -> Any:
        """
        获取会话配置

        Args:
            key: 配置键名，为 None 时返回整个配置字典

        Returns:
            配置值或配置字典
        """
        return self.read_config("SessionConfig.json", key)

    def get_personal_config(self, key: Optional[str] = None) -> Any:
        """
        获取个性化配置

        Args:
            key: 配置键名，为 None 时返回整个配置字典

        Returns:
            配置值或配置字典
        """
        return self.read_config("PersonalConfig.json", key)

    def update_app_config(self, key: str, value: Any) -> bool:
        """更新应用配置"""
        return self.update_config("AppConfig.json", key, value)

    def update_file_config(self, key: str, value: Any) -> bool:
        """更新文件配置"""
        return self.update_config("FileConfig.json", key, value)

    def update_session_config(self, key: str, value: Any) -> bool:
        """更新会话配置"""
        return self.update_config("SessionConfig.json", key, value)

    def update_personal_config(self, key: str, value: Any) -> bool:
        """更新个性化配置"""
        return self.update_config("PersonalConfig.json", key, value)


def get_config_service() -> ConfigService:
    """
    获取 ConfigService 单例

    Returns:
        ConfigService 单例实例
    """
    return ConfigService()
