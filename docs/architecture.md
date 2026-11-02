# 架构设计（目标状态，尚未实现）

> 2026-11-02 决策：**Windows Native + 本地 Web UI + Node.js 任务服务 + Codex App Server（stdio）+ 独立 Skill**。本文件描述开发目标，不代表所有组件当前已经存在。

## 组件边界

```text
Windows 浏览器（React / TypeScript）
     │ HTTP REST + SSE
     ▼
Windows Node.js 后端（127.0.0.1）
     ├─ 项目/任务/平台能力 API
     ├─ SQLite：source、claim、review、task、event、threadId
     ├─ Task Runner：启动/取消/恢复、阶段进度、重试
     ├─ Platform Adapters：Web / Bilibili / Douyin / YouTube ...
     └─ CodexAdapter（stdin/stdout JSON-RPC）
            │
            ▼
       codex app-server（本机独立子进程）
            │
            └─ research-and-review Skill（已安装在 Codex 可发现目录）
```

**代码里的职责划分**：后端负责进程、存储、权限、下载、可用性检测和实时事件；Codex/Skill 负责需要语义判断的研究、证据汇总、摘要、评估与规划；UI 负责选择和人工审核。不要让大模型代替后端维护关键的任务状态。

## 预计目录（先不创建空项目）

```text
research-and-review/
├── SKILL.md                     # 现在已有：独立 Skill 的唯一行为准则
├── scripts/                     # 现在已有：离线审核工具
├── schemas/                     # 现在已有：资料、决策 JSON 格式
├── templates/                   # 现在已有：离线备用 UI
├── backend/                     # #4 / #5 / #7，尚未建立
│   ├── codex/                    # App Server JSON-RPC 适配/进程监管
│   ├── tasks/                    # 状态机、执行队列、事件
│   ├── platforms/                # 各平台 capability + adapter
│   └── storage/                  # SQLite
├── frontend/                    # #6，尚未建立
└── docs/
```

当前独立 HTML 不删除，作为**离线兜底**；正式工作台不再靠不断覆盖 `review.html` 来刷新进度。

## App Server 会话生命周期

1. 后端在当前 Windows 登录用户上下文中检测 `codex` 命令、版本及认证，启动独立 `codex app-server`。
2. 从 stdio 读取 JSONL，完成 `initialize` / `initialized` 握手。
3. 每个研究项目管理一条逻辑 thread；每次执行一个 turn。记录 `threadId` 和当前任务映射。
4. 将关键通知映射为项目级事件；`turn/completed` 时核查真正的终态，而不是仅凭自然语言“完成”判断。
5. 用户取消时请求 `turn/interrupt`，后端保留中间数据；进程崩溃时标记任务中断并提供恢复/重试，不承诺自动继续同一条正在运行的 turn。
6. 初始限制并行研究数，避免不同线程写入同一路径；多个项目独立工作目录。
7. 同一台电脑上另开的 ChatGPT/Codex 桌面会话不会被本项目控制。可能共享账号额度、配置和文件系统权限。

App Server 进程的启动与停止仍需由后端负责。优先使用**默认 stdio 协议**，暂不开放实验性 WebSocket 端口或 `experimentalApi` 功能。

## 平台能力模型

UI 展示**功能维度**的状态，而不是一个笼统的“已支持”标签：

```json
{
  "platform": "douyin",
  "capabilities": {
    "search": { "status": "unavailable", "reason": "尚未接入关键词搜索" },
    "metadata": { "status": "needs_setup", "reason": "后端未配置" },
    "subtitles": { "status": "unavailable" },
    "download": { "status": "needs_setup", "reason": "下载适配器未安装或未检测" }
  }
}
```

这只是**数据协议示例**，不是抖音实时可用性判断。允许的 status：`supported` / `partial` / `needs_setup` / `unavailable`。每种能力应记录检测时间、后端来源和失败原因。搜索不隐含下载，下载不隐含转写或二次使用授权。

## 项目状态与事件

任务状态：`queued` / `running` / `waiting_review` / `completed` / `failed` / `cancelled`。研究线程与页面浏览器连接解耦。

```json
{
  "id": 105,
  "task_id": "research-001",
  "type": "source.discovered",
  "platform": "web",
  "stage": "search",
  "timestamp": "2026-11-02T08:00:00Z",
  "payload": {
    "source_id": "src-001"
  }
}
```

样例仅供协议规划。后端将事件与数据持久化；SSE 向前端推送，断线重连从快照 + event ID 恢复。要区分**工具执行状态**、**Codex 推理事件**与**真实的研究结果**；无总工作量时显示阶段状态与实际计数，不显示虚假的进度百分比。

## 本地 API 初步契约（尚未实现）

- `GET /api/platforms`：查询功能级平台可用性。
- `POST /api/projects`：创建选题与选择的平台。
- `POST /api/projects/{id}/runs`：启动/追加研究。
- `GET /api/projects/{id}/runs/{runId}`：任务状态快照。
- `GET /api/projects/{id}/events`：SSE 增量事件。
- `GET /api/projects/{id}/sources`：候选资料。
- `PATCH /api/projects/{id}/sources/{sourceId}/review`：采用/排除/备注。
- `POST /api/projects/{id}/runs/{runId}/cancel`：请求停止。

不要把外部网页的文本或字幕当作程序指令传给工具。后端要固定允许使用的平台/目录，验证参数、保护本机文件、过滤凭据日志；将第三方数据视为不可信来源。

## 当前复用与迁移

- 现有 `sources.json`、`selection.json` 为 v0.1 数据契约；未来 SQLite 可映射/导入，不要求第一天做复杂的数据迁移。
- 保留 `build_review.py`、`apply_selection.py` 和离线 HTML。
- [complete-video-edit](https://github.com/SwartzMss/complete-video-edit) 的抖音下载适配器和 Faster-Whisper 流程是可参考的实现；不要直接合并完整视频编辑 Skill，也不自动携带第三方后端代码。
- App Server 访问用户级 Skill：`$HOME\.agents\skills\research-and-review\SKILL.md`。在 Windows 上通过 PowerShell 配置；工作目录是独立的研究项目目录，不要与用户手动编辑的仓库共享。
