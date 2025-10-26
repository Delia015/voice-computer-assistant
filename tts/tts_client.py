# tts/tts_client.py
import base64
import requests
from config import (
    QINIU_API_KEY,
    QINIU_OPENAI_BASE_URL,
    QINIU_TTS_MODEL,
    QINIU_TTS_VOICE,
    QINIU_TTS_FORMAT,
)
from utils.audio_player import play_wav_bytes


def speak(text: str, log_fn=print):
    """
    调用七牛 /voice/tts 进行合成，优先请求 WAV，直接播放。
    """
    if not text:
        return

    url = f"{QINIU_OPENAI_BASE_URL}/voice/tts"
    payload = {
        "model": QINIU_TTS_MODEL,
        "audio": {
            "voice_type": QINIU_TTS_VOICE,  # <== 关键字段
            "format": QINIU_TTS_FORMAT,     # 建议 'wav'
        },
        "request": {
            "text": text,                   # <== 关键字段
        }
    }
    headers = {
        "Authorization": f"Bearer {QINIU_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            if log_fn:
                log_fn(f"[TTS] 合成失败 {resp.status_code} {resp.text}")
            return

        # 兼容两种返回：音频二进制 或 JSON(base64)
        ctype = resp.headers.get("Content-Type", "")
        if ctype.startswith("audio/"):
            audio_bytes = resp.content
        else:
            data = resp.json()
            # 常见结构：{"data": {"audio": "<base64>"}}
            b64 = (
                (data.get("data") or {}).get("audio")
                or data.get("audio")
            )
            if not b64:
                if log_fn:
                    log_fn(f"[TTS] 返回无音频字段：{data}")
                return
            audio_bytes = base64.b64decode(b64)

        # 我们请求的是 WAV，直接播
        play_wav_bytes(audio_bytes)

    except Exception as e:
        if log_fn:
            log_fn(f"[TTS] 异常：{e}")
