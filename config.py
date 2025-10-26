# config.py
QINIU_API_KEY = "sk-e46475c3002845cb7bd39e89974fe152c80706212b06ef11c27cf6cc3a1fec88"
QINIU_OPENAI_BASE_URL = "https://openai.qiniu.com/v1"

QINIU_LLM_MODEL = "qwen-turbo"          # 对话/意图解析模型
QINIU_ASR_MODEL = "asr"          # 语音转文本（OpenAI 兼容接口的转写模型名，七牛会兼容或映射）
QINIU_TTS_MODEL = "tts-1"              # 文本转语音
QINIU_TTS_VOICE = "female_3"              # 音色（按七牛文档可替换）
QINIU_TTS_FORMAT = "wav"

# 地域
ALI_REGION = "cn-shanghai"

# 录音参数（16k 单声道）
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_MS = 40          # 每次发送 40ms 音频

# ==== 七牛对象存储（Kodo）用于上传录音换取公网 URL ====
# 控制台 -> 个人中心 -> 密钥管理 获取 AK/SK
QINIU_KODO_AK = "qXwXc7WP5ewKuPYFdcgWVg-cCqO6LnUhhWdyhxBQ"
QINIU_KODO_SK = "4NBokGM5IWh_IrGAssh20fOFA_GlekrAGBPzY1f3"
# 控制台 -> 对象存储 Kodo -> 创建公开读空间 -> 绑定域名
QINIU_KODO_BUCKET = "voice-upload"
QINIU_KODO_DOMAIN = "t4ljzt3ub.hd-bkt.clouddn.com"