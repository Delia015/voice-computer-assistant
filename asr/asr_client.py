import time
import requests
from qiniu import Auth, put_file
from config import (
    QINIU_API_KEY,
    QINIU_OPENAI_BASE_URL,
    QINIU_ASR_MODEL,
    QINIU_KODO_AK,
    QINIU_KODO_SK,
    QINIU_KODO_BUCKET,
    QINIU_KODO_DOMAIN,
)

# 上传录音到 Kodo，换取公网 URL
def upload_to_kodo(local_path):
    try:
        q = Auth(QINIU_KODO_AK, QINIU_KODO_SK)
        key = f"voice/{int(time.time())}_{local_path.split('/')[-1]}"
        token = q.upload_token(QINIU_KODO_BUCKET, key)
        ret, info = put_file(token, key, local_path)

        if info.status_code == 200:
            return f"{QINIU_KODO_DOMAIN}/{key}"
        else:
            print("[ASR] Kodo 上传失败", info)
            return None
    except Exception as e:
        print("[ASR] 上传异常", e)
        return None

# 调用七牛语音识别
def qiniu_asr(audio_url: str) -> str:
    url = f"{QINIU_OPENAI_BASE_URL}/voice/asr"
    payload = {
        "model": QINIU_ASR_MODEL,
        "audio": {
            "format": "wav",
            "rate": 16000,
            "url": audio_url
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {QINIU_API_KEY}"
    }
    resp = requests.post(url, json=payload, headers=headers)

    try:
        data = resp.json()
        return data["data"]["result"]["text"]
    except:
        print("[ASR] 转写失败：", resp.text)
        return ""

# 入口：本地 WAV → 云端转写
def asr_transcribe(local_wav_path: str):
    print("[ASR] 上传音频到 Kodo 获取公网 URL…")
    audio_url = upload_to_kodo(local_wav_path)
    if not audio_url:
        return ""

    print("[ASR] 请求七牛 /voice/asr 进行转写…")
    text = qiniu_asr(audio_url)
    if text.strip():
        print("[ASR] 最终结果：", text)
        return text
    else:
        print("[ASR] 转写失败（无返回文本）")
        return ""
