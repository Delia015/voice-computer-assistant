# llm/llm_client.py
import json
import re
from openai import OpenAI
from config import QINIU_API_KEY, QINIU_OPENAI_BASE_URL, QINIU_LLM_MODEL

client = OpenAI(api_key=QINIU_API_KEY, base_url=QINIU_OPENAI_BASE_URL)

SYSTEM_PROMPT = """你是本地电脑语音助手，只输出严格 JSON，不要解释。
支持意图:
- open_app(app) 例: 打开微信/Chrome/备忘录
- system_control(action[, value]) action ∈ {volume_up, volume_down, volume_set, volume_mute, volume_unmute, screenshot, lock, sleep}
- open_url(url) 例: 打开 bilibili.com
- search(query) 例: 搜索周杰伦演唱会
- chat(say) 例: 纯聊天或无法执行时回复
- macro：复合场景指令，例如：
   - “开启专注模式” → {"intent":"macro","slots":{"name":"专注模式"},"say":"我已为你开启专注模式"}
   - “准备演示” → {"intent":"macro","slots":{"name":"演示模式"},"say":"我已帮你开启演示模式"}

   宏示例1：专注模式
# 需求：调低音量→提高亮度→打开备忘录→搜索 Lo-fi 音乐
{"intent":"macro","slots":{"name":"专注模式","steps":[
  {"intent":"system_control","slots":{"action":"volume_set","value":15}},
  {"intent":"open_app","slots":{"app":"备忘录"}},
  {"intent":"search","slots":{"query":"Lo-fi beats playlist"}}
]},"say":"已为你开启专注模式"}

# 宏示例2：演示模式
{"intent":"macro","slots":{"name":"演示模式","steps":[
  {"intent":"system_control","slots":{"action":"volume_mute"}},
  {"intent":"open_app","slots":{"app":"safari"}},
  {"intent":"open_url","slots":{"url":"https://slides.example.com/demo"}}
]},"say":"演示模式已就绪"}

输出 JSON 示例：
{"intent":"open_app","slots":{"app":"微信"},"say":"好的，我马上为你打开微信"}
或：
{"intent":"system_control","slots":{"action":"volume_set","value":30},"say":"音量已设置为 30%"}
"""

def _safe_json(s: str) -> dict | None:
    if not s:
        return None
    # 1) 提取第一个 {...} 块（模型有时会带解释或包裹在 ```json 中）
    m = re.search(r"\{.*\}", s, flags=re.S)
    if m:
        s = m.group(0)

    # 2) 常见清洗
    s = s.strip().strip("```").strip()
    # 替换全角符号
    s = s.replace("，", ",").replace("：", ":").replace("“", "\"").replace("”", "\"").replace("’", "\"").replace("‘", "\"")
    try:
        return json.loads(s)
    except:
        # 3) 单引号→双引号 的兜底
        s2 = re.sub(r"(?<!\\)'", '"', s)
        try:
            return json.loads(s2)
        except:
            return None

# 规则兜底：避免 LLM 偶发不稳
def _rule_intent(text: str) -> dict | None:
    t = text.strip().lower()

    # 打开应用
    m = re.search(r"打开\s*(微信|weixin|wechat|safari|chrome|finder|备忘录|music|音乐|信息|messages)", text, re.I)
    if m:
        app = m.group(1)
        mapping = {
            "weixin":"微信","wechat":"微信","safari":"Safari","chrome":"Chrome",
            "finder":"Finder","备忘录":"备忘录","music":"音乐","信息":"信息","messages":"信息"
        }
        app = mapping.get(app.lower(), app)
        return {"intent":"open_app","slots":{"app":app},"say":f"我已经帮你打开{app}了"}

    # 截屏
    if re.search(r"(截屏|截图)", text):
        return {"intent":"system_control","slots":{"action":"screenshot"},"say":"已截屏"}

    # 音量 +/-
    if re.search(r"(音量).*?(提高|调高|加|大|升|大声)", text):
        return {"intent":"system_control","slots":{"action":"volume_up"},"say":"音量已调大"}
    if re.search(r"(音量).*?(降低|调低|减|小|降|小声)", text):
        return {"intent":"system_control","slots":{"action":"volume_down"},"say":"音量已调小"}

    # 百分比设置
    m = re.search(r"(音量).{0,3}(到|为|设置为)\s*(\d{1,3})", text)
    if m:
        kind, _, val = m.groups()
        val = max(0, min(100, int(val)))
        if "音量" in kind:
            return {"intent":"system_control","slots":{"action":"volume_set","value":val},"say":f"音量已设置为 {val}%"}

    # 静音/取消静音
    if re.search(r"(静音|mute)", text, re.I):
        return {"intent":"system_control","slots":{"action":"volume_mute"},"say":"已静音"}
    if re.search(r"(取消静音|unmute)", text, re.I):
        return {"intent":"system_control","slots":{"action":"volume_unmute"},"say":"已取消静音"}

    # 锁屏/睡眠/Users/delia/Desktop/voice_computer_assistant
    if re.search(r"(锁屏|锁定屏幕|lock screen)", text, re.I):
        return {"intent":"system_control","slots":{"action":"lock"},"say":"已锁定屏幕"}
    if re.search(r"(睡眠|休眠|sleep)", text, re.I):
        return {"intent":"system_control","slots":{"action":"sleep"},"say":"即将休眠"}

    # 打开网址
    m = re.search(r"(打开|访问)\s*(https?://[^\s]+|[a-z0-9\.\-]+\.[a-z]{2,})", text, re.I)
    if m:
        return {"intent":"open_url","slots":{"url":m.group(2) if m.lastindex==2 else m.group(1)},"say":"我来帮你打开网页"}

    # 搜索
    if re.search(r"(搜索|查一下|搜一下|百度一下|谷歌一下)", text):
        q = re.sub(r"^(搜索|查一下|搜一下|百度一下|谷歌一下)\s*", "", text)
        return {"intent":"search","slots":{"query":q or text},"say":"好的，我来搜一下"}

    return None

def parse_intent(text: str) -> dict:
    # 先问大模型
    try:
        resp = client.chat.completions.create(
            model=QINIU_LLM_MODEL,
            messages=[{"role":"system","content":SYSTEM_PROMPT},
                      {"role":"user","content":text}],
            temperature=0.2
        )
        js = _safe_json(resp.choices[0].message.content)
        if isinstance(js, dict) and "intent" in js:
            return js
    except Exception:
        pass
    # LLM 失败 → 规则兜底
    js = _rule_intent(text)
    if js: return js
    
    return {"intent":"chat","say":"好的，我知道啦"}
