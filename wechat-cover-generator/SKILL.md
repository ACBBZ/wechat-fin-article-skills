---
name: wechat-cover-generator
description: 当微信公众号文章、标题、选题或结构化 cover_context 需要生成封面或可直接用于生图的视觉说明时使用。使用财经语义模式与 GPT-Image2 风格路由，把文章事实转成可控、可复用的封面 Prompt。
---

# 微信公众号封面生成器

## 定位

把已经定稿的文章语义转换成一张适合公众号传播的封面，不改变文章事实含义。先决定封面表达什么，再根据 `awesome-gpt-image-2` 的 Prompt-as-Code 思路选择 category / style / scene / template，最后组装生图提示。

## 核心契约

- 可以接收 `article_text`、`summary`、`title`、`topic`，也可以接收 Writer 生成的结构化 `cover_context`。
- 存在 `cover_context` 时，以其中的语义字段为准，不得把“拟议、可能、历史类比”等内容强化成确定事实。
- `factual_constraints` 和 `avoid_visuals` 是硬约束，点击力和模板匹配不能覆盖它们。
- 支持 `mode: auto | general | emotion_meme`，默认 `auto`。
- 每次都必须读取 `references/gpt-image2-style-routing.md` 并返回 `style_reference`。
- 有生图工具时直接生成并自检；没有生图工具时返回 `status: prompt_only` 和完整生图提示。
- 不得要求 Writer 为了“封面不够炸”去强化正文观点或标题。
- 不复刻某个具体创作者的独特画风或上游案例；只使用可泛化的模板结构、信息层级、风格标签和场景机制。
- 成功生成的封面文件统一为 **`cover.png`**。

## 输入

直接输入可以包含：

```yaml
article_text: ""
summary: ""
title: ""
topic: ""
mode: auto
```

推荐由上游传入：

```yaml
cover_context:
  final_title: ""
  article_topic: ""
  core_event: ""
  core_judgment: ""
  reader_stake: ""
  reader_emotion: ""
  click_hook: ""
  historical_hook:
    text: ""
    usable_for_cover: false
  visual_metaphor_candidates:
    - metaphor: ""
      reason: ""
  recommended_mode:
    value: general
    reason: ""
  text_policy:
    value: allow_minimal
  factual_constraints: []
  avoid_visuals: []
  crop_requirement:
    landscape_safe: true
    square_safe: true
```

直接输入时只能从现有文字中推断，不确定的语义在内部标记，不得补写具体人物、机构关系或事件结果。

## 执行流程

1. 把输入规范化为：核心事件、核心判断、读者情绪、点击钩子和 1–3 个视觉隐喻候选。
2. 根据 `references/visual-modes.md` 选择 `general` 或 `emotion_meme`。用户显式指定的支持模式优先，但不能违反事实安全。
3. 保留全部事实约束、禁用视觉和历史使用限制。
4. 读取 `references/gpt-image2-style-routing.md`，按 role → category → style → scene → template 选择最合适的财经视觉方向，生成 `style_reference`。
5. 按 `references/prompt-contract.md` 把语义与 `style_reference` 组装成 Prompt-as-Code blocks，再汇总成最终完整中文提示。
6. 有生图工具时生成封面；核心主体和动作必须落在中央方形安全区，同时适配横版使用。
7. 按 `references/quality-gates.md` 自检。最多内部重试 2 次，只改变视觉执行，不改变文章语义、事实锁或 `style_reference` 的事实边界。
8. 返回稳定结果结构。

## `style_reference`

示例：

```yaml
style_reference:
  source: awesome-gpt-image-2
  category: poster
  template_id: poster-layout-system
  styles: [poster, realistic]
  scenes: [commerce]
  example_case_ids: ["345"]
  adaptation_reason: "严肃财经深度稿，适合单主体和清楚视觉层级"
```

上游模板 ID 和案例只作为结构参考；如果具体案例不可用，仍保留匹配到的通用 template/category/style/scene 逻辑，不凭记忆发明新的 upstream ID。

## 结果结构

成功生成：

```yaml
status: generated
mode: general
path: cover.png
style_reference:
  source: awesome-gpt-image-2
  category: poster
  template_id: poster-layout-system
composition:
  landscape_safe: true
  square_safe: true
```

没有生图工具：

```yaml
status: prompt_only
mode: emotion_meme
style_reference:
  source: awesome-gpt-image-2
  category: poster
  template_id: poster-layout-system
prompt: "可直接使用的完整中文生图提示"
composition:
  landscape_safe: true
  square_safe: true
negative_constraints:
  - "事实或视觉硬约束"
```

两次重试后仍不合格：

```yaml
status: failed
mode: general
style_reference:
  source: awesome-gpt-image-2
  category: poster
  template_id: poster-layout-system
reason: "两次重试后仍未通过质量闸门"
fallback_prompt: "供人工或外部模型使用的完整中文提示"
composition:
  landscape_safe: true
  square_safe: true
```

`failed` 和 `prompt_only` 都不能阻塞上游文章交付。

## 必读参考

- 模式路由与视觉语言：`references/visual-modes.md`
- GPT-Image2 财经风格路由：`references/gpt-image2-style-routing.md`
- 生图提示与降级输出：`references/prompt-contract.md`
- 自检与重试：`references/quality-gates.md`
