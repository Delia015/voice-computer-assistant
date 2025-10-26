# demo_cli.py
from llm.llm_client import parse_intent
from executor.app_control import open_app
from executor.search_control import web_search
from executor.system_control import (
    volume_up, volume_down, volume_set, volume_mute, volume_unmute,screenshot, lock, sleep
)

def exec_local(intent: dict, dry_run=True) -> bool:
    t = intent.get("intent")
    slots = intent.get("slots", {}) or {}
    say = intent.get("say", "")
    print("Intent:", intent)

    def run(fn, *args):
        if dry_run:
            print(f"  ▶️ [DRY-RUN] {fn.__name__}{args}")
            return True
        return bool(fn(*args))

    if t == "open_app":
        return run(open_app, slots.get("app",""))
    if t == "open_url":
        return run(web_search, slots.get("url",""))
    if t == "search":
        return run(web_search, slots.get("query",""))
    if t == "system_control":
        act = slots.get("action",""); val = slots.get("value")
        m = {
            "volume_up": volume_up, "volume_down": volume_down,
            "volume_set": lambda: volume_set(int(val or 0)),
            "volume_mute": volume_mute, "volume_unmute": volume_unmute,
            "screenshot": screenshot, "lock": lock, "sleep": sleep
        }
        fn = m.get(act)
        return run(fn) if fn and fn.__code__.co_argcount==0 else run(fn)
    if t == "macro":
        steps = (slots or {}).get("steps") or []
        ok = True
        for i, step in enumerate(steps, 1):
            print(f"---- Step {i}/{len(steps)} ----")
            ok = exec_local(step, dry_run=dry_run) and ok
        return ok
    if t == "chat":
        print("💬 Chat:", say or "（聊天）")
        return True
    print("❓ 未知意图")
    return False

if __name__ == "__main__":
    print("Demo CLI（默认 DRY-RUN，不触发系统动作）")
    print("输入中文指令，如：开启专注模式 / 音量设置到 30")
    try:
        while True:
            q = input("> ").strip()
            if not q: continue
            if q.lower() in ("exit","quit","q"): break
            it = parse_intent(q)
            exec_local(it, dry_run=True)
            print()
    except KeyboardInterrupt:
        pass
