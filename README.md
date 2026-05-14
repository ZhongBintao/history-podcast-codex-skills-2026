# History Podcast Codex Skills

这个仓库当前保留历史播客到微信公众号文章草稿的 Codex skill 工作流。

## Skills

### wechat-article-pipeline

公众号文章生产总入口。它负责将生成好的历史口播稿件、播客文章或博客文章转换为可上传微信公众号的文章工作流：

```text
口播稿件/文章
→ article.json
→ 图片选择与 image_manifest.json
→ 微信 HTML
→ 微信公众号草稿
```

默认只创建草稿，不发布、不群发。

路径：

```text
skills/wechat-article-pipeline/SKILL.md
```

内部组件：

```text
skills/wechat-history-article/SKILL.md
skills/wechat-image-director/SKILL.md
skills/wechat-html-publisher/SKILL.md
```

## 使用方式

将需要的 skill 目录复制到 Codex skills 目录中，或按 Codex 配置方式安装使用。
