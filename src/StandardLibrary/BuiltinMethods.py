# 标准库内置方法
BuiltinMethods = {}


# 内置数学方法
BuiltinMethods.update(
    {
        "绝对值": "abs",
        "幂运算": "pow",
        "数舍入": "round",
        "最大值": "max",
        "最小值": "min",
        "数求和": "sum",
        "数商余": "divmod",
    }
)

# 内置文件操作方法
BuiltinMethods.update(
    {
        "打开文件": "open",
        "关闭文件": "close",
        "写入文件": "write",
        "读取文件": "read",
    }
)

# 内置数组操作方法
BuiltinMethods.update(
    {
        "元素末尾插入": "append",  # 向数组添加元素
        "数组插入数组": "extend",  # 向数组添加多个元素
        "数组索引插入": "insert",  # 在指定位置插入元素
        "数组索引查找": "index",  # 查找元素索引
        "数组删除": "remove",  # 从数组中删除元素
        "数组计数": "count",  # 计算数组出现次数
        "数组排序": "sort",  # 数组排序
        "数组升序": "reverse=False",  # 数组升序
        "数组倒序": "reverse=True",  # 数组倒序
        "数组反转": "reverse",  # 数组反转
        "数组复制": "copy",  # 复制数组
        "数组切片": "slice",  # 切片操作
        "数组连接": "join",  # 连接数组元素
    }
)

# 内置类型转换方法
BuiltinMethods.update(
    {
        "转整数": "int",
        "转字符": "str",
        "转数组": "list",
        "转元组": "tuple",
        "转字典": "dict",
        "转布尔": "bool",
        "转浮点": "float",
        "转集合": "set",
        "查看类型": "type",
    }
)

# 内置基本方法
BuiltinMethods.update(
    {
        "获取长度": "__len__",  # 获取对象的长度
        "对象范围": "range",  # 创建范围对象
        "执行": "exec",  # 执行代码
        "输出": "print",  # 输出内容到控制台
        "输入": "input",  # 从控制台获取输入
    }
)


