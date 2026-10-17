import re
from functools import lru_cache
from typing import List, Tuple, Optional, Dict
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
import src.module.builtin_map as BuiltinMap
import src.module.lib_map as LibMap
import src.module.keyword_map as KeyWordMap
import src.module.stdlib_map as stdlib
import src.module.punctuation_map as PunctuationMap
import src.module.method_map as MethodMap


# 预编译中文检查正则
_CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]')

# 关键字字符集合
_KEYWORD_CHARS = frozenset('@如果否则遍历循环当定义返回')

# 最大行长度限制
_MAX_LINE_LENGTH = 2000

# 高亮结果缓存
_HIGHLIGHT_CACHE: Dict[int, Dict[str, object]] = { }
_CACHE_MAX_SIZE = 5000  # 最大缓存条目数

# 深色语法高亮颜色
DARcula_COLORS = {
    'keyword': [86, 156, 214],  # #569CDE - 亮蓝色 - 关键字 (如果、否则、遍历、定义、返回)
    'builtin': [220, 220, 170],  # #DCDC87 - 淡黄色 - 内置函数 (输出、输入、长度、转整数)
    'lib': [210, 160, 210],  # #D2A0D2 - 淡紫色 - 库/模块名 (数学库、系统库)
    'stdlib': [130, 200, 170],  # #82C8AA - 薄荷绿 - 标准库函数 (平方根、随机整数)
    'punctuation': [180, 140, 140],  # #B48C8C - 淡红棕色 - 标点符号 (，。、；：)
    'method': [230, 160, 120],  # #E6A078 - 珊瑚橙 - 对象方法 (追加、删除、查找)
    'comment': [106, 153, 85],  # #6A9955 - 浅绿色 - 注释行
}

# 浅色语法高亮颜色
LIGHT_COLORS = {
    'keyword': [30, 80, 180],  # #1E50B4 - 宝蓝色 - 关键字 (如果、否则、遍历、定义、返回)
    'builtin': [160, 120, 20],  # #A07814 - 琥珀色 - 内置函数 (输出、输入、长度、转整数)
    'lib': [140, 80, 160],  # #8C50A0 - 深紫色 - 库/模块名 (数学库、系统库)
    'stdlib': [40, 140, 100],  # #288C64 - 翠绿色 - 标准库函数 (平方根、随机整数)
    'punctuation': [180, 100, 100],  # #B46464 - 红棕色 - 标点符号 (，。、；：)
    'method': [200, 100, 40],  # #C86428 - 橙红色 - 对象方法 (追加、删除、查找)
    'comment': [0, 128, 0],  # #008000 - 绿色 - 注释行
}


# 从各模块提取词法单元
@lru_cache(maxsize=6)
def _extract_keys(module_name: str) -> Tuple[str, ...]:
    """
    从映射字典中提取键（词法单元），排除括号
    
    Args:
        module_name: 模块名称（keyword/builtin/lib/stdlib/punctuation/method）
        
    Returns:
        Tuple[str, ...]: 词法单元元组（已排除括号）
    """
    module_map = {
        'keyword': KeyWordMap.keyword,  # 关键字（如果、否则、遍历...）
        'builtin': BuiltinMap.builtin,  # 内置函数（输出、输入、长度...）
        'lib': LibMap.lib,  # 库/模块名（数学库、系统库...）
        'stdlib': stdlib.stdlib,  # 标准库函数（平方根、随机整数...）
        'punctuation': PunctuationMap.punctuation,  # 标点符号（，。、；：...）
        'method': MethodMap.method,  # 对象方法（追加、删除、查找...）
    }
    mapping_dict = module_map.get(module_name, { })
    return tuple(str(k) for k in mapping_dict.keys() if str(k) not in { "(", ")" })  # 排除括号


class ChineseHighlighter(QSyntaxHighlighter):
    """中文语法高亮器"""

    def __init__(self, document, editor=None, dark_mode=True):
        """
        初始化语法高亮器
        
        Args:
            document: Qt 文本文档对象（QTextDocument）
            editor: QPlainTextEdit 编辑器引用（可选）
            dark_mode: 是否使用深色主题，默认 True
        """
        super().__init__(document)
        self._editor = editor
        self._current_file = None  # 当前文件路径
        self._dark_mode = dark_mode
        self._rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []  # 预编译的高亮规则
        self._comment_formats: Dict[bool, QTextCharFormat] = { }  # 缓存注释格式（深色/浅色）
        self._precompile_rules()  # 预编译所有高亮规则

    @staticmethod
    def _create_text_format(rgb_color: List[int], style: str = "") -> QTextCharFormat:
        """
        创建文本格式

        Args:
            rgb_color: RGB 颜色值列表，如 [255, 128, 0]
            style: 样式字符串，支持 "bold"（粗体）和 "italic"（斜体）

        Returns:
            配置好的 QTextCharFormat 对象
        """
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(*rgb_color))
        if "bold" in style: fmt.setFontWeight(QFont.Weight.Bold)
        if "italic" in style: fmt.setFontItalic(True)
        return fmt

    @staticmethod
    def _build_pattern(items: List[str], is_punctuation: bool = False) -> Optional[str]:
        """
        构建正则模式字符串

        Args:
            items: 词法单元列表
            is_punctuation: 是否为标点符号
            
        Returns:
            正则模式字符串，若 items 为空则返回 None
        """
        if not items: return None

        # 标点符号使用字符类匹配（如 [，。、；：]）
        if is_punctuation:
            escaped = "".join(re.escape(str(ch)) for ch in items)
            return f"[{escaped}]"

        # @ 开头的词（如 @装饰器）
        if all(str(item).startswith("@") for item in items):
            escaped_items = [re.escape(str(w)) for w in items]
            # 负向前瞻断言：确保后面不跟中文、字母、数字、下划线
            return "(?:" + "|".join(escaped_items) + r")(?![\p{Han}\p{L}\p{N}_])"

        # 普通词法单元使用完整的负向零宽断言
        escaped_items = [re.escape(str(w)) for w in items]
        return r"(?<![\p{Han}\p{L}\p{N}_])(?:" + "|".join(escaped_items) + r")(?![\p{Han}\p{L}\p{N}_])"

    def _precompile_rules(self):
        """预编译所有高亮规则为 (regex, format) 元组"""
        self._rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []

        # 根据主题选择颜色（深色/浅色）
        colors = DARcula_COLORS if self._dark_mode else LIGHT_COLORS

        # 缓存注释格式（避免重复创建）
        self._comment_formats[self._dark_mode] = self._create_text_format(colors['comment'])

        # 定义高亮样式列表
        styles = [
            ('keyword', colors['keyword'], False),  # 关键字（如果、否则、遍历...）
            ('builtin', colors['builtin'], False),  # 内置函数（输出、输入、长度...）
            ('lib', colors['lib'], False),  # 库/模块名（数学库、系统库...）
            ('stdlib', colors['stdlib'], False),  # 标准库函数（平方根、随机整数...）
            ('punctuation', colors['punctuation'], True),  # 标点符号（，。、；：...）
            ('method', colors['method'], False),  # 对象方法（追加、删除、查找...）
        ]

        # 预编译所有规则
        for module_name, color, is_punc in styles:
            items = _extract_keys(module_name)  # 从模块提取词法单元
            pattern = self._build_pattern(list(items), is_punc)  # 构建正则模式
            if pattern:
                regex = QRegularExpression(pattern)  # 创建 Qt 正则对象
                if regex.isValid():  # 验证正则有效性
                    fmt = self._create_text_format(color)  # 创建文本格式
                    self._rules.append((regex, fmt))  # 添加到规则列表

    @staticmethod
    def _should_process_line(text: str) -> bool:
        """
        快速检查行是否需要高亮处理
        
        Args:
            text: 要检查的文本
            
        Returns:
            是否需要高亮处理
        """
        if _CHINESE_PATTERN.search(text):
            return True
        for char in text:
            if char in _KEYWORD_CHARS:
                return True
        return False

    def _should_highlight(self) -> bool:
        """
        检查是否应该执行高亮
        
        Returns:
            是否应该高亮
        """
        # 如果没有设置当前文件路径，默认高亮
        if not self._current_file:
            return True

        # 只对 .cn 文件启用语法高亮
        return self._current_file.endswith('.cn')

    def highlightBlock(self, text: str):
        """
        对文本块进行高亮

        Args:
            text: 要处理的文本行
        """
        # 检查是否应该高亮（仅 .cn 文件启用）
        if not self._should_highlight():
            self.setCurrentBlockState(0)
            return

        # 跳过空行和纯空白行
        if not text or text.isspace():
            self.setCurrentBlockState(0)
            return

        # 超长行跳过语法高亮
        if len(text) > _MAX_LINE_LENGTH:
            self.setCurrentBlockState(0)
            return

        # 检查是否为注释行
        stripped_text = text.lstrip()
        is_comment_line = stripped_text.startswith('#')

        if is_comment_line:
            # 注释行只应用注释颜色，不执行其他语法高亮规则
            comment_fmt = self._comment_formats[self._dark_mode]
            hash_pos = text.index('#')  # 找到 # 的位置
            self.setFormat(hash_pos, len(text) - hash_pos, comment_fmt)  # 从 # 到行末应用注释格式
            self.setCurrentBlockState(0)
            return

        # 尝试从缓存获取高亮结果
        cache_key = hash((text, self._dark_mode))  # 使用文本内容和主题作为缓存键
        if cache_key in _HIGHLIGHT_CACHE:
            cached_result = _HIGHLIGHT_CACHE[cache_key]
            for start, length, fmt in cached_result['formats']:  # type: ignore
                self.setFormat(start, length, fmt)  # 应用缓存的高亮格式
            self.setCurrentBlockState(0)
            return

        # 非注释行使用正则快速检查中文/关键字
        if not self._should_process_line(text):
            self.setCurrentBlockState(0)
            return

        # 执行高亮规则
        formats_to_cache = []  # 收集本次高亮结果用于缓存
        for regex, fmt in self._rules:
            it = regex.globalMatch(text)  # 全局匹配
            while it.hasNext():
                m = it.next()  # 获取下一个匹配项
                start, length = m.capturedStart(), m.capturedLength()
                self.setFormat(start, length, fmt)  # 应用高亮格式
                formats_to_cache.append((start, length, fmt))  # 收集到缓存列表

        # 缓存高亮结果
        if len(_HIGHLIGHT_CACHE) >= _CACHE_MAX_SIZE:
            _HIGHLIGHT_CACHE.clear()  # 缓存满时清空

        _HIGHLIGHT_CACHE[cache_key] = { 'formats': formats_to_cache }  # 存入缓存
        self.setCurrentBlockState(0)

    def update_theme(self, dark_mode: bool):
        """
        更新主题
        
        Args:
            dark_mode: True 为深色主题，False 为浅色主题
        """
        if self._dark_mode == dark_mode:
            return  # 主题未变化，无需更新

        self._dark_mode = dark_mode
        self._rules.clear()  # 清空旧规则
        self._precompile_rules()  # 重新预编译规则

        # 清空缓存
        _HIGHLIGHT_CACHE.clear()

        # 重新高亮整个文档
        doc = self.document()
        if doc:
            self.rehighlight()
