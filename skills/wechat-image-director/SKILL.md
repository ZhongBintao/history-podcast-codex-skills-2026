---
name: wechat-image-director
description: Internal component for wechat-article-pipeline. Selects and downloads reliable images for structured WeChat articles generated from podcast narrations, covering history, humanities, culture, science, social science, and other knowledge topics. Writes images/ and image_manifest.json only.
metadata:
  short-description: 内部组件：文章配图与图片清单
---

# WeChat Image Director

## Purpose

Select useful, reliable, licensed images for a structured WeChat article. Images must serve comprehension, evidence, spatial orientation, comparison, or pacing.

This is an internal component. Do not create illustrated Markdown.

## Input And Output

Input:

- `.wechat-work/article.json`
- output directory

Output:

```text
<stem>-wechat/
├── image_manifest.json
└── images/
    ├── cover.<ext>
    ├── 001-<slug>.<ext>
    └── ...
```

## Manifest

Write `image_manifest.json` as a JSON array. Every item must include:

- `id`
- `type`
- `local_path`
- `caption`
- `placement`
- `source_page_url`
- `image_url`
- `source_name`
- `creator`
- `license`
- `license_status`
- `notes`

Use production wording only. Never write `封面图候选`.

## Placement Values

- `cover`
- `after_summary`
- `before_section:<section-heading>`
- `after_section:<section-heading>`
- `after_paragraph:<section-heading>:<paragraph-index>`

Paragraph index is zero-based.

## Source Strategy

Choose sources by topic:

- History/culture: Wikimedia Commons, museums, libraries, archives, archaeological institutes, universities.
- Science/popular science: NASA, NOAA, NIH, universities, research institutions, government agencies, public datasets, open-license diagrams.
- Humanities/social science: public reports, official statistics, maps, archival photos, universities, research institutes, libraries.
- Technology/nature: government agencies, research institutions, open technical diagrams, public-domain or clearly licensed images.

Avoid:

- Pinterest
- random blogs
- social media reposts
- watermarked images
- stock previews
- movie/TV screenshots
- unclear mirrors
- AI-generated images unless the user explicitly asks

Do not invent URLs, creators, licenses, or source metadata.

## Quantity

- Under 3000 Chinese characters: 3-5 images including cover.
- 3000-6000 Chinese characters: 5-8 images including cover.
- Longer: at most 8-10 images unless requested.

Do not force every section to have an image. Keep images spaced naturally.

## Failure

If a reliable image cannot be found, record a placeholder in `image_manifest.json` with `license_status: "not_found"` and useful search keywords. Do not fake metadata.
