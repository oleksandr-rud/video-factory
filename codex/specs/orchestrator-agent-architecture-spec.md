# Orchestrator Agent Architecture Spec

## Purpose

This is the short operating spec for the Video Factory agent system. It lists each agent's role, local skills, owned file patterns, exchanged contracts, current real artifacts, and the Director orchestration logic that turns user requests into durable production runs.

Read this alongside:

- `AGENTS.md`
- `codex/architecture/research-synthesis.md`
- `codex/architecture/agent-responsibility-map.md`
- `codex/specs/project-artifact-structure-spec.md`
- `codex/specs/agent-system-integrated-spec.md`

## System Shape

Video Factory uses a Director plus seven bounded specialist agents:

```text
User
  -> Director
  -> Channel Intelligence
  -> Creative Producer
  -> Visual Producer
  -> InVideo AI Generator and/or Remotion Clip Builder
  -> Remotion Video Producer
  -> Video Critic
  -> Director delivery or revision loop
```

The Director is the only orchestrator. Specialist agents do not call other specialist skills. If a specialist sees work that belongs to another role, it returns a handoff recommendation. The Director converts that recommendation into a formal `agent-handoff` artifact.

## Global Folder Pattern

```text
codex/
  agents/<agent>/AGENT.md
  agents/<agent>/skills/<skill-name>/SKILL.md
  agents/<agent>/skills/<skill-name>/scripts/
  agents/<agent>/scripts/
  agents/<agent>/references/
  architecture/
  contracts/
  examples/
  scripts/
  specs/
channels/
  <channel-slug>/
    channel-profile.json
    formats/
    references/
    rules/
    assets/
    projects/<project-slug>/
      project.json
      production-run.json
      producer-criteria.json
      media-asset-manifest.json
      scenario/
      voiceover/
      visuals/
      source-media/
      remotion/
      renders/
      reviews/
      runs/<run-id>/context/
      delivery/
remotion/
  remotion-project.json
  src/
  templates/
  public/channels/<channel-slug>/projects/<project-slug>/
  out/
```

Path values persisted in contracts use repo-relative POSIX strings, for example `channels/demo/projects/intro/project.json`. Tools can resolve absolute Windows paths only at execution time.

## Agent Specs

### Director

Role: owns user conversation, decomposition, project/run setup, approvals, producer criteria, handoffs, state compaction, review-loop routing, final integration, and delivery.

Local skills:

- `codex/agents/director/skills/decompose-video-request/SKILL.md`
- `codex/agents/director/skills/producer-criteria-prompt/SKILL.md`
- `codex/agents/director/skills/autonomous-production-run/SKILL.md`
- `codex/agents/director/skills/context-compaction/SKILL.md`
- `codex/agents/director/skills/quality-gated-review-loop/SKILL.md`

Writes or updates:

- `channels/<channel-slug>/projects/<project-slug>/production-run.json`
- `channels/<channel-slug>/projects/<project-slug>/project.json`
- `channels/<channel-slug>/projects/<project-slug>/producer-criteria.json`
- `channels/<channel-slug>/projects/<project-slug>/runs/<run-id>/context/context-snapshot-<timestamp>.json`
- `codex/contracts/agent-handoff.schema.json` shaped handoff files when persisted

Consumes all downstream artifacts and makes the final release or waiver decision.

### Channel Intelligence

Role: owns persistent channel state, source/reference ingestion, reference video and web content analysis, channel format synthesis, style-system extraction, scenario alignment notes, and redundancy-risk audits.

Local skills:

- `codex/agents/channel-intelligence/skills/source-corpus-ingestion/SKILL.md`
- `codex/agents/channel-intelligence/skills/channel-profile-management/SKILL.md`
- `codex/agents/channel-intelligence/skills/reference-video-breakdown/SKILL.md`
- `codex/agents/channel-intelligence/skills/web-content-synthesis/SKILL.md`
- `codex/agents/channel-intelligence/skills/style-system-extraction/SKILL.md`
- `codex/agents/channel-intelligence/skills/channel-format-synthesis/SKILL.md`
- `codex/agents/channel-intelligence/skills/scenario-alignment-brief/SKILL.md`
- `codex/agents/channel-intelligence/skills/redundancy-risk-audit/SKILL.md`

Helpers and references:

- `codex/agents/channel-intelligence/scripts/scaffold_channel_project.py`
- `codex/agents/channel-intelligence/scripts/parse_web_content.py`
- `codex/agents/channel-intelligence/scripts/analyze_reference_video.py`
- `codex/agents/channel-intelligence/references/reference-analysis-dimensions.md`

Writes or updates:

- `channels/<channel-slug>/channel-profile.json`
- `channels/<channel-slug>/formats/<format-id>.json`
- `channels/<channel-slug>/references/source-ledger.json`
- `channels/<channel-slug>/projects/<project-slug>/project.json`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`
- `channels/<channel-slug>/projects/<project-slug>/source-media/reference-videos/<source-id>/`
- `channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/<source-id>/`
- `channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/`

Primary contracts: `channel-profile`, `video-project`, `media-asset-manifest`, `reference-analysis`, `channel-format`.

### Creative Producer

Role: owns scenario, scene breakdown, narration, voice direction, provider voice selection plan, TTS plan, pronunciation notes, pacing notes, and script-level claim notes.

Local skills:

- `codex/agents/creative-producer/skills/write-scenario/SKILL.md`
- `codex/agents/creative-producer/skills/scene-breakdown/SKILL.md`
- `codex/agents/creative-producer/skills/voice-casting/SKILL.md`
- `codex/agents/creative-producer/skills/elevenlabs-voice-selection/SKILL.md`
- `codex/agents/creative-producer/skills/tts-production-plan/SKILL.md`

Helpers:

- `codex/agents/creative-producer/scripts/fetch_elevenlabs_voices.py`
- `codex/agents/creative-producer/scripts/rank_elevenlabs_voices.py`
- `codex/agents/creative-producer/scripts/elevenlabs_tts_with_timestamps.py`
- `codex/agents/creative-producer/scripts/elevenlabs_alignment_to_captions.py`

Writes or updates:

- `channels/<channel-slug>/projects/<project-slug>/scenario/`
- `channels/<channel-slug>/projects/<project-slug>/voiceover/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json` when audio, captions, or alignment files exist

Primary contracts: `scenario`, `voiceover-package`.

### Visual Producer

Role: owns visual route planning, scene visual packs, search query planning, provider search, candidate validation, candidate ranking, primary/fallback visual selections, and downstream handoff recommendations.

Local skills:

- `codex/agents/visual-producer/skills/visual-pack-plan/SKILL.md`
- `codex/agents/visual-producer/skills/visual-research-queries/SKILL.md`
- `codex/agents/visual-producer/skills/provider-clip-search/SKILL.md`
- `codex/agents/visual-producer/skills/freepik-video-search/SKILL.md`
- `codex/agents/visual-producer/skills/pexels-video-search/SKILL.md`
- `codex/agents/visual-producer/skills/ai-video-generation-brief/SKILL.md`
- `codex/agents/visual-producer/skills/visual-validation/SKILL.md`
- `codex/agents/visual-producer/skills/clip-candidate-ranking/SKILL.md`

Helpers and references:

- `codex/agents/visual-producer/references/video-search-providers.md`
- `codex/agents/visual-producer/skills/freepik-video-search/scripts/search_freepik_videos.py`
- `codex/agents/visual-producer/skills/pexels-video-search/scripts/search_pexels_videos.py`

Writes or updates:

- `channels/<channel-slug>/projects/<project-slug>/visuals/`
- `channels/<channel-slug>/projects/<project-slug>/visuals/candidates/search-results/<provider>/`
- `channels/<channel-slug>/projects/<project-slug>/visuals/candidates/<scene-id>/`
- `channels/<channel-slug>/projects/<project-slug>/source-media/provider-clips/<provider>/` only after approval
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json` when downloaded media exists

Primary contracts: `scene-visual-pack`, `clip-candidate`, `media-asset-manifest`.

### InVideo AI Generator

Role: owns provider/model AI generation packages, prompt guides, prompt construction, negative prompt handling, approval packets, bounded variant plans, generated outputs, and generated clip QA.

Local skills:

- `codex/agents/invideo-ai-generator/skills/invideo-model-selection/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/ai-video-prompt-builder/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/negative-prompt-guardrails/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/generation-approval-package/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/generation-iteration-plan/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/generated-clip-qa/SKILL.md`

Reference:

- `codex/agents/invideo-ai-generator/references/invideo-ai-generation.md`

Writes or updates:

- `channels/<channel-slug>/projects/<project-slug>/source-media/generated-clips/`
- `channels/<channel-slug>/projects/<project-slug>/visuals/candidates/<scene-id>/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

Primary contracts: `ai-video-generation-package`, `clip-candidate`, `media-asset-manifest`.

### Remotion Clip Builder

Role: owns deterministic 5-20 second Remotion clips, reusable templates, source-card recreations, motion graphics, VFX overlays, clip packages, and clip-level QA.

Local skills:

- `codex/agents/remotion-clip-builder/skills/remotion-scene-plan/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/remotion-template-library/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/remotion-stack-selection/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/remotion-ai-component-prompt/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/remotion-vfx-clip/SKILL.md`
- `codex/agents/remotion-clip-builder/skills/vfx-quality-performance-hardening/SKILL.md`
- built-in `remotion:remotion-best-practices` when writing Remotion code

Reference:

- `codex/agents/remotion-clip-builder/references/remotion-component-stack.md`

Writes or updates:

- `remotion/src/templates/`
- `remotion/src/templateRegistry.tsx`
- `remotion/templates/*.json`
- `channels/<channel-slug>/projects/<project-slug>/remotion/clips/`
- `channels/<channel-slug>/projects/<project-slug>/remotion/props/`
- `channels/<channel-slug>/projects/<project-slug>/renders/previews/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

Primary contracts: `remotion-template`, `remotion-clip-package`, `clip-candidate`, `media-asset-manifest`.

### Remotion Video Producer

Role: owns full-video assembly, timeline sync, captions/subtitles, audio mix, post-production, preview renders, render release candidates, and technical render QA.

Local skills:

- `codex/agents/remotion-video-producer/skills/subtitle-caption-pipeline/SKILL.md`
- `codex/agents/remotion-video-producer/skills/timeline-sync-plan/SKILL.md`
- `codex/agents/remotion-video-producer/skills/remotion-post-production/SKILL.md`
- `codex/agents/remotion-video-producer/skills/render-release-candidate/SKILL.md`
- `codex/agents/remotion-video-producer/skills/render-qa/SKILL.md`
- built-in `remotion:remotion-best-practices` when writing Remotion code

Helper:

- `codex/agents/remotion-video-producer/scripts/build_timeline_sync_plan.py`

Writes or updates:

- `remotion/src/Root.tsx`
- `remotion/src/Composition.tsx`
- `channels/<channel-slug>/projects/<project-slug>/remotion/timeline/`
- `channels/<channel-slug>/projects/<project-slug>/remotion/props/`
- `channels/<channel-slug>/projects/<project-slug>/renders/previews/`
- `channels/<channel-slug>/projects/<project-slug>/renders/rc/`
- `channels/<channel-slug>/projects/<project-slug>/renders/final/`
- `channels/<channel-slug>/projects/<project-slug>/delivery/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`

Primary contracts: `timeline-sync-plan`, `render-package`, `media-asset-manifest`.

### Video Critic

Role: owns independent final review. It evaluates rendered videos against producer criteria, scenario, source/channel evidence, timeline, captions, audio, visual provenance, platform constraints, and viewer experience. It returns critique and revision guidance; it never edits production artifacts.

Local skills:

- `codex/agents/video-critic/skills/prepare-multimodal-review-package/SKILL.md`
- `codex/agents/video-critic/skills/scene-by-scene-gate-review/SKILL.md`
- `codex/agents/video-critic/skills/artifact-consistency-audit/SKILL.md`
- `codex/agents/video-critic/skills/multimodal-video-critique/SKILL.md`
- `codex/agents/video-critic/skills/revision-prioritization/SKILL.md`

Helpers and references:

- `codex/agents/video-critic/references/video-critique-rubric.md`
- `codex/agents/video-critic/scripts/prepare_video_review_assets.py`
- `codex/agents/video-critic/scripts/run_openrouter_video_critique.py`
- `codex/agents/video-critic/scripts/run_openai_multimodal_critique.py`

Writes or updates:

- `channels/<channel-slug>/projects/<project-slug>/reviews/assets/`
- `channels/<channel-slug>/projects/<project-slug>/reviews/evidence/`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json` for review frames/assets
- critique report artifacts under the project review area

Primary contract: `critique-report`.

## Contract Map

| Contract path | Primary owner | Runtime artifact path |
|---|---|---|
| `codex/contracts/agent-handoff.schema.json` | Director | `channels/<channel-slug>/projects/<project-slug>/runs/<run-id>/handoffs/<handoff-id>.json` when persisted |
| `codex/contracts/video-project.schema.json` | Director / Channel Intelligence | `channels/<channel-slug>/projects/<project-slug>/project.json` |
| `codex/contracts/production-run.schema.json` | Director | `channels/<channel-slug>/projects/<project-slug>/production-run.json` |
| `codex/contracts/channel-profile.schema.json` | Channel Intelligence | `channels/<channel-slug>/channel-profile.json` |
| `codex/contracts/media-asset-manifest.schema.json` | Channel Intelligence plus media-producing agents | `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json` |
| `codex/contracts/remotion-project.schema.json` | Director / Remotion agents | `remotion/remotion-project.json` or project-specific `channels/<channel-slug>/projects/<project-slug>/remotion/remotion-project.json` |
| `codex/contracts/remotion-template.schema.json` | Remotion Clip Builder | `remotion/templates/<template-id>.json` or project-specific `channels/<channel-slug>/projects/<project-slug>/remotion/templates/<template-id>.json` |
| `codex/contracts/producer-criteria.schema.json` | Director | `channels/<channel-slug>/projects/<project-slug>/producer-criteria.json` |
| `codex/contracts/reference-analysis.schema.json` | Channel Intelligence | `channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/reference-analysis.json` |
| `codex/contracts/channel-format.schema.json` | Channel Intelligence | `channels/<channel-slug>/formats/<format-id>.json` or project-specific `channels/<channel-slug>/projects/<project-slug>/channel-format.json` |
| `codex/contracts/scenario.schema.json` | Creative Producer | `channels/<channel-slug>/projects/<project-slug>/scenario/scenario.json` |
| `codex/contracts/voiceover-package.schema.json` | Creative Producer | `channels/<channel-slug>/projects/<project-slug>/voiceover/voiceover-package.json` |
| `codex/contracts/scene-visual-pack.schema.json` | Visual Producer | `channels/<channel-slug>/projects/<project-slug>/visuals/scene-visual-pack.json` |
| `codex/contracts/clip-candidate.schema.json` | Visual Producer / InVideo / Remotion Clip Builder | `channels/<channel-slug>/projects/<project-slug>/visuals/candidates/<scene-id>/<candidate-id>.json` |
| `codex/contracts/ai-video-generation-package.schema.json` | InVideo AI Generator | `channels/<channel-slug>/projects/<project-slug>/source-media/generated-clips/<generation-id>/ai-video-generation-package.json` |
| `codex/contracts/remotion-clip-package.schema.json` | Remotion Clip Builder | `channels/<channel-slug>/projects/<project-slug>/remotion/clips/<clip-id>/remotion-clip-package.json` |
| `codex/contracts/timeline-sync-plan.schema.json` | Remotion Video Producer | `channels/<channel-slug>/projects/<project-slug>/remotion/timeline/timeline-sync-plan.json` |
| `codex/contracts/render-package.schema.json` | Remotion Video Producer | `channels/<channel-slug>/projects/<project-slug>/renders/rc/<render-id>/render-package.json` |
| `codex/contracts/critique-report.schema.json` | Video Critic | `channels/<channel-slug>/projects/<project-slug>/reviews/evidence/<critique-id>/critique-report.json` |

## Current Actual Artifacts

No durable channel or project artifacts exist yet beyond `channels/.gitkeep`.

Current real architecture and runtime artifacts:

- `AGENTS.md`
- `codex/architecture/research-synthesis.md`
- `codex/architecture/agent-responsibility-map.md`
- `codex/architecture/agent-hardening-plan.md`
- `codex/specs/agent-system-integrated-spec.md`
- `codex/specs/project-artifact-structure-spec.md`
- `codex/specs/channel-intelligence-spec.md`
- `codex/specs/channel-management-spec.md`
- `codex/specs/invideo-ai-generation-spec.md`
- `codex/specs/remotion-production-spec.md`
- `codex/specs/video-critique-spec.md`
- `codex/examples/production-run.template.json`
- `codex/contracts/*.schema.json`
- `remotion/remotion-project.json`
- `remotion/package.json`
- `remotion/src/Root.tsx`
- `remotion/src/Composition.tsx`
- `remotion/src/templateRegistry.tsx`
- `remotion/templates/vf.lower-third.minimal.v1.json`
- `remotion/templates/vf.source-card.standard.v1.json`
- `remotion/templates/vf.caption.safe.v1.json`
- `remotion/templates/vf.overlay.soft-vignette.v1.json`
- `remotion/src/templates/lower-thirds/MinimalLowerThird.tsx`
- `remotion/src/templates/source-cards/SourceCard.tsx`
- `remotion/src/templates/captions/SafeCaption.tsx`
- `remotion/src/templates/overlays/SoftVignetteOverlay.tsx`

The shared Remotion contract currently marks the app as validated and lists these compositions:

- `VideoFactoryMain`
- `TemplateLowerThirdMinimal`
- `TemplateSourceCardStandard`
- `TemplateSafeCaption`
- `TemplateSoftVignetteOverlay`

## Orchestrator Logic

### 1. Intake And Scope Resolution

The Director starts from the user request and reads the top-level instructions plus `codex/architecture/research-synthesis.md`. It classifies the request by deliverable type, durability, channel scope, source/reference scope, visual route risk, budget risk, and expected output.

The Director keeps work local when the request is a narrow edit, a direct answer, or a single-scope repository change. It delegates when a phase would require broad production work, heavy context, or a distinct agent skill set.

The first Director output is a production brief with:

- objective
- target channel and project slug
- expected artifacts
- platform, aspect ratio, duration, language, and format constraints
- required approvals
- initial path map
- initial agent plan
- stop conditions

### 2. Durable State Setup

If the request is a real deliverable, the Director creates or resolves:

- `channels/<channel-slug>/channel-profile.json`
- `channels/<channel-slug>/projects/<project-slug>/project.json`
- `channels/<channel-slug>/projects/<project-slug>/production-run.json`
- `channels/<channel-slug>/projects/<project-slug>/producer-criteria.json`
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json`
- `remotion/remotion-project.json`

The production run ledger is the live execution record. Its `context_state` is the compact memory used after resumes and phase boundaries. The project file is the durable deliverable index. The media manifest is the source of truth for source files, generated files, render outputs, subtitles, review frames, rights state, and Remotion `staticFile()` paths.

### 3. Producer Criteria Gate

Before production handoffs, the Director writes producer criteria. This is not generic style advice; it is the binding review contract for the run.

Producer criteria must include:

- user request summary
- acceptance criteria
- required rules
- forbidden rules
- hard gates
- scene-specific criteria when scenes exist
- quality thresholds
- revision policy
- restrictions for rights, sources, paid tools, likeness, captions, and platform fit

Every downstream handoff receives the producer criteria path when available. Video Critic treats it as binding input.

### 4. Handoff Creation

The Director creates handoffs only after enough inputs exist for the target agent. Each formal handoff must include:

- `handoff_id`
- `run_id`
- `request_id`
- source and target agents
- objective
- role and scope
- concrete artifact paths
- `project_path`
- `channel_profile_path` when available
- `channel_format_path` when available
- `producer_criteria_path`
- `media_asset_manifest_path` when media is in scope
- `remotion_project_contract_path` when Remotion is in scope
- local skills to read
- allowed paths
- output contract
- budget policy
- definition of done
- stop conditions
- revision policy

The Director also adds the handoff to `production-run.json` with status. Handoff recommendations from specialists are advisory until the Director turns them into this structure.

### 5. Phase Order

The default autonomous phase order is:

1. Channel Intelligence if channel, references, source URLs/files, brand rules, or anti-redundancy are in scope.
2. Creative Producer once channel/source context and criteria are sufficient.
3. Visual Producer once stable scenario scene ids exist.
4. InVideo AI Generator only for Director-approved AI generation routes recommended by Visual Producer.
5. Remotion Clip Builder only for Director-routed deterministic clip, template, source-card, motion graphic, or VFX work.
6. Remotion Video Producer once scenario, voice/caption inputs, selected candidates, clip packages, media manifest, and Remotion setup are ready.
7. Video Critic once a render candidate and technical QA exist.
8. Director delivery or revision routing.

The Director can skip phases that are out of scope. For example, a pure Remotion template task may go directly to Remotion Clip Builder, while a script-only task may use only Creative Producer or remain local.

### 6. Approval Control

The Director stops for explicit approval before:

- paid API calls
- AI generation credits
- paid stock or licensed downloads
- paid Remotion templates
- voice cloning or real-person likeness imitation
- ElevenLabs or other paid TTS generation
- cloud transcription/alignment with spend or media exposure
- external multimodal video critique
- screenshots or downloads from sensitive or rights-unclear pages
- release-gate waivers

Agents can prepare prompts, payloads, cost estimates, candidate records, and approval packets before approval. They cannot spend, download licensed media, or trigger paid generation.

### 7. Evidence And Manifest Discipline

The Director requires every delivery-relevant artifact to preserve provenance. Valid trace handles include:

- source id
- evidence ref
- media asset id
- local artifact path
- Remotion public path
- Remotion `staticFile()` path
- provider URL or provider asset id
- prompt version
- timestamp
- frame path
- QA report path
- approval id or waiver note

Media-producing agents must update `media-asset-manifest.json` or explicitly state why the update is deferred. Final Remotion renders must not depend on remote URLs unless the Director records an explicit exception.

### 8. Integration And Invalidation

The Director integrates returned artifacts by checking:

- status: complete, needs approval, blocked, or needs revision
- changed files
- populated contracts
- validation performed
- assumptions
- blockers
- risks
- next recommended step

The Director then updates `production-run.json` and marks stale artifacts when upstream changes invalidate downstream outputs.

Common invalidation rules:

- channel profile changes invalidate channel format and may invalidate scenario, voice, visuals, Remotion style, render, and critique
- producer criteria changes invalidate review assumptions and may invalidate all downstream work
- scenario scene id, timing, or script changes invalidate voiceover, visual pack, AI prompts, Remotion clips, timeline, render, and critique
- voiceover or caption changes invalidate timeline sync, render, and critique
- visual route or candidate changes invalidate AI/Remotion clip packages, timeline, render, and critique
- Remotion template or clip changes invalidate dependent clip packages, timeline, render, and critique
- timeline, subtitle, audio mix, or export changes invalidate render and critique

The Director reruns only affected agents and downstream dependents. Stable ids should be preserved wherever possible.

### 9. Review Loop

The quality loop is evaluator-optimizer, with Video Critic independent from producers:

1. Remotion Video Producer produces a render package and technical QA.
2. Video Critic prepares review assets and critiques the render against producer criteria, artifacts, source evidence, and viewer experience.
3. Video Critic returns `critique-report` with scene gates, findings, scores, limitations, gate decision, and revision plan.
4. Director validates the report and maps each finding to an owning agent.
5. Director creates revision handoffs only for affected scopes.
6. Revised artifacts flow back into Remotion Video Producer.
7. A new render candidate is produced.
8. Video Critic reviews again.

The loop stops when gates pass, the user waives failures, approval is required, a repeated blocker appears, or the max review iteration policy is reached.

### 10. Context Compaction And Resume

After phase boundaries, long handoffs, review-loop iterations, user change requests, and resumes, the Director runs the context compaction skill. It updates `production-run.context_state` with:

- working set summary
- current phase summary
- last resume summary
- important open decisions
- active blockers
- recent user requests
- recent changes
- stale or invalidated artifacts
- artifacts to reload next
- next actions
- context budget policy
- optional context snapshot path

This keeps the conversation memory secondary. The authoritative state is the file-backed project/run artifacts.

### 11. Delivery

The Director delivers only after:

- required render outputs exist
- media manifest covers delivery-relevant media
- render QA has passed or blockers are disclosed
- Video Critic gates have passed or user waivers are recorded
- rights and approval notes are recorded
- final artifact paths are clear

The final delivery note should list actual file paths, residual risks, waivers if any, validation performed, and the next recommended step if the project is not fully releasable.

## Audit Snapshot

Current static audit:

- 8 agents
- 48 local agent skills
- 43 non-Director skills
- 43 Director handoff references
- 19 contract schemas
- 21 strong skills by local hardening checks
- 0 missing script references
- 0 missing Director handoff refs
- 0 stale Director handoff refs
- 0 skills missing frontmatter
- 0 paid/API-looking skills missing approval terms

The architecture is structurally ready. The main remaining risk is uneven skill hardness: several skills still behave more like checklists than strict contract-producing procedures.
