# app.py
from gui import ConsoleGUI as AppGUI
from asr.asr_client import QiniuPTTASR
from llm.llm_client import parse_intent
from tts.tts_client import speak
from executor.app_control import open_app
from executor.system_control import volume_up, volume_down, screenshot, brightness_up, brightness_down
from executor.search_control import web_search

class Controller:
    def __init__(self, ui: AppGUI):
        self.ui = ui
        self.asr = None

    def _on_asr_result(self, text):
        self.ui.log(f"🔊 识别文本：{text}")
        intent = parse_intent(text)
        self.ui.log(f"🧠 意图解析：{intent}")
        say = intent.get("say") or "已完成"
        ok = self._execute(intent)
        self.ui.log("✅ 执行完成" if ok else "ℹ️ 未能执行具体动作，已口头回复")
        speak(say)

    def _execute(self, intent: dict) -> bool:
        t = intent.get("intent")
        slots = intent.get("slots", {}) or {}
        if t == "open_app":
            app = slots.get("app", "")
            return open_app(app)
        elif t == "system_control":
            act = slots.get("action", "")
            mapping = {
                "volume_up": volume_up,
                "volume_down": volume_down,
                "screenshot": screenshot,
                "brightness_up": brightness_up,
                "brightness_down": brightness_down
            }
            fn = mapping.get(act)
            if fn: fn(); return True
        elif t == "search":
            q = slots.get("query", "")
            if q: web_search(q); return True
        return False

    # —— 按住开始录音
    def start_rec(self):
        if self.asr:  # 已在录
            return
        self.ui.log("开始录音…")
        self.asr = QiniuPTTASR(on_sentence=self._on_asr_result,
                               on_partial=lambda x: None,
                               log_fn=self.ui.log)
        self.asr.start()

    # —— 松开停止并触发 ASR
    def stop_rec(self):
        if self.asr:
            self.ui.log("停止录音，开始转写…")
            self.asr.stop()
            self.asr = None

if __name__ == "__main__":
    ui = AppGUI(on_press=lambda: ctrl.start_rec(), on_release=lambda: ctrl.stop_rec())
    ctrl = Controller(ui)
    ui.loop()
