import src.module.KeyWords as KeyWords # 导入关键字词
import src.module.BuiltinLibraries as BuiltinLibraries # 导入内置库
import src.module.BuiltinLibraryMethods as BuiltinLibraryMethods # 导入内置库方法

import src.module.PunctuationMark as PunctuationMark # 导入标点符号

Grammar = {**BuiltinLibraryMethods.BuiltinLibraryMethods, **KeyWords.KeyWords, **BuiltinLibraries.BuiltinLibraries} # 合并语法
Symbols = {**PunctuationMark.PunctuationMark} # 合并符号


