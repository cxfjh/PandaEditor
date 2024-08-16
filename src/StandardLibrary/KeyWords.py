# 标准库关键字
KeyWords = {}


# 判断和逻辑关键字
KeyWords.update(
    {
        "如果": "if",  # 条件判断
        "否则": "else",  # 条件分支
        "如否": "elif",  # 条件分支
        "并且": "and",  # 逻辑与
        "或者": "or",  # 逻辑或
        "继续": "continue",  # 跳过当前循环
        "不是": "not",  # 逻辑非
        "是的": "is",  # 比较对象
    }
)

# 类型和值关键字
KeyWords.update(
    {
        "假的": "False",  # 布尔值假
        "真的": "True",  # 布尔值真
        "空值": "None",  # 空值
        "断言": "assert",  # 断言
    }
)

# 循环语句关键字
KeyWords.update(
    {
        "迭代": "for",  # 迭代循环
        "中断": "break",  # 退出循环
        "循环": "while",  # 条件循环
        "跳过": "pass",  # 空操作
        "在内": "in",  # 成员检查
        "匹配": "match",  # 模式匹配
        "情况": "case",  # 模式匹配的分支
    }
)

# 异常关键字
KeyWords.update(
    {
        "捕获": "try",  # 捕获异常
        "异常": "except",  # 处理异常
        "最终": "finally",  # 最终处理
    }
)

# 定义关键字
KeyWords.update(
    {
        "函数": "def",  # 函数定义
        "类别": "class",  # 类定义
        "返回": "return",  # 返回值
    }
)

# 导入模块关键字
KeyWords.update(
    {
        "导入": "import",  # 导入模块
        "作为": "as",  # 模块别名
        "起始": "from",  # 从模块导入
    }
)

# 对象删除关键字
KeyWords.update(
    {
        "删除": "del",  # 删除对象
    }
)

# 变量关键字
KeyWords.update(
    {
        "全局": "global",  # 声明全局变量
    }
)

# 异步操作关键字
KeyWords.update(
    {
        "异步": "async",  # 异步函数
        "等待": "await",  # 等待异步操作
    }
)

# 装饰器关键字
KeyWords.update(
    {
        "匿名": "lambda",  # 匿名函数
    }
)

# 文件操作关键字
KeyWords.update(
    {
        "使用": "with",  # 文件上下文管理
        "编码": "encoding",  # 文件编码
    }
)

# 系统交互关键字
KeyWords.update(
    {
        "退出": "exit",  # 退出程序
    }
)

