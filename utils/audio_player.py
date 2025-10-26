# utils/audio_player.py
# 统一使用 sounddevice 播放 WAV 字节；在 Windows 上无 sounddevice 时兜底 winsound

from __future__ import annotations
import io
import wave
import numpy as np

try:
    import sounddevice as sd
    _HAVE_SD = True
except Exception:
    _HAVE_SD = False

# winsound 仅在 Windows 可用；非 Windows 导入会失败，按需兜底
try:
    import winsound  # type: ignore
    _HAVE_WINSOUND = True
except Exception:
    _HAVE_WINSOUND = False


def _wav_bytes_to_float32(wav_bytes: bytes) -> tuple[np.ndarray, int]:
    """将 WAV 字节解析为 float32 numpy 数组（-1~1）与采样率"""
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        sr = wf.getframerate()
        ch = wf.getnchannels()
        sw = wf.getsampwidth()  # bytes per sample
        nframes = wf.getnframes()
        frames = wf.readframes(nframes)

    if sw == 1:
        # unsigned 8-bit -> center to 0 and scale to [-1, 1]
        audio = np.frombuffer(frames, dtype=np.uint8).astype(np.int16)
        audio = (audio - 128) / 128.0
    elif sw == 2:
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sw == 4:
        audio = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sw} bytes")

    if ch > 1:
        audio = audio.reshape(-1, ch)

    return audio.astype(np.float32), sr


def play_wav_bytes(wav_bytes: bytes) -> None:
    """播放 WAV 字节；优先 sounddevice，无法使用时在 Windows 兜底 winsound"""
    if _HAVE_SD:
        data, sr = _wav_bytes_to_float32(wav_bytes)
        sd.play(data, sr, blocking=True)
        return

    if _HAVE_WINSOUND:
        # winsound 支持内存中的 WAV（含头），无需落盘
        winsound.PlaySound(wav_bytes, winsound.SND_MEMORY)
        return

    raise RuntimeError("No available audio backend: please install 'sounddevice'.")
