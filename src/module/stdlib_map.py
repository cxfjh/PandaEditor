# 标准库函数映射表
stdlib = { }

stdlib.update(
    {
        # math
        "圆周率": "pi",
        "自然常数": "e",
        "平方根": "sqrt",
        "平方": "pow",
        "正弦": "sin",
        "余弦": "cos",
        "正切": "tan",
        "反正弦": "asin",
        "反余弦": "acos",
        "反正切": "atan",
        "弧度转角度": "degrees",
        "角度转弧度": "radians",
        "自然对数": "log",
        "常用对数": "log10",
        "上取整": "ceil",
        "下取整": "floor",
        "浮点绝对值": "fabs",
        "取模": "fmod",
        "阶乘": "factorial",
        "最大公约数": "gcd",
        "欧拉伽马": "gamma",
        "双曲正弦": "sinh",
        "双曲余弦": "cosh",

        # random
        "随机整数": "randint",
        "零一小数": "random",
        "区间小数": "uniform",
        "种子": "seed",
        "抽取一项": "choice",
        "多项抽样": "sample",
        "打乱序列": "shuffle",
        "随机偏移": "randrange",

        # os
        "系统当前路径": "getcwd",
        "切换路径": "chdir",
        "建单文件夹": "mkdir",
        "递归建文件夹": "makedirs",
        "删空文件夹": "rmdir",
        "删文件": "remove",
        "重命名": "rename",
        "列出目录内容": "listdir",
        "执行系统命令": "system",
        "路径拼接": "path.join",
        "路径存在": "path.exists",
        "路径是文件": "path.isfile",
        "路径是目录": "path.isdir",
        "获取文件大小": "path.getsize",
        "获取文件名": "path.basename",
        "获取父路径": "path.dirname",

        # pathlib
        "路径对象": "Path",
        "是否文件": "is_file",
        "是否目录": "is_dir",
        "是否存在": "exists",
        "创建目录": "mkdir",
        "删除文件": "unlink",
        "遍历子文件": "iterdir",
        "全局匹配文件": "glob",
        "父目录": "parent",
        "文件名": "name",
        "后缀名": "suffix",
        "绝对路径": "absolute",

        # time
        "延时": "sleep",
        "时间戳": "time",
        "本地时间结构": "localtime",
        "格式化时间": "strftime",
        "文本转时间戳": "strptime",
        "UTC时间": "gmtime",

        # datetime
        "当前时间": "datetime.now",
        "UTC当前时间": "datetime.utcnow",
        "构造时间": "datetime",
        "时间差": "timedelta",
        "文本转时间": "datetime.strptime",
        "转格式化文本": "strftime",
        "替换年月日": "replace",
        "获取时间戳": "timestamp",
        "今日日期": "date.today",

        # json
        "内存转文本": "dumps",
        "文本转内存": "loads",
        "写入文件": "dump",
        "读取文件": "load",

        # re
        "匹配开头": "match",
        "全文搜索": "search",
        "全部匹配结果": "findall",
        "替换文本": "sub",
        "分割字符串": "split",
        "预编译规则": "compile",
        "匹配迭代器": "finditer",

        # collections
        "计数统计": "Counter",
        "双端队列": "deque",
        "有序字典": "OrderedDict",
        "具名元组": "namedtuple",
        "取最高频": "most_common",
        "左侧添加": "appendleft",
        "左侧弹出": "popleft",

        # sys
        "命令行参数": "argv",
        "退出程序": "exit",
        "标准输出流": "stdout",
        "标准输入流": "stdin",
        "标准错误流": "stderr",
        "Python版本": "version",
        "模块搜索路径": "path",

        # base64
        "字节加密": "b64encode",
        "字节解密": "b64decode",
        "安全加密": "urlsafe_b64encode",
        "安全解密": "urlsafe_b64decode",
    },
)
