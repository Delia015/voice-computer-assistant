# utils/audio_player.py
import io
import wave
import simpleaudio as sa

def play_wav_bytes(wav_bytes: bytes):
    bio = io.BytesIO(wav_bytes)
    with wave.open(bio, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        obj = sa.play_buffer(
            frames,
            wf.getnchannels(),
            wf.getsampwidth(),   # 通常 2 字节
            wf.getframerate(),
        )
        obj.wait_done()
