# app.py
import time
import threading
from config import SAMPLE_RATE
from utils.recorder import Recorder
from asr.asr_client import asr_transcribe
from llm.llm_client import parse_intent
from tts.tts_client import speak

from executor.app_control import open_app
from executor.search_control import web_search
from executor.system_control import (
    volume_up, volume_down, volume_set, volume_mute, volume_unmute,screenshot, lock, sleep
)

class Controller:
    def __init__(self):
        self.recorder = Recorder(SAMPLE_RATE)
        self.recording = False
        self.wav_path = "record.wav"

    # ===== 录音控制 =====
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
            print("❌未识别到有效文本")

    # ===== 主处理 =====
    def handle_intent(self, text: str):
        intent = parse_intent(text)
        print("意图解析：", intent)

        ok = self.execute(intent)

        # 优先使用 LLM 的 say；但执行失败时，覆盖为真实失败提示
        say = intent.get("say")
        if not ok or not say:
            say = self._compose_fail_or_ok_say(intent, ok)
        speak(say)

    def _compose_fail_or_ok_say(self, intent: dict, ok: bool) -> str:
        if ok:
            t = intent.get("intent")
            if t == "system_control":
                act = (intent.get("slots") or {}).get("action", "")
                return {
                    "volume_up": "音量已调大",
                    "volume_down": "音量已调小",
                    "volume_set": "音量已设置",
                    "volume_mute": "已静音",
                    "volume_unmute": "已取消静音",
                    "brightness_up": "亮度已调高",
                    "brightness_down": "亮度已调低",
                    "brightness_set": "亮度已设置",
                    "screenshot": "已截屏",
                    "lock": "已锁定屏幕",
                    "sleep": "已休眠",
                }.get(act, "已完成")
            return "已完成"
        else:
            t = intent.get("intent")
            if t == "system_control":
                act = (intent.get("slots") or {}).get("action","")
                if "brightness" in act:
                    return "抱歉，亮度未能调整：可能缺少权限或该显示器不支持系统亮度控制。"
                if "volume" in act:
                    return "抱歉，音量未能调整：可能默认音频设备不受控或权限不足。"
            return "抱歉，这个动作没有成功。"

    # ===== 编排执行 =====
    def _clip_pct(self, v):
        try:
            iv = int(v)
        except Exception:
            iv = 0
        return max(0, min(100, iv))

    def _exec_one(self, step: dict) -> bool:
        if not isinstance(step, dict):
            return False
        t = step.get("intent")
        slots = step.get("slots", {}) or step

        try:
            if t == "open_app":
                app = slots.get("app", "")
                if not app: return False
                ok = bool(open_app(app))
                return ok

            if t == "open_url":
                url = slots.get("url", "")
                if not url: return False
                return bool(web_search(url))

            if t == "search":
                q = slots.get("query", "")
                if not q: return False
                return bool(web_search(q))

            if t == "system_control":
                action = slots.get("action", "")
                val = slots.get("value")
                action_map = {
                    "volume_up":       volume_up,
                    "volume_down":     volume_down,
                    "volume_set":      (lambda: volume_set(self._clip_pct(val))),
                    "volume_mute":     volume_mute,
                    "volume_unmute":   volume_unmute,

                    "screenshot":      screenshot,
                    "lock":            lock,
                    "sleep":           sleep,
                }
                fn = action_map.get(action)
                if not fn:
                    print(f"[EXEC] 未知系统动作：{action}")
                    return False
                # 统一执行
                r = fn() if fn.__code__.co_argcount == 0 else fn()
                return bool(r)

            if t == "chat":
                return True

            print(f"[EXEC] 未知意图：{t}")
            return False

        except Exception as e:
            print("[EXEC] 单步异常：", e)
            return False

    def _expand_macro(self, slots: dict) -> list[dict]:
        steps = (slots or {}).get("steps") or []
        if steps:
            return steps
        name = (slots or {}).get("name")
        registry = {
            "专注模式": [
                {"intent":"system_control","slots":{"action":"volume_set","value":15}},
                {"intent":"open_app","slots":{"app":"备忘录"}},
                {"intent":"search","slots":{"query":"Lo-fi beats playlist"}}
            ],
            "演示模式": [
                {"intent":"system_control","slots":{"action":"volume_mute"}},
                {"intent":"open_app","slots":{"app":"safari"}},
                {"intent":"open_url","slots":{"url":"https://slides.example.com/demo"}}
            ],
        }
        return registry.get(name, [])

    def execute(self, intent: dict) -> bool:
        t = intent.get("intent")
        slots = intent.get("slots", {}) or {}

        if t == "macro":
            steps = self._expand_macro(slots)
            if not steps:
                print("[EXEC] 空宏：未提供 steps / 未匹配到注册宏")
                return False

            all_ok = True
            for i, step in enumerate(steps, 1):
                ok = self._exec_one(step)
                print(f"[EXEC] Step {i}/{len(steps)} -> {ok} | {step}")
                # 轻节流，给前台激活/亮度设置一点缓冲时间
                time.sleep(0.4)
                all_ok = all_ok and ok
            return all_ok

        return self._exec_one(intent)

from gui import ConsoleGUI

if __name__ == "__main__":
    ctrl = Controller()
    gui = ConsoleGUI(ctrl.start_rec, ctrl.stop_rec)
    gui.loop()
