from PySide6 import QtCore
from src.utils.config_service import get_config_service


class WindowFocusFilter(QtCore.QObject):
    """窗口焦点事件过滤器 - 监听窗口失去焦点事件"""

    def __init__(self, auto_save_callback):
        """
        初始化窗口焦点事件过滤器
        
        Args:
            auto_save_callback: 自动保存回调函数（窗口失焦时调用）
        """
        super().__init__()
        self._auto_save_callback = auto_save_callback

    def eventFilter(self, obj, event):
        """
        事件过滤器核心方法 - 拦截并处理窗口事件
        
        Args:
            obj: QObject 实例，事件目标对象
            event: QEvent 实例，包含事件类型和详细信息
            
        Returns:
            bool: 如果事件已被处理则返回 True，否则返回父类实现的结果
        """
        # 监听窗口失焦事件
        if event.type() == QtCore.QEvent.Type.WindowDeactivate:
            self._auto_save_callback()  # 触发自动保存
        return super().eventFilter(obj, event)


class FontSizeFilter(QtCore.QObject):
    """字体大小事件过滤器 - 支持 Ctrl+滚轮改变字体大小"""

    def __init__(self, text_edit):
        """
        初始化字体大小事件过滤器
        
        Args:
            text_edit: QPlainTextEdit 实例，需要应用字体缩放功能的文本编辑器
        """
        super().__init__(text_edit)  # 设置父对象为编辑器
        self._text_edit = text_edit

    def eventFilter(self, obj, event):
        """
        事件过滤器核心方法 - 拦截并处理鼠标滚轮事件
        
        Args:
            obj: QObject 实例，事件目标对象
            event: QEvent 实例，包含事件类型和详细信息
            
        Returns:
            bool: 如果事件已被处理则返回 True，否则返回父类实现的结果
        """
        if obj == self._text_edit:
            # 拦截 Ctrl+滚轮事件
            if event.type() == QtCore.QEvent.Type.Wheel and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:  # type: ignore
                font = self._text_edit.font()
                current_size = font.pointSize()

                # 检查滚轮方向
                new_size = current_size + 1 if event.angleDelta().y() > 0 else current_size - 1  # type: ignore

                # 限制字体大小在 6 磅到 90 磅之间
                new_size = max(6, min(90, new_size))
                font.setPointSize(new_size)
                self._text_edit.setFont(font)

                # 保存字体大小到配置
                self._save_font_size(new_size)
                return True  # 事件已处理，阻止传递给编辑器

        return super().eventFilter(obj, event)  # 其他事件交给父类处理

    @staticmethod
    def _save_font_size(size):
        """
        保存字体大小到用户配置文件
        
        Args:
            size: 字体大小（磅值）
        """
        try:
            config_service = get_config_service()
            config_service.update_personal_config("fontSize", size)
        except Exception as e:
            print(f"保存字体大小失败: {e}")
