from PyQt6.QtWidgets import * # 导入PyQt6的全部类
from PyQt6.QtGui import * # 导入PyQt6的全部类
from PyQt6.QtCore import * # 导入PyQt6的全部类

import src.StandardLibrary.BuiltinLibraryMethods as BuiltinLibraryMethods # 导入内置库方法
import src.StandardLibrary.KeyWords as KeyWords # 导入关键字词
import src.StandardLibrary.BuiltinLibraries as BuiltinLibraries # 导入内置库
import src.StandardLibrary.BuiltinMethods as BuiltinMethods # 标准库内置方法
import src.StandardLibrary.PunctuationMark as PunctuationMark # 导入标点符号
import src.StandardLibrary.ExpressionSymbols as ExpressionSymbols # 导入运算符


# 处理关键字
def processKeywords(dictionaries): return [[item for pair in d.items() for item in pair] for d in dictionaries]

# 处理关键字
result = processKeywords([BuiltinLibraryMethods.BuiltinLibraryMethods, KeyWords.KeyWords, BuiltinLibraries.BuiltinLibraries, BuiltinMethods.BuiltinMethods, PunctuationMark.PunctuationMark, ExpressionSymbols.ExpressionSymbols ])
charactersFilter = set('()+*[]?') # 定义要过滤的字符集合
result = [[item for item in sublist if item not in charactersFilter] for sublist in result] # 进行过滤操作


class ChineseHighlighter(QSyntaxHighlighter):
    # 定义ChineseHighlighter类，继承自QSyntaxHighlighter类
    def format(color, style=''):
        _color = QColor()
        if type(color) is not str: _color.setRgb(color[0], color[1], color[2])
        else: _color.setNamedColor(color)
        _format = QTextCharFormat()
        _format.setForeground(_color)
        if 'bold' in style: _format.setFontWeight(QFont.Weight.Bold)
        if 'italic' in style: _format.setFontItalic(True)
        return _format
    

    # 定义ChineseHighlighter的样式
    STYLES = {
        "BuiltinLibraryMethods": format([78, 201, 176]),
        "KeyWords": format([197, 134, 192]),
        "BuiltinMethods": format([220, 220, 170]),
        "PunctuationMark": format([172, 110, 89]),
        "ExpressionSymbols": format([156, 220, 254]),
    }


    # 定义构造函数
    def __init__(self, document):
        super().__init__(document)  # 调用父类的构造函数
       
        rules = []  # 定义规则列表
        rules += [(r'(?<!\p{Han})%s(?!\p{Han})' % w, 0, ChineseHighlighter.STYLES['BuiltinLibraryMethods']) for w in result[0]] # 关键字匹配规则
        rules += [(r'(?<!\p{Han})%s(?!\p{Han})' % w, 0, ChineseHighlighter.STYLES['KeyWords']) for w in result[1]] # 关键字匹配规则
        rules += [(r'(?<!\p{Han})%s(?!\p{Han})' % w, 0, ChineseHighlighter.STYLES['BuiltinLibraryMethods']) for w in result[2]] # 关键字匹配规则
        rules += [(r'(?<!\p{Han})%s(?!\p{Han})' % w, 0, ChineseHighlighter.STYLES['BuiltinMethods']) for w in result[3]] # 关键字匹配规则
        rules += [(r'%s' % b, 0, ChineseHighlighter.STYLES['PunctuationMark']) for b in result[4]]
        rules += [(r'%s' % b, 0, ChineseHighlighter.STYLES['ExpressionSymbols']) for b in result[5]]
        self.rules = [(QRegularExpression(pat), index, fmt) for (pat, index, fmt) in rules]  # 规则列表转换为元组列表
        

    # 定义highlightBlock函数，实现语法高亮
    def highlightBlock(self, text: str) -> None:
        for expression, nth, format in self.rules:  # 遍历规则列表
            matchIterator = expression.globalMatch(text)  # 全局正则匹配
            while matchIterator.hasNext():  # 遍历匹配结果
                match = matchIterator.next()  # 获取下一个匹配结果
                self.setFormat(match.capturedStart(), match.capturedLength(), format)  # 设置格式
        self.setCurrentBlockState(0)  # 重置当前块状态
        
