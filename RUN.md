# RUN — 如何在 2 分钟内运行本项目

本项目支持macOS，并基于七牛云完成 ASR / LLM / TTS 与本地自动控制
本项目在 macOS 上完整实现并测试（推荐演示环境），可在以下平台运行：

| 平台                   支持度                                   说明 
| macOS 12+      ✅ 完整支持（含系统控制） 
| Windows 10+    ⚠️ 语音识别/LLM/TTS 完全可运行      系统控制需改为 `os.startfile` 或 `nircmd` 等调用 

> 若在非 macOS 环境运行，建议关闭系统控制功能，仅测试语音识别、意图解析与语音反馈。后面有兼容性运行说明

跨平台兼容说明：
本项目已在 macOS 上完整实现与测试，并针对 Windows 做了兼容性扩展。
核心逻辑（ASR / LLM / TTS / Kodo 上传）全平台可运行，仅系统控制部分存在差异。

模块	               macOS	                 Windows
语音识别（ASR）	       ✅ 七牛 /voice/asr	 ✅ 七牛 /voice/asr	
意图解析（LLM）	       ✅ Qwen-plus	        ✅ Qwen-plus	
语音合成（TTS）	       ✅ 七牛 /voice/tts	 ✅ 七牛 /voice/tts	
应用控制（open_app）   ✅ open -a	        ⚙️ os.startfile()	
系统控制（音量/锁屏）   ✅ AppleScript	     ⚙️ PowerShell + nircmd	
截屏功能	          ✅ screencapture	   ✅ PowerShell	

✅ 表示已测试可运行 ⚙️ 表示逻辑兼容或需轻度配置

# 运行方式说明
# macOS 环境：
# （1）若想一键运行
macOS ： 终端执行 `sh run_voice_assistant.sh` 

# （2）手动运行
# 1）准备
建虚拟环境：python3 -m venv .venv
激活虚拟环境（macOS）：source + 项目路径 + /.venv/bin/activate（我的source /Users/delia/Desktop/voice_computer_assistant/.venv/bin/activate）
安装依赖：pip install -r requirements.txt

# 2）配置七牛云密钥

在项目根目录编辑 `config.py`：

QINIU_API_KEY = "个人key"
QINIU_OPENAI_BASE_URL = "https://openai.qiniu.com/v1"

QINIU_KODO_AK = "个人AK"
QINIU_KODO_SK = "个人SK"
QINIU_KODO_BUCKET = "个人空间名"
QINIU_KODO_DOMAIN = "http://个人域名"

无需改其他配置。
> 提醒：确保 Kodo 绑定为“**公开读空间**”，否则 ASR 无法访问录音 URL。

# 3）运行并开始语音交互

直接运行：python app.py

启动后界面提示：
回车开始录音 → 回车结束录音 → 自动识别、执行并语音播报

可以尝试以下语音指令：
“打开微信” 
“调大音量” 
“截图一下” 
“搜索周杰伦演唱会” 

完整交互流程：说话 → ASR 识别 → LLM 理解 → 执行动作 → TTS 播报反馈

# Windows 环境：
### Windows 额外说明（系统控制能力）
Windows 系统不提供原生命令行接口来控制音量/静音/截图等动作，本项目在 Windows 端使用 **NirCmd** 作为系统控制执行器，已从官网下载并放置 `nircmd.exe`（用于音量/静音/截图）到根目录下。

# 具体做法：
已完成：
1. 从官网获取 `nircmd.exe`（NirSoft 发布，安全可靠）
2. 将 `nircmd.exe` 放到项目根目录（与 `app.py` 同级）
3. 即可支持：音量调整（支持百分比），静音 / 取消静音，截屏，锁屏
> 若不放置 `nircmd.exe`，Windows 版本仍可运行 ASR + LLM + TTS 与“打开应用/搜索”等能力，但系统级控制（音量/静音/截图等）将不可用。

请在 VS Code终端（建议）中 或者 PowerShell / CMD 中运行以下命令：
1. 创建 & 激活虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1

如遇 “执行策略” 报错（Win 常见），先执行：
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

然后再执行激活命令。
终端出现前缀：
(.venv) C:\xxx\voice_assistant>
虚拟环境成功

2. 安装依赖
pip install -r requirements.txt
（或临时替换镜像以加速
$env:PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
pip install -r requirements.txt --default-timeout=120）

3. 运行程序
python app.py

终端显示：
就绪：按回车开始录音…
说明成功运行 

接着可以：
回车 → 讲话 → 回车
请说：“休眠“ / “音量设置到 30” / “静音” / “打开浏览器” / “搜索周杰伦演唱会”

若出现提示 “nircmd.exe 未找到”，可前往：
https://www.nirsoft.net/utils/nircmd.html 下载后放入项目目录或系统 PATH 中（用于音量等控制）。

4.如果运行报错？

现象                      解决方式 
ASR 报错         检查 Kodo URL 是否可公网访问 
TTS 报错         检查 `voice_id` 是否正确 
App 打不开       将应用名加到 `executor/app_control.py` 映射表 
 
# 若您电脑无法运行 NirCmd，请使用此模式。
python demo_cli.py

该模式将：
完整运行 ASR / LLM / 宏编排能力

不触发系统动作
所有动作以 Step-by-step 的形式打印出来可用来展示智能组合能力，例如：

输入：开启专注模式

输出：
Step 1: volume_set 15
Step 2: open_app 备忘录
Step 3: search Lo-fi beats playlist
✅ Macro completed
这样即使系统指令无法执行，也能清晰展示本项目的 “复杂任务编排 + 智能语音助手能力”。
