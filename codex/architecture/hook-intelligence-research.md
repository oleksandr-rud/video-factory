# Hook Intelligence Research

Date: 2026-05-18

## Purpose

This note analyzes how Video Factory should create and extract strong video hooks across the existing agent architecture. The conclusion is that hooks should become a first-class cross-stage production concern, not a new production agent.

A good hook is not only the first line of narration. It is the first viewer contract: the title/thumbnail or feed frame sets an expectation, the first seconds confirm the viewer is in the right place, and the opening visual/audio/text creates enough curiosity, tension, proof, or emotion to earn the next beat.

## External Evidence

### Platform And Analytics Signals

- YouTube's audience retention report treats the intro as the percentage of viewers still watching after the first 30 seconds. YouTube says a strong intro can mean the first 30 seconds matched the viewer's title/thumbnail expectation and kept interest; it recommends changing the first 30 seconds and testing different styles when intro retention is weak. Source: https://support.google.com/youtube/answer/9314415
- YouTube also says discovery uses absolute and relative watch time as engagement signals, and recommends using audience retention to understand how long viewers are willing to watch. Source: https://support.google.com/youtube/answer/141805
- Google Ads' ABCD guidance for YouTube video ads says to hook attention with an immersive story, jump into the story faster, use engaging pacing and tight framing, support the story with audio and text supers, keep visuals bright/high-contrast, brand early, and keep messages focused. Source: https://support.google.com/google-ads/answer/14783551
- Google's ABCD reference guide adds opening mechanics: surprising or unexpected visuals, tightly framed people or product at the beginning, more than two frames in the first five seconds, and people speaking directly to the viewer when people are featured. Source: https://services.google.com/fh/files/misc/youtube_google_abcd_reference_guide_en.pdf
- TikTok's current creative best-practice page says to prioritize the hook in the first six seconds, introduce the content proposition in the first three seconds, use captions/text overlays, and use transitions, stickers, and graphics to retain engagement. Source: https://ads.tiktok.com/help/article/creative-best-practices
- TikTok's Creative Codes describe the hook as the first six seconds, and identify suspense, surprise, and emotion as hook types. The same guide points to fast scene changes, music transitions, movement, and text popups as attention triggers. Source: https://ads.tiktok.com/business/library/TikTok_CreativeCodes_May2023.pdf
- Meta/Facebook's own mobile video-ad guidance says Facebook and Nielsen found up to 47% of video campaign value happens in the first three seconds and up to 74% in the first ten. It also says 65% of people who watch the first three seconds watch at least ten seconds, and 45% continue for 30 seconds. Source: https://about.fb.com/es/news/2016/02/capta-la-atencion-con-nuevas-funcionalidades-para-anuncios-de-video/

### Attention Research

- A 2026 Journal of the Academy of Marketing Science study found that short and visually simple scenes produced higher attentional synchrony; visual complexity had a delayed negative effect, while scene cuts, meaning shorter scene durations, boosted attention. Source: https://link.springer.com/article/10.1007/s11747-025-01137-x
- A 2026 arXiv paper frames the "hooking period" as the first three seconds and argues that hook analysis must be multimodal, combining visual, audio, text, and targeting features. Source: https://arxiv.org/abs/2602.22299
- Curiosity research based on information-gap theory supports hooks that reveal enough concrete information to make the gap salient, without satisfying it immediately. Practical implication: vague mystery is weak; a specific gap tied to the viewer's goal is strong. Source: https://www.cmu.edu/dietrich/sds/docs/golman/golman_loewenstein_curiosity.pdf

## Current Architecture Read

The current Director plus production-agent architecture is already close to the right shape:

- Channel Intelligence already owns reference analysis, channel format, reusable hook families, anti-redundancy, performance evidence, and visual-format extraction.
- Creative Producer already owns scenario structure, novelty angle, narration, first scene purpose, and source-grounded story promise.
- Visual Producer already owns scene-level visual goals, first practical visual routes, candidate requirements, references, source-card recreation, AI generation route briefs, Remotion route briefs, and candidate ranking.
- Video Critic already owns final viewer-experience critique against producer criteria.

The important gap is not agent count. The gap is explicit hook data. Hooks are currently implied by `reference_beats[].purpose = "hook"`, `channel_format.narrative_system.hook_patterns`, scenario scene purpose, and visual goals. That is enough for human reading, but not strong enough for autonomous extraction, variant generation, scoring, reuse prevention, or critique.

## Recommendation

Do not add a separate Hook Agent. Add a `hook_intelligence` lane across the existing artifacts and skills.

Reasoning:

- A hook depends on source truth, channel history, packaging expectation, scenario promise, visual immediacy, audio/caption behavior, and final retention/critique. No single production agent owns all of that.
- Adding a new agent would create boundary collisions with Channel Intelligence, Creative Producer, and Visual Producer.
- The current architecture already says specialist-to-specialist work crosses through the Director. Hook work should follow the same pattern: extract upstream, write creatively, plan visually, execute through existing generation/build agents, then critique.

## Hook Ownership Model

### Director

Owns the required hook criteria and approval gates:

- target hook window by platform: first 1-3 seconds for short-form feed, first 6 seconds for TikTok-style ads, first 30 seconds for YouTube long-form intros
- required hook variants, if testing is requested
- title/thumbnail/feed-frame promise alignment
- budget/rights approval before external reference downloads, paid multimodal analysis, stock downloads, or generation
- producer criteria for hook gates

### Channel Intelligence

Owns hook extraction and durable hook rules:

- extract hook beats from reference videos: first frame, first line, first on-screen text, first cut, first proof, first tension, audio onset, caption style, visual density, first payoff promise
- classify hook family: contradiction, result-first, problem-first, proof-first, cold open, stakes, myth-bust, before/after, challenge, countdown/list, expert/source reveal, transformation, demo-first, emotional shock, or curiosity gap
- record evidence: timestamp, transcript line, keyframes, OCR, title/thumbnail expectation, retention metrics when supplied, confidence, do-not-copy risks
- turn repeated evidence into channel-format hook families and anti-redundancy thresholds
- preserve hook patterns from mismatched references as visual/narrative mechanics only, not facts or subject matter

### Creative Producer

Owns the script hook:

- select the content-specific hook family based on audience, source evidence, novelty angle, platform, and channel format
- write the first line, on-screen text promise, curiosity gap, stakes, and payoff anchor
- ensure the hook is honest to the title/thumbnail and supported by later video content
- separate `must_say`, `must_show`, and flexible execution so Visual Producer can design the opening without rewriting the premise
- generate hook variants when requested, changing one variable at a time: angle, first line, proof item, emotional lever, or opening structure

### Visual Producer

Owns the visual hook plan:

- design the first frame and first 3/6/30-second visual system against the chosen script hook
- choose visual route: source-card recreation, product/UI demo, face-to-camera, stock proof, AI video generation, Remotion motion graphic, or user media
- define first-second motion, cut density, text overlay, safe areas, visual proof, and fallback route
- validate that the opening works sound-off and does not depend on unapproved web images, copied reference shots, or unclear rights
- pass route-specific hook briefs to InVideo AI Generator or Remotion Clip Builder through Director handoffs

### InVideo AI Generator

Owns model-ready AI hook clips only after Visual Producer recommends the route:

- turn the hook brief into provider/model prompt packages
- prepare variants that change one hook variable at a time
- keep generation approval, settings, negative constraints, outputs, and QA traceable

### Remotion Clip Builder

Owns deterministic hook motion assets:

- build first-frame/first-seconds overlays, source-card recreations, kinetic text, graph reveals, product/UI motion, VFX accents, or template-based hook components
- keep outputs deterministic, renderable, and reusable as local template or clip packages where appropriate

### Remotion Video Producer

Owns hook integration into the timeline:

- align hook timing to voiceover, captions, selected visual candidates, transitions, safe areas, and render specs
- make sure the first frame renders correctly, the first seconds are not blank/slow, and the opening media is present in Remotion public/static paths

### Video Critic

Owns hook gate critique:

- judge whether the first seconds match packaging expectation
- check whether the first line, first visual, and first text overlay are clear without extra context
- flag slow logos, vague intros, unsupported clickbait, over-complex frames, excessive caption density, weak payoff linkage, or repeated channel hooks
- review sampled frame stills plus video/audio when approved

## Best-Hook Extraction Workflow

Use this workflow for each reference video, source article, competitor video, previous channel upload, or current scenario:

1. Capture packaging promise: title, thumbnail/cover, first frame, description/context, platform, target audience.
2. Capture the opening window:
   - short-form: 0-1s, 1-3s, 3-6s, 6-10s
   - long-form: 0-5s, 5-15s, 15-30s
3. Extract multimodal evidence:
   - transcript first line and first complete thought
   - OCR/on-screen text
   - keyframe/frame samples
   - shot size, subject, movement, cuts, complexity
   - audio start, SFX, music, voice energy, silence
   - first proof object: chart, source, product, result, person, problem, transformation
4. Classify the hook family and the viewer job:
   - What question does this create?
   - What expectation does it confirm?
   - What payoff does it promise?
   - What viewer pain, desire, risk, contradiction, or curiosity gap is activated?
5. Score the hook:
   - packaging alignment
   - clarity/specificity
   - tension/curiosity
   - visual immediacy
   - proof/payoff linkage
   - novelty versus channel history
   - platform fit
   - rights/production viability
6. Record do-not-copy risks:
   - exact phrasing
   - proprietary footage
   - exact shot rhythm
   - likeness/brand/logos
   - page imagery or screenshots without approval
7. Convert the mechanism to target content:
   - keep the hook job and structure
   - replace facts, examples, subject matter, claims, and visuals with source-grounded target content
8. Feed downstream artifacts:
   - Channel Intelligence: reusable hook family and anti-redundancy
   - Creative Producer: script hook candidates
   - Visual Producer: first-frame and route plan
   - Video Critic: hook review criteria

## Hook Scoring Matrix

Suggested default scoring before platform-specific overrides:

| Dimension | Weight | What Good Looks Like |
|---|---:|---|
| Packaging alignment | 20 | First seconds match the title/thumbnail/feed promise without bait-and-switch. |
| Clarity and specificity | 15 | Viewer knows who this is for and why it matters immediately. |
| Curiosity or tension | 15 | The opening creates a concrete information gap, contradiction, risk, or unresolved outcome. |
| Visual immediacy | 15 | First frame/seconds show motion, proof, person/product, result, or source evidence. |
| Payoff linkage | 15 | The opening clearly points to a later answer/result, not empty shock. |
| Novelty and anti-redundancy | 10 | The pattern is not overused by this channel or too close to references. |
| Platform and sound-off fit | 10 | Timing, captions, text density, safe areas, and audio assumptions fit the platform. |

Rights, factual support, and technical viability should be hard gates, not weighted preferences.

## Hook Families By Content Type

### News, Explainers, Essays

Best hook families:

- contradiction: "Everyone is saying X. The evidence points to Y."
- missing context: "The part nobody is showing is..."
- consequence-first: "This one change affects..."
- timeline anomaly: "This started before the headline."
- source reveal: "The document/chart/data says something different."

Visual opening:

- source-card recreation, highlighted chart, date jump, map, split-screen claim versus evidence, fast evidence stack

### Product, SaaS, Commerce

Best hook families:

- result-first demo
- problem-first pain point
- before/after transformation
- objection-first: "You do not need X to get Y."
- proof-first: real metric, customer moment, product behavior

Visual opening:

- product in use, UI outcome, hands-on demo, real customer/creator, tight product framing, motion in first second

### Tutorials And How-To

Best hook families:

- final result first, then reverse-engineer
- common mistake
- "do this before you..."
- speedrun/challenge
- checklist gap

Visual opening:

- finished output, failure moment, side-by-side bad/good, step counter, tool/UI closeup

### Story, Documentary, Founder, Case Study

Best hook families:

- cold open at peak tension
- "this almost failed because..."
- unexplained anomaly
- emotional stakes
- irreversible decision

Visual opening:

- human face, urgent action, archival/source moment, dramatic before/after, key object, location cue

### Data, Reports, Research

Best hook families:

- surprising stat
- ranking inversion
- "the chart that changed the answer"
- benchmark gap
- hidden segment/audience split

Visual opening:

- animated chart reveal, highlighted outlier, big-number card, table-to-insight motion, source-card recreation

## Variant Generation Rules

Generate variants by changing one variable at a time:

- angle: pain, opportunity, contradiction, proof, identity, urgency
- first line: statement, question, challenge, source reveal, result
- first visual: face, product, chart, source card, before/after, motion graphic
- proof type: data, demo, social proof, expert/source, direct observation
- emotional lever: surprise, suspense, relief, frustration, curiosity, delight

Do not test five rewrites that all use the same first frame and same promise. For video hooks, the visual opening is usually as important as the copy.

## Proposed Contract Additions

Smallest useful change: add optional `hook_intelligence` fields to existing contracts.

### `reference-analysis.schema.json`

Add hook extraction fields:

- `hook_windows[]`: time ranges, first frame path, keyframe refs, transcript, OCR, audio notes, cut count, visual complexity notes
- `hook_mechanisms[]`: family, viewer job, curiosity gap, proof object, payoff promise, evidence refs, confidence
- `hook_do_not_copy_risks[]`

### `channel-format.schema.json`

Extend `narrative_system` and `anti_redundancy`:

- hook families by format
- platform-specific hook timing
- required hook variation dimensions
- max repeated hook family/window/promise similarity
- intro freshness triggers using retention evidence

### `producer-criteria.schema.json`

Add hook gates:

- first-frame not blank or slow
- first seconds match packaging
- hook supported by source/scenario
- first visual proof or concrete subject appears inside platform-specific window
- sound-off comprehension pass
- no copied reference hook without transformation

### `scenario.schema.json`

Add per-scene hook fields for the opening scene:

- `hook_family`
- `hook_promise`
- `curiosity_gap`
- `payoff_anchor_scene_id`
- `first_line`
- `first_onscreen_text`
- `must_show_in_hook`
- `hook_variant_id`

### `scene-visual-pack.schema.json`

Add visual hook planning fields:

- `first_frame_plan`
- `hook_window_plan`
- `first_3_seconds_visuals`
- `first_6_seconds_visuals`
- `motion_or_cut_plan`
- `sound_off_text_plan`
- `hook_proof_asset_ids`
- `hook_fallback_route`

### `critique-report.schema.json`

Add hook critique fields:

- packaging alignment
- first-frame clarity
- first-3/6/30-second hold risk
- sound-off comprehension
- proof/payoff linkage
- redundancy risk
- source/rights risk

If these optional blocks grow too large after real runs, promote them into a dedicated `hook-package.schema.json`. Do that only after the smaller embedded-block approach proves insufficient.

## Skill Updates To Apply Later

1. `channel-intelligence/skills/reference-video-breakdown`: explicitly extract `hook_windows[]` and `hook_mechanisms[]`.
2. `channel-intelligence/skills/web-content-synthesis`: extract source-backed hook opportunities from claims, visuals, contradictions, dates, charts, and quotes.
3. `channel-intelligence/skills/channel-format-synthesis`: turn strong hook mechanisms into channel hook families, variation rules, and freshness triggers.
4. `creative-producer/skills/write-scenario`: require hook candidate selection, payoff anchor, and first-line/on-screen-text variants.
5. `creative-producer/skills/scene-breakdown`: preserve opening hook fields and report invalidation when the first scene changes.
6. `visual-producer/skills/visual-pack-plan`: add first-frame and first-window visual planning as a required part of scene 1.
7. `visual-producer/skills/visual-validation`: validate opening candidates for first-frame clarity, sound-off comprehension, rights, and technical fit.
8. `visual-producer/skills/clip-candidate-ranking`: increase semantic/continuity weight for opening scene candidates, or add a hook-specific tie breaker.
9. `video-critic/references/video-critique-rubric`: add hook gates for first-frame, first-window, packaging match, and payoff linkage.

## Implementation Order

1. Update schemas with optional hook fields. Keep backward compatibility.
2. Update Channel Intelligence extraction skills first so downstream agents receive hook evidence instead of guessing.
3. Update Creative Producer scenario writing to choose and justify hook candidates.
4. Update Visual Producer planning and validation to design the visual hook.
5. Update Producer Criteria and Video Critic so hooks become release gates.
6. Add an example fixture showing one complete hook-intelligence path from reference to scenario to visual pack to critique.

## Bottom Line

Yes, the hook system should be used in visual analysis, creative production, and visual production. The right architecture is:

```text
Channel Intelligence extracts hook mechanisms
  -> Creative Producer chooses the truthful content hook
  -> Visual Producer designs the first-frame/first-window visual proof
  -> InVideo or Remotion produces variants when needed
  -> Remotion Video Producer integrates timing
  -> Video Critic judges the opening against hook gates
  -> Director preserves metrics and routes revisions
```

This keeps the existing agent boundaries intact while making hooks measurable, reusable, testable, and reviewable.
