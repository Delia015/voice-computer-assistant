# executor/search_control.py
import re
import urllib.parse
import webbrowser

_URL_RE = re.compile(r"^(https?://|www\.|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}).*")

def web_search(q: str) -> bool:
    if not q:
        return False
    text = q.strip()

    # 是 URL 就直开；不是就搜索
    if _URL_RE.match(text):
        if not text.startswith(("http://", "https://")):
            text = "https://" + text
        try:
            webbrowser.open(text)
            return True
        except Exception:
            return False
    else:
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(text)}"
            webbrowser.open(url)
            return True
        except Exception:
            return False
