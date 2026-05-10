---
name: wechat-image-director
description: Internal component for the wechat-article-pipeline skill. Finds, selects, downloads, and places reliable images for structured WeChat history article objects, creating local image files plus image_manifest.json. Prefer the public wechat-article-pipeline entrypoint for normal user requests; use this directly only when explicitly asked to work on the image-director component.
metadata:
  short-description: 内部组件：文章配图与图片清单
---

# WeChat Image Director

## Purpose

This is a lower-level production component. For normal podcast-to-WeChat work, use `wechat-article-pipeline` as the external entrypoint and let it call this component.

Act as the visual editor for a structured history or culture article. Select images that clarify meaning, evidence, space, objects, comparison, or pacing; download reliable local image files; and write `image_manifest.json`.

This is a production workflow. Do not create `article_with_images.md`, do not insert Markdown image syntax, and do not write review language such as `封面图候选`.

## Input

- Structured article object from `wechat-history-article`, usually `article.json`.
- Output directory, usually `<article-stem>-wechat/`.

The article object shape:

```json
{
  "title": "文章标题",
  "summary": "摘要/导语",
  "sections": [
    {"heading": "小标题", "paragraphs": ["段落"]}
  ]
}
```

## Output

Create or update:

```text
<article-stem>-wechat/
├── image_manifest.json
└── images/
    ├── cover.<ext>
    ├── 001-<slug>.<ext>
    └── ...
```

`image_manifest.json` is the only stage output besides image files.

## Manifest Format

Write a JSON array. Include one object per image or unresolved placeholder:

```json
[
  {
    "id": "cover",
    "type": "cover",
    "local_path": "/absolute/path/to/images/cover.jpg",
    "caption": "封面图：玉米与类蜀黍的形态对比。",
    "placement": "cover",
    "source_page_url": "https://commons.wikimedia.org/...",
    "image_url": "https://upload.wikimedia.org/...",
    "source_name": "Wikimedia Commons",
    "creator": "Unknown",
    "license": "CC BY-SA 4.0",
    "license_status": "clear",
    "search_keywords": ["maize teosinte comparison", "玉米 类蜀黍 对比"],
    "notes": "用于封面图。"
  }
]
```

For placeholders, set `local_path` and `image_url` to `null`, set `license_status` to `not_found`, include `suggested_image`, `search_keywords`, and a production-safe `placement`.

## Placement Values

Use these values so the HTML publisher can render images deterministically:

- `cover`
- `after_summary`
- `before_section:<section-heading>`
- `after_section:<section-heading>`
- `after_paragraph:<section-heading>:<paragraph-index>`

Paragraph index is zero-based within the section's `paragraphs` array.

## Workflow

1. Read the structured article.
   - Identify title, summary, sections, major narrative turns, evidence points, spatial references, and object/ritual/material details.
   - Do not rewrite article text.

2. Choose image functions.
   - Always attempt 1 cover image.
   - Strongly consider 1 opening main visual after the summary.
   - Add images only when they improve comprehension, evidence, contrast, or pacing.

3. Search reliable sources.
   - Search in Chinese and English when useful.
   - Prefer Wikimedia Commons, museum official websites, universities, research institutions, governments, libraries, archives, archaeological institutions, and public-domain or clearly licensed collections.
   - Avoid Pinterest, random blogs, social media reposts, watermarked images, commercial stock previews, movie/TV screenshots, AI-generated images, and unclear mirrors.

4. Verify each image.
   - Open the source page when possible.
   - Confirm the image depicts the intended subject.
   - Record source page URL, image URL, source name, creator, license, and license status.
   - Do not invent URLs, licenses, creators, institutions, or file metadata.

5. Download images.
   - Save under `images/`.
   - Use stable ASCII filenames: `cover.jpg`, `001-tenochtitlan-map.jpg`.
   - Prefer `.jpg`, `.jpeg`, `.png`, or `.webp`.
   - Keep files practical for article use.

6. Write `image_manifest.json`.
   - Use absolute `local_path` values.
   - Include `placement` for every image.
   - Use production wording only: `封面图：...` or direct factual captions.
   - Never write `封面图候选`.

## Image Types

- `cover`: readable thumbnail communicating the theme.
- `opening-main-visual`: establishes the core scene or object.
- `spatial-or-map`: explains geography, routes, cities, regions, or movement.
- `structure-explainer`: explains buildings, infrastructure, objects, biological form, production, or technical systems.
- `evidence`: shows sites, excavated objects, manuscripts, inscriptions, codices, archival documents, or museum holdings.
- `comparison`: makes a core contrast visible.
- `daily-life`: supports ordinary work, food, ritual, craft, farming, transport, or domestic life.
- `closing`: quiet final visual when it strengthens the ending.

## Quantity

- Under 3000 Chinese characters: 3-5 images including cover.
- 3000-6000 Chinese characters: 5-8 images including cover.
- Longer articles: at most 8-10 images unless the user asks for more.
- Do not force every section to have an image.
- Usually leave 3-5 natural paragraphs between inline images.

## Failure And Degradation

If internet search, verification, or download fails:

- Do not fake metadata.
- Record a placeholder entry in `image_manifest.json`.
- Tell the caller which images need manual search.
- Continue so the HTML stage can render the article with available images.
