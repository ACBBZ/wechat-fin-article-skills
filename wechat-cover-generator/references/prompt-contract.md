# 生图提示契约

本文件规定封面视觉说明的组装顺序。最终提示以中文为主，但内部先按 Prompt-as-Code blocks 组织，再汇总为可直接交给生图模型的完整提示。

## 输入前提

组装 Prompt 前必须已经有：

- `mode`：`general | emotion_meme`；
- `style_reference`：来自 `references/gpt-image2-style-routing.md`；
- 核心事件、核心判断、读者情绪；
- `factual_constraints`；
- `avoid_visuals`；
- 横版与中央方形安全区要求。

## Prompt-as-Code blocks

```yaml
prompt_blocks:
  task_and_role: "微信公众号财经文章横版封面"
  subject: ""
  composition: ""
  visual_style: ""
  text_policy: ""
  aspect_ratio: "横版，中央 1:1 安全区"
  factual_constraints: []
  negative_constraints: []
```

### 1. `task_and_role`

说明输出是封面，不是新闻照片、数据图或 UI 截图。

### 2. `subject`

只保留一个主要主体，并说明动作、表情或核心视觉关系。主体来自文章语义，不从模板案例里抄角色。

### 3. `composition`

结合 `style_reference.template_id` 和模式规则说明：主体占比、布局层级、背景复杂度、中央方形安全区、横版两侧辅助信息。

### 4. `visual_style`

使用 `style_reference.styles` / `scenes` 中的泛化风格和场景语言，说明材质、光影、写实/插画/海报属性。不得要求复刻具体创作者或具体 upstream 案例。

### 5. `text_policy`

`general` 可以 `allow_minimal`；`emotion_meme` 默认 `no_text`。出现文字时必须短、准确、可读，不重复完整文章标题。

### 6. `aspect_ratio`

默认横版公众号封面，同时中央 1:1 裁切后仍保留主体、关键动作和主要视觉关系。

### 7. `factual_constraints`

逐条保留 Writer 传入的事实状态，例如“征求意见而非正式生效”“只是可能上涨”“历史案例不能冒充当前事件”。

### 8. `negative_constraints`

至少包括：

- 不添加正文没有的人物、机构关系、政策结果；
- 不把“拟议、可能”画成“已经发生”；
- 不把历史事件冒充当前事件；
- 不生成密集小文字；
- 不用复杂多主体构图；
- 不用无关 K 线、美元符号、交易所大楼等财经装饰抢主体；
- 不把 AI 生成画面伪装成新闻现场。

## 最终提示组装顺序

1. 任务与比例；
2. 文章核心事件；
3. 核心判断与读者情绪；
4. `style_reference` 的 category / template / styles / scenes；
5. 主体；
6. 动作、表情或核心视觉关系；
7. 构图与安全区；
8. 背景、光影、材质与色彩；
9. 文字策略；
10. 事实与负面约束。

## 通用模式示例骨架

```text
为微信公众号财经文章生成一张横版封面，同时保证中央方形裁切可用。
文章核心事件：……
核心判断：……
视觉路由：poster / poster-layout-system / poster + realistic / commerce。
主体：……
画面动作或关系：……
构图：单一主视觉，主体位于中央方形安全区，横版两侧只放辅助信息。
视觉语言：……
背景：简单、低干扰。
文字：无文字或极少量中文短词，不重复文章标题。
必须避免：……
```

## 强情绪模式示例骨架

```text
为微信公众号财经文章生成强情绪、单主体的横版封面。
文章核心事件：……
核心判断：……
视觉路由：poster / poster-layout-system / poster + illustration / social + commerce。
主体占画面约 65%–90%。
主体：……
情绪或动作：……
财经隐喻：……
背景：极简。
默认无文字。
中央 1:1 裁切后仍完整看到主体、表情和关键动作。
必须避免：……
```

## 无生图工具时

返回完整中文 `prompt`、`style_reference`、模式、构图说明和 `negative_constraints`。提示必须能够直接交给其他生图模型，不要求用户再次阅读全文才能补充关键信息。

## 文件格式

有生图能力且质量通过时，最终文件路径固定为 `cover.png`。
