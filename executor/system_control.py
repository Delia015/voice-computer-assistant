# executor/system_control.py
import os
from pathlib import Path

def volume_up():
    # 每次+10
    os.system('osascript -e "set volume output volume (output volume of (get volume settings) + 10)"')

def volume_down():
    os.system('osascript -e "set volume output volume (output volume of (get volume settings) - 10)"')

def screenshot():
    dest = str(Path.home() / "Desktop" / "screenshot.png")
    os.system(f'screencapture -x "{dest}"')

def brightness_up():
    # 若安装了 brightness 工具则使用；否则提示
    if os.system("command -v brightness >/dev/null 2>&1") == 0:
        os.system("brightness +0.1")
    else:
        print("[提示] 亮度调节需要安装 brightness 工具：brew install brightness")

def brightness_down():
    if os.system("command -v brightness >/dev/null 2>&1") == 0:
        os.system("brightness -0.1")
    else:
        print("[提示] 亮度调节需要安装 brightness 工具：brew install brightness")
