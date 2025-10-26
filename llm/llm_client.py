from openai import OpenAI
from config import QINIU_API_KEY, QINIU_OPENAI_BASE_URL, QINIU_LLM_MODEL

client = OpenAI(api_key=QINIU_API_KEY, base_url=QINIU_OPENAI_BASE_URL)

SYSTEM_PROMPT = """你是一个本地电脑语音助手，只输出 JSON，不要解释。
支持意图：
1) open_app(app) —— 打开应用，例如：微信、Finder、Safari
2) system_control(action) —— volume_up / volume_down / brightness_up / brightness_down / screenshot
3) search(query) —— 触发浏览器搜索查询内容
4) chat —— 其他内容直接作为聊天回复

输出 JSON 示例：
{"intent": "open_app", "slots": {"app":"微信"}, "say":"我已经帮你打开微信了"}
"""

def parse_intent(text: str) -> dict:
    try:
        resp = client.chat.completions.create(
            model=QINIU_LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        return eval(resp.choices[0].message.content)
    except:
        return {"intent": "chat", "say": "好的，我知道啦"}
