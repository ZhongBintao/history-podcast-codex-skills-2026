# History Podcast Codex Skills

这个仓库收录用于历史文化播客创作与微信公众号生产发布的 Codex skills。

## Skills

### civilization-narrative-director

用于策划系列化历史播客、历史内容 IP 和多集叙事结构。它更像一个“文明叙事总导演”，负责主题解构、系列方向、单集结构、品牌系统和历史真实性约束。

路径：

```text
skills/civilization-narrative-director/SKILL.md
```

### podcast-script-generator

用于生成历史文化类单集播客脚本，目标长度约对应约 30-35 分钟播出时长。它包含主持人人格、六段式脚本结构、语言风格规范和事实核查备注。

路径：

```text
skills/podcast-script-generator/SKILL.md
```

### wechat-article-pipeline

公众号文章生产总入口。默认将播客脚本、播客文章或博客文章转换为结构化文章，自动配图，生成微信 HTML，并在配置 `WECHAT_APPID` / `WECHAT_APPSECRET` 后创建微信公众号草稿。只创建草稿，不发布、不群发。

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

将需要的 skill 目录复制到你的 Codex skills 目录中，或按你的 Codex 配置方式安装使用。
