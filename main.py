import sys
import os
import asyncio
from src.utils.config_service import get_config_service
from src.utils.exceptions import install_global_exception_handler
from src.views.main_win import MainWindowUI
from PySide6.QtWidgets import QApplication, QMainWindow


# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    # 异步执行初始化文件配置
    await asyncio.to_thread(get_config_service().init_config)
    app = QApplication(sys.argv)
    main_window = QMainWindow()

    # 安装全局异常处理器
    install_global_exception_handler(main_window)
    MainWindowUI().setup_ui(main_window)

    # 处理命令行参数
    if len(sys.argv) > 1:
        launch_path = sys.argv[1]
        main_window.setProperty("launch_path", launch_path)

    main_window.show()

    # 运行应用主循环
    sys.exit(app.exec())


if __name__ == '__main__':
    asyncio.run(main())
