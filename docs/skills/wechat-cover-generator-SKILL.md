---
name: wechat-cover-generator
description: 当微信公众号文章、标题、选题或结构化 cover_context 需要生成封面或可直接用于生图的视觉说明时使用。
---

# 微信公众号封面生成器

## 定位

把已经定稿的文章语义转换成一张适合公众号传播的封面，不改变文章事实含义。优先用一个强主体、一个清楚动作或情绪、一个视觉隐喻完成表达，而不是把正文所有信息塞进画面。

## 核心契约

- 可以接收 `article_text`、`summary`、`title`、`topic`，也可以接收 Writer 生成的结构化 `cover_context`。
- 存在 `cover_context` 时，以其中的语义字段为准，不得把“拟议、可能、历史类比”等内容强化成确定事实。
- `factual_constraints` 和 `avoid_visuals` 是硬约束，点击力不能覆盖它们。
- 支持 `mode: auto | general | emotion_meme`，默认 `auto`。
- 有生图工具时直接生成并自检；没有生图工具时返回 `status: prompt_only` 和完整生图提示。
- 不得要求 Writer 为了“封面不够炸”去强化正文观点或标题。
- 不复刻某个具体创作者的独特画风，只使用可泛化的视觉机制：强主体、清楚情绪、明确隐喻、简单构图、小图可读。
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
4. 按 `references/prompt-contract.md` 组装最终视觉说明。
5. 有生图工具时生成封面；核心主体和动作必须落在中央方形安全区，同时适配横版使用。
6. 按 `references/quality-gates.md` 自检。最多内部重试 2 次，只改变视觉执行，不改变文章语义。
7. 返回稳定结果结构。

## 结果结构

成功生成：

```yaml
status: generated
mode: general
path: cover.png
composition:
  landscape_safe: true
  square_safe: true
```

没有生图工具：

```yaml
status: prompt_only
mode: emotion_meme
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
reason: "两次重试后仍未通过质量闸门"
fallback_prompt: "供人工或外部模型使用的完整中文提示"
composition:
  landscape_safe: true
  square_safe: true
```

`failed` 和 `prompt_only` 都不能阻塞上游文章交付。

## 必读参考

- 模式路由与视觉语言：`references/visual-modes.md`
- 生图提示与降级输出：`references/prompt-contract.md`
- 自检与重试：`references/quality-gates.md`
