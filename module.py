import shutil
import subprocess
import urllib.request
import os
import re
import sys
import threading
from tkinter import messagebox
from StandardLibrary import PunctuationMarks, Keywords1, Keywords2 ,Keywords3, Keywords4, Keywords5, BuiltinModules

# 初始化全局变量
saveFileName = ""
nameFile = ""  # 当前文件名
newFile = ""  # 储存目录
fileName = "temporary.py"  # 文件名，默认为temporary.py
lastSavedContent = ""  # 保存上次内容
grammaticalColors = True
replacements = {**PunctuationMarks, **Keywords1, **Keywords2, **Keywords3, **Keywords4, **Keywords5, **BuiltinModules}


# 将文件解析成代码
def translate(string):
    try:
        pattern = re.compile('|'.join(map(re.escape, replacements.keys())))
        result = pattern.sub(lambda match: replacements[match.group(0)], string)
        return result
    except Exception as e: messagebox.showinfo("代码解析", "错误提示\n联系作者：2449579731")


# 编译完成后复制文件到指定目录
def copyFiles(sourceDir, targetDir, name, sourceCodeDir):
    try:
        # 创建存放文件位置
        os.makedirs(targetDir, exist_ok=True)
        os.makedirs(os.path.join(targetDir, "源代码"), exist_ok=True)

        # 复制文件到指定目录
        shutil.copy2(os.path.join(sourceDir, "dist", f"{name}.exe"), targetDir)
        shutil.copy2(os.path.join(sourceDir, f"{name}.py"), os.path.join(targetDir, "源代码"))

        shutil.rmtree(sourceCodeDir) # 删除额外文件
    except Exception as e: print("文件已经解析与编译完成。")


# 打开文件按钮的点击事件
def openFile(filedialog, text, topFrame, tk):
    global nameFile, newFile, fileName, saveFileName, lastSavedContent # 将变量声明为全局变量，以便其他函数使用
    
    filePath = saveFileName = filedialog.askopenfilename(filetypes=[("*", "*.cn")])
    history("Code.txt", filePath)  # 历史记录函数
    with open(filePath, "r", encoding="utf-8") as file: content = file.read()

    text.delete(1.0, "end")
    text.insert("end", content)
    lastSavedContent = text.get(1.0, "end")
    
    nameFile = os.path.splitext(os.path.basename(filePath))[0]  # 获取文件名（不包含扩展名）
    newFile = os.path.join(os.path.dirname(filePath), "源文件", nameFile)  # 设置文件的储存目录
    fileName = nameFile + ".py"  # 设置文件名为 文件名.py
    highlightKeywords(text)
    
    # 解除禁用其他按钮
    for child in topFrame.winfo_children():
        if isinstance(child, tk.Button) and child["text"] == "编译代码": child["state"] = "normal"
        

# 保存文件按钮的点击事件
def saveFile(text):
    global lastSavedContent, saveFileName
    content = lastSavedContent = text.get(1.0, "end")
    with open(saveFileName, "w", encoding="utf-8") as file: file.write(content)


# 另存文件
def saveNewFile(filedialog, text):
    filePath = filedialog.asksaveasfilename(defaultextension="cn", filetypes=[(".cn", ".cn")])
    content = text.get(1.0, "end")
    with open(filePath, "w", encoding="utf-8") as file: file.write(content)


# 解析并执行代码
def preview(text, sourceCodeDir, subprocess):
    try:
        translatedCode = translate(text.get("1.0", "end-1c"))  # 解析文件内容
        os.makedirs(sourceCodeDir, exist_ok=True)  # 创建源代码的存储目录
        sourceFilePath = os.path.join(sourceCodeDir, fileName)  # 创建python文件路径

        with open(sourceFilePath, "w", encoding="utf-8") as file: file.write(translatedCode) # 将解析后的代码写入文件
        subprocess.Popen(["python", sourceFilePath])  # 打开新进程运行python文件
    except Exception as e: messagebox.showinfo("运行代码", "错误提示\n联系作者：2449579731")


# 历史记录
def history(file, text):
    try:
        folderName = r"C:\PandaEditorHistory"
        fileName = file
        fileContent = text

        os.makedirs(folderName, exist_ok=True)
        filePath = os.path.join(folderName, fileName)
        with open(filePath, 'w', encoding='utf-8') as file: file.write(fileContent)
    except Exception as e: messagebox.showinfo("恢复记录", "错误提示\n联系作者：2449579731")


# 新线程执行编译代码的逻辑
def compileCodeInThread(topFrame, tk, text, sourceCodeDir, subprocess, root):
    try:
        for child in topFrame.winfo_children(): # 禁用按钮
            if isinstance(child, tk.Button) and child["text"] != "联系作者": child["state"] = "disabled"

        translatedCode = translate(text.get("1.0", "end-1c"))  # 解析文件内容
        os.makedirs(sourceCodeDir, exist_ok=True)  # 创建源代码的存储目录
        sourceFilePath = os.path.join(sourceCodeDir, fileName)  # 创建python文件路径
        with open(sourceFilePath, "w", encoding="utf-8") as file: file.write(translatedCode)  # 将解析后的代码写入文件

        os.chdir(sourceCodeDir)  # 切换到源代码目录
        subprocess.run(["pyinstaller", "-F", fileName])  # 使用pyinstaller打包成exe可执行文件
        copyFiles(sourceCodeDir, newFile, nameFile, sourceCodeDir)  # 复制文件到指定目录

        os.startfile(newFile)  # 打开编译好的文件夹

    except FileNotFoundError: messagebox.showinfo("错误提示", "文件不存在")
    except Exception as e: messagebox.showinfo("错误提示", "发生错误")
    finally:
        for child in topFrame.winfo_children(): # 解除禁用其他按钮
            if isinstance(child, tk.Button) and child["text"] != "联系作者": child["state"] = "normal"
        root.update()


# 编译代码文件
def compileCode(topFrame, tk, text, sourceCodeDir, subprocess, root): threading.Thread(target=compileCodeInThread, args=(topFrame, tk, text, sourceCodeDir, subprocess, root)).start()


# 联系按钮的点击事件
def contact(): messagebox.showinfo("联系作者", "邮箱：2449579731qq.com\n开源：https://github.com/cxfjh/PandaEditor")


# 使用教程
def tutorial(): messagebox.showinfo("使用教程", "<编译代码>功能要打开文件即可使用\n运行环境：python、pyinstaller\n缺少某个环境会导致<编译代码>，<运行代码>功能无法加载\n联系作者：2449579731")


# 窗口置顶
def toggleTopmost(root):
    try:
        topmost = int(not root.attributes('-topmost'))
        root.attributes('-topmost', topmost)
        history("WindowConfiguration.txt", str(topmost))
    except Exception as e: messagebox.showinfo("窗口置顶", "错误提示\n联系作者：2449579731")


# 暗夜功能
def toggleDarkMode(text, color="white"):
    try:    
        currentBg = text.cget("background")
        if currentBg == color: text.config(background="#1f1f1f", foreground="white", insertbackground="white")
        else: text.config(background="white", foreground="#1f1f1f", insertbackground="#1f1f1f")
        history("ColorConfiguration.txt", currentBg)
    except Exception as e: messagebox.showinfo("暗夜模式", "错误提示\n联系作者：2449579731")


# 恢复历史记录
def restoreHistory(file):
    try:
        filePath = os.path.join(r"C:\PandaEditorHistory", file)
        if not os.path.exists(filePath): return None
        with open(filePath, 'r', encoding="utf-8") as f: text = f.read()
        if not text: return None
        return text
    except Exception as e: messagebox.showinfo("配置提示", "错误提示\n联系作者：2449579731")


# 恢复代码历史
def codeRecovery(text, topFrame, tk, file):
    try:
        global nameFile, newFile, fileName, saveFileName, lastSavedContent  # 将变量声明为全局变量，以便其他函数使用
        filePath = saveFileName = restoreHistory(file)
        if filePath is None: return
        if not os.path.exists(filePath): return
        with open(filePath, "r", encoding="utf-8") as file: content = file.read()

        text.delete(1.0, "end")
        text.insert("end", content)
        lastSavedContent = text.get(1.0, "end")

        nameFile = os.path.splitext(os.path.basename(filePath))[0]  # 获取文件名（不包含扩展名）
        newFile = os.path.dirname(filePath) + r"\源文件\\" + nameFile  # 设置文件的储存目录
        fileName = nameFile + ".py"  # 设置文件名为 文件名.py

        for child in topFrame.winfo_children(): # 解除禁用其他按钮
            if isinstance(child, tk.Button) and child["text"] == "编译代码": child["state"] = "normal"
    except Exception as e: messagebox.showinfo("配置提示", "恢复代码历史时出错")


# 窗口配置恢复
def windowRecovery(file, root):
    try:
        disposition = restoreHistory(file)
        if disposition is None: return
        root.attributes('-topmost', int(disposition))
    except Exception as e: messagebox.showinfo("配置提示", "窗口配置恢复时出错")


# 暗夜配置恢复
def styleRecovery(file, text):
    try:
        disposition = restoreHistory(file)
        if disposition is None: return
        toggleDarkMode(text, disposition)
    except Exception as e: messagebox.showinfo("配置提示", "暗夜模式配置恢复时出错")


# 语法高亮恢复
def syntaxConfiguration(file):
    try:
        if restoreHistory(file) is None: return
        global grammaticalColors 
        grammaticalColors = restoreHistory(file).lower() == "true"
    except Exception as e: messagebox.showinfo("配置提示", "语法高亮恢复恢复时出错")    


# 按Tab键时插入4个空格
def insertTab(text, tk):
    text.insert(tk.INSERT, "    ")
    return 'break'  # 阻止默认事件


# 绑定ctrl+s
def ctrlS(event, text):
    if event.keysym == 's' and event.state == 4: saveFile(text)


# 自动保存
def onClosing(root, text):
    global lastSavedContent
    if lastSavedContent != text.get(1.0, "end") and not (len(lastSavedContent) == 0 and len(text.get(1.0, "end")) == 1):
        answer = messagebox.askyesno("保存提示", "是否要自动保存代码！！！")
        if answer: saveFile(text)
    root.destroy()


# # 初始化
# def init(topFrame, tk):
#     if sys.version_info.major < 3: return hideButton(topFrame, tk, '编译代码', '运行代码')
#     try: import PyInstaller
#     except ImportError:
#         try:
#             response = urllib.request.urlopen('http://www.baidu.com', timeout=1)
#             if response.getcode() == 200:
#                 try:
#                     hideButton(topFrame, tk, '编译代码', '空')
#                     subprocess.Popen([sys.executable, "-m", "pip", "install", "pyinstaller"]).wait()
#                     messagebox.showinfo("熊猫编辑器", "配置环境成功\n需要重新启动程序才能使用<编译代码>功能")
#                 except Exception as e: hideButton(topFrame, tk, '编译代码', '空')
#             else: hideButton(topFrame, tk, '编译代码', '空')
#         except Exception as e: hideButton(topFrame, tk, '编译代码', '空')


# # 隐藏按钮
# def hideButton(topFrame, tk, text1, text2, hide=True):
#     buttons = [child for child in topFrame.winfo_children() if isinstance(child, tk.Button)]
#     buttons = [button for button in buttons if button["text"] in (text1, text2)]
#     [button.pack_forget() if hide else button.pack() for button in buttons]


# # 判断是否安装环境
# def disposition(topFrame, tk): threading.Thread(target=lambda: init(topFrame, tk)).start()


# 语法高亮
def highlightKeywords(text, start="1.0", end="end"):
    if not grammaticalColors: return
    text.tag_remove("keyword", start, end)
    text.tag_remove("builtin", start, end)

    for cnKeyword, enKeyword in replacements.items():
        pattern = re.compile(re.escape(cnKeyword))
        matches = pattern.finditer(text.get(start, end))

        for match in matches:
            startPos = f"{start}+{match.start()}c"
            endPos = f"{start}+{match.end()}c"
            tag = None
            keywordTags = {
                **{keyword: "punctuation" for keyword in PunctuationMarks},
                **{keyword: "keyword1" for keyword in Keywords1},
                **{keyword: "keyword2" for keyword in Keywords2},
                **{keyword: "keyword3" for keyword in Keywords3},
                **{keyword: "keyword4" for keyword in Keywords4},
                **{keyword: "keyword5" for keyword in Keywords5},
                **{keyword: "builtin" for keyword in BuiltinModules}
            }
            tag = keywordTags.get(cnKeyword, None)
            if tag: text.tag_add(tag, startPos, endPos)
    
        # 设置不同类型关键字对应的颜色
        tagColors = { "punctuation": "#ff6347", "keyword1": "#c580ab", "keyword2": "#cccccc","keyword3": "#569cd6", "keyword4": "#4ec9b0", "keyword5": "#dcdcaa", "builtin": "#90ee90"}
        for tag, color in tagColors.items():
            text.tag_config(tag, foreground=color)


# 控制语法高亮显示
def grammar(text, start="1.0", end="end"):
    global grammaticalColors
    grammaticalColors = not grammaticalColors
    history("GrammaticalColors.txt", str(grammaticalColors))
    if grammaticalColors: return highlightKeywords(text)
    tags = ["punctuation", "keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "builtin"]
    for tag in tags:
        text.tag_remove(tag, start, end)

