import re
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PySide6.QtCore import QRegularExpression
import src.module.KeyWords as KeyWords
import src.module.BuiltinLibraries as BuiltinLibraries
import src.module.PunctuationMark as PunctuationMark
import src.module.BuiltinLibraryMethods as BuiltinLibraryMethods


def merge_and_filter_dictionaries(dictionaries, filter_chars):
    """合并多部字典并过滤指定字符，只保留 key"""
    merged_data = []
    for dict_item in dictionaries:
        if isinstance(dict_item, dict):
            # 只取 key，避免把 value (模块/对象) 也加入
            filtered_list = [k for k in dict_item.keys() if k not in filter_chars]
        else:
            # 如果不是 dict，当作列表直接处理
            filtered_list = [item for item in dict_item if item not in filter_chars]
        merged_data.append(filtered_list)
    return merged_data


# 合并所有语法高亮相关的字典并过滤括号字符
merged_highlight_data = merge_and_filter_dictionaries(
    [
        KeyWords.KeyWords,
        BuiltinLibraryMethods.BuiltinLibraryMethods,
        BuiltinLibraries.BuiltinLibraries,
        PunctuationMark.PunctuationMark
    ],
    filter_chars=set("()")
)


class ChineseHighlighter(QSyntaxHighlighter):
    """中文语法高亮器"""

    def __init__(self, document):
        super().__init__(document)

        self.highlight_styles = {
            "KeyWords": self._create_text_format([197, 134, 192]),  # 紫色
            "BuiltinLibraryMethods": self._create_text_format([78, 201, 176]),  # 绿色
            "BuiltinLibraries": self._create_text_format([156, 220, 254]),  # 蓝色
            "PunctuationMark": self._create_text_format([172, 110, 89])  # 棕色
        }

        # 预编译所有正则模式
        self._precompile_patterns()


    @staticmethod
    def _create_text_format(rgb_color, style=""):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(*rgb_color))
        if "bold" in style: fmt.setFontWeight(QFont.Weight.Bold)
        if "italic" in style: fmt.setFontItalic(True)
        return fmt


    @staticmethod
    def _join_patterns(items, is_punctuation=False):
        """将多个关键字/符号合并为一个正则模式"""
        if not items: return None

        if is_punctuation:
            # 标点符号合并为字符类
            escaped = "".join(re.escape(ch) for ch in items)
            return QRegularExpression(f"[{escaped}]")

        # 特殊情况：@开头的关键字
        if all(item.startswith("@") for item in items):
            escaped_items = [re.escape(w) for w in items]

            # 左边不加边界，右边加边界
            pattern = "(?:" + "|".join(escaped_items) + r")(?![\p{Han}\p{L}\p{N}_])"
            return QRegularExpression(pattern)

        # 默认关键字/方法/库模式，加上边界限制
        escaped_items = [re.escape(w) for w in items]
        pattern = (
            r"(?<![\p{Han}\p{L}\p{N}_])"
            + "(?:" + "|".join(escaped_items) + ")"
            + r"(?![\p{Han}\p{L}\p{N}_])"
        )
        return QRegularExpression(pattern)


    def _precompile_patterns(self):
        """预编译正则模式"""
        self.keyword_regex = self._join_patterns(merged_highlight_data[0])
        self.builtin_method_regex = self._join_patterns(merged_highlight_data[1])
        self.builtin_library_regex = self._join_patterns(merged_highlight_data[2])
        self.punctuation_regex = self._join_patterns(merged_highlight_data[3], is_punctuation=True)


    def _apply_highlight(self, text, regex, style):
        """通用高亮函数"""
        if not regex: return
        it = regex.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), style)


    def highlightBlock(self, text):
        """对文本块进行高亮"""
        self._apply_highlight(text, self.keyword_regex, self.highlight_styles["KeyWords"])
        self._apply_highlight(text, self.builtin_method_regex, self.highlight_styles["BuiltinLibraryMethods"])
        self._apply_highlight(text, self.builtin_library_regex, self.highlight_styles["BuiltinLibraries"])
        self._apply_highlight(text, self.punctuation_regex, self.highlight_styles["PunctuationMark"])

        self.setCurrentBlockState(0)
