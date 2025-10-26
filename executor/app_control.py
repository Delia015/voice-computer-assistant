# executor/app_control.py
import os
import subprocess
from pathlib import Path

# 常用应用的别名到 bundleId / 可执行名称 / 路径 的映射
APP_ALIASES = {
    # 微信
    "微信": {"bundle": "com.tencent.xinWeChat", "names": ["WeChat", "微信"], "paths": ["/Applications/WeChat.app"]},
    "wechat": {"bundle": "com.tencent.xinWeChat", "names": ["WeChat"], "paths": ["/Applications/WeChat.app"]},

    # Safari
    "safari": {"bundle": "com.apple.Safari", "names": ["Safari"], "paths": ["/Applications/Safari.app"]},

    # Finder
    "finder": {"bundle": "com.apple.finder", "names": ["Finder"], "paths": ["/System/Library/CoreServices/Finder.app"]},

    # 你可以继续在这里加：备忘录、音乐、信息 等
    "备忘录": {"bundle": "com.apple.Notes", "names": ["Notes", "备忘录"], "paths": ["/System/Applications/Notes.app"]},
    "音乐":   {"bundle": "com.apple.Music", "names": ["Music", "音乐"], "paths": ["/System/Applications/Music.app"]},
    "信息":   {"bundle": "com.apple.iChat", "names": ["Messages", "信息"], "paths": ["/System/Applications/Messages.app"]},
}

def _run(cmd: list[str]) -> bool:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def _spotlight_find(name: str) -> str | None:
    """用 Spotlight 找 *.app 路径"""
    try:
        out = subprocess.check_output([
            "mdfind",
            f'kMDItemKind == "Application" && kMDItemFSName == "{name}.app"'
        ], text=True)
        for line in out.strip().splitlines():
            p = line.strip()
            if p.endswith(".app") and os.path.exists(p):
                return p
    except Exception:
        pass
    return None

def open_app(app: str) -> bool:
    key = (app or "").strip()
    low = key.lower()
    info = APP_ALIASES.get(key) or APP_ALIASES.get(low)

    # 1) 优先用 Bundle ID
    if info and info.get("bundle"):
        if _run(["open", "-b", info["bundle"]]):
            return True

    # 2) 退回用 -a 名称（WeChat / 微信）
    if info and info.get("names"):
        for nm in info["names"]:
            if _run(["open", "-a", nm]):
                return True

    # 3) 退回硬路径
    if info and info.get("paths"):
        for p in info["paths"]:
            if Path(p).exists() and _run(["open", p]):
                return True

    # 4) 最后再猜测：按用户说的名字搜 Spotlight
    guess_names = [key, key.capitalize(), key.title()]
    for nm in guess_names:
        p = _spotlight_find(nm)
        if p and _run(["open", p]):
            return True

    return False
