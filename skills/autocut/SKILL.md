---
name: autocut
description: Guide users through Autocut short-video editing in CapCut or ChatCut, from first use to an editable rough cut or finished project. Use for setup, walkthroughs, talking-head videos, factory promos, multilingual captions, and revisions. In an active Autocut chat, 开始、怎么做、我想开始剪辑 resume the workflow.
license: See LICENSE.md for trial-use terms; commercial rights reserved.
metadata:
  version: "0.3.0"
---

# Autocut

把用户的素材和简短要求做成流畅、可检查的短视频工程。适合口播、广告、工厂宣传与人物＋电脑演示。当前任务要求优先于默认值。

每次新任务先通读[《Autocut 章程》](references/charter.md)，再回复或开工。续做、返修和交付前重看所处环节的条款。章程管理通用工作规则，客户及系列喜好独立保存。

## 用户一句话就能开始

在已选择、已明确调用 Autocut 或已开始 Autocut 工作的对话里，「开始」「怎么做」「我想开始剪辑」都从当前步骤接着走。普通对话里只有「开始」且上下文无法确定剪辑意图时，不接管其他任务。第一次使用可提供「使用 $autocut 开始」。

第一次开工、继续到下一步或用户卡住时，读[主动引导与模拟](references/onboarding.md)。没有素材时，告诉用户可以拖入文件、发位置或指定现有工程，也可以回复「模拟」。新手可随时打开[七步流程图](assets/guide/flow.png)或[图文指南](assets/guide/quickstart.pdf)。

新项目首次收到可识别的素材及位置（含截图、附件或当前工程），下一条先给预填的[剪辑前确认卡](references/quick-intake.md)，包括「其他要求」（默认无），以及编辑器、模型提供方、确切型号和推理强度。卡片先于方案和时间线。只让用户补真正缺少的项。真实开工前核实选定编辑器已打开且可访问、实际用的模型和可用档位，受限时按[开工核对规则](references/backends.md#开工前核对)处理。卡已确认或用户给足要求并说开剪，条件具备就直接执行。续做与返修沿用原卡，权限按所选工具和实际操作处理。

开工前读取匹配当前用户或系列的[喜好库](assets/brand-profile.example.md)或编辑器偏好；首次使用时在可用且可写的私有位置建档，受限时沿用当前会话记录。Codex 可检查当前项目的 `brand-profile.local.md` 和 Codex 配置目录下 `autocut/brand-profile.local.md`（默认 `~/.codex`）。本轮要求优先，其次是已确认的相关偏好，再用默认值。交付后记录明确反馈，按章程在两三次制作后归纳喜好。共享包只含通用示例。

## 按需调用能力

- 先读[工具与依赖](references/backends.md)中本次工具对应部分；使用可用的官方工具与任务技能，不虚构API或重新安装一套依赖。
- 口播/广告/工厂组片：读[剪辑与声音标准](references/editing-standards.md)。
- 字幕、翻译或配音：读[多语言标准](references/localization.md)；已有文字稿优先复用。
- 用户给了参考成片、希望提炼风格：按需读[参考分析](references/reference-analysis.md)。不要把每次普通剪辑扩展成参考片研究。
- 用户反馈、手动改动或要求看进度：读[进度与纠偏](references/live-feedback.md)。
- 收尾、耗时或失败恢复：读[效率与交付](references/delivery-and-efficiency.md)。

## 制作顺序

素材与需求 → 识别/选段 → 粗剪时间线 → 所需字幕/包装 → 核心检查 → 待用户审核。

- **人物口播**：按章程在确认卡说明「粗剪白版」「粗剪完整版」「直出（最终完整版）」三档；已选定档位时直接带入。用户指定的增减项可以覆盖该档默认包装，保留原档位与交付约定。
- **其他类型**：按确认卡明确切剪、字幕、画面与声音包装范围，交付按约定执行。
- 本轮明确要求“只能用收藏”才限制收藏；否则可合理选择符合用途的字体、音乐与效果。不要把旧任务的收藏限制套到所有用户。
- 口播保留完整意思和自然情绪；删除无意义的“呃”、失败起句和被后面流畅表达替代的内容。不能只靠静音检测、ASR文字或波形自动判断。
- 双语默认中文在上、目标语言在下，留出画面安全边距；根据需求卡或品牌规范选择长句拆屏或换行，按真实字体检查越界。SRT检查不能替代排版检查。
- 不能确定的产品事实、姓名、价格、数量和单位不猜。单独标出该处并继续可独立完成的部分。

## 用户随时能看、随时能改

保持真实编辑器或可打开的工程入口可见。无法显示实际画面时说明能显示的是阶段状态；不能把示意进度面板称为实时编辑器。

默认快速执行，不在每阶段停下来等批准；用户指定“先看结构再包装”时在该点等待。耗时包装前尽早在工程中呈现开头、主要切点及一处字幕样式，不为看预览强制导出整片。

修改以最新指令为准，只重做受影响部分；收到反馈不等于已应用。用户手动修改优先，写入前读取最新工程。明确说停下时停止发起新变更，不能取消的后台任务如实说明。

## 完成条件

只核对本次必要项：表达与接点、时长/画幅、字幕长句与事实、人声/BGM/音效、请求的包装、工程可打开。标记完成、跳过或未完成，不能遗漏后报成功。通常规划粗剪20–30分钟、完整版30–40分钟，包含等待；这是常规短片目标，不是性能保证。

默认维护**一个可编辑主工程**。直出默认包含已复核的成片，其他档默认交工程；本轮交付约定优先。核实用户确实能在约定位置打开交付物。原片和工程依赖保留，旧版本仅在授权且确认不被引用时清理。说明做了什么、在哪里检查、还有什么待确认；音效或配乐交付后按章程收集反馈。保存后状态为“待你审核”。

## 本地辅助脚本（可选）

使用Python 3.9+，均不调用云服务。已导入的工程不必为流程完整而再次扫描。

- `python3 scripts/prepare_job.py doctor`：只检查FFmpeg/ffprobe是否可用。
- `python3 scripts/prepare_job.py prepare ./media --output ./job`：只读登记素材，复用尺寸/修改时间缓存；首次哈希需要读取文件，不适合无必要的反复扫描。
- `python3 scripts/analyze_reference.py ./reference.mp4 --output ./job/measurements.json`：需要现有FFmpeg；低分辨率扫描切点候选和混音静区，不生成视频、不决定切段。
- `python3 scripts/check_srt.py ./captions.srt --duration 60`：检查UTF-8、时码、重叠及阅读速度；不判断翻译或画面越界。

这是可分享的试用版流程技能，不是捆绑剪辑软件、模型额度或所有子技能的独立程序。能力与效果以当前工具及素材为准。
