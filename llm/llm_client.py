# llm/llm_client.py
from openai import OpenAI
from http import HTTPStatus
from config import QINIU_API_KEY, QINIU_OPENAI_BASE_URL, QINIU_LLM_MODEL

client = OpenAI(api_key=QINIU_API_KEY, base_url=QINIU_OPENAI_BASE_URL)

SYSTEM_PROMPT = """
你是桌面语音助手的意图解析器。请将用户中文语句结构化成：
{"intent":"<open_app|system_control|search|chat>","slots":{...},"say":"给用户的简短口头回复"}

- open_app: slots={"app":"应用名"}，如"音乐|QQ音乐|微信|VS Code|浏览器|Notion"
- system_control: slots={"action":"volume_up|volume_down|screenshot|brightness_up|brightness_down"}
- search: slots={"query":"搜索关键词"}
- chat: 普通对话，进行自然回答（say 即可）
不要输出多余文字。
""".strip()

def parse_intent(text: str) -> dict:
    try:
        resp = client.chat.completions.create(
            model=QINIU_LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content.strip()
        # 粗暴“去围栏”，确保是纯 JSON
        for junk in ["```json", "```", "“", "”", "\n"]:
            content = content.replace(junk, "")
        import json
        data = json.loads(content)
        if "say" not in data:
            data["say"] = "好的"
        return data
    except Exception as e:
        return {"intent": "chat", "slots": {}, "say": f"我解析失败了：{e}"}
