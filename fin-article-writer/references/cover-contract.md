# 第 9 步：封面上下文与子 Skill 交接

`fin-article-writer` 决定封面“表达什么且不能误导什么”；`wechat-cover-generator` 决定“怎么画”，并使用 `awesome-gpt-image-2` 的结构化路由思想选择视觉模板参考。Writer 不直接塞完整生图规则。

## 交接原则

- 文章、事实核查、Style 正文和主标题先定稿，再生成封面上下文。
- 封面不能反向要求正文变得更刺激。
- 历史旁例不能因为更吸睛就升级成封面主角。
- “拟、可能、征求意见”等事实状态必须在视觉上保留，不得画成已经发生。
- `style_reference` 只决定视觉结构和语言，不得覆盖 `factual_constraints` / `avoid_visuals`。

## `cover_context` 结构

机器字段保持英文，字段内容用中文：

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
  factual_constraints:
    - ""
  avoid_visuals:
    - ""
  crop_requirement:
    landscape_safe: true
    square_safe: true
```

## Writer 必须填写的事实约束

`factual_constraints` 用来告诉封面 Skill 什么不能被画错。例如：

- 不能把征求意见稿画成正式生效；
- 不能暗示所有同类产品都会退市；
- 不能把历史事件画成当前正在发生；
- 不能生成正文没有的机构关系或人物行为；
- 不能把第一人称判断画成已经确认的客观结论。

## 视觉隐喻候选

Writer 可以提供 1–3 个隐喻候选，不要锁死唯一方案。每个候选说明为什么符合文章语义。Cover Skill 从中选择最有视觉表现力且事实风险最低的方案。

## GPT-Image2 风格路由

Cover Skill 必须读取自己的 `references/gpt-image2-style-routing.md`，按 role → category → style → scene → template 生成：

```yaml
style_reference:
  source: awesome-gpt-image-2
  category: poster
  template_id: poster-layout-system
  styles: [poster, realistic]
  scenes: [commerce]
  example_case_ids: ["345"]
  adaptation_reason: ""
```

Writer 不指定固定案例 ID，只提供文章语义和事实边界。具体路由由 Cover Skill 根据 upstream 参考选择。

## 历史钩子

只有同时满足以下条件，`usable_for_cover` 才能为 `true`：

- 历史案例相关度至少 8/10；
- 正文实际使用该案例；
- 历史事件确实承担文章传播钩子；
- 封面不会让人误以为历史事件就是当前事件。

## 调用结果

封面子 Skill 返回 `generated | prompt_only | failed`，同时必须返回 `style_reference`。无论哪种结果都记录进内容包。

正文至少 3 张 PNG 配图与封面是两个独立要求，封面不能替代正文图片。
