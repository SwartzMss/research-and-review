# Research & Review

**Windows 原生的 AI 热点研究与资料审核项目。** 目标是让用户选择信息平台，查看 AI 搜索与分析进度，审核来源，再把经过筛选的资料交给后续的文案/分镜工具。

> **当前可运行的是 v0.1「离线资料审核 MVP」；常驻 Web 工作台、Codex App Server 集成、多平台自动搜索都还没有实现。** 不要将路线图误认为已实现功能。

## 产品目标

用户打开本地 Research Workspace，输入主题，勾选新闻、B站、抖音、YouTube 等**当前实际可用**的平台；系统启动研究，逐步展示搜索结果、摘要、来源、视频时间码及核验状态。用户随时标记「仅供研究 / 候选画面 / 排除 / 待定」，所有记录可在刷新或重启后恢复。

- **Codex App Server（规划中）**：通过独立的 Windows 本地进程执行 Agent，维护 thread/turn 和流式事件。你的 ChatGPT 桌面版可以同时独立使用；不要求 WSL。
- **research-and-review Skill（已存在）**：定义资料收集、信息提取、溯源、评估与审核的规范；也可以在 Codex 中单独使用。
- **Web UI + 本地任务服务（规划中）**：负责平台选择、任务进度、资料审阅、SQLite 持久化；不用让 Codex 每次重建 HTML。
- **平台适配器（规划中）**：工具应显式区分搜索、元数据、字幕、下载等能力；支持不足时在界面说明原因。
- **视频制作不属于本仓库**：后续通过结构化研究资料包对接 Video Director / Video Production。

详细架构与实施边界：[docs/architecture.md](docs/architecture.md)。

## 当前完成情况

| 功能 | 状态 | 实现 |
| --- | --- | --- |
| Codex 研究流程规则 | ✅ 已有 | [SKILL.md](SKILL.md) |
| 资料/用户决策 JSON 结构 | ✅ 已有 | `schemas/` |
| 离线 HTML 审核页（过滤、备注、导出） | ✅ 已有 | `scripts/build_review.py` / `templates/review.html` |
| 筛选结果导出为 selected.json | ✅ 已有 | `scripts/apply_selection.py` |
| 自动化测试 | ✅ 已有 | GitHub Actions + unittest |
| Windows 本地 Web 工作台（实时任务/持久化） | ⏳ 规划中 | [#5](https://github.com/SwartzMss/research-and-review/issues/5)、[#6](https://github.com/SwartzMss/research-and-review/issues/6) |
| Codex App Server 进程桥接 | ⏳ 规划中 | [#4](https://github.com/SwartzMss/research-and-review/issues/4) |
| 平台能力检测、自动搜索 | ⏳ 规划中 | [#7](https://github.com/SwartzMss/research-and-review/issues/7)、[#1](https://github.com/SwartzMss/research-and-review/issues/1) |
| 视频下载、字幕、转写、视觉理解 | ⏳ 规划中 | [#2](https://github.com/SwartzMss/research-and-review/issues/2) |
| 数据溯源和交叉核验的自动化增强 | ⏳ 规划中 | [#3](https://github.com/SwartzMss/research-and-review/issues/3) |

注意：Skill 可以指导具备搜索能力的 Codex 收集资料，但**当前仓库没有独立的 B站/抖音搜索器、下载器或自动事实核查引擎**。示例 JSON 均为虚构，不能用于真实新闻引用。

## Windows：现在就可以体验的离线功能

需要 Git 和 Python 3.10+，**无需 Node.js、API Key、WSL 或第三方 Python 包**。在 **PowerShell** 中执行：

```powershell
git clone https://github.com/SwartzMss/research-and-review.git
Set-Location .\research-and-review

py -3 scripts/build_review.py examples/sources.json --output output/review.html
Start-Process (Resolve-Path .\output\review.html).Path
```

浏览器里给资料标注待定、仅供研究、候选画面或排除，填写备注，然后点击 **导出 selection.json**。将导出的 JSON 复制到项目的 `output\selection.json`，执行：

```powershell
py -3 scripts/apply_selection.py examples/sources.json output/selection.json --output output/selected.json
py -3 -m unittest discover -s tests -v
```

如果没有 `py` 启动器，可改用 `python`。输出的 `selected.json` 仅包含人工明确采纳的记录，采纳不代表事实已核实或素材已获得使用授权。

### Windows：让 Codex 发现 Skill

本仓库根目录的 `SKILL.md` 是内容源文件；**仅将 App Server 的工作目录指向此仓库，不能保证 Codex 自动发现根目录的 Skill**。按官方约定将整个仓库安装到用户级 Skill 目录：

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
git clone https://github.com/SwartzMss/research-and-review.git "$HOME\.agents\skills\research-and-review"
```

如果已经克隆到该目录，无须再次 clone；在该目录 `git pull` 即可更新。Codex 通常会自动检测 Skill 更新，未显示时重启。使用 `$research-and-review` 显式调用。

**未来使用 App Server 还需要 Codex CLI 可执行程序**，但不代表必须用 CLI 聊天，也不能假定安装了 ChatGPT Windows 桌面应用就自动具备 CLI：

```powershell
Get-Command codex -ErrorAction SilentlyContinue
codex --version
codex app-server --help
```

找不到命令时，先参阅 [Codex CLI 官方文档](https://developers.openai.com/codex/cli) 安装及登录。后端会使用本机 Codex 的认证配置；**当前仓库尚未包含该后端**。

## 使用 Codex 进行研究（现阶段）

在能够使用 Skill 的 Codex 会话里输入：

> 使用 $research-and-review 研究「塞尔维亚学生运动」。搜索多个独立来源的新闻与相关视频，保留 URL、日期、关键观点、未验证数据和版权状态。输出符合 schemas/sources.schema.json 的 sources.json，生成本地 review.html 让我审核；我做完选择之前不要生成视频。

研究产物放在独立的项目目录或 gitignore 排除的 `output/`，不要提交个人文件、媒体、凭据或第三方下载后端。

## 后续路线（按依赖开发）

1. **P0：工作台底座** — [#4 App Server](https://github.com/SwartzMss/research-and-review/issues/4) → [#5 任务服务](https://github.com/SwartzMss/research-and-review/issues/5) + [#7 能力检测](https://github.com/SwartzMss/research-and-review/issues/7) → [#6 Web UI](https://github.com/SwartzMss/research-and-review/issues/6)。先用 mock 搜索结果验证整个交互闭环。
2. **P1：真实资料发现** — [#1 多平台搜索](https://github.com/SwartzMss/research-and-review/issues/1)，按平台逐个接入、测试，不承诺一开始全部支持。
3. **P2：内容理解与核验** — [#2 视频理解](https://github.com/SwartzMss/research-and-review/issues/2)、[#3 事实核查](https://github.com/SwartzMss/research-and-review/issues/3)。

项目不会把「用户选择了某平台」等同于「那个平台的所有能力都可用」。平台具体能力的检测结果应由后端真实工具确定。

## 开发约束

- Windows Native 优先；未来可以考虑跨平台，但 MVP 不依赖 WSL。
- App Server 优先使用 stdio JSON-RPC，默认不使用 experimental API 或公开监听的服务端口。
- 前端不直接接触 Codex 凭据；后端默认只监听 `127.0.0.1`。
- 真实研究任务的进度应由工具/任务管理器报告；不得由 AI 自称的百分比推断。
- 资料来源与视频版权需分开记录；用户标记候选镜头不代表获得再使用许可。

相关官方文档：[Codex App Server](https://developers.openai.com/codex/app-server) · [Codex Skills](https://developers.openai.com/codex/skills)。

License: [MIT](LICENSE).
