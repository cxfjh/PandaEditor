import sys 
import asyncio 
from src.utils.Config import initFileConfig 
from src.views.MainWin import Ui_MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow


async def asyncInit(): await asyncio.to_thread(initFileConfig) # 异步执行初始化文件配置


# 异步执行初始化窗口配置
async def main():
    await asyncInit()  # 异步执行初始化文件配置
    app = QApplication(sys.argv)  # 创建应用程序对象
    mainWindow = QMainWindow()    # 创建主窗口对象
    Ui_MainWindow().setupUi(mainWindow)  # 设置 UI 到主窗口
    mainWindow.show()  # 显示主窗口
    sys.exit(app.exec())  # 执行应用程序主循环

    
if __name__ == '__main__':
    asyncio.run(main())




