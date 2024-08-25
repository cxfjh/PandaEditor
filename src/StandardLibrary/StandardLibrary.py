import src.StandardLibrary.KeyWords as KeyWords # 导入关键字词
import src.StandardLibrary.BuiltinLibraries as BuiltinLibraries # 导入内置库
import src.StandardLibrary.BuiltinLibraryMethods as BuiltinLibraryMethods # 导入内置库方法
import src.StandardLibrary.BuiltinMethods as BuiltinMethods # 标准库内置方法

import src.StandardLibrary.PunctuationMark as PunctuationMark # 导入标点符号
import src.StandardLibrary.ExpressionSymbols as ExpressionSymbols # 导入运算符
import src.StandardLibrary.StringSymbols as StringSymbols # 导入字符串符号

Grammar = {**BuiltinLibraryMethods.BuiltinLibraryMethods, **KeyWords.KeyWords, **BuiltinLibraries.BuiltinLibraries, **BuiltinMethods.BuiltinMethods} # 合并语法
Symbols = {**PunctuationMark.PunctuationMark, **ExpressionSymbols.ExpressionSymbols} # 合并符号
Character = {**StringSymbols.StringSymbols} # 合并字符