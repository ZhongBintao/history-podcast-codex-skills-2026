---
name: podcast-episode-director
description: 内部模块：播客单集导演。Normally invoked by podcast-series-showrunner. Reads series_plan.json, selects one episode by episode_no or title, inherits style and domain constraints, and outputs episode_brief.json. Do not expose as the default user-facing entrypoint.
---

# Podcast Episode Director

Internal module. Normal users should enter through `podcast-series-showrunner`.

## Role

Convert one episode from `series_plan.json` into an executable `episode_brief.json` for downstream writing and voice production.

## Current MVP Boundary

- Do create: episode brief, recommended writer skill, narrative angle, structure, fact-check requirements, inherited host persona, inherited voice direction, and avoid rules.
- Do not create: full scripts, `narration.txt`, TTS audio, timestamps, music direction, sound-effect notes, or final mix instructions.
- Do not override the series identity unless the user explicitly asks for a creative change.

## Inputs

Require `series_plan.json` and `episode_no`. If no target episode is provided for a demo, choose episode 1 and record that default in the output.

## Workflow

1. Parse `series_plan.json`.
2. Select the requested episode from `episodes`.
3. Identify `content_domain` and choose `recommended_writer_skill`.
4. Inherit `series_name`, `target_audience`, `global_style.host_persona`, `global_style.voice_identity`, `global_style.visual_identity`, and `domain_constraints`.
5. Expand the selected episode into `core_question`, `narrative_angle`, `structure`, `content_modules`, `emotional_arc`, `voice_direction`, `fact_check_requirements`, and `avoid`.
6. Write `episode_brief.json` beside `series_plan.json` unless another output folder is specified.
7. Validate JSON.

## Writer Skill Map

- `history` -> `history-script-writer`
- `science` -> `science-script-writer`
- `humanities` -> `humanities-script-writer`
- `travel` -> `travel-script-writer`
- `business` -> `business-script-writer`
- otherwise -> `custom-script-writer`

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
    "required": true,
    "source_level": "reliable_secondary_or_primary_when_possible",
    "mark_uncertainty": true,
    "focus": ["概念来源", "关键年代", "地理与政权更替"]
  },
  "avoid": ["强行悬疑", "全程史诗化", "广告腔", "短视频腔"],
  "next_step": {
    "target_skill": "history-script-writer",
    "expected_outputs": ["script_full.md", "fact_check.md", "script_meta.json"]
  }
}
```

## Quality Checklist

- Selected episode exists.
- `episode_brief.json` is valid JSON.
- Host persona, voice identity, visual identity, and domain constraints are inherited.
- `recommended_writer_skill` matches `content_domain`.
- No music, sound-effect, timestamp, or final editing fields are introduced.
- Next step points to the writer skill.
