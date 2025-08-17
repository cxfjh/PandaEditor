import re
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PySide6.QtCore import QRegularExpression
import src.module.KeyWords as KeyWords
import src.module.BuiltinLibraries as BuiltinLibraries
import src.module.PunctuationMark as PunctuationMark
import src.module.BuiltinLibraryMethods as BuiltinLibraryMethods


def merge_and_filter_dictionaries(dictionaries, filter_chars):
    """
    合并多部字典并过滤指定字符

    参数:
        dictionaries: 字典列表，每部字典包含需要高亮的关键词组
        filter_chars: 需要过滤的字符集合

    返回:
        合并后并过滤完成的二维列表，每个子列表对应一类关键词
    """
    merged_data = []
    for dict_item in dictionaries:
        # 展平字典的键值对为列表（键和值都会被保留）
        flattened_list = [item for pair in dict_item.items() for item in pair]
        # 过滤掉指定字符
        filtered_list = [item for item in flattened_list if item not in filter_chars]
        merged_data.append(filtered_list)
    return merged_data


# 合并所有语法高亮相关的字典并过滤括号字符
merged_highlight_data = merge_and_filter_dictionaries(
    [
        KeyWords.KeyWords,  # 关键字列表
        BuiltinLibraryMethods.BuiltinLibraryMethods,  # 内置库方法列表
        BuiltinLibraries.BuiltinLibraries,  # 内置库列表
        PunctuationMark.PunctuationMark  # 标点符号列表
    ],
    filter_chars=set('()')  # 过滤掉括号字符
)


class ChineseHighlighter(QSyntaxHighlighter):
    """中文语法高亮器，用于对文本中的关键字、库、方法和标点进行高亮显示"""

    def __init__(self, document):
        """
        初始化高亮器

        参数:
            document: 需要应用高亮的QTextDocument对象
        """
        super().__init__(document)

        # 定义不同类型文本的高亮样式
        self.highlight_styles = {
            "KeyWords": self._create_text_format([197, 134, 192]),  # 关键字样式（紫色系）
            "BuiltinLibraryMethods": self._create_text_format([78, 201, 176]),  # 内置方法样式（绿色系）
            "BuiltinLibraries": self._create_text_format([156, 220, 254]),  # 内置库样式（蓝色系）
            "PunctuationMark": self._create_text_format([172, 110, 89])  # 标点符号样式（棕色系）
        }

        # 预编译各类关键词的正则表达式模式（提升性能）
        self._precompile_patterns()


    @staticmethod
    def _create_text_format(rgb_color, style=''):
        """
        创建文本格式化对象

        参数:
            rgb_color: RGB颜色值的列表，如[255, 0, 0]
            style: 文本样式，支持 'bold'（粗体）和 'italic'（斜体）

        返回:
            配置好的QTextCharFormat对象
        """
        text_format = QTextCharFormat()

        # 设置前景色
        color = QColor()
        color.setRgb(*rgb_color)
        text_format.setForeground(color)

        # 设置字体样式
        if 'bold' in style:
            text_format.setFontWeight(QFont.Weight.Bold)
        if 'italic' in style:
            text_format.setFontItalic(True)

        return text_format


    def _precompile_patterns(self):
        """预编译所有需要得正则表达式模式，避免重复编译提升性能"""
        # 关键字正则模式
        self.keyword_patterns = [
            self._create_regex_pattern(word)
            for word in merged_highlight_data[0]
        ]

        # 内置库方法正则模式
        self.builtin_method_patterns = [
            self._create_regex_pattern(method)
            for method in merged_highlight_data[1]
        ]

        # 内置库正则模式
        self.builtin_library_patterns = [
            self._create_regex_pattern(library)
            for library in merged_highlight_data[2]
        ]

        # 标点符号正则模式
        self.punctuation_patterns = [
            self._create_regex_pattern(punct, is_punctuation=True)
            for punct in merged_highlight_data[3]
        ]


    @staticmethod
    def _create_regex_pattern(text, is_punctuation=False):
        """
        创建正则表达式模式

        参数:
            text: 需要匹配的文本
            is_punctuation: 是否为标点符号（标点符号不需要单词边界匹配）

        返回:
            正则表达式字符串
        """
        # 转义特殊字符
        escaped_text = re.escape(text)

        if is_punctuation:
            # 标点符号直接返回转义后的文本
            return escaped_text
        else:
            # 关键字/方法/库需要添加单词边界（支持中文）
            # \p{Han}匹配汉字，\p{L}匹配字母，\p{N}匹配数字
            return r'(?<![\p{Han}\p{L}\p{N}])' + escaped_text + r'(?![\p{Han}\p{L}\p{N}])'


    def highlightBlock(self, text):
        """
        对文本块进行高亮处理（QSyntaxHighlighter核心方法）

        参数:
            text: 当前需要处理的文本块内容
        """
        # 高亮关键字
        for pattern in self.keyword_patterns:
            regex = QRegularExpression(pattern)
            match_iterator = regex.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(),  # 匹配开始位置
                    match.capturedLength(),  # 匹配长度
                    self.highlight_styles["KeyWords"]  # 应用的样式
                )

        # 高亮内置库方法
        for pattern in self.builtin_method_patterns:
            regex = QRegularExpression(pattern)
            match_iterator = regex.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    self.highlight_styles["BuiltinLibraryMethods"]
                )

        # 高亮内置库
        for pattern in self.builtin_library_patterns:
            regex = QRegularExpression(pattern)
            match_iterator = regex.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    self.highlight_styles["BuiltinLibraries"]
                )

        # 高亮标点符号
        for pattern in self.punctuation_patterns:
            regex = QRegularExpression(pattern)
            match_iterator = regex.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    self.highlight_styles["PunctuationMark"]
                )

        # 重置当前块状态（用于复杂语法高亮的状态跟踪）
        self.setCurrentBlockState(0)
