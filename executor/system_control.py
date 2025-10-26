# executor/system_control.py
"""
系统控制模块（macOS + Windows）
--------------------------------
- macOS: AppleScript / 音量用 AppleScript
- Windows: NirCmd（项目根或 PATH），无 NirCmd 时降级；截图可走 PowerShell
提供能力：
- 音量：volume_up / volume_down / volume_set / volume_mute / volume_unmute
- 其他：screenshot / lock / sleep
"""

import os
import platform
import subprocess
import re
from pathlib import Path
from shutil import which

system = platform.system()
IS_MAC = (system == "Darwin")
IS_WIN = (system == "Windows")

# ---------- 通用 ----------
def _run(cmd, check=False, shell=False) -> bool:
    try:
        subprocess.run(
            cmd,
            check=check,
            shell=shell,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False

# ---------- macOS ----------
def _osascript(script: str) -> bool:
    if not IS_MAC:
        return False
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False

def _mac_read_volume_pct() -> int | None:
    if not IS_MAC:
        return None
    try:
        out = subprocess.check_output(
            ["osascript", "-e", "output volume of (get volume settings)"],
            text=True
        )
        val = int(re.findall(r"\d+", out.strip())[0])
        return max(0, min(100, val))
    except Exception:
        return None

# ---------- Windows ----------
def _find_nircmd() -> str | None:
    if not IS_WIN:
        return None
    for c in [str(Path.cwd() / "nircmd.exe"), "nircmd.exe"]:
        try:
            subprocess.run([c], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return c
        except Exception:
            pass
    return None

_NIRCMD = _find_nircmd()

def _need_nircmd_warn():
    print("[WARN] Windows 未检测到 nircmd.exe，请将 nircmd.exe 放在项目根目录或加入 PATH："
          "https://www.nirsoft.net/utils/nircmd.html")

def _win_read_volume_pct() -> int | None:
    # 可选依赖：pycaw + comtypes（无则返回 None）
    if not IS_WIN:
        return None
    try:
        from ctypes import POINTER, cast  # type: ignore
        from comtypes import CLSCTX_ALL   # type: ignore
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        level = volume.GetMasterVolumeLevelScalar()  # 0.0~1.0
        return int(round(level * 100))
    except Exception:
        return None

# ---------- 音量 ----------
def volume_set(val: int) -> bool:
    v = max(0, min(100, int(val)))
    if IS_MAC:
        ok = _osascript(f"set volume output volume {v}")
        cur = _mac_read_volume_pct()
        if cur is not None:
            return ok and abs(cur - v) <= 5
        return ok
    if IS_WIN:
        if not _NIRCMD:
            _need_nircmd_warn()
            return False
        target = int(v / 100 * 65535)
        ok = _run([_NIRCMD, "setsysvolume", str(target)])
        cur = _win_read_volume_pct()
        if cur is not None:
            return ok and abs(cur - v) <= 5
        return ok
    print(f"[INFO] 暂不支持此系统 ({system}) 的音量设置。")
    return False

def volume_up() -> bool:
    if IS_MAC:
        return _osascript("set volume output volume (output volume of (get volume settings) + 10)")
    if IS_WIN:
        if not _NIRCMD:
            _need_nircmd_warn()
            return False
        return _run([_NIRCMD, "changesysvolume", "5000"])
    print(f"[INFO] 暂不支持此系统 ({system}) 的音量提升。")
    return False

def volume_down() -> bool:
    if IS_MAC:
        return _osascript("set volume output volume (output volume of (get volume settings) - 10)")
    if IS_WIN:
        if not _NIRCMD:
            _need_nircmd_warn()
            return False
        return _run([_NIRCMD, "changesysvolume", "-5000"])
    print(f"[INFO] 暂不支持此系统 ({system}) 的音量降低。")
    return False

def volume_mute() -> bool:
    if IS_MAC:
        return _osascript("set volume with output muted")
    if IS_WIN:
        if not _NIRCMD:
            _need_nircmd_warn()
            return False
        return _run([_NIRCMD, "mutesysvolume", "1"])
    print(f"[INFO] 暂不支持此系统 ({system}) 的静音。")
    return False

def volume_unmute() -> bool:
    if IS_MAC:
        return _osascript("set volume without output muted")
    if IS_WIN:
        if not _NIRCMD:
            _need_nircmd_warn()
            return False
        return _run([_NIRCMD, "mutesysvolume", "0"])
    print(f"[INFO] 暂不支持此系统 ({system}) 的取消静音。")
    return False

# ---------- 截屏 / 锁屏 / 睡眠 ----------
def screenshot() -> bool:
    try:
        if IS_MAC:
            return _run(["screencapture", "-x", os.path.expanduser("~/Desktop/voice_ss.png")], check=True)
        if IS_WIN:
            if _NIRCMD:
                return _run([_NIRCMD, "savescreenshot", "screenshot.png"], check=True)
            # 无 NirCmd → PowerShell 方案
            return _run([
                "powershell", "-command",
                r"Add-Type -AssemblyName System.Windows.Forms;"
                r"Add-Type -AssemblyName System.Drawing;"
                r"$bmp = New-Object Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height);"
                r"$graphics = [System.Drawing.Graphics]::FromImage($bmp);"
                r"$graphics.CopyFromScreen(0,0,0,0,$bmp.Size);"
                r"$bmp.Save((Get-Location).Path + '\screenshot.png');"
            ], check=True)
        print(f"[INFO] 暂不支持此系统 ({system}) 的截图功能。")
        return False
    except Exception as e:
        print("[ERROR] 截屏失败：", e)
        return False

def lock() -> bool:
    try:
        if IS_MAC:
            return _osascript('tell application "System Events" to keystroke "q" using {control down, command down}')
        if IS_WIN:
            return _run(["Rundll32.exe", "User32.dll,LockWorkStation"], check=True)
        print(f"[INFO] 暂不支持此系统 ({system}) 的锁屏功能。")
        return False
    except Exception as e:
        print("[ERROR] 锁屏失败：", e)
        return False

def sleep() -> bool:
    try:
        if IS_MAC:
            return _run(["pmset", "sleepnow"], check=True)
        if IS_WIN:
            return _run(["Rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
        print(f"[INFO] 暂不支持此系统 ({system}) 的休眠功能。")
        return False
    except Exception as e:
        print("[ERROR] 休眠失败：", e)
        return False
