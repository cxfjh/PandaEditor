import re
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import src.module.KeyWords as KeyWords
import src.module.BuiltinLibraries as BuiltinLibraries 
import src.module.PunctuationMark as PunctuationMark 
import src.module.BuiltinLibraryMethods as BuiltinLibraryMethods

# 合并所有的字典
def processKKeywords(dictionaries): 
    return [[item for pair in d.items() for item in pair] for d in dictionaries]

# 合并所有的字典
result = processKKeywords([
    KeyWords.KeyWords, 
    BuiltinLibraryMethods.BuiltinLibraryMethods, 
    BuiltinLibraries.BuiltinLibraries, 
    PunctuationMark.PunctuationMark, 
])
charactersFilter = set('()')
result = [[item for item in sublist if item not in charactersFilter] for sublist in result]

# 语法高亮
class ChineseHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        self.styles = {
            "KeyWords": self.format([197, 134, 192]),
            "BuiltinLibraryMethods": self.format([78, 201, 176]),
            "BuiltinLibraries": self.format([156, 220, 254]),
            "PunctuationMark": self.format([172, 110, 89]),
        }
        
        self.rules = []
        self._createRules(result)

    # 格式化
    @staticmethod
    def format(color, style=''):
        _color = QColor()
        if isinstance(color, str):  _color.setNamedColor(color)
        else: _color.setRgb(*color)
        _format = QTextCharFormat()
        _format.setForeground(_color)
        if 'bold' in style:  _format.setFontWeight(QFont.Weight.Bold)
        if 'italic' in style:  _format.setFontItalic(True)
        return _format

    # 这里的result是合并后的列表
    def _createRules(self, result):

        self.rules.extend([(self._createPattern(w), 0, self.styles['KeyWords']) for w in result[0]])
        self.rules.extend([(self._createPattern(w), 0, self.styles['BuiltinLibraryMethods']) for w in result[1]])  
        self.rules.extend([(self._createPattern(w), 0, self.styles['BuiltinLibraries']) for w in result[2]])
        self.rules.extend([(self._createPattern(b, is_punctuation=True), 0, self.styles['PunctuationMark']) for b in result[3]])
        self.rules = [(QRegularExpression(pat), index, fmt) for pat, index, fmt in self.rules]

    # 匹配边界的字符        
    def _createPattern(self, word, is_punctuation=False):
        if is_punctuation: return re.escape(word) # 不添加中文字符边界匹配
        else: return r'(?<![\p{Han}\p{L}\p{N}])' + re.escape(word) + r'(?![\p{Han}\p{L}\p{N}])'  # 添加中文字符边界匹配

    # 高亮
    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
        self.setCurrentBlockState(0)
