# Agent System Integrated Spec

## Purpose

This spec consolidates the Video Factory agent architecture, contracts, skill responsibilities, relation model, and remaining gaps. It is meant to be the system-level audit artifact to read before changing agent boundaries, adding skills, or wiring a full autonomous production run.

## Research Basis

The architecture should stay close to these external patterns:

- OpenAI Agents SDK handoffs: use explicit delegation with structured handoff input, optional input filtering, and specialist agents rather than informal cross-agent context sharing. Source: https://openai.github.io/openai-agents-python/handoffs/
- Anthropic agent workflow guidance: prefer simple workflows when possible; use routing, orchestrator-worker, and evaluator-optimizer loops only where the task benefits from specialist context or iterative review. Source: https://www.anthropic.com/engineering/building-effective-agents
- LangGraph workflows: orchestrator-worker workflows use shared state and worker outputs returned to the orchestrator; evaluator-optimizer loops route feedback back until an acceptance condition passes. Source: https://docs.langchain.com/oss/python/langgraph/workflows-agents
- Remotion docs: Remotion supports project scaffolding, Studio, CLI render, server-side rendering, captions/subtitles, render variants, transparent video, stills, GIFs, Lambda, GitHub Actions, and Cloud Run. Sources: https://www.remotion.dev/docs/ and https://www.remotion.dev/docs/render/
- Remotion captions: captions/subtitles are a first-class Remotion workflow with import, transcribe, display, and export paths. Source: https://www.remotion.dev/docs/captions/
- ElevenLabs TTS with timestamps: the timestamp endpoint returns audio plus character-level original and normalized alignment data, which is useful for subtitle and visual sync. Source: https://elevenlabs.io/docs/api-reference/text-to-speech-with-timestamps
- InVideo Agent One credit controls: generation can spend credits and should be approval-gated; approval UI exposes prompt, model, duration, and aspect ratio before generation. Source: https://help.invideo.io/en/articles/14718313-how-credits-are-charged-in-agent-one

## Current Architecture Status

The system now has:

- 8 agents
- 48 local skills
- 31 skills matching the full local hardening section template
- 19 contracts
- 7 local specs
- persistent channel/project state
- first-class producer criteria
- media asset manifests
- Remotion project contracts
- independent critic/review loop
- skill-local scripts for one-skill Visual Producer provider helpers
- repo-level agent audit script for script refs, Director handoff coverage, frontmatter, approval gates, and hardening status

This is no longer just a prompt collection. It is a typed production workflow where agents exchange file-backed contracts and the Director owns the run ledger.

## Core Pattern

Use a Director plus bounded production agents and one independent validation agent.

```text
User request
  -> Director
  -> Channel Intelligence
  -> Creative Producer
  -> Visual Producer
  -> InVideo AI Generator and/or Remotion Clip Builder
  -> Remotion Video Producer
  -> Video Critic
  -> Director review loop and delivery
```

The key rule is that specialist-to-specialist work crosses through the Director. Production agents do not execute another production agent's skills. They may recommend handoffs; the Director turns those recommendations into `agent-handoff` artifacts.

## State Model

Use three durable state levels:

- Channel: reusable brand, format, voice, governance, assets, references, and project registry.
- Project: one video deliverable with all source media, artifacts, render candidates, review evidence, and delivery files.
- Run: one execution attempt with handoffs, approvals, blockers, review loops, rerun state, and compact context/resume state.

Canonical media should live under the project. Remotion `public/` should be treated as a render-visible projection, not the source of truth.

## Contract Map

| Contract | Owner | Purpose | Gap |
|---|---|---|---|
| `agent-handoff.schema.json` | Director | Structured delegation, inputs, allowed paths, skills, output contract, budget policy | Strong. Canonical autonomous fields are required: `handoff_id`, `run_id`, `project_path`, `skills_to_read`, `output_contract`, `definition_of_done`, `stop_conditions`, and `budget_policy`. |
| `video-project.schema.json` | Director / Channel Intelligence | Durable project index under a channel | Good. Scaffold helper exists; needs examples/templates and validation fixtures. |
| `production-run.schema.json` | Director | Execution ledger, handoffs, approvals, review loops, blockers, context state, and resume snapshots | Strong after `context_state` hardening. Minimal fixture exists at `codex/examples/production-run.template.json`; could add explicit invalidation graph if reruns become complex. |
| `channel-profile.schema.json` | Channel Intelligence | Persistent channel identity, brand, content, voice, governance | Good. Needs examples/templates. |
| `media-asset-manifest.schema.json` | Channel Intelligence / media-producing agents | Canonical source/generated/rendered/review asset ledger | Strong direction. Needs strict update rules in every media-producing skill. |
| `remotion-project.schema.json` | Director / Remotion agents | Shared or project Remotion app metadata, commands, dependencies, public asset policy | Good. Shared app exists. Keep setup validation checklist-based before adding helpers. |
| `remotion-template.schema.json` | Remotion Clip Builder | Reusable Remotion component/template contract, props, safe areas, previews, usage rules | Good. Template registry exists; keep template contracts and Remotion project registry aligned. |
| `producer-criteria.schema.json` | Director | Binding acceptance criteria, hard gates, scene criteria, thresholds, revision policy | Strong. Needs every production handoff to receive the path. |
| `reference-analysis.schema.json` | Channel Intelligence | Source/reference evidence and downstream guidance | Stronger after evidence graph fields: `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `downstream_guidance`, and `invalidation_impact[]`. |
| `channel-format.schema.json` | Channel Intelligence | Reusable format rules derived from profile/references, including per-channel VFX rule extensions | Good. Needs freshness/version policy. |
| `scenario.schema.json` | Creative Producer | Timed scenario and scene list | Good after scene-breakdown hardening. |
| `voiceover-package.schema.json` | Creative Producer | Voice direction, provider payload, audio paths, captions, QA | Good after TTS hardening. |
| `scene-visual-pack.schema.json` | Visual Producer | Per-scene visual goals, routes, constraints, downstream handoff recommendations | Good. Needs selected primary/fallback fields or a separate selection artifact if rankings get richer. |
| `clip-candidate.schema.json` | Visual Producer / InVideo / Remotion Clip Builder | Comparable candidate record across source routes | Good. Could add `validation_report_path` if evidence grows. |
| `ai-video-generation-package.schema.json` | InVideo AI Generator | Model route, prompts, approval, outputs, QA | Good. Needs provider-specific examples. |
| `remotion-clip-package.schema.json` | Remotion Clip Builder | Short clip/component package, dependencies, outputs, QA | Good. Needs stack decision path if dependency choices become formal artifacts. |
| `timeline-sync-plan.schema.json` | Remotion Video Producer | Frame-accurate scene, audio, caption, visual alignment | Good. Timeline skill now enforces selected-candidate authority and repair-only helper fallback. |
| `render-package.schema.json` | Remotion Video Producer | Render RC package, outputs, commands, subtitles, audio mix, QA | Good. Render RC skill now requires immutable versioning and reproducibility evidence; release approval intentionally stays outside this contract. |
| `critique-report.schema.json` | Video Critic | Independent review, scene gates, scores, findings, revision plan, gate decision | Good. Needs reviewer prompt archive for reproducibility. |

## Agent Relation Model

### Director

Owns user conversation, decomposition, producer criteria, approvals, handoffs, run ledger, final integration, review-loop routing, and delivery.

Consumes all artifacts. Produces `agent-handoff`, `production-run`, `video-project`, `producer-criteria`, and final delivery notes.

Relations:

- Calls Channel Intelligence when channel, references, source material, or anti-redundancy matter.
- Calls Creative Producer after source/channel context is sufficient.
- Calls Visual Producer after scenario exists.
- Converts Visual Producer handoff recommendations into InVideo or Remotion Clip Builder handoffs.
- Calls Remotion Video Producer after approved candidates/clip packages and voice/caption inputs exist.
- Calls Video Critic after a render candidate exists.

Gaps:

- `decompose-video-request` is now hardened with production brief, path map, agent plan, approval gates, and handoff summary.
- The Director has enough rules, but the autonomous run should eventually write a machine-readable invalidation graph, not only prose.
- The Director handoff map must stay complete for every current agent-owned skill; missing map entries are a P0 routing issue.
- Handoff creation should first be hardened in prompts/specs. Add a deterministic helper only later if real runs still miss required fields.
- The Director should always attach `run_id`, `project_path`, `producer_criteria_path`, `media_asset_manifest_path`, `remotion_project_contract_path`, and relevant Remotion template paths when available.
- `context-compaction` should run after phase boundaries, long handoffs, review-loop iterations, user changes, and resumes so `production-run.context_state` remains the authoritative compact working set.

### Channel Intelligence

Owns channel profile, source corpus, reference analysis, channel format, style extraction, scenario alignment, and redundancy risk.

Relations:

- Feeds Creative Producer with source evidence, channel voice, and format rules.
- Feeds Visual Producer with visual style, reference patterns, evidence refs, and anti-copy guidance.
- Feeds InVideo and Remotion agents indirectly through channel format, media manifest, and producer criteria.
- Feeds Video Critic with source/channel criteria for final comparison.

Gaps:

- Many skills are still checklist-like and need exact return shapes.
- Media asset manifest updates are now explicit in `source-corpus-ingestion` and `reference-video-breakdown`; propagate the same policy to the remaining Channel Intelligence media-touching skills.
- Channel profile updates need change impact rules: channel voice/visual changes can invalidate channel format, scenario, visuals, voiceover, Remotion themes, and critique criteria.

### Creative Producer

Owns scenario, scene breakdown, narration, voice direction, provider-ready voiceover package, and script-level claim notes.

Relations:

- Consumes Channel Intelligence and producer criteria.
- Feeds Visual Producer with stable scene ids, visual intent, and source ids.
- Feeds Remotion Video Producer with scenario timing, voiceover package, captions, and pronunciation/timing notes.
- Feeds Video Critic with intended script, claims, and audio expectations.

Gaps:

- `write-scenario` and `voice-casting` remain thinner than `scene-breakdown` and `tts-production-plan`.
- Claim-check ownership needs sharper split: Creative may draft claim notes, but source confidence belongs to Channel Intelligence.
- If human voiceover is used, the package should still use the same voiceover contract rather than bypassing it.

### Visual Producer

Owns scene visual pack, visual research, provider search specs, candidate validation, ranking, and downstream handoff recommendations.

Relations:

- Consumes scenario, reference analysis, channel format, media manifest, and producer criteria.
- Produces candidate records and handoff recommendations for InVideo or Remotion Clip Builder.
- Does not perform InVideo model selection or Remotion component planning.
- Feeds Remotion Video Producer with approved primary/fallback candidates.
- Feeds Video Critic with visual expectations, provenance, and selection rationale.

Gaps:

- `visual-validation`, `clip-candidate-ranking`, `provider-clip-search`, `freepik-video-search`, `pexels-video-search`, `visual-research-queries`, `visual-pack-plan`, and `ai-video-generation-brief` are now strong.
- Provider search now stores candidate records before download and separates remote preview evidence from downloaded production media.
- Freepik and Pexels one-skill helper scripts now live inside their skill bundles.

### InVideo AI Generator

Owns provider/model AI generation package, prompts, negative constraints, approval packet, variants, generated outputs, and generated clip QA.

Relations:

- Runs only after Visual Producer selects or recommends `ai_video_generation` and Director creates a handoff.
- Returns AI generation package and clip candidates.
- Updates media asset manifest for downloaded/generated outputs.
- Feeds Remotion Video Producer through approved clip candidates.
- Feeds Video Critic with prompts, approvals, outputs, and QA.

Gaps:

- All InVideo AI Generator skills now include the local hardening sections.
- Model selection writes a structured route decision, not only a recommendation.
- Prompt builder requires scene/model/settings/reference/constraint fields and approval-aware reproducibility.
- Generation iteration defines max variants, one-variable-change discipline, budget ceiling, fallback triggers, and stop conditions.
- Generated clip QA should mirror Visual Validation's pass/fail evidence format.

### Remotion Clip Builder

Owns deterministic 5-20 second clips, VFX overlays, motion graphics, component templates, preview evidence, and reusable clip packages.

Relations:

- Runs after Visual Producer recommends `remotion_generated` and Director creates a handoff.
- Consumes scenario scene ids, visual briefs, media manifest, Remotion project contract, and producer criteria.
- Produces Remotion clip packages and sometimes clip candidates.
- Feeds Remotion Video Producer with component paths, composition ids, props, outputs, and render commands.

Gaps:

- `remotion-stack-selection` is now strong.
- `remotion-template-library` now exists and should be kept as the authority for reusable template selection, creation, promotion, and template contract updates.
- `remotion-scene-plan` should include an explicit component plan object, props plan, asset needs, and preview frames.
- `remotion-ai-component-prompt` needs an output format for generated prompt packets and compile-error repair loops.
- `remotion-vfx-clip` has a definition of done but should more explicitly map outputs into `remotion-clip-package`.
- `vfx-quality-performance-hardening` exists and should be used for complex VFX render stability, alpha/export, GPU, memory, and fallback-risk checks.
- Remotion app setup should remain checklist-based for now. Add a helper only if repeated setup drift appears in real runs.

### Remotion Video Producer

Owns full-video assembly, timeline sync, captions/subtitles, audio mix, post-production, render RC package, and technical render QA.

Relations:

- Consumes scenario, voiceover, visual candidates, Remotion clip packages, media manifest, Remotion project contract, and producer criteria.
- Produces timeline sync plan, render package, subtitles, audio mix notes, preview/final outputs, and technical QA.
- Requests Director handoff to Clip Builder if new reusable clips/VFX are needed.
- Does not approve viewer-facing release gates.

Gaps:

- `timeline-sync-plan` is now strong: it requires all selected visuals/audio/captions by scene id and frame range and preserves Visual Producer selection authority.
- `subtitle-caption-pipeline` needs exact Caption JSON/SRT output contract and safe-area QA.
- `render-release-candidate` is now strong: it requires manifest actions, explicit RC versioning, reproducibility evidence, logs, hashes, metadata, QA links, and immutable RC behavior.
- `render-qa` should have stricter technical pass/fail categories and explicitly exclude release approval.
- `remotion-post-production` should define expected timeline source files, composition ids, and render-readiness checks.

### Video Critic

Owns independent validation of the final rendered candidate. Produces critique report and revision plan; never edits production artifacts.

Relations:

- Consumes render package, final video path, producer criteria, scenario, channel format, source evidence, media manifest, timeline sync, voiceover, captions, visual pack, candidates, AI packages, and Remotion packages.
- Produces critique report with scene gates, scores, findings, gate decision, limitations, and revision plan.
- Sends recommendations to Director, not directly to producers.

Gaps:

- Critic skills are conceptually strong but need more exact return shapes.
- `prepare-multimodal-review-package` should require manifest entries for sampled frames and review assets.
- `artifact-consistency-audit` should produce findings in the same structure as critique report.
- `multimodal-video-critique` should archive prompt and raw response paths for reproducibility.
- `revision-prioritization` should output an explicit owner/rerun dependency map.

## Skill Gap Matrix

Legend:

- Strong: enough for autonomous handoff now.
- Medium: usable but needs stricter return shape or evidence rules.
- Thin: checklist-level; should be upgraded before high-autonomy use.

| Agent | Skill | Status | Gap | Recommended Spec Upgrade |
|---|---|---:|---|---|
| Channel Intelligence | `source-corpus-ingestion` | Strong | Hardened with `source_ledger[]`, `claim_ledger[]`, rights state, reusable scope, missing evidence, confidence, downstream guidance, invalidation impact, manifest actions, stop conditions, and handoff summary. | Keep as the source provenance entry point before reference and channel-format work. |
| Channel Intelligence | `channel-profile-management` | Medium | Has workflow but not strict output summary or invalidation impact. | Add channel profile delta, project creation result, changed fields, downstream invalidation, and QA summary. |
| Channel Intelligence | `reference-video-breakdown` | Strong | Hardened with `reference_beats[]`, timecoded beat/shot evidence, transcript/audio/caption observations, reusable patterns, do-not-copy risks, sidecar artifacts, media asset ids, model limitations, confidence, invalidation impact, and manifest actions. | Keep deterministic evidence separate from model-inferred evidence. |
| Channel Intelligence | `web-content-synthesis` | Strong | Hardened with one-page web capture paths, local parser workflow, `web_pages[]`, `claim_ledger[]`, image candidates, annotations, rights/robots gates, manifest actions, and handoff summary. | Keep direct links bounded by default; add a separate crawl scope only if future projects require it. |
| Channel Intelligence | `style-system-extraction` | Strong | Hardened with tokenized style taxonomy, policy levels, inheritance priority, do-not-copy rules, evidence/confidence, reusable template candidates, invalidation impact, manifest policy, and handoff summary. | Keep abstract reusable style separate from copied reference execution. |
| Channel Intelligence | `channel-format-synthesis` | Strong | Hardened with versioned format package, freshness policy, `must_reuse`/`must_vary`/experimental rules, anti-redundancy thresholds, evidence/confidence, downstream invalidation, and manifest policy. | Keep stale or weakly evidenced formats in `needs_review` or experimental state. |
| Channel Intelligence | `scenario-alignment-brief` | Strong | Hardened with scene-level findings, claim/source coverage, channel-fit state, visual-proof state, severity, owner routing, disposition, manifest policy, and required-change summary. | Use as the pre-production gate before expensive production. |
| Channel Intelligence | `redundancy-risk-audit` | Strong | Hardened with redundancy score, factor-level evidence, minimum novelty requirements, risk categories, waiver policy, owner recommendations, manifest policy, and pass/block states. | Keep healthy consistency distinct from low-novelty repetition. |
| Creative Producer | `write-scenario` | Strong | Hardened with dual-layer scenario output, scene production logic, claim/source coverage, novelty policy, duration/format/producibility validation, media deferrals, and handoff summary. | Preserve stable scene ids and keep must-say/must-show/flexible execution separated. |
| Creative Producer | `scene-breakdown` | Strong | Recently upgraded. | Keep as reference pattern for other skills. |
| Creative Producer | `voice-casting` | Strong | Hardened with structured voice direction, inheritance chain, voice need classification, weighted rubric, rejected styles, pronunciation risks, accessibility notes, rights/consent gates, and provider handoff readiness. | Keep provider inventory ranking in provider-specific voice selection. |
| Creative Producer | `elevenlabs-voice-selection` | Medium | Has workflow/scripts but not a compact output schema. | Add provider inventory snapshot path, ranked candidates, selected voice, approval state, continuity/risk notes, and dry-run evidence. |
| Creative Producer | `tts-production-plan` | Strong | Recently upgraded. | Keep provider execution guarded; ensure human narration also uses the contract. |
| Director | `decompose-video-request` | Strong | Hardened with structured production brief, artifact path map, agent plan, initial handoffs, approvals, media manifest policy, stop conditions, and handoff summary. | Keep as the Director's first planning gate before autonomous runs. |
| Director | `producer-criteria-prompt` | Medium | Contract exists, but skill needs a stricter example return shape. | Add exact producer criteria summary, scene criteria coverage, hard gate ids, threshold defaults, and revision policy. |
| Director | `autonomous-production-run` | Strong | Good run loop. | Add deterministic invalidation graph and handoff validation helper later. |
| Director | `context-compaction` | Strong | New Director skill for durable resume summaries and reload lists. | Keep run-ledger context state authoritative; do not replace artifact contracts with prose summaries. |
| Director | `quality-gated-review-loop` | Medium | Good policy, but rerun dependency graph should be more formal. | Add owner-to-rerun matrix and explicit stale artifact marking rules. |
| Visual Producer | `visual-pack-plan` | Strong | Hardened with scene pack summary, route decision evidence, fallback coverage, approval needs, manifest policy, and handoff recommendations. | Keep as the visual routing contract before provider search or specialist handoffs. |
| Visual Producer | `visual-research-queries` | Strong | Hardened with query groups by route/provider, expected evidence, rejected queries, provider priority, and search stop criteria. | Keep search provenance visible to provider skills and candidate ranking. |
| Visual Producer | `provider-clip-search` | Strong | Hardened with canonical candidate storage, pre-download checks, scoped approval model, manifest policy, and handoff summary shape. | Keep provider-specific skills aligned with this general policy. |
| Visual Producer | `freepik-video-search` | Strong | Hardened with Freepik-specific command policy, candidate storage, pre-download checks, separate download-link/file-download approval gates, manifest policy, and handoff summary shape. | Keep helper script flags aligned with the skill. |
| Visual Producer | `pexels-video-search` | Strong | Hardened with Pexels-specific command policy, secondary-provider guidance, attribution/rate-limit evidence, guarded file downloads, manifest policy, and handoff summary shape. | Keep helper script flags aligned with the skill and Pexels API guidelines. |
| Visual Producer | `ai-video-generation-brief` | Strong | Hardened with structured route brief, prompt intent, references, constraints, target settings, risk, fallback, and Director-routable handoff recommendation. | Keep provider-final prompt and generation package ownership in InVideo AI Generator. |
| Visual Producer | `visual-validation` | Strong | Recently upgraded. | Use as validation template for generated clip QA. |
| Visual Producer | `clip-candidate-ranking` | Strong | Hardened with required inputs, workflow, weighted scoring, evidence, primary/fallback/rejected decisions, manifest policy, stop conditions, and handoff summary. | Keep as the candidate-selection authority for timeline sync. |
| InVideo AI Generator | `invideo-model-selection` | Strong | Hardened with route decision, model limits, duration/aspect ratio, quality mode, cost risk, fallback model, assumptions, approval need, and manifest deferrals. | Keep model/provider limits marked unknown rather than guessed. |
| InVideo AI Generator | `ai-video-prompt-builder` | Strong | Hardened with positive prompt, negative constraints, prompt guide notes, references, model settings, residual risks, approval gates, and reproducibility fields. | Keep provider submission blocked until approval package is approved. |
| InVideo AI Generator | `negative-prompt-guardrails` | Strong | Hardened with `negative_prompt_mode`, positive rewrites, prompt-guide constraints, unsupported constraints, contradiction check, and residual risks. | Keep negative prompts compatible with provider support and do not use them as rights/safety bypasses. |
| InVideo AI Generator | `generation-approval-package` | Strong | Hardened with exact generation dialog fields, credit/cost estimate, approval state/scope, expiry/staleness notes, reference rights checks, and blocked state. | Any field change after approval requires re-approval. |
| InVideo AI Generator | `generation-iteration-plan` | Strong | Hardened with max variants, one-variable-change plan, QA target per variant, budget ceiling, retry stop conditions, fallback triggers, and version lineage. | Keep rerolls bounded by approved scope and QA evidence. |
| InVideo AI Generator | `generated-clip-qa` | Strong | Hardened with pass/fail dimensions, candidate/package updates, generated output ids, rights state, manifest policy, reroll recommendation, and stop conditions. | Keep aligned with `visual-validation` evidence style. |
| Remotion Clip Builder | `remotion-scene-plan` | Strong | Hardened with deterministic Remotion scene plan, implementation mode, composition id, props schema, frame timing map, asset requirements, safe areas, VFX triggers, preview commands, and validation gates. | Use this before coding 5-20 second Remotion clips or overlays. |
| Remotion Clip Builder | `remotion-template-library` | Medium | New template authority exists and has a solid shape, but it must stay aligned with registry/project contract updates. | Require selected/new template decision, template contract path, registry update evidence, instance clip package path, and versioning rules. |
| Remotion Clip Builder | `remotion-stack-selection` | Strong | Recently upgraded. | Consider a formal stack-decision artifact if choices become large. |
| Remotion Clip Builder | `remotion-ai-component-prompt` | Medium | Strong guidance but output is prompt-oriented, not contract-oriented. | Add generated prompt packet, targeted edit plan, compile error repair loop, and validation checklist. |
| Remotion Clip Builder | `remotion-vfx-clip` | Medium | Has DoD but should map every output into clip package fields. | Add `remotion-clip-package` update checklist and manifest output entries. |
| Remotion Clip Builder | `vfx-quality-performance-hardening` | Strong | Good technical hardening shape for complex VFX. | Wire into complex VFX handoffs and require findings to land in clip package QA or VFX profile. |
| Remotion Video Producer | `subtitle-caption-pipeline` | Strong | Hardened with caption source route, normalized Caption JSON, SRT/VTT export policy, burned-in/sidecar decision, caption style, scene ranges, QA checks, manifest policy, and timeline sync handoff. | Treat captions as timed production artifacts, not transcript text. |
| Remotion Video Producer | `timeline-sync-plan` | Strong | Hardened with selected-candidate authority, scene frame ranges, voice/caption ranges, manifest actions, repair-only helper fallback, and QA failure policy. | Keep Visual Producer as selection authority and keep helper-selected visuals blocked for Director review. |
| Remotion Video Producer | `remotion-post-production` | Medium | Good scope but needs exact deliverables. | Add timeline source files, composition ids, media normalization, audio mix, transition map, render-readiness checks. |
| Remotion Video Producer | `render-release-candidate` | Strong | Hardened as immutable RC attestation with versioning, attempt id, input/output hashes, commands, logs, environment, metadata, manifest actions, rights notes, known blockers, and QA links. | Keep final release approval owned by Video Critic plus Director. |
| Remotion Video Producer | `render-qa` | Strong | Hardened as technical-only QA with render health, duration, scene timing, asset availability, audio/caption sync, safe area, visual usage, export metadata, rights, manifest coverage, and explicit release boundary. | Keep final release approval owned by Video Critic plus Director. |
| Video Critic | `prepare-multimodal-review-package` | Medium | Workflow exists but output should be structured. | Add frame sample list, ffprobe metadata, direct video route, manifest asset ids, missing evidence, and limitations. |
| Video Critic | `scene-by-scene-gate-review` | Medium | Good process, no final JSON shape. | Add exact scene review object, criterion results, gate status, unknown evidence policy, and failed gate ids. |
| Video Critic | `artifact-consistency-audit` | Strong | Hardened with critique-report-shaped findings, artifact mismatch categories, provenance failures, owner mapping, manifest policy, stop conditions, and blocks-delivery flags. | Use before or alongside multimodal critique. |
| Video Critic | `multimodal-video-critique` | Medium | Good dimensions, needs reproducibility output. | Add prompt path, raw response path, model limits, media handling approval, and hybrid/direct/frame-only mode notes. |
| Video Critic | `revision-prioritization` | Medium | Good owner mapping, but rerun dependencies are implicit. | Add affected artifacts, invalidation scope, approval needs, expected rerun chain, and stop/waiver recommendations. |

## Cross-Agent Relation Rules

### Skill Rule Ownership

Every skill file is a local rule set. Agents apply only their `AGENT.md`, named local skills, explicitly approved built-in skills, and artifact inputs passed by the Director. Specs can define shared intent, but they do not replace skill-local instructions; when a shared rule changes, update every affected skill together with the relevant slice of that rule.

Channel/project artifacts carry rule extensions between independently running skills and agents. For VFX, the channel format may extend the shared hardening rules through `visual_system.vfx_rules`, and downstream handoffs should pass `channel_format_path` plus any relevant VFX rule refs so the rule survives context loss.

### Handoff Rules

Every handoff must include:

- `handoff_id`
- `run_id` when a run ledger exists
- role and scope
- agent path
- skill files to read
- objective
- inputs with artifact paths
- `project_path` when a durable project exists
- `channel_profile_path` when available
- `channel_format_path` when available
- `producer_criteria_path` when available
- `media_asset_manifest_path` when media exists
- `remotion_project_contract_path` when Remotion is in scope
- Remotion template registry/contract paths when reusable templates are in scope
- allowed paths
- output contract
- budget and approval policy
- definition of done
- stop conditions
- revision policy

Specialist agents may return handoff recommendations, but recommendations are not executable. Only the Director creates executable `agent-handoff` records.

### Approval Rules

Approval is required for:

- paid API spend
- AI generation credits
- licensed media downloads
- paid Remotion Pro templates or commercial assets
- voice cloning, likeness use, or unclear voice rights
- cloud transcription/alignment if it spends credits
- multimodal critique through a paid or external provider
- release gate waivers

### Evidence Rules

Every source-backed claim, reference-derived rule, visual candidate, generated clip, Remotion asset, render output, sampled review frame, and critique finding should be traceable through one of:

- source id
- evidence ref
- media asset id
- artifact path
- timestamp
- frame path
- provider request id

Missing evidence is allowed in early planning but should become a blocker before release-candidate approval when it affects rights, factual claims, selected media, captions, audio sync, or delivery quality.

## Artifact Flow

```text
channel-profile
  -> channel-format
  -> producer-criteria
  -> scenario
  -> voiceover-package
  -> scene-visual-pack
  -> clip-candidate
  -> ai-video-generation-package / remotion-template / remotion-clip-package
  -> timeline-sync-plan
  -> render-package
  -> critique-report
  -> production-run review loop
  -> video-project delivery state
```

The media asset manifest runs alongside the whole flow. It is not a late-stage artifact; it should be updated whenever source, generated, rendered, subtitle, thumbnail, review, or delivery media becomes real.

Media-producing skills must either update the manifest or explicitly defer it with a reason. For every real media file, generated clip, render, subtitle, thumbnail, review frame, or Remotion public projection, record:

- media asset id
- canonical path
- Remotion public path and `staticFile()` path when relevant
- rights state and approval state
- technical metadata such as duration, dimensions, fps, codec, audio presence, or probe path when available
- evidence refs, source asset ids, and related contract paths

## Rerun And Invalidation Rules

| Change | Invalidate | Rerun |
|---|---|---|
| Channel profile brand/audio/visual rules | Channel format, producer criteria, scenario/visual/voice assumptions | Channel Intelligence, affected downstream agents, Critic |
| Channel format rules, including VFX extensions | Producer criteria, visual pack constraints, Remotion clip packages that depend on the format, timeline/render QA, critique | Channel Intelligence, Visual Producer, affected Remotion agents, Critic |
| Source/reference evidence | Reference analysis, claims, visual evidence, factual gates | Channel Intelligence, Creative Producer, affected downstream agents |
| Producer criteria | All subsequent review assumptions | Director criteria update, affected production agents if rules changed, Critic |
| Scenario scene ids/timing/script | Voiceover, visual pack, AI prompts, Remotion clips, timeline, render, critique | Creative Producer, Visual Producer, affected generators, Remotion Video Producer, Critic |
| Voiceover audio/timestamps | Timeline sync, captions, render, critique | Creative Producer, Remotion Video Producer, Critic |
| Visual route/candidate | InVideo/Remotion clip packages, timeline, render, critique | Visual Producer, affected generator, Remotion Video Producer, Critic |
| AI generated clip | Clip candidate, media manifest, timeline, render, critique | InVideo AI Generator, Remotion Video Producer, Critic |
| Remotion clip/component | Clip package, timeline, render, critique | Remotion Clip Builder, Remotion Video Producer, Critic |
| Remotion template contract/component | Every clip package that references the template, timeline, render, critique | Remotion Clip Builder, Remotion Video Producer, Critic |
| Timeline/captions/audio mix/export | Render package, critique | Remotion Video Producer, Critic |
| Critique metadata only | Critique report, run ledger | Video Critic or Director only |

Timeline helpers must not become hidden creative authorities. Visual Producer owns primary/fallback visual selection. Timeline sync tools may consume selected candidates and mark missing selections as blockers; they should not silently choose a new primary candidate except as an explicitly marked repair/default behavior that the Director can review.

## Review Loop Spec

The review loop is an evaluator-optimizer loop:

1. Remotion Video Producer produces a render candidate and technical QA.
2. Video Critic evaluates the final video against producer criteria, scenario, source/channel evidence, artifacts, and viewer experience.
3. Director validates the critique report and gate decision.
4. Director routes exact findings to owning agents.
5. Affected agents revise only stale artifacts.
6. Remotion Video Producer rerenders.
7. Video Critic reviews again.
8. Loop stops when gates pass, a user waiver is recorded, approval is needed, a blocker repeats, or max iterations is reached.

Do not let producing agents self-approve final viewer quality. Do not let the critic edit artifacts directly.

## Standard Skill Hardening Template

Every skill that will be used in autonomous production should eventually include:

```text
Inputs
Workflow
Required Output
Contract Fields Populated
Status Policy
Evidence Required
Approval / Stop Conditions
Definition Of Done
Handoff Summary Shape
```

Standard handoff summary:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["string"],
  "validation_performed": ["string"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```

Validation-style skills should additionally return:

```json
{
  "item_id": "string",
  "status": "pass | fail | partial | unknown | needs_approval",
  "evidence": "string",
  "reason": "string",
  "recommendation": "string",
  "owner_agent": "string",
  "blocks_delivery": true
}
```

## Priority Backlog

### P0: Required Before Reliable Autonomous Runs

1. Keep the four critical judgment/QA skills hardened and regression-check their required sections: `clip-candidate-ranking`, `generated-clip-qa`, `render-qa`, and `artifact-consistency-audit`.
2. Keep the Director handoff map complete for all existing local agent skills, and require canonical handoff fields: `handoff_id`, `run_id`, `project_path`, `skills_to_read`, `output_contract`, `definition_of_done`, `stop_conditions`, and `budget_policy`.
3. Keep Director context compaction explicit: after phase boundaries, long handoffs, review-loop iterations, user changes, and resumes, update required `production-run.context_state` fields with the compact working set, open decisions, blockers, stale artifacts, and files to reload next.
4. Require all media-producing skills to update or explicitly defer media asset manifest entries with asset id, canonical path, Remotion public/static path when relevant, rights state, technical metadata, and evidence refs.
5. Maintain timeline helper authority: consume Visual Producer selections by default; any helper fallback must be explicit `repair_default` and require Director review.
6. Keep Remotion template contracts, template registry, Remotion project contract, and clip package references aligned whenever reusable templates are selected, created, revised, or promoted.

### P1: Required Before Multi-Project Channel Operation

1. Add examples/templates for channel profile, video project, media manifest, producer criteria, Remotion project, and Remotion template contracts.
2. Harden Channel Intelligence skills with structured output and channel/profile invalidation.
3. Harden Visual Producer search/research skills with evidence, route query provenance, provider metadata, and fallback coverage.
4. Harden InVideo prompt/model/approval and subtitle-caption pipeline skills after the four P0 skills are contract-shaped.
5. Add explicit invalidation graph support to production-run handling if review-loop reruns become hard to audit from prose rules.

### P2: Useful For Scale

1. Add skill-level golden test prompts or fixture artifacts.
2. Add an optional `validate_artifact.py` helper only if real runs show schema drift; it should validate JSON, check required paths, and avoid API calls or creative judgment.
3. Add optional handoff or Remotion app setup check helpers only if checklist-based specs fail repeatedly in real runs.
4. Add reviewer prompt archive and raw model response archive policy.
5. Add report generation from production-run ledger.

## Final Architecture Judgment

The current agent count is justified. The system is not over-split by intent; it is split by production responsibility:

- Director for orchestration and approvals
- Channel Intelligence for reusable channel/source state
- Creative Producer for script and voice
- Visual Producer for visual route and candidate decisions
- InVideo AI Generator for credit-sensitive AI video generation
- Remotion Clip Builder for reusable deterministic short clips/VFX
- Remotion Video Producer for full timeline/render production
- Video Critic for independent final review

The remaining risk is not the number of agents. The risk is uneven skill hardness. No matrix skills remain classified as Thin, but several Medium skills still need stricter return shapes, evidence, status, stop conditions, and definitions of done before high-autonomy production runs are fully reliable.
