# tts/tts_client.py
import base64
import tempfile
import subprocess
import requests
from config import QINIU_API_KEY, QINIU_OPENAI_BASE_URL
from utils.audio_player import play_wav_bytes

PREFERRED_VOICE_TYPE = "qiniu_zh_female_xyqxxj"

def _save_tmp(bytes_data: bytes, suffix: str) -> str:
    f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.write(bytes_data)
    f.flush(); f.close()
    return f.name

def _play_mp3(audio_bytes: bytes, log=print):
    path = _save_tmp(audio_bytes, ".mp3")
    try:
        subprocess.run(["afplay", path], check=False)
        log(f"[TTS] 已播放 MP3：{path}")
    except Exception as e:
        log(f"[TTS] MP3 播放失败：{e}（文件已保存：{path}）")

def _play_wav(audio_bytes: bytes, log=print):
    try:
        play_wav_bytes(audio_bytes)
        log("[TTS] ✅ 播放成功（WAV）")
    except Exception as e:
        log(f"[TTS] WAV 播放失败：{e}，使用 afplay 兜底")
        path = _save_tmp(audio_bytes, ".wav")
        try:
            subprocess.run(["afplay", path], check=False)
            log(f"[TTS] 已播放 WAV（afplay）：{path}")
        except Exception as e2:
            log(f"[TTS] WAV afplay 也失败：{e2}（文件已保存：{path}）")

def _extract_b64(data_obj, log=print) -> bytes | None:
    """
    从 JSON 中安全提取 base64 音频：
    支持 {"data":".."} / {"data":{"audio":".."}} / {"audio":".."}
    """
    # data_obj 可能是 str / dict / 其他
    if isinstance(data_obj, str):
        # 整个就是 base64 字符串
        try:
            return base64.b64decode(data_obj)
        except Exception as e:
            log(f"[TTS] base64 解码失败（顶层即字符串）：{e}")
            return None

    if isinstance(data_obj, dict):
        # 优先 data.audio
        try:
            data_field = data_obj.get("data")
            if isinstance(data_field, dict) and isinstance(data_field.get("audio"), str):
                return base64.b64decode(data_field["audio"])
        except Exception as e:
            log(f"[TTS] 解 data.audio 失败：{e}")

        # 其次 data 是字符串
        try:
            if isinstance(data_obj.get("data"), str):
                return base64.b64decode(data_obj["data"])
        except Exception as e:
            log(f"[TTS] 解 data 失败：{e}")

        # 其次 audio 顶层
        try:
            if isinstance(data_obj.get("audio"), str):
                return base64.b64decode(data_obj["audio"])
        except Exception as e:
            log(f"[TTS] 解 audio 失败：{e}")

    # 其他结构：保存原始 JSON 以便排查
    log(f"[TTS] 未识别的 JSON 结构：{type(data_obj)}，将保存原始响应以排查")
    return None

def speak(text: str, log_fn=print):
    if not text or not text.strip():
        return

    url = f"{QINIU_OPENAI_BASE_URL}/voice/tts"
    headers = {"Authorization": f"Bearer {QINIU_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "tts",
        "audio": {
            "voice_type": PREFERRED_VOICE_TYPE,
            "encoding": "wav",      # 请求 wav；若返回 mp3 也能播
            "speed_ratio": 1.0
        },
        "request": {"text": text}
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        ctype = (resp.headers.get("Content-Type") or "").lower()
        log_fn(f"[TTS] HTTP {resp.status_code}, Content-Type: {ctype}")

        if resp.status_code != 200:
            log_fn(f"[TTS] 合成失败：{resp.text}")
            return

        # A) 直接返回音频二进制
        if ctype.startswith("audio/") or "octet-stream" in ctype:
            audio_bytes = resp.content
            if "wav" in ctype:
                _play_wav(audio_bytes, log_fn)
            else:
                _play_mp3(audio_bytes, log_fn)
            return

        # B) JSON + base64
        try:
            data = resp.json()
        except Exception as e:
            # 既非音频也非可解析 JSON — 保存原始内容
            raw_path = _save_tmp(resp.content, ".bin")
            log_fn(f"[TTS] 返回既非音频也非JSON，已保存：{raw_path}（{e}）")
            return

        audio_bytes = _extract_b64(data, log_fn)
        if not audio_bytes:
            # 看看 JSON，保存下来便于排查
            raw_path = _save_tmp(resp.content, ".json")
            log_fn(f"[TTS] 无法从 JSON 中提取音频，已保存：{raw_path}")
            return

        # 尝试按 WAV 播放，不行就当 MP3 播
        try:
            _play_wav(audio_bytes, log_fn)
        except Exception:
            _play_mp3(audio_bytes, log_fn)

    except Exception as e:
        log_fn(f"[TTS] 异常：{e}")
