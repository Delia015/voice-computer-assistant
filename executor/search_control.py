# executor/search_control.py
import subprocess
import urllib.parse

def web_search(q:str)->bool:
    if not q: return False
    # 如果像 URL，就直接打开；否则走搜索
    if q.startswith("http://") or q.startswith("https://") or ("." in q and " " not in q):
        url = q if q.startswith("http") else f"https://{q}"
    else:
        url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
    try:
        subprocess.run(["open", url], check=True)
        return True
    except: return False
