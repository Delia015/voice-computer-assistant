# executor/system_control.py
import subprocess

def volume_up():
    script = 'set o to output volume of (get volume settings)\nset n to o + 10\nif n > 100 then set n to 100\nset volume output volume n'
    subprocess.run(["osascript", "-e", script], check=False)

def volume_down():
    script = 'set o to output volume of (get volume settings)\nset n to o - 10\nif n < 0 then set n to 0\nset volume output volume n'
    subprocess.run(["osascript", "-e", script], check=False)

def screenshot():
    subprocess.run(["screencapture", "-x", "~/Desktop/voice_assistant_screenshot.png"], check=False)

def brightness_up():
    # 亮度可选装 brightness 工具；没有则忽略
    subprocess.run(["bash", "-lc", "command -v brightness >/dev/null && brightness +0.1 || true"], check=False)

def brightness_down():
    subprocess.run(["bash", "-lc", "command -v brightness >/dev/null && brightness -0.1 || true"], check=False)
