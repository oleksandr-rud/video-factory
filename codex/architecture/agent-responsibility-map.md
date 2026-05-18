# Video Factory Agent Responsibility Map

This is the per-agent inventory and analysis for the current Video Factory architecture. It was derived from `AGENTS.md`, `codex/architecture/research-synthesis.md`, all `codex/agents/*/AGENT.md` files, all local agent skills, all contract schemas, local specs, and the shared Remotion app registry.

Local scan summary:

- Agents: 8
- Local agent skills: 44
- Contract schemas: 19
- Specs: 7
- Agent reference docs: 3
- Shared Remotion template contracts: 4
- Channel project artifacts currently present: none beyond `channels/.gitkeep`

## Architecture Rule

The architecture is a Director-managed production system. Production agents own bounded production responsibilities; they do not execute another production agent's skills. When an agent needs another role, it returns a handoff recommendation. The Director converts that recommendation into an `agent-handoff` artifact with inputs, allowed paths, output contract, budget policy, and definition of done.

Paid APIs, credit usage, licensed downloads, voice generation, cloud transcription/alignment, paid critique, paid Remotion templates, likeness-sensitive work, and release-gate waivers require explicit user approval before execution.

## Local Reference And Spec Inventory

Architecture and global specs:

- `AGENTS.md`: top-level operating rules, pipeline, agent folders, contracts, and base subagent instruction.
- `codex/architecture/research-synthesis.md`: research basis and architecture decision.
- `codex/specs/agent-system-integrated-spec.md`: consolidated system audit, contract map, relation model, skill gap matrix, and backlog.
- `codex/specs/project-artifact-structure-spec.md`: durable channel/project/run folder and artifact structure.
- `codex/specs/channel-intelligence-spec.md`: Channel Intelligence boundary, outputs, and evidence basis.
- `codex/specs/channel-management-spec.md`: channel folder contract and profile/project linkage.
- `codex/specs/invideo-ai-generation-spec.md`: InVideo boundary, model/prompt workflow, and generation checklist.
- `codex/specs/remotion-production-spec.md`: Remotion agent split, reusable template rules, clip/render/timeline requirements.
- `codex/specs/video-critique-spec.md`: independent critique route, review loop, gates, and QA standard.

Agent-local reference docs:

- `codex/agents/channel-intelligence/references/reference-analysis-dimensions.md`: dimensions for reference video, web/blog source, and channel format analysis.
- `codex/agents/invideo-ai-generator/references/invideo-ai-generation.md`: InVideo routes, model notes, positive prompt structure, negative prompt policy, and generation checklist.
- `codex/agents/remotion-clip-builder/references/remotion-component-stack.md`: Remotion-native stack, official templates, packages, dependency guardrails, and local template rules.
- `codex/agents/video-critic/references/video-critique-rubric.md`: final critique rubric for viewer outcome, story/source fit, visuals, audio/captions, platform/delivery, and finding severity.

Shared Remotion runtime artifacts:

- `remotion/remotion-project.json`: shared Remotion app contract.
- `remotion/src/templateRegistry.tsx`: local reusable template registry.
- `remotion/templates/vf.lower-third.minimal.v1.json`: lower-third template contract.
- `remotion/templates/vf.source-card.standard.v1.json`: source-card template contract.
- `remotion/templates/vf.caption.safe.v1.json`: safe caption template contract.
- `remotion/templates/vf.overlay.soft-vignette.v1.json`: soft vignette overlay template contract.
- `remotion/src/templates/lower-thirds/MinimalLowerThird.tsx`: lower-third implementation.
- `remotion/src/templates/source-cards/SourceCard.tsx`: source-card implementation.
- `remotion/src/templates/captions/SafeCaption.tsx`: caption implementation.
- `remotion/src/templates/overlays/SoftVignetteOverlay.tsx`: overlay implementation.

## Contract And Artifact Map

| Contract | Primary owner | Main artifact role |
|---|---|---|
| `codex/contracts/agent-handoff.schema.json` | Director | Structured handoff between Director and target agent. |
| `codex/contracts/video-project.schema.json` | Director / Channel Intelligence | Durable project index under a channel. |
| `codex/contracts/production-run.schema.json` | Director | Run ledger for phases, handoffs, approvals, blockers, changes, and review loops. |
| `codex/contracts/channel-profile.schema.json` | Channel Intelligence | Durable channel identity, brand, content, audio, governance, and project registry. |
| `codex/contracts/media-asset-manifest.schema.json` | Channel Intelligence plus media-producing agents | Canonical ledger for source, generated, rendered, subtitle, thumbnail, review, and delivery media. |
| `codex/contracts/remotion-project.schema.json` | Director / Remotion agents | Remotion app metadata, commands, dependencies, public asset policy, and composition registry. |
| `codex/contracts/remotion-template.schema.json` | Remotion Clip Builder | Reusable Remotion component/template contract. |
| `codex/contracts/producer-criteria.schema.json` | Director | Binding acceptance criteria, hard gates, style/provider/media constraints, thresholds, and revision policy. |
| `codex/contracts/reference-analysis.schema.json` | Channel Intelligence | Source/reference analysis and downstream guidance. |
| `codex/contracts/channel-format.schema.json` | Channel Intelligence | Production-ready reusable channel format package. |
| `codex/contracts/scenario.schema.json` | Creative Producer | Timed script, scene ids, scene purpose, narration, on-screen text, visual intent, and source notes. |
| `codex/contracts/voiceover-package.schema.json` | Creative Producer | Voice direction, provider selection, generation policy, audio/caption paths, and QA. |
| `codex/contracts/scene-visual-pack.schema.json` | Visual Producer | Per-scene visual routes, search/generation/Remotion briefs, constraints, and handoff recommendations. |
| `codex/contracts/clip-candidate.schema.json` | Visual Producer / InVideo / Remotion Clip Builder | Comparable visual candidate record across stock, user media, AI generation, and Remotion routes. |
| `codex/contracts/ai-video-generation-package.schema.json` | InVideo AI Generator | Model route, prompts, negative constraints, prompt guides, approval, outputs, variants, and QA. |
| `codex/contracts/remotion-clip-package.schema.json` | Remotion Clip Builder | Deterministic short clip/VFX/component package. |
| `codex/contracts/timeline-sync-plan.schema.json` | Remotion Video Producer | Frame-accurate scene, voice, caption, visual, transition, and overlay sync. |
| `codex/contracts/render-package.schema.json` | Remotion Video Producer | Render release candidate package, outputs, commands, subtitles, audio mix, QA, and known blockers. |
| `codex/contracts/critique-report.schema.json` | Video Critic | Independent review, scene gates, findings, scores, limitations, revision plan, and release decision. |

## Artifact Flow

```text
user request
  -> producer criteria
  -> channel profile / source ledger / media asset manifest
  -> reference analysis
  -> channel format
  -> scenario
  -> voiceover package
  -> scene visual pack
  -> clip candidates
  -> AI generation packages and/or Remotion clip packages
  -> timeline sync plan
  -> render package
  -> critique report
  -> production-run review loop
  -> video-project delivery state
```

The media asset manifest runs alongside the full pipeline. It should be updated whenever a source file, reference capture, generated clip, Remotion output, subtitle sidecar, thumbnail, sampled review frame, QA report, or delivery artifact becomes real.

## Director

### Goal

Own user conversation, request decomposition, producer criteria, budget/rights approvals, handoff creation, final integration, review-loop routing, release decisions, and delivery.

### Core Instructions

- Keep the user-facing conversation and final integration local.
- Create or resolve durable channel, project, run, producer criteria, media manifest, and Remotion project paths before downstream work needs them.
- Use production agents only for broad artifact production or distinct skill sets.
- Convert production-agent handoff recommendations into formal `agent-handoff` records.
- Attach `producer_criteria_path`, `channel_profile_path`, `media_asset_manifest_path`, `remotion_project_contract_path`, and template paths to handoffs when available.
- Preserve scene ids once downstream work begins.
- Stop for approval before paid APIs, generation credits, licensed downloads, paid templates, voice generation, paid critique, rights-sensitive work, or gate waivers.
- Keep final assembly conflict resolution and release-candidate approval local.

### Local Skills

- `codex/agents/director/skills/decompose-video-request/SKILL.md`
- `codex/agents/director/skills/producer-criteria-prompt/SKILL.md`
- `codex/agents/director/skills/autonomous-production-run/SKILL.md`
- `codex/agents/director/skills/quality-gated-review-loop/SKILL.md`

### Reads And References

- `AGENTS.md`
- `codex/architecture/research-synthesis.md`
- `codex/specs/agent-system-integrated-spec.md`
- `codex/specs/project-artifact-structure-spec.md`
- `codex/specs/remotion-production-spec.md`
- `codex/specs/video-critique-spec.md`
- Every target agent `AGENT.md` and only the target skill files named in each handoff.
- All current run artifacts when integrating, rerouting, or delivering.

### Owns Or Writes

- `codex/contracts/agent-handoff.schema.json`
- `codex/contracts/production-run.schema.json`
- `codex/contracts/video-project.schema.json`
- `codex/contracts/producer-criteria.schema.json`
- `codex/contracts/remotion-project.schema.json` when resolving Remotion setup.
- Final delivery notes and release-gate decisions.

### Consumes

- All downstream artifacts: channel profile, reference analysis, channel format, scenario, voiceover package, scene visual pack, clip candidates, AI generation packages, Remotion clip packages, timeline sync plan, render package, critique report, media manifest, and QA evidence.

### Runtime Paths

- `channels/<channel-slug>/channel-profile.json`
- `channels/<channel-slug>/projects/<project-slug>/project.json`
- `channels/<channel-slug>/projects/<project-slug>/production-run.json`
- `channels/<channel-slug>/projects/<project-slug>/producer-criteria.json`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`
- `remotion/remotion-project.json`
- `remotion/src/templateRegistry.tsx`
- `remotion/templates/*.json`

### Handoff Relations

- Calls Channel Intelligence for persistent channel folders, reference/source analysis, channel format, and redundancy risk.
- Calls Creative Producer after enough source/channel context exists.
- Calls Visual Producer after scenario scene ids exist.
- Calls InVideo AI Generator after Visual Producer recommends an AI generation route and approval state is clear.
- Calls Remotion Clip Builder after Visual Producer recommends deterministic Remotion clips, VFX, or templates.
- Calls Remotion Video Producer after approved visuals, clip packages, voice/captions, and Remotion setup are available.
- Calls Video Critic after a render candidate exists.

### Analysis Notes

Director is the system's control point. The main risk is missing path propagation or stale artifact invalidation, not lack of authority. The existing skills define the run loop well; the next useful improvement would be a deterministic handoff validation helper that checks required paths, skills, contracts, and budget policy before any agent runs.

## Channel Intelligence

### Goal

Own upstream channel, source, reference, and reusable format intelligence. It manages persistent channel folders, analyzes source/reference evidence, extracts style systems, creates channel format packages, and flags anti-redundancy risks before production.

### Core Instructions

- Analyze patterns and constraints; do not choose every scene clip.
- Keep reusable channel rules separate from one-off episode choices.
- Preserve evidence links, timestamps, media asset ids, source ids, and confidence notes.
- Preserve existing channel profile values unless user instructions or evidence changes them.
- Treat reference videos as inspiration and evidence, not content to copy.
- Persist contract paths as repo-relative POSIX strings.
- Record loaded source/reference media in the media asset manifest.
- Flag redundant, mass-produced, reused-content, or over-templated risks before production begins.

### Local Skills

- `codex/agents/channel-intelligence/skills/source-corpus-ingestion/SKILL.md`
- `codex/agents/channel-intelligence/skills/channel-profile-management/SKILL.md`
- `codex/agents/channel-intelligence/skills/reference-video-breakdown/SKILL.md`
- `codex/agents/channel-intelligence/skills/web-content-synthesis/SKILL.md`
- `codex/agents/channel-intelligence/skills/style-system-extraction/SKILL.md`
- `codex/agents/channel-intelligence/skills/channel-format-synthesis/SKILL.md`
- `codex/agents/channel-intelligence/skills/scenario-alignment-brief/SKILL.md`
- `codex/agents/channel-intelligence/skills/redundancy-risk-audit/SKILL.md`

### Reads And References

- `codex/agents/channel-intelligence/AGENT.md`
- `codex/agents/channel-intelligence/references/reference-analysis-dimensions.md`
- `codex/specs/channel-intelligence-spec.md`
- `codex/specs/channel-management-spec.md`
- `codex/specs/project-artifact-structure-spec.md`
- User request, Director brief, source URLs/files, reference videos, transcripts, screenshots, thumbnails, brand materials, channel data, best-practice specs, existing channel folder, existing project folder, and media manifest.

### Scripts And Tools

- `codex/agents/channel-intelligence/scripts/scaffold_channel_project.py`

### Owns Or Writes

- `codex/contracts/reference-analysis.schema.json`
- `codex/contracts/channel-profile.schema.json`
- `codex/contracts/channel-format.schema.json`
- `codex/contracts/media-asset-manifest.schema.json` for loaded source/reference media.
- `codex/contracts/video-project.schema.json` when creating or updating durable project folders.
- Source ledger files, reference analysis artifacts, scenario alignment notes, redundancy reports, and channel-format packages.

### Consumes

- `codex/contracts/scenario.schema.json` when aligning or auditing a scenario.
- `codex/contracts/producer-criteria.schema.json` when criteria are already defined.
- `codex/contracts/media-asset-manifest.schema.json` for existing source/reference assets.

### Runtime Paths

- `channels/<channel-slug>/channel-profile.json`
- `channels/<channel-slug>/brand/`
- `channels/<channel-slug>/formats/`
- `channels/<channel-slug>/references/source-ledger.json`
- `channels/<channel-slug>/references/reference-videos/`
- `channels/<channel-slug>/references/evidence/`
- `channels/<channel-slug>/rules/production-rules.md`
- `channels/<channel-slug>/rules/voice-and-tone.md`
- `channels/<channel-slug>/rules/rights-and-approvals.md`
- `channels/<channel-slug>/assets/`
- `channels/<channel-slug>/projects/<project-slug>/project.json`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

### Feeds

- Creative Producer: channel voice, source facts, reference rhythm, format rules, scenario alignment.
- Visual Producer: visual language, evidence refs, reusable template hints, source assets, anti-copy guidance.
- InVideo AI Generator and Remotion Clip Builder: indirectly through channel format, producer criteria, media manifest, and handoff inputs.
- Remotion Video Producer: channel style, template constraints, source handling rules.
- Video Critic: source evidence, channel criteria, anti-redundancy rules, and provenance expectations.

### Analysis Notes

Channel Intelligence is correctly upstream because its outputs affect script, voice, visual routes, AI prompts, Remotion styling, final timeline, and critique. Several skills remain checklist-level and should be hardened with explicit return shapes, especially source ledger fields, reference timestamp evidence, channel profile deltas, and downstream invalidation when profile rules change.

## Creative Producer

### Goal

Own pre-production creative output: scenario, scene breakdown, narration, voice direction, provider-ready voiceover package, pronunciation notes, pacing, and script-level claim notes.

### Core Instructions

- Keep every scene short enough for the target platform.
- Preserve stable scene ids across scenario, voice, TTS filenames, captions, timeline, and review.
- Tie factual claims to supplied source ids or mark them unverified.
- Use channel format rules without turning every episode into the same template.
- Inherit voice direction in this order: explicit user/Director instructions, producer criteria, scenario tone, channel profile audio identity, channel format audio system, reference evidence, provider inventory.
- Prefer one consistent voice per final video unless the script requires multiple speakers.
- Use actual provider inventory for ElevenLabs when provider access is approved.
- Do not clone or imitate a real person without explicit rights confirmation.
- Do not trigger paid TTS generation without Director approval.

### Local Skills

- `codex/agents/creative-producer/skills/write-scenario/SKILL.md`
- `codex/agents/creative-producer/skills/scene-breakdown/SKILL.md`
- `codex/agents/creative-producer/skills/voice-casting/SKILL.md`
- `codex/agents/creative-producer/skills/elevenlabs-voice-selection/SKILL.md`
- `codex/agents/creative-producer/skills/tts-production-plan/SKILL.md`

### Reads And References

- `codex/agents/creative-producer/AGENT.md`
- Director brief and producer criteria.
- `codex/contracts/channel-profile.schema.json`
- `codex/contracts/reference-analysis.schema.json`
- `codex/contracts/channel-format.schema.json`
- Source notes, anti-redundancy guidance, platform constraints, language constraints, aspect ratio, duration, brand constraints, and provider preference.

### Scripts And Tools

- `codex/agents/creative-producer/scripts/fetch_elevenlabs_voices.py`
- `codex/agents/creative-producer/scripts/rank_elevenlabs_voices.py`
- `codex/agents/creative-producer/scripts/elevenlabs_tts_with_timestamps.py`
- `codex/agents/creative-producer/scripts/elevenlabs_alignment_to_captions.py`

### Owns Or Writes

- `codex/contracts/scenario.schema.json`
- `codex/contracts/voiceover-package.schema.json`
- Voice direction brief.
- Scene breakdown with stable scene ids.
- Pronunciation, pacing, claim-check, and source-alignment notes.
- Caption JSON/SRT artifacts derived from provider timestamp alignment when TTS is approved.

### Consumes

- `codex/contracts/producer-criteria.schema.json`
- `codex/contracts/channel-profile.schema.json`
- `codex/contracts/reference-analysis.schema.json`
- `codex/contracts/channel-format.schema.json`
- `codex/contracts/media-asset-manifest.schema.json` when audio/captions are tracked.

### Runtime Paths

- `channels/<channel-slug>/projects/<project-slug>/scenario/`
- `channels/<channel-slug>/projects/<project-slug>/voiceover/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

### Feeds

- Visual Producer: scenario scenes, stable scene ids, visual intent, source ids, tone, and scene purpose.
- Remotion Video Producer: scenario timing, narration, voiceover package, audio paths, caption paths, pronunciation/timing notes.
- Video Critic: intended script, scene purpose, source claims, voice expectations, and caption/audio evidence.

### Analysis Notes

Creative Producer's strong point is scene-id preservation and voice/TTS approval gating. `scene-breakdown` and `tts-production-plan` are contract-ready. `write-scenario` and `voice-casting` are still thinner than the downstream workflow and should eventually emit structured summaries for source validation, novelty angle, inherited voice traits, rejected voice styles, and downstream invalidation.

## Visual Producer

### Goal

Own scene-level visual decisions before editing: visual pack planning, research queries, stock/provider search specs, route briefs, candidate validation, candidate ranking, primary/fallback selections, and downstream handoff recommendations.

### Core Instructions

- Decide practical scene routes: `remotion_generated`, `ai_video_generation`, `stock_clip`, or `user_supplied_media`.
- Apply channel style rules and reference evidence without copying references shot-for-shot.
- Separate "can be searched" from "can be used"; rights and technical fit must be validated.
- Keep provider, URL, prompt/query, media asset id, license summary, and technical metadata with every candidate when available.
- Prefer continuity across the whole video over a single impressive clip.
- Penalize expensive generation/licensing when a good deterministic route exists.
- Do not perform InVideo model selection, provider-ready prompt construction, generation approval, generated clip QA, Remotion component planning, or Remotion implementation.
- Return `handoff_recommendations[]` for InVideo AI Generator or Remotion Clip Builder when specialist work is needed.
- Never download paid/licensed media or execute paid generation without Director approval.

### Local Skills

- `codex/agents/visual-producer/skills/visual-pack-plan/SKILL.md`
- `codex/agents/visual-producer/skills/visual-research-queries/SKILL.md`
- `codex/agents/visual-producer/skills/provider-clip-search/SKILL.md`
- `codex/agents/visual-producer/skills/ai-video-generation-brief/SKILL.md`
- `codex/agents/visual-producer/skills/visual-validation/SKILL.md`
- `codex/agents/visual-producer/skills/clip-candidate-ranking/SKILL.md`

### Reads And References

- `codex/agents/visual-producer/AGENT.md`
- `codex/contracts/scenario.schema.json`
- `codex/contracts/reference-analysis.schema.json`
- `codex/contracts/channel-format.schema.json`
- `codex/contracts/media-asset-manifest.schema.json`
- `codex/contracts/producer-criteria.schema.json`
- Brand/style constraints, source assets, provider availability, credentials, budget policy, and license policy.

### Owns Or Writes

- `codex/contracts/scene-visual-pack.schema.json`
- `codex/contracts/clip-candidate.schema.json`
- Search query sets.
- AI generation route briefs.
- Remotion route briefs.
- Downstream handoff recommendations.
- Primary and fallback visual selections.
- License notes, validation gaps, and approval flags.

### Consumes

- `codex/contracts/scenario.schema.json`
- `codex/contracts/reference-analysis.schema.json`
- `codex/contracts/channel-format.schema.json`
- `codex/contracts/media-asset-manifest.schema.json`
- `codex/contracts/producer-criteria.schema.json`

### Runtime Paths

- `channels/<channel-slug>/projects/<project-slug>/visuals/`
- `channels/<channel-slug>/projects/<project-slug>/visuals/candidates/`
- `channels/<channel-slug>/projects/<project-slug>/source-media/provider-clips/`
- `channels/<channel-slug>/projects/<project-slug>/source-media/generated-clips/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

### Handoff Recommendations

- `invideo-ai-generator`: when route is `ai_video_generation` and model feasibility, provider prompts, approval packets, variants, generation, or generated clip QA are needed.
- `remotion-clip-builder`: when route is `remotion_generated` and a deterministic 5-20 second clip, reusable template, motion graphic, or VFX overlay is needed.

### Feeds

- InVideo AI Generator: scene route brief, visual goal, references, constraints, fallback, cost risk.
- Remotion Clip Builder: scene visual brief, template hints, Remotion route constraints, source asset needs.
- Remotion Video Producer: approved visual candidates, primary/fallback decisions, local paths, staticFile readiness, technical metadata.
- Video Critic: visual intent, selected candidates, provenance, rights state, and validation rationale.

### Analysis Notes

Visual Producer owns the critical route-selection boundary. `visual-validation` is strong and should be the model for other validation skills. Search, ranking, and provider candidate normalization remain thin; they need structured output, query provenance, tie-breakers, fallback coverage, and explicit rights/technical evidence before high-autonomy runs.

## InVideo AI Generator

### Goal

Own InVideo AI and model-backed AI video clip generation packages. It turns approved scene-level AI routes into model-ready prompts, prompt guides, negative constraints, approval packets, generation variants, generated outputs, QA, and clip candidates.

### Core Instructions

- Run only after Visual Producer selects/recommends `ai_video_generation` and Director creates a handoff.
- Do not decide whether a scene needs AI generation; Visual Producer owns route selection.
- Do not spend credits, execute paid generation, download licensed outputs, or use premium modes without Director approval.
- Keep positive prompts visual, concrete, and clip-scoped.
- Keep negative constraints separate when supported; convert them to positive constraints when the model behaves better that way.
- Use reference images, first/last frames, product images, and prompt guides when continuity matters.
- Generate variants intentionally and change one meaningful variable at a time.
- Preserve prompt version, settings, provider output ids, local paths, media asset ids, and QA provenance.

### Local Skills

- `codex/agents/invideo-ai-generator/skills/invideo-model-selection/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/ai-video-prompt-builder/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/negative-prompt-guardrails/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/generation-approval-package/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/generation-iteration-plan/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/generated-clip-qa/SKILL.md`

### Reads And References

- `codex/agents/invideo-ai-generator/AGENT.md`
- `codex/agents/invideo-ai-generator/references/invideo-ai-generation.md`
- `codex/specs/invideo-ai-generation-spec.md`
- Scene visual pack entries where AI video generation is selected.
- Scenario scene ids, durations, audience, platform, tone.
- Brand/style constraints, product URLs, reference assets, continuity requirements.
- Budget, credit policy, provider access, Director approvals.
- Project path and media asset manifest path.

### Owns Or Writes

- `codex/contracts/ai-video-generation-package.schema.json`
- `codex/contracts/clip-candidate.schema.json` for generated clips that become candidates.
- `codex/contracts/media-asset-manifest.schema.json` entries for generated/downloaded outputs, thumbnails, metadata, and QA reports when files exist.
- Approval packets with prompt, model, duration, aspect ratio, quality mode, reference assets, output count, credit/cost estimate, and approval state.

### Consumes

- `codex/contracts/scene-visual-pack.schema.json`
- `codex/contracts/scenario.schema.json`
- `codex/contracts/channel-format.schema.json`
- `codex/contracts/producer-criteria.schema.json`
- `codex/contracts/media-asset-manifest.schema.json`

### Runtime Paths

- `channels/<channel-slug>/projects/<project-slug>/source-media/generated-clips/`
- `channels/<channel-slug>/projects/<project-slug>/visuals/candidates/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

### Feeds

- Visual Producer: generated candidate QA and candidate records for ranking or reranking.
- Remotion Video Producer: approved local generated clips and editability metadata.
- Video Critic: prompts, settings, approvals, outputs, variants, provider ids, QA findings, and rights/credit records.

### Analysis Notes

This agent exists because AI generation is credit-sensitive and provider-specific. The reference doc is clear, but most skills should still be hardened with explicit required outputs: model decision object, prompt version object, negative prompt mode, cost estimate, approval state, variant plan, generated output ids, and pass/fail QA evidence aligned with Visual Producer validation.

## Remotion Clip Builder

### Goal

Own deterministic 5-20 second Remotion clips, reusable component templates, motion graphics, VFX overlays, preview evidence, and Remotion clip packages for downstream timeline assembly.

### Core Instructions

- Build standalone clips and overlays; do not own full-video assembly.
- Use the shared `remotion/` app unless Director approves a project-specific Remotion app.
- Check the local template registry and template contracts before bespoke code when reusable patterns or `template_hint` exist.
- Keep clips deterministic: fixed fps, fixed duration, typed props, stable seeds, local assets via `staticFile()` or repo paths.
- Prefer Remotion-native templates and packages over generic React/web component libraries.
- Use `useCurrentFrame()`, `useVideoConfig()`, `interpolate()`, `spring()`, `Sequence`, `Series`, and `AbsoluteFill` for frame-accurate motion.
- Mark paid templates, paid generation, or licensed asset needs as approval blockers.
- Return exact commands attempted and whether previews/renders completed.

### Local Skills

- `codex/agents/remotion-clip-builder/skills/remotion-scene-plan/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/remotion-template-library/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/remotion-stack-selection/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/remotion-ai-component-prompt/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/remotion-vfx-clip/SKILL.md`
- Built-in `remotion:remotion-best-practices` when writing or validating Remotion code.

### Reads And References

- `codex/agents/remotion-clip-builder/AGENT.md`
- `codex/agents/remotion-clip-builder/references/remotion-component-stack.md`
- `codex/specs/remotion-production-spec.md`
- `codex/contracts/remotion-project.schema.json`
- `remotion/remotion-project.json`
- `remotion/src/templateRegistry.tsx`
- `remotion/templates/*.json`
- Scene visual pack entries, scenario scene ids, visual goals, brand constraints, aspect ratio, platform, source assets, candidate requirements, fallback notes, budget/license policy.

### Owns Or Writes

- `codex/contracts/remotion-clip-package.schema.json`
- `codex/contracts/remotion-template.schema.json`
- `codex/contracts/clip-candidate.schema.json` when a Remotion clip becomes a visual candidate.
- `codex/contracts/media-asset-manifest.schema.json` entries for source/output assets, previews, rendered clips, thumbnails, and QA reports.
- Remotion component files, props, preview stills, low-resolution review clips, render commands, and template registry updates.

### Consumes

- `codex/contracts/scene-visual-pack.schema.json`
- `codex/contracts/scenario.schema.json`
- `codex/contracts/channel-format.schema.json`
- `codex/contracts/producer-criteria.schema.json`
- `codex/contracts/media-asset-manifest.schema.json`
- `codex/contracts/remotion-project.schema.json`
- `codex/contracts/remotion-template.schema.json`

### Runtime Paths

- `remotion/src/templates/`
- `remotion/src/templateRegistry.tsx`
- `remotion/templates/`
- `channels/<channel-slug>/projects/<project-slug>/remotion/clips/`
- `channels/<channel-slug>/projects/<project-slug>/remotion/props/`
- `channels/<channel-slug>/projects/<project-slug>/remotion/public-projection/`
- `channels/<channel-slug>/projects/<project-slug>/renders/previews/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

### Current Shared Templates

- `vf.lower-third.minimal.v1`: `remotion/templates/vf.lower-third.minimal.v1.json`, `TemplateLowerThirdMinimal`, lower-third labels.
- `vf.source-card.standard.v1`: `remotion/templates/vf.source-card.standard.v1.json`, `TemplateSourceCardStandard`, citation/source cards.
- `vf.caption.safe.v1`: `remotion/templates/vf.caption.safe.v1.json`, `TemplateSafeCaption`, high-contrast captions.
- `vf.overlay.soft-vignette.v1`: `remotion/templates/vf.overlay.soft-vignette.v1.json`, `TemplateSoftVignetteOverlay`, focus overlay.

### Feeds

- Visual Producer: Remotion-generated clip candidate records and validation notes when relevant.
- Remotion Video Producer: clip packages, template ids, component paths, composition ids, props, staticFile paths, render commands, previews, and QA.
- Video Critic: clip provenance, template contracts, preview evidence, and QA notes.

### Analysis Notes

Remotion Clip Builder is a justified split from full video assembly because reusable clips/templates and VFX need different validation than a 1-10 minute timeline. `remotion-stack-selection` and `remotion-template-library` are strong. `remotion-scene-plan` should be hardened into a stricter component-plan artifact with props, frame map, asset needs, preview frames, and contract fields.

## Remotion Video Producer

### Goal

Own full Remotion video assembly: timeline sync, scene sequencing, captions/subtitles, voice/music/SFX mix, post-production, render release candidates, and technical render QA.

### Core Instructions

- Own timeline integrity across the whole video.
- Consume approved visual candidates and Remotion clip packages; do not produce every short clip itself.
- Request Director handoff to Remotion Clip Builder when a new 5-20 second clip, reusable VFX, or template is needed.
- Consume template-backed clip packages through their public props/contracts; do not edit reusable template internals.
- Use the timeline sync plan as source of truth for scene frame ranges, audio placement, captions, and selected visual layers.
- Use local Remotion `public/` assets tracked by the media asset manifest.
- Do not leave final renders dependent on remote media URLs unless Director explicitly accepts the risk.
- Use lower-cost preview/still renders before expensive final renders where practical.
- Do not approve release-candidate viewer quality; Video Critic evaluates final quality and Director approves or waives gates.

### Local Skills

- `codex/agents/remotion-video-producer/skills/subtitle-caption-pipeline/SKILL.md`
- `codex/agents/remotion-video-producer/skills/timeline-sync-plan/SKILL.md`
- `codex/agents/remotion-video-producer/skills/remotion-post-production/SKILL.md`
- `codex/agents/remotion-video-producer/skills/render-release-candidate/SKILL.md`
- `codex/agents/remotion-video-producer/skills/render-qa/SKILL.md`
- Built-in `remotion:remotion-best-practices` when writing or validating Remotion code.

### Reads And References

- `codex/agents/remotion-video-producer/AGENT.md`
- `codex/specs/remotion-production-spec.md`
- `codex/contracts/remotion-project.schema.json`
- `remotion/remotion-project.json`
- Scenario artifact and scene timing.
- Voiceover package, music, SFX, captions, subtitle requirements, timestamp alignment.
- Approved visual candidates and Remotion clip packages.
- Template registry paths and template contracts.
- Brand, platform, aspect ratio, export settings, delivery variants, rights notes, budget approvals.

### Scripts And Tools

- `codex/agents/remotion-video-producer/scripts/build_timeline_sync_plan.py`

### Owns Or Writes

- `codex/contracts/timeline-sync-plan.schema.json`
- `codex/contracts/render-package.schema.json`
- Caption/subtitle artifacts.
- Timeline source files and composition ids.
- Audio mix notes.
- Preview render paths, release candidate render paths, metadata, and technical render QA report.
- `codex/contracts/media-asset-manifest.schema.json` entries for previews, release candidates, subtitles, thumbnails, and review-prep outputs.

### Consumes

- `codex/contracts/scenario.schema.json`
- `codex/contracts/voiceover-package.schema.json`
- `codex/contracts/scene-visual-pack.schema.json`
- `codex/contracts/clip-candidate.schema.json`
- `codex/contracts/ai-video-generation-package.schema.json`
- `codex/contracts/remotion-clip-package.schema.json`
- `codex/contracts/remotion-template.schema.json`
- `codex/contracts/media-asset-manifest.schema.json`
- `codex/contracts/remotion-project.schema.json`
- `codex/contracts/producer-criteria.schema.json`

### Runtime Paths

- `remotion/src/Root.tsx`
- `remotion/src/Composition.tsx`
- `channels/<channel-slug>/projects/<project-slug>/remotion/timeline/`
- `channels/<channel-slug>/projects/<project-slug>/remotion/props/`
- `channels/<channel-slug>/projects/<project-slug>/remotion/public-projection/`
- `channels/<channel-slug>/projects/<project-slug>/renders/previews/`
- `channels/<channel-slug>/projects/<project-slug>/renders/rc/`
- `channels/<channel-slug>/projects/<project-slug>/renders/final/`
- `channels/<channel-slug>/projects/<project-slug>/delivery/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

### Handoff Recommendations

- `remotion-clip-builder`: if timeline assembly reveals a missing reusable template, VFX overlay, transition clip, lower third, source card, caption component, or short deterministic clip.

### Feeds

- Video Critic: render package, final video path, timeline sync plan, subtitles, captions, output metadata, audio mix, render QA, and manifest entries.
- Director: release-candidate package and residual technical blockers.

### Analysis Notes

Remotion Video Producer's boundary is clean: it assembles and validates the full timeline but does not judge final viewer-facing quality. The main hardening needs are exact pass/fail categories for render QA, explicit RC versioning, strict manifest update rules, and complete frame-range/caption/audio coverage in the timeline sync plan.

## Video Critic

### Goal

Own independent final validation of rendered videos. It evaluates the render candidate against user request, producer criteria, scenario, source/channel evidence, visual artifacts, timeline, captions, audio, platform constraints, and final viewer experience. It returns critique and revision guidance; it never edits production artifacts directly.

### Core Instructions

- Stay independent from producing agents.
- Judge the final viewer experience first, then contract compliance.
- Apply producer criteria exactly; do not replace them with a generic rubric.
- Use evidence: timestamps, frames, captions, artifact fields, media asset ids, source ids, and concrete observations.
- Missing provenance or missing evidence is a review finding.
- Review every scene id and mark insufficient evidence as unknown or failing according to gate policy.
- Separate blocking delivery issues from taste preferences.
- Use multimodal model review only after Director approval for API spend and media handling.
- Prefer approved hybrid review when possible: direct video plus sampled frame stills, transcript/captions, timeline metadata, and artifacts.
- Do not infer spoken audio from a visual-only model; use transcript, captions, voiceover artifacts, or audio-capable provider evidence.
- Do not modify render, scenario, visual, or Remotion files.

### Local Skills

- `codex/agents/video-critic/skills/prepare-multimodal-review-package/SKILL.md`
- `codex/agents/video-critic/skills/scene-by-scene-gate-review/SKILL.md`
- `codex/agents/video-critic/skills/artifact-consistency-audit/SKILL.md`
- `codex/agents/video-critic/skills/multimodal-video-critique/SKILL.md`
- `codex/agents/video-critic/skills/revision-prioritization/SKILL.md`

### Reads And References

- `codex/agents/video-critic/AGENT.md`
- `codex/agents/video-critic/references/video-critique-rubric.md`
- `codex/specs/video-critique-spec.md`
- Render package and final video path.
- Producer criteria, quality gates, acceptance criteria, previous critique reports.
- Scenario, reference analysis, channel format, source evidence.
- Media asset manifest, Remotion project contract, review frames, and source/output provenance.
- Timeline sync plan, voiceover package, captions, subtitle artifacts.
- Visual pack, clip candidates, Remotion clip packages, AI generation packages.
- Platform, duration, aspect ratio, brand rules, rights notes, and delivery requirements.

### Scripts And Tools

- `codex/agents/video-critic/scripts/prepare_video_review_assets.py`
- `codex/agents/video-critic/scripts/run_openrouter_video_critique.py`
- `codex/agents/video-critic/scripts/run_openai_multimodal_critique.py`

### Owns Or Writes

- `codex/contracts/critique-report.schema.json`
- Multimodal review package.
- Sampled review frames and review metadata.
- Scene-by-scene gate results.
- Artifact consistency findings.
- Prioritized revision plan mapped to owning agents and affected artifacts.
- Residual risk notes for Director.

### Consumes

- `codex/contracts/render-package.schema.json`
- `codex/contracts/producer-criteria.schema.json`
- `codex/contracts/scenario.schema.json`
- `codex/contracts/reference-analysis.schema.json`
- `codex/contracts/channel-format.schema.json`
- `codex/contracts/media-asset-manifest.schema.json`
- `codex/contracts/remotion-project.schema.json`
- `codex/contracts/timeline-sync-plan.schema.json`
- `codex/contracts/voiceover-package.schema.json`
- `codex/contracts/scene-visual-pack.schema.json`
- `codex/contracts/clip-candidate.schema.json`
- `codex/contracts/remotion-clip-package.schema.json`
- `codex/contracts/ai-video-generation-package.schema.json`

### Runtime Paths

- `channels/<channel-slug>/projects/<project-slug>/reviews/assets/`
- `channels/<channel-slug>/projects/<project-slug>/reviews/evidence/`
- `channels/<channel-slug>/projects/<project-slug>/renders/rc/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

### Feeds

- Director: gate decision, blocker/major/minor findings, revision plan, owner mapping, invalidation recommendations, approval/waiver needs.
- Production agents indirectly through Director-routed revision handoffs.

### Analysis Notes

Video Critic is the independent evaluator in the evaluator-optimizer loop. It is correctly separate from production. Its skills are conceptually strong, but artifact consistency and critique outputs should be made more schema-exact: prompt archive path, raw model response path, review mode, sampled frame ids, direct-video limitations, failed gate ids, owner/rerun dependency map, and waiver recommendations.

## Cross-Agent Dependency Analysis

### Strong Boundaries

- Director owns approvals and final release decisions.
- Channel Intelligence owns reusable source/channel state, not individual clip choices.
- Creative Producer owns scenario and voice, not final visual candidates.
- Visual Producer owns route/candidate decisions, not provider-specific AI generation or Remotion implementation.
- InVideo AI Generator owns AI generation package work, not visual route selection.
- Remotion Clip Builder owns deterministic short clips/templates, not full timeline assembly.
- Remotion Video Producer owns timeline/render technical QA, not final quality approval.
- Video Critic owns review and revision guidance, not artifact edits.

### Critical Handoff Points

- Channel profile changes can invalidate channel format, producer criteria, scenario, visual plan, voice direction, Remotion styles, render, and critique.
- Scenario scene id/timing/script changes invalidate voiceover, visual pack, AI prompts, Remotion clips, timeline, render, and critique.
- Voiceover/caption/timestamp changes invalidate timeline sync, render, and critique.
- Visual candidate changes invalidate affected AI/Remotion specialist outputs, timeline, render, and critique.
- AI generation output changes invalidate clip candidates, timeline, render, and critique.
- Remotion clip/template changes invalidate clip packages, timeline, render, and critique.
- Timeline/subtitle/audio/export changes invalidate render and critique.

### Approval Gates

- Paid API calls, AI video credits, premium provider modes, paid stock/licensed media, paid Remotion templates, ElevenLabs or other paid voice/TTS generation, cloud transcription/alignment, multimodal critique APIs, likeness/voice cloning, rights-uncertain assets, and release gate waivers.

### Evidence Requirements

Every artifact that affects delivery should preserve at least one trace:

- source id
- evidence ref
- media asset id
- local path
- Remotion `staticFile()` path
- provider URL or provider asset id
- prompt/version id
- timestamp
- frame path
- QA report path
- approval id or waiver note

## Current Gaps And Recommended Hardening

1. Count drift exists in the docs: the integrated spec says 41 local skills and 18 contracts, but the current repo scan found 44 local skills and 19 contracts.
2. Several thin skills should be upgraded before reliable autonomous runs: `clip-candidate-ranking`, `provider-clip-search`, `render-qa`, `render-release-candidate`, `generated-clip-qa`, `artifact-consistency-audit`, and the thinner Channel Intelligence skills.
3. A deterministic handoff validation helper would reduce Director errors in paths, target skills, output contracts, and approval policy.
4. Every media-producing skill should either update the media asset manifest or explicitly state why no media manifest update was possible.
5. Review assets and paid model critique need reproducibility fields: prompt path, request preview path, raw response path, model, review mode, frame list, and limitations.
6. Remotion template governance is now present, but project/channel template override examples are still needed.
7. Current `channels/` has no durable project artifacts yet, so the next real production run should generate example channel profile, project, manifest, run ledger, and criteria artifacts.
