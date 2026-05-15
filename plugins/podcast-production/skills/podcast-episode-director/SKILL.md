---
name: podcast-episode-director
description: 内部模块：播客单集导演。Normally invoked by podcast-series-showrunner. Reads series_plan.json, selects one episode by episode_no or title, inherits style and domain constraints, and outputs episode_brief.json. Do not expose as the default user-facing entrypoint.
---

# Podcast Episode Director

Internal module. Normal users should enter through `podcast-series-showrunner`.

## Role

Convert one episode from `series_plan.json` into an executable `episode_brief.json` for downstream writing and voice production.

## Current MVP Boundary

- Do create: episode brief, recommended writer skill, narrative angle, structure, lightweight fact-check policy, inherited host persona, inherited voice direction, and avoid rules.
- Do not create: narration, TTS audio, timestamps, music direction, sound-effect notes, or final mix instructions.
- Do not override the series identity unless the user explicitly asks for a creative change.

## Inputs

Require `series_plan.json` and `episode_no`. If no target episode is provided for a demo, choose episode 1 and record that default in the output.

## Workflow

1. Parse `series_plan.json`.
2. Select the requested episode from `episodes`.
3. Identify `content_domain` and resolve `recommended_writer_skill` from the plugin registry at `skills/writer_registry.json`.
4. Inherit `series_name`, `target_audience`, `global_style.host_persona`, `global_style.voice_identity`, and `domain_constraints`.
5. Expand the selected episode into `core_question`, `narrative_angle`, `structure`, `content_modules`, `emotional_arc`, `voice_direction`, lightweight `fact_check_requirements`, and `avoid`.
6. Write `episode_brief.json` beside `series_plan.json` unless another output folder is specified.
7. Validate JSON.

## Writer Registry

Use the registry at:

```text
skills/writer_registry.json
```

Selection rules:

- Read `skills/writer_registry.json` before choosing a writer.
- Match `content_domain` against a writer key or any value in `writers.*.domains`.
- If the matched writer has `available: true`, set `recommended_writer_skill` to that writer's `skill`.
- If the matched writer has `available: false`, use its `fallback_skill`, or `default_writer.skill` if no writer-specific fallback exists.
- If no writer matches, use `default_writer.skill`.
- Always write `writer_selection_source: "writer_registry"`.
- Write `writer_fallback_reason: null` only when the selected writer was available directly.
- When a fallback is used, write a short `writer_fallback_reason` explaining whether the writer was missing or unavailable.

The helper command mirrors the expected selection behavior:

```bash
python3 scripts/resolve_writer.py --domain history
python3 scripts/resolve_writer.py --domain science
python3 scripts/resolve_writer.py --validate
```

## Structure Patterns

History/culture default:

```json
["反常识开场", "传统认知", "证据链", "历史场景重建", "机制解释", "现代回响", "余韵式结尾"]
```

Science default:

```json
["生活问题开场", "旧直觉", "核心机制", "关键证据", "边界与争议", "现实影响", "克制结尾"]
```

Travel default:

```json
["抵达感开场", "路线展开", "关键场景", "人的经验", "地方机制", "避开清单化总结", "余韵结尾"]
```

Humanities default:

```json
["文本或场景开场", "问题提出", "概念辨析", "解释路径", "反面限制", "当代回声", "开放式结尾"]
```

## Output Schema

```json
{
  "series_name": "穿过欧亚的路",
  "episode_no": 1,
  "episode_title": "不是一条路",
  "content_domain": "history",
  "episode_type": "history_culture",
  "recommended_writer_skill": "history-script-writer",
  "writer_selection_source": "writer_registry",
  "writer_fallback_reason": null,
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
  "domain_constraints": {
    "history": {
      "must_distinguish": ["史实", "推测", "争议观点"],
      "fact_check_focus": ["概念来源", "关键年代", "地理与政权更替"],
      "avoid": ["伪历史", "编造人物言论", "营销号历史"]
    }
  },
  "fact_check_requirements": {
    "required": false,
    "source_level": "reliable_secondary_or_primary_when_possible",
    "mark_uncertainty": true,
    "create_fact_check_file": "only_for_disputed_or_high_risk_claims",
    "focus": ["概念来源", "关键年代", "地理与政权更替"]
  },
  "avoid": ["强行悬疑", "全程史诗化", "广告腔", "短视频腔"]
}
```

## Quality Checklist

- Selected episode exists.
- `episode_brief.json` is valid JSON.
- Host persona, voice identity, and domain constraints are inherited.
- `recommended_writer_skill` comes from `skills/writer_registry.json`.
- `writer_selection_source` is `writer_registry`.
- `writer_fallback_reason` is null for a direct available writer, or explains the fallback.
- No music, sound-effect, timestamp, or final editing fields are introduced.
