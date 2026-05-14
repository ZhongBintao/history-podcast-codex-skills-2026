---
name: wechat-narration-article
description: Internal component for wechat-article-pipeline. Converts a completed Chinese podcast narration, usually narration.txt, into a structured WeChat article object with one title, summary, and sectioned body. Use directly only when explicitly working on the narration-to-article component.
metadata:
  short-description: 内部组件：口播稿转结构化文章
---

# WeChat Narration Article Component

## Purpose

Convert a finished podcast narration into a structured WeChat article object. The input can cover history, humanities, culture, science, social science, or other knowledge topics.

This is an internal component. Normal users should call `wechat-article-pipeline`.

## Output

Return or write this JSON object to `.wechat-work/article.json`:

```json
{
  "title": "一个最终标题",
  "summary": "100-180 字摘要/导语。",
  "sections": [
    {
      "heading": "小标题",
      "paragraphs": ["段落一", "段落二"]
    }
  ]
}
```

## Rules

- Generate exactly one title.
- Do not produce Markdown.
- Do not produce title options, rewrite notes, fact-check notes, source lists, or internal commentary.
- Preserve the narration's facts, logic, viewpoint, tone, emotional progression, and necessary personal expression.
- Remove口播-only repetition, filler transitions, recording/TTS artifacts, and excessive rhythm words.
- Keep about 70%-85% of the source information density unless the user asks otherwise.
- Do not add facts, numbers, people, concepts, sources, quotes, scenes, psychology, or causal claims absent from the narration.
- Preserve uncertainty markers such as `可能`, `大概`, `估计`, `有些学者`, `据称`, and `存在争议`.

## Domain Handling

- History/culture: preserve chronology, evidence, uncertainty, and narrative progression.
- Humanities/social science: preserve argument structure, conceptual distinctions, and nuance.
- Science/popular science: preserve concept order, definitions, mechanisms, and limits of certainty.
- Commentary: preserve viewpoint boundaries and avoid turning opinion into fact.

## Style

Write in Chinese unless the user asks otherwise.

Use a restrained public-account article voice:

- clear
- readable on mobile
- article-like rather than spoken
- concrete but not sensational
- thoughtful but not preachy

Paragraphs should be short to medium. Section headings should guide reading, not sound like production notes.
