# gui.py —— 控制台版，不依赖 tkinter
class ConsoleGUI:
    def __init__(self, on_press, on_release):
        self.on_press = on_press
        self.on_release = on_release

    def log(self, s: str):
        print(s, flush=True)

    def loop(self):
        self.log("就绪：按回车开始录音；再次回车停止；Ctrl+C 退出。")
        while True:
            try:
                input("【开始】按回车键开始录音…")
                self.on_press()
                input("【停止】再次按回车键停止录音…")
                self.on_release()
            except KeyboardInterrupt:
                self.log("👋 已退出")
                break

# 兼容旧引用
DesktopGUI = ConsoleGUI
