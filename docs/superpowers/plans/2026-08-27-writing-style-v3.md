# Writing Style v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the repository to a four-Skill workflow with a 3000–3600-character author-style layer and GPT-Image2-backed visual routing.

**Architecture:** `fin-article-writer` remains the research/fact authority and orchestration layer. New `fin-writing-style` consumes locked facts and rewrites only expression. Image placement moves from fixed H2 anchors to semantic anchors, and the cover generator uses a curated GPT-Image2 routing reference.

**Tech Stack:** Agent Skills Markdown/YAML, Python 3.11 validation script, pytest, JSON Schema.

**Spec:** `docs/superpowers/specs/2026-08-27-writing-style-v3-design.md`

## Global Constraints

- Body visible-text target is 3000–3600 characters, ideal 3200–3400; title, image markdown, captions, and source list are excluded.
- No fabricated first-hand experience; experience voice requires explicit `author_experience`.
- Style rewrites cannot alter locked facts, numbers, quotes, causal strength, or uncertainty.
- Default body has no required H2 headings.
- Final article must contain at least 3 `AUTO_INSERT` PNG body images, normally 3–5, placed by semantic anchors.
- AI-generated visuals may explain or illustrate but may not impersonate documentary/news evidence.
- Existing source, compliance, and uploader safety rules remain in force.

---

### Task 1: Update validator behavior with TDD

**Files:**
- Modify: `fin-article-writer/tests/test_validate_article_format.py`
- Modify: `fin-article-writer/scripts/validate_article_format.py`

**Interfaces:**
- Produces: `validate_article(path: Path) -> list[str]` accepting zero or more H2 headings and enforcing 3000–3600 visible body characters plus existing sentence/source rules.

- [ ] Add failing tests that accept a 3000–3600-character article without H2 headings, reject a body below 3000, reject a body above 3600, and retain source/sentence formatting checks.
- [ ] Run writer tests and confirm the new length/H2 tests fail for the expected old behavior.
- [ ] Implement visible-body character extraction excluding title/headings, image markdown, captions, separators, and source section; remove the exact-two-H2 rule; enforce 3000–3600 characters.
- [ ] Run `uv run --with pytest pytest -q fin-article-writer/tests` and confirm green.

### Task 2: Add the independent `fin-writing-style` Skill

**Files:**
- Create: `fin-writing-style/SKILL.md`
- Create: `fin-writing-style/agents/openai.yaml`
- Create: `fin-writing-style/references/style-principles.md`
- Create: `fin-writing-style/references/article-archetypes.md`
- Create: `fin-writing-style/references/first-person-voice.md`
- Create: `fin-writing-style/references/rhythm-and-narrative.md`
- Create: `fin-writing-style/references/language-patterns.md`
- Create: `fin-writing-style/references/style-examples.md`
- Create: `fin-writing-style/references/quality-gates.md`
- Create: `THIRD_PARTY_NOTICES.md`

**Interfaces:**
- Consumes: `style_context` with locked facts/numbers/quotes, counter evidence, historical context, author experience/opinions, target length, and tone settings.
- Produces: styled article body, visible character count, semantic section anchors, and internal four-layer quality status.

- [ ] Create the Skill contract with the 3000–3600 target, strict fact-lock boundary, six article archetypes, and `restrained | natural | spicy` tone routing.
- [ ] Add reference files covering generalized methods from `khazix-writer` without the named blogger identity, fixed signature, contact details, or assumed personal experiences.
- [ ] Preserve MIT attribution for adapted methodology in `THIRD_PARTY_NOTICES.md`.
- [ ] Add Agent metadata and validate Skill structure.

### Task 3: Integrate Style Skill into Writer orchestration

**Files:**
- Modify: `fin-article-writer/SKILL.md`
- Modify: `fin-article-writer/references/writing-expression.md`
- Modify: `fin-article-writer/references/editorial-standards.md`

**Interfaces:**
- Produces: explicit Step 6 call to `fin-writing-style` after facts are locked, with a defined `style_context` handoff.

- [ ] Change article length to 3000–3600 visible characters and remove required two-H2 structure.
- [ ] Define first-person truth boundaries and locked-fact handoff.
- [ ] Make Style Skill the expression step while Writer remains authoritative for facts and judgment strength.

### Task 4: Replace fixed subtitle image placement with semantic anchors

**Files:**
- Modify: `fin-article-writer/references/article-images.md`
- Modify: `fin-article-writer/references/output-contract.md`
- Modify: `fin-article-writer/references/article-package.schema.json`

**Interfaces:**
- Produces: `section_anchors[]`; image assets with `anchor_id`/`placement_anchor`; at least 3 `AUTO_INSERT` PNG images.

- [ ] Update documentation to default 3–5 body images and semantic anchor placement.
- [ ] Update schema to require at least 3 images, allow explanatory roles such as `mechanism_explainer`, and replace fixed subtitle placement enums with anchor strings.
- [ ] Keep copyright/source requirements unchanged.

### Task 5: Add GPT-Image2 visual routing

**Files:**
- Create: `wechat-cover-generator/references/gpt-image2-style-routing.md`
- Modify: `wechat-cover-generator/SKILL.md`
- Modify: `wechat-cover-generator/references/prompt-contract.md`
- Modify: `wechat-cover-generator/references/visual-modes.md`
- Modify: `fin-article-writer/references/cover-contract.md`

**Interfaces:**
- Produces: `style_reference` with source, category, template_id, styles, scenes, example_case_ids, and adaptation reason.

- [ ] Add a curated finance-focused route based on `awesome-gpt-image-2` template/category/style/scene selection rules.
- [ ] Route cover generation through semantic mode then style reference then prompt blocks.
- [ ] Keep all factual/negative constraints higher priority than visual style.

### Task 6: Documentation and repository metadata

**Files:**
- Modify: `README.md`

**Interfaces:**
- Produces: v3.0.0 documentation and four-Skill install/test commands.

- [ ] Update suite version and four-Skill table/architecture.
- [ ] Add `fin-writing-style` to install and validation commands.
- [ ] Update output image examples away from subtitle-based filenames.

### Task 7: Final verification

**Files:** none

- [ ] Run Writer pytest suite.
- [ ] Validate all four Skill directories using `skills-ref` if CI/tooling is available.
- [ ] Review the branch diff for accidental identity references (`Khazix`, `卡兹克`, fixed email/signature) in the new Style Skill; third-party attribution is the only allowed named reference.
- [ ] Verify no `1500` or exact-two-H2 production rule remains.
- [ ] Open a pull request to `main` with implementation summary and test evidence.
