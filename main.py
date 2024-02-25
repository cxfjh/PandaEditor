import subprocess
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog

from module import (
    compileCode,
    openFile,
    saveFile,
    saveNewFile,
    preview,
    contact,
    tutorial,
    toggleTopmost,
    toggleDarkMode,
    codeRecovery,
    insertTab,
    windowRecovery,
    styleRecovery,
    disposition,
    ctrlS,
    onClosing,
    highlightKeywords,
    grammar,
    syntaxConfiguration
)

# 创建主窗口
root = tk.Tk()
root.title("熊猫编辑器")

# 获取屏幕宽度和高度
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()

# 设置窗口大小为屏幕的90%
windowWidth = int(screenWidth * 0.8)
windowHeight = int(screenHeight * 0.8)
root.geometry(f"{windowWidth}x{windowHeight}")

# 创建顶部区域的Frame
topFrame = tk.Frame(root)
topFrame.pack(side="top", fill="x")

# 创建按钮
buttonConfigs = [
    ("打开文件", lambda: openFile(filedialog, text, topFrame, tk)),
    ("另存文件", lambda: saveNewFile(filedialog, text)),
    ("保存文件", lambda: saveFile(text)),
    ("运行代码", lambda: preview(text, sourceCodeDir, subprocess)),
    ("编译代码", lambda: compileCode(topFrame, tk, text, sourceCodeDir, subprocess, root),),
    ("使用教程", tutorial),
    ("窗口置顶", lambda: toggleTopmost(root)),
    ("暗夜模式", lambda: toggleDarkMode(text)),
    ("语法高亮", lambda: grammar(text)),
    ("联系作者", contact),
]

# 遍历按钮配置，创建并添加到顶部区域
buttons = {}
for btnText, btnCommand in buttonConfigs:
    btn = tk.Button(topFrame, text=btnText, command=btnCommand, padx=12, pady=7)  # 设置按钮的内边距
    btn.pack(side="left", fill="x")
    buttons[btnText] = btn

# 禁用编译代码按钮
buttons["编译代码"]["state"] = "disabled"

# 创建底部区域的Frame
bottomFrame = tk.Frame(root)
bottomFrame.pack(fill="both", expand=True)

# 创建文本框用于显示文件内容
textFont = tkFont.Font(size=20)  # 设置文本框字体大小
text = tk.Text(bottomFrame, wrap="word", font=textFont, padx=12, pady=12, undo=True, autoseparators=True,)  # 设置文本框的内边距
text.pack(fill="both", expand=True)
text.config(background="white", foreground="black", insertbackground="black")

# 设置按钮字体大小
buttonFont = tkFont.Font(size=12)
for child in topFrame.winfo_children():
    if isinstance(child, tk.Button): child["font"] = buttonFont

# 创建子组件字典，避免 O(n) 的遍历操作
children = {child["text"]: child for child in topFrame.winfo_children()}

syntaxConfiguration("GrammaticalColors.txt", text)

# 为文本框绑定按键事件
text.bind("<Tab>", lambda event: insertTab(text, tk))
text.bind("<Key>", lambda event: ctrlS(event, text))
text.bind("<KeyRelease>", lambda event: highlightKeywords(text))
root.protocol("WM_DELETE_WINDOW", lambda: onClosing(root, text))

# 恢复代码记录、窗口记录和暗夜记录
codeRecovery(text, topFrame, tk, "Code.txt")
windowRecovery("WindowConfiguration.txt", root)
styleRecovery("ColorConfiguration.txt", text)

# 初始化界面布局
disposition(topFrame, tk)
highlightKeywords(text)

# 缓存目录
sourceCodeDir = r"C:\CompileCache\\"

root.mainloop()
