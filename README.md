# 一、项目简介
本项目为七牛校招提交作品，已完成 ASR + LLM + TTS + Macro + 跨平台兼容能力演示。

本项目实现了一个语音控制电脑操作的 MVP：
用户可通过一句话完成如“打开微信 / 跳高亮度 / 截屏 / 搜索周杰伦演唱会”等操作。
系统完成：ASR → LLM → 执行动作 → TTS 的端到端自动化。

环境
| **macOS 12+（推荐）**    支持ASR / LLM / TTS / 打开应用 / 搜索 / 音量 / 亮度 / 截屏 / 宏（专注/演示）
| **Windows 10+**         ASR / LLM / TTS / 打开应用 / 搜索 / 音量/静音/截屏（**已内置 nircmd.exe**） / 宏 
| **Windows Demo（最次）** 不执行系统动作，仅打印宏步骤 + TTS（无需 nircmd）

# 二、运行环境（推荐）mac/win详情如需运行步骤与快速检查清单，请看 `RUN.md`
macOS 12+
Python 3.11+
网络可访问七牛 API
麦克风可用

本项目实现目标：
语音说话 → 自动识别 → 理解意图 → 执行动作 → 口播反馈
七牛云 ASR + LLM + TTS 完整链路打通
本地支持：打开应用、系统音量/亮度控制、屏幕截图、网页搜索

# 三、安装依赖与环境搭建
# (1) 重新建虚拟环境
python3 -m venv .venv
# (2) 激活虚拟环境（macOS）
source.venv/bin/activate
# (3) 安装依赖
pip install -r requirements.txt

# 四、运行项目
python app.py

控制台输出示例：
就绪：按回车开始录音；再次回车停止；Ctrl+C 退出。

# 五、语音命令示例
类型	示例
打开类	打开微信
系统类	调大音量 / 截屏一下
搜索类	搜索周杰伦演唱会
复杂/宏    打开专注模式 / 演示模式 （下面有详细说明）

Demo 示例：

语音输入	系统行为
“打开微信”	自动启动 WeChat，并 TTS 播报“好的，已为你打开微信”
“调大音量”	调整系统音量，并 TTS 播报“音量已调大”
“截图一下”	自动截屏保存，并 TTS 播报
“搜索周杰伦演唱会”	自动打开浏览器并搜索

# 六、宏能力（Macro Orchestration）

在原子动作（open_app / system_control / search / open_url）基础上，引入宏（macro）：
当用户通过一句自然语言提出复杂场景需求时，LLM 产出一个多步骤的可执行 JSON，执行器顺序落地；遇到个别失败不中断、容错继续，并在末尾播报结果。

宏示例 1：专注模式
完成的内容（按顺序）：
1. 把系统音量设置为 15%：尽量减少环境干扰；
2. 打开“备忘录”：进入可记录状态；
3. 搜索 Lo-fi 背景音乐：在浏览器中打开可播放/搜索页面，营造专注氛围。

触发方式（口令示例）：
“开启专注模式” / “我要专心工作，帮我进入专注模式”。

异常与容错：
某步失败（例如：找不到“备忘录”）→ 不中断，继续后续步骤；
终端打印每步日志：[EXEC] Step i/n -> True/False | {...}，便于评审与定位问题。

可配置项：
记事应用（可改为 Notion/Obsidian 等）；
音乐关键词（Lo-fi/White Noise/Rainy Jazz…）。

设计动机：
把“环境控制 + 工具就绪 + 背景资源”打包为一次口令，降摩擦、快进入心流。

宏示例 2：演示模式

完成的内容（按顺序）：
1. 静音：避免会议/舞台被系统音打断；
2. 打开 Safari（可换 Chrome/Edge）；
3. 直达演示页面：通过 open_url（内部复用 web_search 的 URL 分流）。

触发方式（口令示例）：
“开启演示模式。”

异常与容错：
浏览器名不匹配或未安装 → 后续仍会尝试打开 URL（用默认浏览器）；
链接失败 → 前 2 步已完成，能迅速手动补救。

设计动机：
将“演示前准备动作”变为一次口令，减少现场手忙脚乱与出错。

# 七、系统架构与时序
主流程：
flowchart LR
A[用户语音] --> B[🎧 Recorder 录音 WAV]
B --> C[七牛 ASR /voice/asr]
C --> D[七牛 LLM /chat/completions<br/>意图: open_app/system/search/macro...]
D --> E[本地执行器 Executor]
E --> F[七牛 TTS /voice/tts]
F --> G[本地播放]

单次指令“打开微信”的时序：
sequenceDiagram
    User->>Recorder: 按回车讲话
    Recorder->>Qiniu ASR: 上传音频
    Qiniu ASR-->>App: 文本“打开微信”
    App->>Qiniu LLM: 意图解析
    Qiniu LLM-->>App: {intent: open_app, app: 微信}
    App->>macOS: open -a "WeChat"
    App->>Qiniu TTS: “我已为你打开微信”
    Qiniu TTS-->>App: 返回 WAV
    App->>Speaker: 播放语音

# 八、配置说明
在 config.py 中填写个人七牛云密钥：
QINIU_API_KEY = "个人key"
QINIU_OPENAI_BASE_URL = "https://openai.qiniu.com/v1"

QINIU_KODO_AK = "个人AK"
QINIU_KODO_SK = "个人SK"
QINIU_KODO_BUCKET = "个人空间名"
QINIU_KODO_DOMAIN = "http://个人域名"

# 九、目录结构
voice_computer_assistant/
├── app.py                 # 主流程控制（含宏编排执行）
├── config.py              # Key & 模型配置
├── asr/                   # 七牛 ASR
├── tts/                   # 七牛 TTS
├── llm/                   # 七牛 LLM（仅输出严格 JSON）
├── executor/              # 本地执行器（音量/App/搜索/截屏/休眠/锁屏）
├── utils/                 # 播放器、录音工具
├── README.md
├── nircmd.exe             # Windows 系统控制工具（已内置）
├── RUN.md                 # Windows 运行指南              
├── run_voice_assistant.sh # mac一键运行
├── ARCH.md                # ARCH — 系统架构与扩展说明
├── requirements.txt       # 依赖说明文件，可通过 pip install -r requirements.txt 安装所有库
├── demo_cli.py            # （兜底模式）模拟语音指令的执行逻辑，不依赖麦克风与系统控制
├── gui.py                 # 控制台交互界面（Console GUI），负责录音控制循环，不依赖图形界面
└── .gitignore             # Git 忽略配置文件，防止上传虚拟环境与缓存文件


# 十、快速上手
1️⃣ unzip 项目包
2️⃣ 填好 config.py 里的 Key
3️⃣ python3 -m venv .venv && source .venv/bin/activate
4️⃣ pip install -r requirements.txt
5️⃣ python app.py
6️⃣ 按回车说一句“打开微信”

# 十一、故障排查
1. Win 安装依赖慢/超时：临时使用镜像
setx PIP_INDEX_URL https://pypi.tuna.tsinghua.edu.cn/simple（重开终端生效）
2. Win 系统控制无效：确认项目根目录存在 nircmd.exe；企业电脑受策略限制时可使用 demo_cli.py 最次演示。
3. 命令行显示已成功但系统无变化：确认默认输出设备/截图权限；或使用 demo_cli.py 兜底模式验证宏能力。
4. 依赖安装超时：使用镜像并增加超时：pip install -r requirements.txt --default-timeout=180
5. 无麦克风：Windows 设置 → 隐私与安全 → 麦克风 → 允许桌面应用访问。
