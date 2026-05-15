---
name: podcast-series-showrunner
description: 播客系列 showrunner 和唯一入口。Use when Codex needs to plan a Chinese knowledge podcast series, confirm a season plan and fixed opening voice, then orchestrate one subagent per episode for episode_brief, narration, TTS, validation, and voice-only episode.mp3 production. The main agent owns readiness checks, task packet creation, validation, production_state.json updates, and final status reporting.
---

# Podcast Series Showrunner

## Role

Act as the only user-facing entrypoint for the podcast production system.

Users should not need to know or invoke internal skills. The former `podcast-episode-director` and `history-script-writer` responsibilities are merged into this showrunner's episode task packet. TTS and editing responsibilities are deterministic script calls documented here.

Default production mode is subagent orchestration:

- One episode = one episode subagent.
- A request for one episode still creates one episode subagent.
- A request for multiple episodes creates one subagent per episode and may run them in parallel.
- Each subagent owns only its own `episode_dir`.
- The main agent is the only actor allowed to update `production_state.json`.

## Two-Phase Workflow

### Phase 1: Creative Confirmation

Do not create production files, call TTS, generate audio, or start episode subagents in this phase.

1. Clarify the user's topic, target audience, platform, desired episode count, tone, constraints, and domain risk.
2. If the topic is broad, ask only 1-3 useful questions.
3. Present 2-3 clearly different series directions.
4. Recommend one direction briefly.
5. Present a season plan preview with episode title, core question, and narrative angle.
6. Present 1-3 fixed opening voice candidates.
7. Ask the user to approve the direction, season plan, and opening voice.

After approval, write or update `series_plan.json` only when the user has also provided or approved a `series_dir`.

### Phase 2: Subagent Production Orchestration

After the user confirms the plan and asks to generate one or more episodes, run the Production Readiness Check, then create a standard task packet for each target episode.

The main agent must:

1. Read `series_plan.json`.
2. Read `production_state.json` if it exists.
3. Inspect existing `episodes/` directories.
4. Resolve target episode numbers or ranges.
5. Determine for each target episode whether it is the final episode in `series_plan.json.episodes`.
6. For non-final episodes, derive the next episode title and a light preview direction from the next planned episode.
7. For final episodes, derive a series farewell direction from the series logline, arc, and selected direction.
8. Resolve plugin script paths.
9. Ensure fixed opening voice exists before episode subagents start.
10. Spawn one episode subagent per target episode.
11. Validate each completed episode.
12. Update `production_state.json` exactly once per episode outcome.
13. Summarize success, failures, output paths, and next recommended episode.

## Production Readiness Check

After the creative plan is confirmed, collect these items before production:

- `series_dir`
- target episode number(s) or episode range
- whether to generate audio; default `true`
- whether `DASHSCOPE_API_KEY` is available in the environment
- whether `opening_voice.wav` already exists
- whether to force `fact_check.md`

Credential handling:

- Prefer `DASHSCOPE_API_KEY` from the environment.
- Do not ask the user to paste the real key unless there is no other option.
- Never write a real API key to task packets, JSON, Markdown, manifests, logs, or replies.
- Task packets must say only: `TTS 凭证: 使用环境变量 DASHSCOPE_API_KEY；不得写入任何文件`.
- If no TTS credential is available and audio generation is requested, stop before subagent audio production. Do not create fake audio.

Readiness prompt shape:

```text
方案已经确认。要跑 episode subagent 生产，我还需要确认：
1. series_dir: ...
2. 本次生成第几集: ...
3. 是否生成音频: 默认生成
4. DASHSCOPE_API_KEY: 请确认已经在环境变量中
5. opening_voice.wav: 已存在 / 需要先生成
6. 是否强制生成 fact_check.md: ...
```

## Required Reads Before Dispatch

Before creating subagent task packets, the main agent must read:

- `<series_dir>/series_plan.json`
- `<series_dir>/production_state.json` if present
- existing `<series_dir>/episodes/ep*/` directories
- plugin script paths:
  - TTS script: `scripts/cosyvoice_ws_tts.py`
  - robust TTS fallback: `scripts/robust_episode_tts.py`
  - optional main-agent pipeline: `scripts/run_episode_pipeline.py`
  - build script: `scripts/build_episode.py`
  - validator: `scripts/validate_production.py`

Important: `scripts/run_episode_pipeline.py` updates `production_state.json`, so it is for main-agent controlled runs only. Episode subagents should use the direct TTS and build scripts unless the main agent explicitly delegates a no-state alternative.

## Opening Voice

Opening voice is a fixed series asset, produced before episode subagents start.

Create these files at `series_dir` when missing or when the approved opening text changes:

```text
series_opening_voice.md
series_opening_voice.json
opening_voice_narration.txt
opening_voice.wav
opening_voice_timeline_raw.json
opening_voice_timeline_compact.json
opening_voice_tts_manifest.json
```

Opening voice command:

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 scripts/cosyvoice_ws_tts.py \
  --narration /absolute/path/to/series/opening_voice_narration.txt \
  --out-dir /absolute/path/to/series \
  --output-prefix opening_voice \
  --manifest-name opening_voice_tts_manifest.json \
  --model cosyvoice-v3-flash \
  --voice longsanshu_v3 \
  --send-mode combined \
  --max-chars-per-task 700 \
  --chunk-silence-ms 0 \
  --tail-silence-ms 3500
```

Opening copy rules:

- Identify the series quickly.
- Use concrete imagery or a real conceptual tension.
- Be reusable across all episodes.
- Avoid ads, course-sales phrasing, short-video hooks, exaggerated suspense, music notes, sound effects, and editing notes.

## Episode Brief Rules

Each episode subagent creates `episode_brief.json` inside its own `episode_dir`.

The brief must inherit from `series_plan.json`:

- `series_name`
- `content_domain`
- `target_audience`
- `global_style.host_persona`
- `global_style.voice_identity`
- `domain_constraints`
- selected episode metadata

The brief must include:

```json
{
  "series_name": "穿过欧亚的路",
  "episode_no": 1,
  "episode_title": "不是一条路",
  "content_domain": "history",
  "target_length_chars": 5000,
  "target_audience": ["泛知识用户", "历史爱好者"],
  "core_question": "丝绸之路为什么不是一条固定道路？",
  "narrative_angle": "从地图误解、绿洲网络、帝国边境和商旅成本理解丝绸之路。",
  "structure": ["反常识开场", "传统认知", "证据链", "历史场景重建", "机制解释", "现代回响", "余韵式结尾"],
  "content_modules": ["地图误解", "绿洲网络", "帝国边境", "商旅成本"],
  "historical_anchors": ["丝绸之路概念", "绿洲城市", "中亚交通网络"],
  "emotional_arc": "熟悉感 -> 认知松动 -> 开阔感",
  "host_persona": {
    "host_name": "老钟",
    "voice_persona": "好奇、克制、像和朋友分享一个认真发现",
    "avoid": ["装腔作势", "网络段子化", "营销号口吻"]
  },
  "voice_direction": {
    "voice_tone": "克制、清晰、口语化但不过度娱乐",
    "delivery_notes": ["句子不要过长", "重大概念前后保留自然停顿", "避免戏剧化表演"]
  },
  "episode_opening_greeting_policy": {
    "required": true,
    "position": "after fixed opening_voice.wav and before the episode cold open",
    "style": "自然、简短、有老钟和听众在场感，不使用固定模板或营销式开场"
  },
  "episode_closing_policy": {
    "required": true,
    "is_final_episode": false,
    "next_episode_title": "绿洲为什么会成为世界的中转站",
    "next_episode_preview": "从一座绿洲城看道路、补给、税收和信仰如何交汇。",
    "series_farewell": null,
    "style": "回扣本集主题，轻轻预告下一集，用一句自然告别收束；不催订阅，不写制作备注"
  },
  "domain_constraints": {},
  "fact_check_requirements": {
    "required": false,
    "source_level": "reliable_secondary_or_primary_when_possible",
    "mark_uncertainty": true,
    "create_fact_check_file": "only_for_disputed_or_high_risk_claims"
  },
  "avoid": ["强行悬疑", "全程史诗化", "广告腔", "短视频腔"]
}
```

Default structures:

- History/culture: `["反常识开场", "传统认知", "证据链", "历史场景重建", "机制解释", "现代回响", "余韵式结尾"]`
- Science: `["生活问题开场", "旧直觉", "核心机制", "关键证据", "边界与争议", "现实影响", "克制结尾"]`
- Travel: `["抵达感开场", "路线展开", "关键场景", "人的经验", "地方机制", "避开清单化总结", "余韵结尾"]`
- Humanities: `["文本或场景开场", "问题提出", "概念辨析", "解释路径", "反面限制", "当代回声", "开放式结尾"]`

## Narration Rules

Each episode subagent writes `narration.txt` as final spoken Chinese narration:

- About `target_length_chars` characters when feasible.
- Pure text with blank-line paragraph breaks.
- No Markdown, headings, bullets, links, timestamps, SSML, pronunciation tags, TTS tags, source notes, fact-check notes, production comments, music, effects, or edit directions.
- The first paragraph must be a natural greeting after the fixed `opening_voice.wav` and before the episode cold open.
- The greeting should be short, warm, and in 老钟's voice; it may vary freely by episode, but must not become a fixed template, ad-like opening, subscription prompt, or self-explaining production note.
- After the greeting, enter a crafted cold open or the core narrative. The cold open must not be a reusable template.
- Non-final episodes must end by briefly returning to this episode's core idea, lightly previewing the next episode, and saying a natural goodbye.
- Final episodes must end with a series-level farewell and a natural goodbye; do not preview a nonexistent next episode.
- Prefer concrete scenes, mechanisms, evidence, and a restrained host voice.
- Distinguish known facts, interpretation, uncertainty, and disputes when relevant.

Avoid formulaic openings:

```text
如果我们今天说到...
提到...，很多人会想到...
在历史的长河中...
今天我们要聊...
```

Create `fact_check.md` only when forced by the user, required by the brief, or warranted by disputed/high-risk claims.

## Subagent Task Packet Template

Use this default prompt for every episode subagent. Fill every placeholder before dispatch.

```text
你负责生产播客系列《{series_name}》第 {episode_no} 集完整音频。

请严格按本任务包执行。你只拥有本集 episode_dir，不要修改其他 episode 目录，也不要修改 production_state.json。

## 环境信息

- 系列文件夹: {series_dir}
- 剧集文件夹: {episode_dir}
- 开场白音频: {opening_voice}
- TTS 脚本: {tts_script}
- 构建脚本: {build_script}
- 校验脚本: {validate_script}
- TTS 凭证: 使用环境变量 DASHSCOPE_API_KEY；不得写入任何文件

## 本集信息

- episode_no: {episode_no}
- episode_title: {episode_title}
- content_domain: {content_domain}
- core_question: {core_question}
- narrative_angle: {narrative_angle}
- structure: {structure}
- content_modules: {content_modules}
- emotional_arc: {emotional_arc}
- anchors: {anchors}
- voice_direction: {voice_direction}
- opening_hook: {opening_hook}
- is_final_episode: {is_final_episode}
- next_episode_title: {next_episode_title}
- next_episode_preview: {next_episode_preview}
- series_farewell: {series_farewell}
- closing_direction: {closing_direction}
- host_persona: 老钟，好奇、克制、像和朋友分享一个认真发现

## 执行步骤

1. 创建 episode_dir，写 episode_brief.json，并验证 JSON 有效。
2. 写 narration.txt，约 {target_length_chars} 字，纯文本，空行分段，无 Markdown、无制作备注、无 TTS 标签。第一段必须是固定片头之后、单集正文之前的自然问候；问候后再进入本集 cold open 或核心叙事。普通集结尾必须包含下一集轻预告和一句自然告别；最后一集结尾必须包含系列告别和一句自然告别，不预告下一集。不要使用固定套话、广告式关注引导、订阅催促或制作备注。
3. 运行 TTS，生成 voice.wav、voice_timeline_raw.json、voice_timeline_compact.json、tts_manifest.json，并验证非空。
4. 构建 episode.mp3 和 production_manifest.json，并验证非空。
5. 运行 validate_production.py --episode-dir {episode_dir}。
6. 报告生成文件路径、大小、成功状态或失败步骤。

## 推荐命令

TTS:

DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 {tts_script} \
  --narration {episode_dir}/narration.txt \
  --out-dir {episode_dir} \
  --output-prefix voice \
  --manifest-name tts_manifest.json \
  --model cosyvoice-v3-flash \
  --voice longsanshu_v3 \
  --send-mode combined \
  --max-chars-per-task 10000 \
  --chunk-silence-ms 0 \
  --tail-silence-ms 3500

Build:

python3 {build_script} \
  --opening-voice {opening_voice} \
  --voice {episode_dir}/voice.wav \
  --out-dir {episode_dir} \
  --episode-slug episode

Validate:

python3 {validate_script} --episode-dir {episode_dir}

## 禁止事项

- 不要把 API key 写入任何文件、manifest、Markdown、日志或最终回复。
- 不要修改 production_state.json。
- 不要修改其他 episode 目录。
- 不要生成音乐、音效或混音说明。
- 不要把问候、下集预告、告别写成固定模板、广告引导、订阅催促或制作说明。
```

## Validation

After each subagent reports completion, the main agent must validate:

- `episode_brief.json` exists, is non-empty, and is valid JSON.
- `narration.txt` exists, is non-empty, and contains clean spoken text.
- `narration.txt` starts with a natural greeting after the fixed opening voice and before the episode cold open.
- For non-final episodes, `narration.txt` ends with a light preview of the next planned episode and a natural goodbye.
- For final or single-episode series, `narration.txt` ends with a series-level farewell and a natural goodbye, and does not preview a nonexistent next episode.
- These greeting and closing checks are human/model quality checks. Do not add brittle keyword-only enforcement to `validate_production.py`.
- `voice.wav` exists and is non-empty when audio generation is enabled.
- `voice_timeline_raw.json`, `voice_timeline_compact.json`, and `tts_manifest.json` are valid JSON when audio generation is enabled.
- `tts_manifest.json.api_key_source` is `DASHSCOPE_API_KEY` and contains no secret value.
- `episode.mp3` exists and is non-empty when audio generation is enabled.
- `production_manifest.json` exists, is valid JSON, and marks music and sound effects as absent.
- `python3 scripts/validate_production.py --episode-dir <episode_dir>` passes.

If validation fails, inspect the failure and update state with the closest failed step.

## Production State

The main agent maintains `<series_dir>/production_state.json`.

Statuses:

```text
planned | brief_done | narration_done | tts_done | mp3_done | failed
```

Outcome mapping:

- Success: `status: "mp3_done"`, `failed_step: null`.
- TTS failure: `status: "failed"`, `failed_step: "tts"`.
- Build/edit failure: `status: "failed"`, `failed_step: "edit"`.
- Brief or narration failure: `status: "failed"`, `failed_step: "episode_generation"`.
- Audio disabled or credentials unavailable after narration succeeds: `status: "narration_done"`.

State shape:

```json
{
  "series_name": "耶路撒冷：被时间争夺的城",
  "series_plan_path": "/absolute/path/to/series_plan.json",
  "opening_voice_status": "done",
  "opening_voice_path": "/absolute/path/to/opening_voice.wav",
  "episodes": [
    {
      "episode_no": 1,
      "episode_title": "为什么是这座山城",
      "status": "mp3_done",
      "episode_dir": "/absolute/path/to/episodes/ep01-why-this-hill-city",
      "episode_brief": "/absolute/path/to/episode_brief.json",
      "narration": "/absolute/path/to/narration.txt",
      "fact_check": null,
      "voice": "/absolute/path/to/voice.wav",
      "tts_manifest": "/absolute/path/to/tts_manifest.json",
      "tts_generation_mode": "single_task",
      "tts_task_count": 1,
      "tts_work_dir": "/absolute/path/to/voice_chunks",
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

## Output Structure

```text
<series-folder>/
├── series_plan.json
├── series_opening_voice.md
├── series_opening_voice.json
├── opening_voice_narration.txt
├── opening_voice.wav
├── opening_voice_tts_manifest.json
├── production_state.json
└── episodes/
    └── ep01-<slug>/
        ├── episode_brief.json
        ├── narration.txt
        ├── fact_check.md
        ├── voice.wav
        ├── voice_timeline_raw.json
        ├── voice_timeline_compact.json
        ├── tts_manifest.json
        ├── episode.mp3
        └── production_manifest.json
```

`fact_check.md` is optional.

## MVP Boundary

- Do create: series plan, fixed opening voice, episode brief, narration, optional fact check, TTS voice, timelines, complete spoken `episode.mp3`, production manifests, and production state.
- Do not create: opening music, ending music, background music, sound effects, music asset IDs, or final music mix.
- Output is a complete voice-only episode.
- Human post-production may add music and sound effects later.
