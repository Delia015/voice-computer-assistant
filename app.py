import os
import threading
from config import SAMPLE_RATE
from utils.recorder import Recorder
from asr.asr_client import asr_transcribe
from llm.llm_client import parse_intent
from tts.tts_client import speak
from executor.app_control import open_app
from executor.system_control import volume_up, volume_down, screenshot, brightness_up, brightness_down
from executor.search_control import web_search

class Controller:
    def __init__(self):
        self.recorder = Recorder(SAMPLE_RATE)
        self.recording = False
        self.wav_path = "record.wav"

    def start_rec(self):
        if self.recording:
            return
        print("开始录音…")
        self.recording = True
        self.recorder.start(self.wav_path)

    def stop_rec(self):
        if not self.recording:
            return
        print("停止录音，开始转写…")
        self.recording = False
        self.recorder.stop()

        text = asr_transcribe(self.wav_path)
        if text.strip():
            print("🔊 识别文本：", text)
            self.handle_intent(text)
        else:
            print("❌ 未识别到有效文本")

    def handle_intent(self, text: str):
        intent = parse_intent(text)
        print("🧠 意图解析：", intent)
        say = intent.get("say", "已完成")
        ok = self.execute(intent)
        if not ok:
            print("📝 我先口头回复，稍后我会继续优化动作能力")

        speak(say)

    def execute(self, intent: dict) -> bool:
        t = intent.get("intent")
        slots = intent.get("slots", {})

        if t == "open_app":
            return open_app(slots.get("app", ""))
        elif t == "system_control":
            action_map = {
                "volume_up": volume_up,
                "volume_down": volume_down,
                "screenshot": screenshot,
                "brightness_up": brightness_up,
                "brightness_down": brightness_down
            }
            fn = action_map.get(slots.get("action", ""))
            if fn:
                fn(); return True
        elif t == "search":
            q = slots.get("query", "")
            if q:
                web_search(q); return True
        return False


if __name__ == "__main__":
    ctrl = Controller()
    print("就绪：按回车开始录音；再次回车停止；Ctrl+C 退出。")

    try:
        while True:
            input("【开始】按回车键开始录音…")
            ctrl.start_rec()
            input("【停止】再次按回车键停止录音…")
            ctrl.stop_rec()
    except KeyboardInterrupt:
        print("\n👋 已退出")
