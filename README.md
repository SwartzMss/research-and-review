# Research & Review

A research-first Codex Skill for collecting, assessing, and reviewing information **before** writing a script or editing a video.

> 当前重点：热点事件、多来源资料和视频线索的研究、评估与人工审核。**本仓库暂不制作成片。**

## 能做什么

- 根据选题，用 Agent 可用的搜索工具搜集新闻、官方材料、B站/抖音/YouTube 等视频链接。
- 保留每条信息的原始 URL、发布日期、摘要、可信度依据、关键主张与待核实问题。
- 将搜索结果保存为结构化 JSON，生成可在本地浏览器打开的审核台。
- 人工将资料标记为 **仅供研究 / 候选画面 / 排除 / 待定**，并附上备注。
- 从审核结果导出资料包，交给后续文案或分镜 Skill 使用。

本版 **没有**实现任意平台自动搜索或视频下载、转写、OCR、视觉理解、全自动事实核查；这些是后续迭代。Agent 的网页搜索结果也必须明确来源和核验状态。

## 快速开始（Python 3.10+，无第三方依赖）

```bash
git clone https://github.com/SwartzMss/research-and-review.git
cd research-and-review

# 用示例数据生成审核页
python scripts/build_review.py examples/sources.json --output output/review.html
```

在浏览器打开 `output/review.html`，按来源选择决策和填写备注，点击 **导出 selection.json**。将下载的文件放到 `output/selection.json`，然后运行：

```bash
python scripts/apply_selection.py examples/sources.json output/selection.json --output output/selected.json

# 测试
python -m unittest discover -s tests -v
```

生成的 `selected.json` 只包含人工明确选为「仅供研究」或「候选画面」的记录。审核页不会自动向 GitHub 或外部服务器发送选择结果。

### 安装到 Codex

仓库根目录就是 Skill 目录（包含 `SKILL.md`）。在本地安装到 Codex 用户级 Skills 目录：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/SwartzMss/research-and-review.git ~/.agents/skills/research-and-review
```

如果你已经克隆了仓库，可将仓库作为 `~/.agents/skills/research-and-review` 使用。更新时在该目录执行 `git pull`。Windows PowerShell 对应用户目录为 `$HOME\.agents\skills\research-and-review`。重新启动或刷新 Codex 的 Skill 列表后，检查是否能发现 `research-and-review`。

### 让 Codex 按 Skill 工作

在 Codex 能读取本仓库的环境中，指示它遵循 [SKILL.md](SKILL.md)：

> 研究「塞尔维亚学生运动」，先搜集 10–20 个具有来源的新闻与视频候选，按照 schemas/sources.schema.json 生成项目 sources.json，标明未核实的信息；执行 build_review.py，交给我筛选。未得到选择结果，不要继续写解说文案或制作视频。

**研究与运行产物应放在仓库外的项目目录**，或者放在被 gitignore 忽略的 `output/` 下。仓库本身只保留 Skill、工具和示例。

## 工作流

```text
用户选题
  → Agent 搜索、去重、摘取关键事实/观点
  → 标注原始来源、核验状态、使用授权
  → sources.json
  → build_review.py
  → 浏览器查看资料、缩略图/本地预览、时间码
  → 人工决策 + 备注 → selection.json
  → apply_selection.py → selected.json
  → （未来）Video Director / Video Production
```

### 最重要的原则

1. 不把“视频作者声称”直接当成已核实事实；相关数字需要溯源到原始证据。
2. 视频画面展示了什么，与画面发生在何时何地，是两个不同的问题。
3. 找不到来源就标注 `unverified`，不要编造时间码、播放量、评论量、图片授权或事实。
4. 「候选画面」只是编辑决策，不代表获得版权许可；另行核查授权。
5. 涉及平台内容的抓取、下载、转写和展示，应遵守适用法规及平台规则。

## 文件结构

```text
SKILL.md                     Codex 工作指引
schemas/sources.schema.json  输入数据契约
schemas/selection.schema.json 审核选择格式
scripts/common.py            数据验证
scripts/build_review.py      构建 HTML 审核台
scripts/apply_selection.py   审核结果导出
templates/review.html        无依赖审核界面
examples/                    虚构演示数据（不可当事实引用）
tests/                       标准库 unittest
```

## 路线图

- **v0.1：研究与审核闭环（当前）**：数据契约、审核台、选择结果导出、测试。
- **v0.2：视频理解**：授权媒体导入、字幕提取、Whisper 转写、关键帧和 OCR，精确记录时间码。
- **v0.3：更强的研究**：可配置搜索适配器、证据追溯、来源独立性判断和交叉核实。
- **后续项目**：文案导演与视频制作保持独立，通过 JSON 资料包对接。

License: [MIT](LICENSE).
