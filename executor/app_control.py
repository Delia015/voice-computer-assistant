# executor/app_control.py
import os, platform, subprocess, time
from pathlib import Path

IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"

# -------- macOS 映射 --------
APP_ALIASES_MAC = {
    "微信": {"bundle":"com.tencent.xinWeChat","names":["WeChat","微信"],"paths":["/Applications/WeChat.app"]},
    "wechat":{"bundle":"com.tencent.xinWeChat","names":["WeChat"],"paths":["/Applications/WeChat.app"]},
    "safari":{"bundle":"com.apple.Safari","names":["Safari"],"paths":["/Applications/Safari.app"]},
    "chrome":{"bundle":"com.google.Chrome","names":["Google Chrome","Chrome"],"paths":["/Applications/Google Chrome.app"]},
    "finder":{"bundle":"com.apple.finder","names":["Finder"],"paths":["/System/Library/CoreServices/Finder.app"]},
    "备忘录":{"bundle":"com.apple.Notes","names":["Notes","备忘录"],"paths":["/System/Applications/Notes.app"]},
    "音乐":{"bundle":"com.apple.Music","names":["Music","音乐"],"paths":["/System/Applications/Music.app"]},
    "信息":{"bundle":"com.apple.iChat","names":["Messages","信息"],"paths":["/System/Applications/Messages.app"]},
    "系统设置":{"bundle":"com.apple.systempreferences","names":["System Settings","系统设置","System Preferences"],"paths":["/System/Applications/System Settings.app","/Applications/System Preferences.app"]},
    "钉钉":{"bundle":"com.alibaba.dingtalk","names":["DingTalk","钉钉"],"paths":["/Applications/DingTalk.app"]},
    "企业微信":{"bundle":"com.tencent.WeWorkMac","names":["企业微信","WeCom"],"paths":["/Applications/WeCom.app","/Applications/企业微信.app"]},
    "qq":{"bundle":"com.tencent.qq","names":["QQ"],"paths":["/Applications/QQ.app"]},
    "飞书":{"bundle":"com.bytedance.mira","names":["Lark","飞书"],"paths":["/Applications/Lark.app"]},
}

# -------- Windows 映射 --------
APP_ALIASES_WIN = {
    "微信": r"D:\Program Files (x86)\Tencent\Weixin.exe",
    "浏览器": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
}

def _run(cmd:list[str]) -> bool:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
        return True
    except Exception:
        return False

def _spotlight(name:str)->str|None:
    try:
        out = subprocess.check_output(["mdfind", f'kMDItemKind == "Application" && kMDItemFSName == "{name}.app"'], text=True)
        for line in out.splitlines():
            p=line.strip()
            if p.endswith(".app") and os.path.exists(p):
                return p
    except: pass
    return None

def _activate_app(name: str) -> None:
    if not IS_MAC:
        return
    try:
        subprocess.run(["osascript", "-e", f'tell application "{name}" to activate'],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def open_app(app:str)->bool:
    if not app:
        return False
    key = (app or "").strip()

    if IS_MAC:
        info = APP_ALIASES_MAC.get(key) or APP_ALIASES_MAC.get(key.lower())
        # 1) Bundle
        if info and info.get("bundle"):
            if _run(["open","-b",info["bundle"]]):
                nm = (info.get("names") or [key])[0]
                time.sleep(0.2)
                _activate_app(nm)
                return True
        # 2) 名称
        if info and info.get("names"):
            for nm in info["names"]:
                if _run(["open","-a",nm]):
                    time.sleep(0.2)
                    _activate_app(nm)
                    return True
        # 3) 路径
        if info and info.get("paths"):
            for p in info["paths"]:
                if Path(p).exists() and _run(["open",p]):
                    nm = (info.get("names") or [Path(p).stem])[0]
                    time.sleep(0.2)
                    _activate_app(nm)
                    return True
        # 4) Spotlight 猜测
        for guess in [key, key.capitalize(), key.title()]:
            p=_spotlight(guess)
            if p and _run(["open",p]):
                time.sleep(0.2)
                _activate_app(Path(p).stem)
                return True
        return False

    if IS_WIN:
        exe = APP_ALIASES_WIN.get(key) or APP_ALIASES_WIN.get(key.lower())
        if exe and Path(exe).exists():
            try:
                subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                pass
        try:
            subprocess.run(f'start "" "{key}"', shell=True)
            return True
        except Exception:
            pass
        try:
            os.startfile(key)
            return True
        except Exception:
            return False

    return False
