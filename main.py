import subprocess  # 用于执行外部命令
import tkinter as tk  # Tkinter库，用于创建GUI
import tkinter.font as tkFont  # Tkinter字体模块，用于设置字体
from tkinter import filedialog  # Tkinter文件对话框模块，用于打开和保存文件对话框

from module import (  # 导入自定义模块中的函数
    compileCode,  # 编译代码
    openFile,  # 打开文件
    saveFile,  # 保存文件
    saveNewFile,  # 另存文件
    preview,  # 运行代码预览
    contact,  # 联系作者
    tutorial,  # 使用教程
    toggleTopmost,  # 窗口置顶
    toggleDarkMode,  # 切换暗夜模式
    codeRecovery,  # 恢复代码
    insertTab,  # 插入制表符
    windowRecovery,  # 恢复窗口配置
    styleRecovery,  # 恢复样式配置
    ctrlS,  # Ctrl + S 保存
    onClosing,  # 窗口关闭事件
    highlightKeywords,  # 关键词高亮
    grammar,  # 语法检查
    syntaxConfiguration,  # 语法配置
)

# 创建主窗口
root = tk.Tk()
root.title("熊猫编辑器")
root.geometry(f"{int(root.winfo_screenwidth() * 0.8)}x{int(root.winfo_screenheight() * 0.8)}")

# 创建顶部区域的Frame
topFrame = tk.Frame(root)  # 创建顶部区域的Frame
topFrame.pack(side="top", fill="x")  # 放置在主窗口的顶部，并横向填充

# 创建按钮
buttonConfigs = [  # 定义按钮配置列表
    ("打开文件", lambda: openFile(filedialog, text, topFrame, tk)),  # 打开文件按钮
    ("另存文件", lambda: saveNewFile(filedialog, text)),  # 另存文件按钮
    ("保存文件", lambda: saveFile(text)),  # 保存文件按钮
    ("运行代码", lambda: preview(text, sourceCodeDir, subprocess)),  # 运行代码按钮
    ("编译代码", lambda: compileCode(topFrame, tk, text, sourceCodeDir, subprocess, root)),  # 编译代码按钮
    ("使用教程", tutorial),  # 使用教程按钮
    ("窗口置顶", lambda: toggleTopmost(root)),  # 窗口置顶按钮
    ("暗夜模式", lambda: toggleDarkMode(text)),  # 暗夜模式切换按钮
    ("语法高亮", lambda: grammar(text)),  # 语法高亮按钮
    ("联系作者", contact),  # 联系作者按钮
]

buttons = {}  # 创建按钮字典
for btnText, btnCommand in buttonConfigs:  # 遍历按钮配置
    btn = tk.Button(topFrame, text=btnText, command=btnCommand, padx=12, pady=7)  # 创建按钮并设置内边距
    btn.pack(side="left", fill="x")  # 将按钮放置在顶部区域，并横向填充
    buttons[btnText] = btn  # 将按钮添加到按钮字典中

buttons["编译代码"]["state"] = "disabled"  # 禁用编译代码按钮

# 创建底部区域的Frame
bottomFrame = tk.Frame(root)  # 创建底部区域的Frame
bottomFrame.pack(fill="both", expand=True)  # 放置在主窗口底部并向所有方向填充

# 创建文本框用于显示文件内容
textFont = tkFont.Font(size=20)  # 设置文本框字体大小
text = tk.Text(bottomFrame, wrap="word", font=textFont, padx=12, pady=12, undo=True, autoseparators=True,)  # 创建文本框并设置属性
text.pack(fill="both", expand=True)  # 将文本框放置在底部区域并向所有方向扩展
text.config(background="white", foreground="black", insertbackground="black")  # 设置文本框的背景色、前景色和插入符颜色

buttonFont = tkFont.Font(size=12)  # 设置按钮字体大小
for child in topFrame.winfo_children():  # 遍历顶部区域的子组件
    if isinstance(child, tk.Button):  # 判断子组件是否为按钮
        child["font"] = buttonFont  # 设置按钮的字体

children = {child["text"]: child for child in topFrame.winfo_children()}  # 创建子组件字典，用于避免 O(n) 的遍历操作

syntaxConfiguration("GrammaticalColors.txt")  # 语法配置，加载语法颜色配置文件

text.bind("<Tab>", lambda event: insertTab(text, tk))  # 为文本框绑定 Tab 键事件
text.bind("<Key>", lambda event: ctrlS(event, text))  # 为文本框绑定按键事件，用于保存文件
text.bind("<KeyRelease>", lambda event: highlightKeywords(text))  # 为文本框绑定按键释放事件，用于高亮关键词
root.protocol("WM_DELETE_WINDOW", lambda: onClosing(root, text))  # 为主窗口绑定关闭事件，用于窗口关闭时的处理

codeRecovery(text, topFrame, tk, "Code.txt")  # 恢复代码记录
windowRecovery("WindowConfiguration.txt", root)  # 恢复窗口记录
styleRecovery("ColorConfiguration.txt", text)  # 恢复样式记录

highlightKeywords(text)  # 初始化界面布局，进行关键词高亮

sourceCodeDir = r"C:\CompileCache\\"  # 缓存目录

root.mainloop()  # 运行主循环
