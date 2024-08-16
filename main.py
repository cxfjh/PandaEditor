import sys # 导入 sys 模块 处理命令行参数
import asyncio # 导入 asyncio 模块 异步执行
from src.utils.config import initFileConfig # 导入初始化配置文件
from src.views.mainWin import Ui_MainWindow # 导入 UI 类
from PyQt6.QtWidgets import QApplication, QMainWindow # 导入 PyQt6 库 处理 UI 相关


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
    asyncio.run(main())  # 异步执行主函数


