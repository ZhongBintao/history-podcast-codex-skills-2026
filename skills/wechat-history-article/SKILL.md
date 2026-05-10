---
name: wechat-history-article
description: Internal component for the wechat-article-pipeline skill. Converts Chinese history podcast scripts into structured WeChat article objects with one final title, a summary, and sectioned body text. Prefer the public wechat-article-pipeline entrypoint for normal user requests; use this directly only when explicitly asked to work on the content-restructuring component.
metadata:
  short-description: 内部组件：播客脚本转结构化文章
---

# WeChat History Article

## Purpose

This is a lower-level production component. For normal podcast-to-WeChat work, use `wechat-article-pipeline` as the external entrypoint and let it call this component.

Convert a Chinese history podcast script into a structured WeChat article object. Preserve the source's historical facts, narrative order, viewpoint, emotional progression, and necessary personal expression, but make the result read like a restrained long-form article rather than spoken audio.

This skill is a production component. Do not create review Markdown, title-option lists, fact-check notes, or internal commentary unless the user explicitly asks for them outside the production workflow.

## Output

Return or write one structured article object:

```json
{
  "title": "可可不是甜点：古代中美洲的一杯苦味权力",
  "summary": "100-180 字摘要/导语。",
  "sections": [
    {
      "heading": "先把甜味拿掉",
      "paragraphs": ["段落一", "段落二"]
    }
  ]
}
```

When used by `wechat-article-pipeline`, write this object as `article.json` in the final output directory. This JSON is a machine intermediate artifact, not a human review Markdown file.

## Hard Requirements

- Generate exactly 1 final title.
- Do not ask the user to choose among title options.
- Do not output or save `公众号文章_第一版.md`.
- Do not output Markdown as the stage interface.
- Do not output fact-check notes, source lists, rewrite notes, internal notes, or production explanations.
- Keep the summary at about 100-180 Chinese characters.
- Keep about 70%-80% of the source information density.
- Preserve cautious wording from the source, such as `可能`, `大概`, `估计`, `有些学者`, `据称`, and `存在争议`.

## Workflow

1. Identify the source structure.
   - Map the opening hook, background, evidence, historical reconstruction, modern meaning, and ending.
   - Keep the original narrative order unless the user asks for restructuring.

2. Remove podcast-only texture.
   - Delete or compress repeated oral transitions, pauses, filler phrases, and host rhythm markers.
   - Trim phrases such as `好`, `先停一下`, `说真的`, `你想想`, repeated restatements, and excessive rhetorical prompts.
   - Keep personal expression only when it carries viewpoint or trust.

3. Build the structured object.
   - `title`: one final WeChat title, restrained and concrete.
   - `summary`: one lead paragraph, not a section heading.
   - `sections`: article-style headings and paragraph arrays.
   - Paragraphs should be short to medium, suitable for mobile reading.

4. Validate the object before handing it downstream.
   - All fields are non-empty strings.
   - `sections` is a non-empty array.
   - Each section has a non-empty `heading` and at least one paragraph.
   - No Markdown headings such as `# 公众号标题`, `# 摘要/导语`, or `# 正文` appear in the content.

## Fact Boundaries

- Do not add historical facts.
- Do not add people, events, numbers, place names, dates, institutions, documents, quotes, technical terms, psychology, dialogue, scenes, motives, or causal links absent from the source.
- Do not turn uncertainty into certainty.
- Exclude fact-check appendices, production notes, and `内部使用` style annotations from the article body.
- If a sentence cannot be supported by the source, remove it or make it no stronger than the source's own wording.

## Style

Write in Chinese unless the user asks otherwise.

Use a voice that is:

- 克制
- 清晰
- 有画面感但不煽情
- 有思辨性但不说教

Avoid marketing language, exaggerated suspense, shock-style titles, and over-arranged parallel prose. Let judgment emerge from the material.
