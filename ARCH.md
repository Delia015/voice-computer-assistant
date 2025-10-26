# ARCH — 系统架构与扩展说明

本项目是一个基于 **「离线录音 + 七牛云 ASR + 七牛云 TTS + LLM 意图解析 + Mac 系统控制」** 的语音助手，实现了从语音输入到系统动作的完整闭环。

系统具备 **清晰模块边界、可替换的云厂商能力、可水平扩展的指令体系**，便于后续升级。


## 1. 核心流程架构图

 Microphone ────▶Recorder ────▶ASR    (七牛 /voice/asr)
                                │ text
                                ▼
                               LLM      (七牛 openai 对齐接口)
                                
                                │ intent(json)
                                ▼       
                        Command Executor 
                        (App / System / Web)
                                │
                                ▼
                        TTS Speech Player   (七牛 /voice/tts)


## 2. 模块职责划分

模块           文件                作用 
录音模块   `recorder.py`      采集本地麦克风音频（wav） 
ASR 模块  `asr_client.py`    上传到 Kodo → 调用七牛 ASR → 返回文本 
LLM 解析  `llm_client.py`    将句子转为意图与指令（结构化 JSON） 
指令执行器 `executor/`        控制系统音量、亮度、应用启动、搜索 
TTS 模块  `tts_client.py`    文本 → 语音 → 本地播放 
UI 层     `gui.py / app.py`  控制录音生命周期、日志输出、流程调度 

##  3. 意图解析设计

{
  "intent": "open_app",
  "slots": { "app": "微信" },
  "say": "我已经帮你打开微信了"
}

当前已支持：

意图                     示例 
`open_app`           打开微信 
`system_control`     调大音量 / 调亮一点 / 截屏 
`search`             搜索周杰伦演唱会 
`chat`               你是谁 

扩展方式（例如想加“播放音乐”）：
只需新增 `intent = play_music` → 在 `executor` 新增执行函数  
不用修改 ASR / TTS / UI → 可线性演进

##  4. Mac 控制层能力（OSA / shell + 解耦执行器）

支持控制能力来源：
能力                技术实现
打开应用        `open -a <AppName>` 
截屏           `screencapture` 
调整音量        `osascript` AppleScript 
系统 TTS 播放   七牛声音生成 + 本地播放器 

后续可继续增强：
可选能力               实现方式 
读微信消息        AppleScript + Accessibility 
打开文件         `open ~/xxx.pdf` |
自动执行快捷指令   Shortcuts (`shortcuts run`) 

## 5. MVP → 完整体进阶路线

阶段  能力 
当前：语音指令 → 控制 Mac + 语音播报 |
下一步：语音对话 + 多轮意图记忆 |
再之后：语音流式识别 / 流式 TTS（更拟人） |
终极：本地唤醒词（Hey 小牛）+ 无按钮全自动 |

此结构可以直接演进到 **“类 Siri 桌面语音助手”**。

## 6. 结语

该系统架构具备：
- 清晰分层
- 模块职责单一
- 云服务可热插拔
- 指令可扩展
- 可作为真正产品继续迭代

这不仅是一个 Demo，而是一个可以演变成真正语音助手的底座。
