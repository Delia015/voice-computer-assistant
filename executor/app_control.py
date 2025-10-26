# executor/app_control.py
import os, subprocess
from pathlib import Path

APP_ALIASES = {
    # 常用
    "微信": {"bundle":"com.tencent.xinWeChat","names":["WeChat","微信"],"paths":["/Applications/WeChat.app"]},
    "wechat":{"bundle":"com.tencent.xinWeChat","names":["WeChat"],"paths":["/Applications/WeChat.app"]},
    "safari":{"bundle":"com.apple.Safari","names":["Safari"],"paths":["/Applications/Safari.app"]},
    "chrome":{"bundle":"com.google.Chrome","names":["Google Chrome","Chrome"],"paths":["/Applications/Google Chrome.app"]},
    "finder":{"bundle":"com.apple.finder","names":["Finder"],"paths":["/System/Library/CoreServices/Finder.app"]},
    "备忘录":{"bundle":"com.apple.Notes","names":["Notes","备忘录"],"paths":["/System/Applications/Notes.app"]},
    "音乐":{"bundle":"com.apple.Music","names":["Music","音乐"],"paths":["/System/Applications/Music.app"]},
    "信息":{"bundle":"com.apple.iChat","names":["Messages","信息"],"paths":["/System/Applications/Messages.app"]},
    "系统设置":{"bundle":"com.apple.systempreferences","names":["System Settings","系统设置","System Preferences"],"paths":["/System/Applications/System Settings.app","/Applications/System Preferences.app"]},
}

def _run(cmd:list[str])->bool:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except: return False

def _spotlight(name:str)->str|None:
    try:
        out = subprocess.check_output(["mdfind", f'kMDItemKind == "Application" && kMDItemFSName == "{name}.app"'], text=True)
        for line in out.splitlines():
            p=line.strip()
            if p.endswith(".app") and os.path.exists(p):
                return p
    except: pass
    return None

def open_app(app:str)->bool:
    key=(app or "").strip()
    info=APP_ALIASES.get(key) or APP_ALIASES.get(key.lower())

    # 1) Bundle ID
    if info and info.get("bundle"):
        if _run(["open","-b",info["bundle"]]): return True
    # 2) 应用名
    if info and info.get("names"):
        for nm in info["names"]:
            if _run(["open","-a",nm]): return True
    # 3) 路径
    if info and info.get("paths"):
        for p in info["paths"]:
            if Path(p).exists() and _run(["open",p]): return True
    # 4) Spotlight 猜测
    for guess in [key, key.capitalize(), key.title()]:
        p=_spotlight(guess)
        if p and _run(["open",p]): return True
    return False
