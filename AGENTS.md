# History Podcast Codex Skills 交接文档

更新时间：2026-05-14

## 1. 仓库定位

本仓库保存历史/知识类播客生产相关 Codex skills。当前稳定目标是两条工作流并存：

- 播客声音生产工作流：从系列策划到 voice-only `episode.mp3`。
- 微信公众号文章工作流：将口播稿件转成可上传微信公众号的文章草稿。

仓库不再保留旧的独立播客策划、播客脚本生成、口播稿生成 skills；这些能力已经被新的播客生产工作流覆盖。

当前播客系统用于系列化中文播客的 voice-only 音频生产。目标是让一个新用户从 GitHub 拉取仓库后，可以按照稳定、可续跑、机器可校验的流程生成完整口播版 `episode.mp3`。

当前架构：

- 唯一用户入口是 `podcast-series-showrunner`。
- 内部模块负责单集策划、写稿、口播适配、TTS、剪辑和校验。
- AI 输出完整口播版 `episode.mp3`：系列固定片头口播、短静音、正文口播、尾部静音。
- 系统不生成、不选择、不管理、不混合音乐或音效。
- 写稿、单集 brief、口播适配仍由 skills 完成；确定性音频后半段由 `tools/run_episode_pipeline.py` 调度。
- 续跑状态只写入 `production_state.json`，不追加到 `AGENTS.md`。

推荐主流程：

```text
用户需求
→ podcast-series-showrunner 澄清需求
→ 给出 2-3 个系列方案、推荐方向、每集策划、系列固定片头口播候选
→ 用户明确说“开始执行/生成第 X 集/跑完整流程”
→ 写入 series_plan.json、series_opening_voice.md/json、production_state.json
→ 生成 opening_voice.wav
→ 生成 episode_brief.json
→ 生成 script_full.md、fact_check.md、script_meta.json
→ 生成 narration.txt、narration_meta.json
→ tools/run_episode_pipeline.py 生成 voice.wav、真实时间戳、tts_manifest.json、episode.mp3、production_manifest.json
→ tools/validate_production.py 校验产物
```

## 2. 当前保留 Skills

### 播客声音生产

唯一用户入口：

```text
skills/podcast-series-showrunner/
```

内部模块：

```text
skills/podcast-series-opening-voice-producer/
skills/podcast-episode-director/
skills/history-script-writer/
skills/podcast-narration-adapter/
skills/podcast-tts-producer/
skills/podcast-episode-editor/
```

职责边界：

- `podcast-series-showrunner`：唯一用户入口，负责系列方案、执行触发、内部调度、状态续跑。
- `podcast-series-opening-voice-producer`：生成系列固定片头口播文案记录和 `opening_voice.wav`。
- `podcast-episode-director`：从 `series_plan.json` 生成某一集的 `episode_brief.json`。
- `history-script-writer`：从 `episode_brief.json` 生成 `script_full.md`、`fact_check.md`、`script_meta.json`。
- `podcast-narration-adapter`：把审稿脚本转换为干净 TTS 文本 `narration.txt` 和 `narration_meta.json`。
- `podcast-tts-producer`：说明 TTS 产物契约；长正文默认使用 `tools/robust_episode_tts.py`。
- `podcast-episode-editor`：拼接 `opening_voice.wav` 和 `voice.wav`，输出 voice-only `episode.mp3`。

默认不使用 subagent。未来如果用户明确要求多集并行，必须按 episode 目录隔离写入并合并 `production_state.json`。

### 微信公众号文章生产

总入口：

```text
skills/wechat-article-pipeline/
```

内部模块：

```text
skills/wechat-history-article/
skills/wechat-image-director/
skills/wechat-html-publisher/
```

稳定产物：

```text
article.json
image_manifest.json
images/
article.html
meta.json
微信公众号草稿
```

边界：

- 默认创建微信公众号草稿。
- 不发布、不群发、不删除账号资产。
- 不把 WeChat AppSecret 写入 Markdown、JSON、脚本、日志或最终回复。

## 3. 播客产物契约

新系列目录结构：

```text
<series-folder>/
├── series_plan.json
├── series_opening_voice.md
├── series_opening_voice.json
├── opening_voice.wav
├── opening_voice_timeline_raw.json
├── opening_voice_timeline_compact.json
├── opening_voice_tts_manifest.json
├── production_state.json
└── episodes/
    └── ep01-<slug>/
        ├── episode_brief.json
        ├── script_full.md
        ├── fact_check.md
        ├── script_meta.json
        ├── narration.txt
        ├── narration_meta.json
        ├── voice.wav
        ├── voice_timeline_raw.json
        ├── voice_timeline_compact.json
        ├── tts_manifest.json
        ├── episode.mp3
        └── production_manifest.json
```

关键规则：

- `narration.txt` 是纯 TTS 文本，不包含 Markdown、事实核查、内部备注、模型标签、时间戳、音乐或音效指令。
- `narration.txt` 开头默认加入：“好的，欢迎回到这期节目。”
- `narration.txt` 末尾默认加入：“好，这一期就先到这里。我们下期再见。”
- `opening_voice.wav` 是系列固定片头口播，除非系列改版，不应每集重做。
- `voice.wav` 是每集正文口播，包含正文和固定片尾收束语。
- `episode.mp3` 是 AI 输出的完整口播版单集音频。
- 所有 JSON 必须可解析，路径字段使用绝对路径。
- 所有 TTS manifest 只能记录 `api_key_source: "DASHSCOPE_API_KEY"`，不得记录真实 API key。

`production_state.json` 状态枚举：

```text
planned | brief_done | script_done | narration_done | tts_done | mp3_done | failed
```

推荐 state 字段：

```json
{
  "series_name": "示例系列",
  "series_plan_path": "/absolute/path/to/series_plan.json",
  "opening_voice_status": "done",
  "opening_voice_path": "/absolute/path/to/opening_voice.wav",
  "episodes": [
    {
      "episode_no": 1,
      "episode_title": "第一集",
      "status": "mp3_done",
      "episode_dir": "/absolute/path/to/episodes/ep01-title",
      "episode_brief": "/absolute/path/to/episode_brief.json",
      "script_full": "/absolute/path/to/script_full.md",
      "fact_check": "/absolute/path/to/fact_check.md",
      "narration": "/absolute/path/to/narration.txt",
      "voice": "/absolute/path/to/voice.wav",
      "tts_manifest": "/absolute/path/to/tts_manifest.json",
      "tts_generation_mode": "chunked_external_orchestration",
      "tts_chunk_count": 12,
      "tts_chunk_dir": "/absolute/path/to/voice_robust_chunks",
      "retryable": true,
      "episode_mp3": "/absolute/path/to/episode.mp3",
      "production_manifest": "/absolute/path/to/production_manifest.json",
      "failed_step": null,
      "failed_reason": null,
      "updated_at": "2026-05-14T00:00:00+08:00"
    }
  ],
  "next_recommended_episode_no": 2
}
```

## 4. 确定性工具

```text
tools/robust_episode_tts.py
tools/run_episode_pipeline.py
tools/validate_production.py
```

### `tools/robust_episode_tts.py`

长正文 TTS 默认使用该脚本：

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 tools/robust_episode_tts.py \
  --narration /absolute/path/to/narration.txt \
  --meta /absolute/path/to/narration_meta.json \
  --out-dir /absolute/path/to/episode-dir \
  --output-prefix voice \
  --manifest-name tts_manifest.json \
  --model cosyvoice-v3-flash \
  --voice longsanshu_v3 \
  --max-chars-per-task 300 \
  --chunk-silence-ms 450 \
  --tail-silence-ms 3500 \
  --retries 2
```

行为要求：

- 从脚本位置自动推导仓库根目录，不使用用户机器绝对路径。
- Python 解释器选择顺序：`PODCAST_AUDIO_PYTHON`、仓库 `.venv/bin/python`、当前 `sys.executable`。
- 每个外部分段最多重试 2 次。
- 成功分段按签名复用，支持断点续跑。
- 失败时写入 `tts_manifest.json.failed_reason`、`failed_chunk_index`、`failed_chunk_dir`。

### `tools/run_episode_pipeline.py`

该脚本只负责音频后半段，不调用 LLM，不生成 brief、脚本或口播适配文本。

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 tools/run_episode_pipeline.py \
  --series-dir /absolute/path/to/series \
  --episode-dir /absolute/path/to/series/episodes/ep01-title
```

输入要求：

- `series_plan.json`
- `production_state.json`
- `opening_voice.wav`
- `episode_brief.json`
- `narration.txt`
- `narration_meta.json`

输出：

- `voice.wav`
- `voice_timeline_raw.json`
- `voice_timeline_compact.json`
- `tts_manifest.json`
- `episode.mp3`
- `production_manifest.json`
- 更新后的 `production_state.json`

常用参数：

```text
--opening-voice /path/to/opening_voice.wav
--episode-slug episode
--force-tts
--skip-tts
--skip-edit
--model cosyvoice-v3-flash
--voice longsanshu_v3
--max-chars-per-task 300
--chunk-silence-ms 450
--tail-silence-ms 3500
--retries 2
```

### `tools/validate_production.py`

用于上传、交接或续跑前做机器校验：

```bash
python3 tools/validate_production.py --series-dir /absolute/path/to/series
python3 tools/validate_production.py --episode-dir /absolute/path/to/series/episodes/ep01-title --strict
```

校验内容：

- JSON 可解析。
- 音频文件存在且非空。
- `narration.txt` 与 `narration_meta.json.paragraphs` 完全一致。
- `tts_manifest.json.generation_mode` 为 `chunked_external_orchestration`。
- manifest 不包含真实 API key。
- `production_manifest.json.edit_scope.music` 和 `sound_effects` 均为 `false`。
- `production_state.json` 中 episode 状态与真实文件一致。

## 5. TTS 与安全

默认 TTS：

```text
model: cosyvoice-v3-flash
voice: longsanshu_v3
api: 阿里云百炼 CosyVoice WebSocket API
opening_generation_mode: chunked
episode_body_generation_mode: chunked_external_orchestration
episode_body_script: tools/robust_episode_tts.py
episode_body_max_chars_per_task: 300
episode_body_retries_per_chunk: 2
```

安全规则：

- API Key 只能通过环境变量传入，例如 `DASHSCOPE_API_KEY`。
- 不得把 API Key 写入脚本、manifest、Markdown、日志或最终回复。
- 使用低并发，默认一次只处理一集。
- 不无限重试；长正文默认每段重试 2 次。
- 网络断连、WebSocket keepalive timeout、服务端中段断连都视为常见生产条件，必须保留已成功分段以便续跑。

## 6. 后续演进方向

下一阶段要把微信公众号文章工作流整合进播客生产工作流，但保持两个工作流可独立运行。

目标形态：

```text
用户提出历史/知识类播客选题
→ podcast-series-showrunner 统一澄清需求和确定系列方案
→ 播客工作流生成 script_full.md、narration.txt、episode.mp3
→ 公众号文章工作流读取同一集脚本或口播稿，生成 article.json、HTML 和微信公众号草稿
```

推荐并行策略：

- 默认仍由 `podcast-series-showrunner` 作为总入口。
- 当单集 `script_full.md` 或 `narration.txt` 稳定后，可以启动一个独立 subagent 运行 `wechat-article-pipeline`。
- 主线程继续执行 TTS 和 `episode.mp3` 生产。
- WeChat subagent 独立生成文章包和公众号草稿，不阻塞音频 TTS。
- 两个工作流通过明确文件路径交接，不共享可写中间文件。
- 最终在 `production_state.json` 或后续扩展的 manifest 中记录对应文章目录和草稿状态。

未来整合时应注意：

- 公众号文章应基于已确认脚本或口播稿，不重新发明事实和叙事主线。
- 播客音频失败不应自动取消文章草稿生成；文章 workflow 可以独立完成。
- 公众号上传失败不应影响已经完成的 `episode.mp3`。
- 两个 workflow 都必须避免泄露 API key、AppSecret 或上传凭证。
- 发布和群发仍然需要人类明确授权；自动流程只创建草稿。

## 7. GitHub 维护规则

仓库应包含：

- 稳定播客 skills
- 稳定 WeChat skills
- `tools/robust_episode_tts.py`
- `tools/run_episode_pipeline.py`
- `tools/validate_production.py`
- `AGENTS.md`
- `README.md`
- `.gitignore`

仓库不应包含：

- `.venv/`
- `.DS_Store`
- `__pycache__/`
- 本地测试系列产物
- 大音频输出文件
- API key、AppSecret 或含密钥日志

提交前至少运行：

```bash
python3 -m py_compile tools/*.py \
  skills/podcast-tts-producer/scripts/*.py \
  skills/podcast-episode-editor/scripts/*.py \
  skills/wechat-html-publisher/scripts/*.py
```

如有测试系列产物，运行：

```bash
python3 tools/validate_production.py --series-dir /absolute/path/to/series
```

最终稳定边界：本系统只生产完整口播版节目。音乐、音效、最终审美后期由人类在外部剪辑流程中决定。
