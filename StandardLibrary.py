# 关键字
KeyWords = {
    "导入": "import",
    "特定导入": "from",
    "别名": "as",
    "定义": "def",

    "如果": "if",
    "否则": "else",
    "或者如果": "elif",
    "退出": "exit",

    "迭代": "for",
    "循环": "while",
    "和": "and",
    "或": "or",
    "结束": "break",
    "跳过": "continue",
    "返回": "return",
    "真": "True",
    "假": "False",
    "空": "None",
    
    "类": "class",
    "对象": "object",

    "异常": "except",
    "捕获": "try",
    "最终": "finally",

    "除数为零": "ZeroDivisionError",
    "文件不存在": "FileNotFoundError",
    "索引错误": "IndexError",
    "键错误": "KeyError",
    "类型错误": "TypeError",
    "值错误": "ValueError",

    "断言": "assert",
    "删除": "del",
    "格式化": "f",
}

# 语句
Statements = {
    "打印": "print",
    "输入框": "input",
    "执行": "exec",

    "全局": "global",
    "非本地": "nonlocal",

    "打开": "open",
    "读取": "read",
    "写入": "write",
    "关闭": "close",
    "布尔型": "bool",
    "空型": "None",
    "整数型": "int",
    "长整数型": "long",
    "短浮点型": "short",
    "字节型": "byte",
    "复数型": "complex",
    "浮点型": "float",
    "字符串型": "str",
    "列表型": "list",
    "元组型": "tuple",
    "字典型": "dict",
    "集合型": "set",

    "数组排序": "sorted",
    "数组反转": "reversed",
    "数组切片": "slice",
    "数组拼接": "join",
    "数组计数": "count",
    "数组索引": "index",
    "数组删除": "remove",
    "数组插入": "insert",
    "数组替换": "replace",
    "数组遍历": "enumerate",
    "数组过滤": "filter",
    "数组映射": "map",
    "数组分组": "groupby",
}


# 方法
Methods = {
    "整数随机": "random.randint",
    "浮点数随机": "random.uniform",
    "数组随机": "random.sample",

    "获取当前时间": "time.time",
    "休眠": "time.sleep",

    "三角函数": "math.sin",
    "平方根": "math.sqrt",
    "指数运算": "math.exp",
    "对数运算": "math.log",

    "创建目录": "os.mkdir",
    "删除目录": "os.rmdir",
    "删除文件": "os.remove",
    "文件重命名": "os.rename",
    "文件大小": "os.path.getsize",
    "文件是否存在": "os.path.exists",

    "JSON解析": "json.loads",
    "JSON序列化": "json.dumps",

    "获取当前日期": "datetime.datetime.now",
    "日期格式化": "datetime.datetime.strptime",
    "转换日期": "datetime.datetime.date",
    "转换时间": "datetime.datetime.time",
    
    "编译正则表达式": "re.compile",
    "匹配正则表达式": "re.match",
    "搜索正则表达式": "re.search",
    "替换正则表达式": "re.sub",
    "分割字符串": "re.split",
    "查找字符串": "re.findall",
    "查找字符串位置": "re.finditer",

    "读取CSV文件": "csv.reader",
    "写入CSV文件": "csv.writer",

    "主界面": "Tk",
    "子界面": "Toplevel",
    "弹窗输入框": "simpledialog.askstring",
    "警告弹窗": "messagebox.showwarning",
    "错误弹窗": "messagebox.showerror",
    "询问弹窗": "messagebox.askquestion",
    "确认弹窗": "messagebox.askokcancel",
    "输入弹窗": "messagebox.askstring",
    "界面循环": "mainloop",
    "界面标题": "title",
    "界面形态": "geometry",
    "界面状态": "attributes",
    "界面关闭": "destroy",
    "界面退出": "quit",
    "界面显示": "deiconify",
    "界面隐藏": "withdraw",
    "界面按钮": "Button",
    "界面标签": "Label",
    "界面文本框": "Entry",
    "界面列表框": "Listbox",
    "界面滚动条": "Scrollbar",
    "界面菜单": "Menu",

    "获取组件内容": "get",
    "设置组件内容": "insert",
    "组件点击事件": "command",

    "组件文本": "text",
    "组件背景色": "bg",
    "组件字体色": "fg",
    "组件字体大小": "font",
    "组件提示信息": "placeholder",
    "组件可变值": "StringVar",
    "组件变量绑定": "textvariable",
    "组件宽": "width",
    "组件高": "height",
    "组件位置": "grid",
    "组件列间距": "padx",
    "组件行间距": "pady",
    "组件对齐": "anchor",
    "组件填充": "fill",
    "组件权重": "weight",
    "组件列": "column",
    "组件行": "row",
    "组件列跨度": "columnspan",
    "组件行跨度": "rowspan",
    "组件列宽": "columnconfigure",
    "组件行高": "rowconfigure",
    "组件显示": "show",
    "组件隐藏": "hide",
    "组件选中": "select",
    "放置组件": "pack",

    "新线程": "threading.Thread",
    "启动新进程": "multiprocessing.Process",
}

# 内置模块
BuiltinModules = {
    "随机数": "random",
    "时间": "time",
    "数学": "math",
    "文件操作": "os",
    "JSON处理": "json",
    "正则表达式": "re",
    "日期时间处理": "datetime",
    "处理文件": "csv",
    "图形界面": "tkinter",
    "多线程": "threading",
    "界面弹窗": "messagebox",
    "界面输入框": "tkinter.simpledialog"
}

# 表达式
Expressions = {
    "等于": "=",
    "全等": "==",
    "不等": "!=",
    "大于": ">",
    "小于": "<",
    "减": "-",
    "加": "+",
    "乘": "*",
    "除": "/",
    "取模": "%",
}

# 符号
Symbols = {
    "（": "(",
    "）": ")",
    "：": ":",
    "“": '"',
    "”": '"',
    "，": ",",
    "；": ";",
    "，": ",",
    "‘": "'",
    "’": "'",
    "【": "[",
    "】": "]",
    "？": "?",
    "！": "!",
    "{": "{",
    "}": "}",
}
