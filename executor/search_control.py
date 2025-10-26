# executor/search_control.py
import webbrowser
import urllib.parse

def web_search(q: str):
    if not q: return
    url = f"https://www.baidu.com/s?wd={urllib.parse.quote(q)}"
    webbrowser.open(url)
