# GPT-Image2 财经视觉路由

本文件把 `freestylefly/awesome-gpt-image-2` 的结构化选择思路收敛成适合财经公众号的轻量路由。不要复制整套 `cases.json`；当模板、案例 ID 或上游能力发生变化时，以 upstream 仓库为准。

## 选择顺序

每次生成先走：

1. **role**：这张图承担什么任务；
2. **category**：poster / infographic / photography / illustration；
3. **style**：realistic / poster / infographic / illustration 等；
4. **scene**：commerce / tech / education / social / story；
5. **template**：选择最接近的结构模板；
6. **example cases**：只作为构图和信息层级参考，不复刻具体作品；
7. 组装最终 Prompt blocks。

事实约束和 `avoid_visuals` 永远高于模板匹配。

## 推荐路由

### 1. 严肃财经封面

适合：政策制度、宏观分析、公司深度、行业趋势。

```yaml
category: poster
template_id: poster-layout-system
styles: [poster, realistic]
scenes: [commerce]
example_case_ids: ["345"]
```

执行重点：单一主视觉、克制背景、标题不是必须、中央安全区明确。不要堆 K 线、美元符号、交易所大楼等无信息装饰。

### 2. 强情绪市场封面

适合：暴涨暴跌、荒诞价格、强烈盈亏、市场失控感，且不涉及伤亡/灾害娱乐化。

```yaml
category: poster
template_id: poster-layout-system
styles: [poster, illustration]
scenes: [social, commerce]
example_case_ids: ["345", "355"]
```

执行重点：一个主体 + 一个动作/情绪 + 一个财经隐喻 + 极简背景。模板提供版式纪律，情绪强度仍由 `emotion_meme` 模式控制。

### 3. 机制解释图

适合：政策传导、资金流、商业模式、退出机制、利润/现金流关系。

```yaml
category: infographic
template_id: infographic-engine
styles: [infographic, charts]
scenes: [education, tech]
example_case_ids: ["334", "1", "8"]
```

执行重点：3–5 个模块、明确箭头/流向、短标签、干净留白。不要把整段正文塞进图中。

### 4. 时间线 / 历史脉络图

适合：政策演进、公司事件链、历史案例对照。

```yaml
category: infographic
template_id: infographic-engine
styles: [infographic]
scenes: [education, story]
example_case_ids: ["334"]
```

执行重点：节点少而清楚；每个节点只使用已核实日期和事实；未来或推测节点必须显式标记“拟议 / 可能 / 待确认”。

### 5. 数据解释图

适合：两到三组关键指标的对比、趋势或结构关系。

```yaml
category: infographic
template_id: infographic-engine
styles: [charts, infographic]
scenes: [commerce, education]
example_case_ids: ["334"]
```

执行重点：数据精确、单位清楚、视觉服务判断。优先真正的可复核数据图，不为了艺术感牺牲坐标、比例和标签可读性。

### 6. 概念解释视觉

适合：正文核心隐喻、抽象风险、信息折叠、流动性、挤兑、杠杆等不能用真实照片直接表达的概念。

```yaml
category: illustration
template_id: poster-layout-system
styles: [illustration, poster]
scenes: [story, commerce]
example_case_ids: ["345", "359"]
```

执行重点：明确这是解释性资产，不得让画面看起来像真实新闻摄影。

## `style_reference` 输出

每次路由都返回：

```yaml
style_reference:
  source: awesome-gpt-image-2
  category: poster
  template_id: poster-layout-system
  styles: [poster, realistic]
  scenes: [commerce]
  example_case_ids: ["345"]
  adaptation_reason: "严肃公司深度稿，适合单主体、强层级、横版安全裁切"
```

## Prompt-as-Code blocks

选定路由后，最终提示按以下块组装：

1. `task_and_role`：封面 / 机制图 / 时间线 / 概念视觉；
2. `subject`：画面主角或核心对象；
3. `composition`：主体比例、布局、信息层级、安全区；
4. `visual_style`：风格、材质、光影、背景；
5. `text_policy`：无文字 / 极少短词 / 必须准确的短标签；
6. `aspect_ratio`：横版及方形裁切要求；
7. `factual_constraints`：事实状态不能画错；
8. `negative_constraints`：禁止多主体、密集小字、无关财经装饰、假新闻现场等。

## 不做风格复刻

上游案例只用于泛化的结构、类别和提示组织参考。不要求“画得像某位具体创作者”，也不复刻具体案例的独特构图、角色或文字。
