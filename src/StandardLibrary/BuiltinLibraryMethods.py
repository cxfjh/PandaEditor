# 内置库方法
BuiltinLibraryMethods = {}


# 内置系统时间库方法
BuiltinLibraryMethods.update(
    {
        "系统时间->休眠": "time.sleep",
    }
)

# 内置时间处理库方法
BuiltinLibraryMethods.update(
    {
        "时间处理->时间戳": "datetime.datetime.now().timestamp",
        "时间处理->当前日期": "datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "时间处理->格式化": "strftime",
        "时间处理->差值": "datetime.timedelta",
        "时间处理->指定日期": "datetime.datetime",
        "时间处理->天数": "days",
        "时间处理->秒数": "seconds",
        "时间处理->毫秒数": "microseconds",
    }
)

# 内置数学运算库方法
BuiltinLibraryMethods.update(
    {
        "数学运算->对数": "math.log",
        "数学运算->对数底": "math.exp",
        "数学运算->平方根": "math.sqrt",
        "数学运算->次方": "math.pow",
        "数学运算->正弦": "math.sin",
        "数学运算->余弦": "math.cos",
        "数学运算->正切": "math.tan",
        "数学运算->下取整": "math.floor",
        "数学运算->上取整": "math.ceil",
        "数学运算->圆周率": "math.pi",
        "数学运算->对数底": "math.e",
    }
)

# 内置线程处理库方法
BuiltinLibraryMethods.update(
    {
        "线程处理->创建": "threading.Thread",
        "线程处理->启动": "start",
        "线程处理->等待": "join",
        "线程处理->函数名": "target",
        "线程处理->函数参数": "args",
    }
)

# 内置异步处理库方法
BuiltinLibraryMethods.update(
    {
        "异步处理->并发": "asyncio.gather",
        "异步处理->等待": "asyncio.sleep",
        "异步处理->运行": "asyncio.run",
    }
)

# 内置文件处理库方法
BuiltinLibraryMethods.update(
    {
        "文件操作->删除文件": "shutil.unlink",
        "文件操作->删除文件夹": "shutil.rmtree",
        "文件操作->创建文件夹": "shutil.os.makedirs",
        "文件操作->文件夹判断": "shutil.os.path.isdir",
        "文件操作->文件判断": "shutil.os.path.isfile",
        "文件操作->复制文件夹": "shutil.copytree",
        "文件操作->复制文件": "shutil.copy",
        "文件操作->移动": "shutil.move",
    }
)

# 内置文件交互库方法
BuiltinLibraryMethods.update(
    {
        "文件交互->工作目录": "os.getcwd",
        "文件交互->目录列表": "os.listdir",
    }
)

# 内置随机数库方法
BuiltinLibraryMethods.update(
    {
        "随机处理->浮点数": "random.uniform",
        "随机处理->整数": "random.randint",
        "随机处理->数组": "random.choice",
        "随机处理->打乱数组": "random.shuffle",
        "随机处理->始种子": "random.seed",
        "随机处理->数组抽样": "random.sample",
        "随机处理->范围": "random.randrange",
    }
)

# 内置正则处理库方法
BuiltinLibraryMethods.update(
    {
        "正则处理->匹配查找": "re.search",
        "正则处理->匹配所有": "re.findall",
        "正则处理->匹配开头": "re.match",
        "正则处理->匹配替换": "re.sub",
        "正则处理->编译正则": "re.compile",
        "正则处理->匹配分割": "re.split",
        "正则处理->获取内容": "group",
    }
)

# 内置鼠键处理库方法
BuiltinLibraryMethods.update(
    {
        "鼠键控制->坐标移动": "pyautogui.moveTo",
        "鼠键控制->相对移动": "pyautogui.moveRel",
        "鼠键控制->当前位置": "pyautogui.position",
        "鼠键控制->安全异常": "pyautogui.FAILSAFE",
        "鼠键控制->操作暂停": "pyautogui.pause",
        "鼠键控制->鼠标点击": "pyautogui.click",
        "鼠键控制->点击间隔": "interval",
        "鼠键控制->点击次数": "clicks",
        "鼠键控制->鼠标双击": "pyautogui.doubleClick",
        "鼠键控制->鼠标右击": "pyautogui.rightClick",
        "鼠键控制->鼠标左击": "pyautogui.leftClick",
        "鼠键控制->鼠标滚动": "pyautogui.scroll",
        "鼠键控制->坐标拖动": "pyautogui.dragTo",
        "鼠键控制->现对拖动": "pyautogui.dragRel",
        "鼠键控制->拖动时间": "duration",
        "鼠键控制->执行按键": "pyautogui.press",
        "鼠键控制->按键组合": "pyautogui.hotkey",
        "鼠键控制->键盘输入": "pyautogui.write",
        "鼠键控制->按键按下": "pyautogui.keyDown",
        "鼠键控制->按键弹起": "pyautogui.keyUp",
        "鼠键控制->屏幕大小": "pyautogui.size",
    }
)

# 内置界面绘制库方法
BuiltinLibraryMethods.update(
    {
        "图形界面->创建": "PyQt6.GuiStart",
        "图形界面->程序": "PyQt6.QtWidgets.QApplication",
        "图形界面->窗口": "PyQt6.QtWidgets.QWidget",
        "图形界面->标签": "PyQt6.QtWidgets.QLabel",
        "图形界面->按钮": "PyQt6.QtWidgets.QPushButton",
        "图形界面->输入框": "PyQt6.QtWidgets.QLineEdit",
        "图形界面->提示弹窗": "PyQt6.QtWidgets.QMessageBox.information",
        "图形界面->警告弹窗": "PyQt6.QtWidgets.QMessageBox.warning",
        "图形界面->错误弹窗": "PyQt6.QtWidgets.QMessageBox.critical",
        "图形界面->设置图标": "setWindowIcon",
        "图形界面->图标": "PyQt6.QtGui.QIcon",
        "图形界面->标题": "setWindowTitle",
        "图形界面->位置": "move",
        "图形界面->大小": "resize",
        "图形界面->显示": "show",
        "图形界面->关闭": "close",
        "图形界面->隐藏": "hide",
        "图形界面->父类": "setParent",
        "图形界面->固定大小": "setFixedSize",
        "图形界面->点击事件": "clicked.connect",
        "图形界面->组件内容": "text",
    }
)

# 扩展库
ExtensionLibrary = """
def 图形界面窗口(size, icon, title, width, height, x, y):
    window = PyQt6.QtWidgets.QWidget()  # 创建QWidget对象
    window.setWindowIcon(PyQt6.QtGui.QIcon(icon))  # 设置窗口图标
    window.setWindowTitle(title)  # 设置窗口标题
    window.resize(width, height)  # 设置窗口大小
    if size: window.setFixedSize(width, height)  # 固定窗口大小
    window.move(x, y)  # 设置窗口位置
    window.show()  # 显示窗口
    return window  # 返回窗口对象


def 图形界面组件(subassembly, title, window, width, height, x, y):
    component = subassembly(title, window)  # 创建QLabel组件
    component.resize(width, height)  # 设置组件大小
    component.move(x, y)  # 设置组件位置
    component.show()  # 显示组件
    return component  # 返回组件对象
"""

# 扩展库
BuiltinLibraryMethods.update(
    {
        "图形界面->生成": ExtensionLibrary,
    }
)
