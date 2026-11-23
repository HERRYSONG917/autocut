# Autocut

**v0.3.0 · 2026-11-23**

把素材、要求和修改意见交给 AI，由 Autocut 组织选段、剪辑、字幕、声音与交付。适合口播、商业 IP、产品广告、工厂宣传、人物＋电脑和活动探访。

选择 Autocut 后说 **「开始」**。它会主动带你交素材、选择剪辑方式、检查工程和反馈修改。

> 这是流程技能，不是剪辑软件或独立自动剪辑程序。它不附赠账号、模型额度、音乐版权或所有第三方子技能。需要可用的Codex及实际连接的CapCut/ChatCut；具体功能取决于当前版本和账号。现阶段为试用版，不能承诺无人审核即可商用交付。

## 快速开始

1. 把完整安装 ZIP 交给 Codex，说「请安装 Autocut」。已有同名技能时先核对版本。安装后选择 Autocut，或在新对话说「使用 $autocut 开始」。
2. 在 Autocut 对话说「开始」「怎么做」或「我想开始剪辑」，按提示拖入原片、发位置或 Finder 截图，或指定已打开的工程。暂无素材时回复「模拟」。
3. 收到素材和位置，Autocut 会先给你一张预填的剪辑前确认卡，含「其他要求」。有改动就说一句，确认可以直接回「按卡开始」。
4. 开工前核对 [ChatCut](https://chatcut.io/docs/desktop-app) 或 [CapCut](https://www.capcut.com/tools/capcut-x-codex) 已打开且可用，同时核对实际执行模型及推理强度。编辑器和需求均就绪后直接剪。完成后打开同一个可编辑工程，想修改就指出时间点或台词。

技能通常在安装后的下一轮可用；若列表未更新，再按宿主提示刷新或重启。Codex本机Skill与ChatCut“我的技能”不是同一个位置，本包不会自动注册到ChatCut原生技能菜单。

图文说明见[七步流程图](skills/autocut/assets/guide/flow.png)、[三页新手 PDF](skills/autocut/assets/guide/quickstart.pdf)、[文字版入门](docs/QUICKSTART.md)与[安装说明](skills/autocut/INSTALL.md)。

## 已整理的制作标准

| 项目 | 默认规则 |
| --- | --- |
| 开工确认 | 素材一到就出预填卡，30–60 秒，只补缺项。开工前核对编辑器、模型及推理强度 |
| 人物口播 | 粗剪白版只剪顺口播；粗剪完整版按确认加轻量包装；直出（最终完整版）通常交成片和可编辑工程。指定的增减项按当次处理 |
| Autocut 章程与喜好库 | 新任务先读章程，返修与交付前复查对应条款。个人喜好单独保存，剪过两三次后从明确反馈归纳 |
| 声音与动效 | 开场强调在实际混音里可辨，黄字重点用同步轻提示。配乐按谈话气氛选择，动效给人物与字幕留空间 |
| 口播 | 不只删静音；失败起句和重复补词需按真实声音重组，保护句意和词尾 |
| 多语言 | 原声、字幕和配音分别确认。双语按当次或系列要求排版，关键存疑处留时码供复核 |
| 素材选择 | 本轮说“只用收藏”才限制收藏；否则可选择符合用途的素材 |
| 及时纠偏 | 随时用时间点＋一句话；基于最新工程定点改，保留人工调整 |
| 可视进度 | 显示真实阶段与工程入口；不伪装直播、完成百分比或token账单 |
| 效率 | 普通短片粗剪20–30分钟、完整版30–40分钟作为计划目标，含等待，非性能保证 |
| 交付 | 一个可编辑主工程。直出默认附成片，用户也可以选择自己导出。发布需用户明确要求 |

档位、包装及验收规则见[《Autocut 章程》](skills/autocut/references/charter.md)。

只需局部修订可直接说：

> 00:23附近英文分两行，其他不变。我刚手动改过工程，请读取最新版本后再改。

> 先停一下，不要继续写工程。我整理好意见后再继续。

## 文件结构

```text
README.md / LICENSE.md / CHANGELOG.md
docs/                         新手图文手册、GitHub上传与验证说明
skills/autocut/
  SKILL.md                    AI读取的主入口
  INSTALL.md / LICENSE.md      安装与试用授权
  agents/openai.yaml          Codex显示信息
  references/                 分场景规则，按需读取
  assets/guide/               七步流程图与新手图文手册
  assets/                     需求与品牌配置示例
  scripts/                    可选本地辅助，不是完整剪辑引擎
```

分享给朋友时发 `autocut-v0.3.0.zip`。里面有完整技能文件夹、流程图和图文手册。仓库发布后，也可以直接发 Releases 中对应版本的下载页。

上传GitHub：上传本仓库**解压后的源码内容**，保持`skills/autocut/SKILL.md`路径；在Release附安装ZIP。见[GitHub上传指南](docs/GITHUB_UPLOAD.md)。

## 依赖和费用

主流程依赖当前宿主可用的编辑器工具；官方技能和服务由各使用者独立连接，不在包里复制分发。只有本地辅助脚本需要Python 3.9+；参考扫描需要FFmpeg，完整素材元数据需要ffprobe。没有需要时不运行脚本或安装这些依赖。

Codex推理与ChatCut托管生成等是不同用量来源，不能认为登录ChatGPT就全免费。新增收费动作应先明确费用/范围，已授权的相同范围不反复确认。软件版本、支持格式和用量规则见官方说明：[Codex技能](https://learn.chatgpt.com/docs/build-skills)、[ChatCut桌面](https://chatcut.io/docs/desktop-app)、[ChatCut积分](https://chatcut.io/docs/credits-policy)。

## 试用与商业权利

本项目**保留商业权利，允许试用；不是MIT开源项目**。生产部署、付费转售、分发修改版或其他商业授权需与发布者另行约定，详见[LICENSE.md](LICENSE.md)。

包中没有作者私人原片、账号、密钥、客户名单、私人路径、收藏资产或语音模型。你自己的品牌偏好可在本地使用[品牌配置模板](skills/autocut/assets/brand-profile.example.md)维护；不要提交私人配置和客户工程。

能力验证范围见[VALIDATION.md](docs/VALIDATION.md)。每个用户仍需用自己的小样片检查工具连接与实际效果。
