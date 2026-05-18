# Video Factory Agent Hardening Plan

This plan turns the current architecture gaps into concrete implementation work. It assumes the core architecture is correct and that the reliability problem is uneven skill hardness, loose evidence policy, and handoff drift.

Current repo inventory from local scan:

- Agents: 8
- Local `SKILL.md` files: 50
- Non-Director skills: 44
- Director handoff map entries: 44
- Contract schemas: 20
- Specs: 7
- Example fixtures: `codex/examples/channel-profile.template.json`, `codex/examples/video-project.template.json`, `codex/examples/media-asset-manifest.template.json`, `codex/examples/producer-criteria.template.json`, `codex/examples/remotion-project.template.json`, `codex/examples/remotion-template.template.json`, `codex/examples/production-run.template.json`, and `codex/examples/agent-handoff.artifact-repair.template.json`
- Duplicate skill names: 0
- Missing Director handoff map entries: 0
- Strong skills by hardening template: 31
- Missing skill script references: 0
- API/paid-looking skills missing approval terms: 1 (`codex/agents/remotion-clip-builder/skills/vfx-quality-performance-hardening/SKILL.md`)
- Durable channel/project examples in `channels/`: none beyond `channels/.gitkeep`; reusable placeholders live under `codex/examples/`

## Hardening Standard

Every production skill that can run autonomously should eventually contain these sections:

```text
Inputs
Workflow
Required Output
Contract Fields Populated
Status Policy
Evidence Required
Media Manifest Policy
Approval And Stop Conditions
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
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["string"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```

Validation-style skills should additionally return item findings shaped like this:

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

## Current Decision

Harden prompts, skill specs, and contract usage before adding production helpers. A repo-level maintenance audit now exists at `codex/scripts/audit_agent_system.py`; it checks skill script references, Director handoff coverage, approval-gate wording, frontmatter, and section-hardening status without changing production artifacts.

The integrated architecture already has the right direction:

- Director plus seven specialist agents.
- File-backed contracts for handoffs, project state, media manifests, Remotion project/template data, producer criteria, render packages, and critique reports.
- Independent Video Critic release review.
- Remotion Video Producer owns technical render QA only.
- Visual Producer owns primary/fallback candidate selection.

The former thin-skill backlog is now hardened. The remaining work is to upgrade Medium skills that still need stricter return shapes, evidence, status, stop conditions, and handoff summaries.

## P0: Required Before Reliable Autonomous Runs

### 1. Harden Four Critical Judgment And QA Skills

These are the first implementation target:

- `codex/agents/visual-producer/skills/clip-candidate-ranking/SKILL.md`
- `codex/agents/invideo-ai-generator/skills/generated-clip-qa/SKILL.md`
- `codex/agents/remotion-video-producer/skills/render-qa/SKILL.md`
- `codex/agents/video-critic/skills/artifact-consistency-audit/SKILL.md`

Required upgrades:

- Add the hardening standard sections.
- Require exact input artifacts and output artifacts.
- Require structured pass/fail/partial/unknown evidence.
- Require blocker and approval behavior.
- Require `manifest_actions[]` when media is created, consumed, or inspected.
- Return a Director-routable handoff summary.

Acceptance criteria:

- Each file contains every hardening standard section.
- Each file names the contract fields it populates or validates.
- Each file defines what counts as complete, blocked, needs approval, and needs revision.
- Each file produces structured findings that the Director can route without interpreting prose.

### 2. Keep Director Handoff Map Current

Current status: complete for the current scan.

Required rule:

- Every non-Director local skill must appear in `codex/agents/director/AGENT.md` under the handoff skill map.
- New skills are not complete until the Director handoff map is updated.
- Handoffs must include `handoff_id`, `run_id` when a run ledger exists, `project_path`, `skills_to_read`, `output_contract`, `definition_of_done`, `stop_conditions`, and `budget_policy`.

Do not add a validation helper yet. Revisit a helper only if persisted handoffs repeatedly miss required fields.

### 2a. Keep Director Context Compaction Explicit

Current status: Director has a dedicated `context-compaction` skill, required `production-run.context_state` contract fields, optional `production-run.invalidation_graph` support, repair-handoff routing reference, and reusable fixtures under `codex/examples/` for channel profile, video project, media manifest, producer criteria, Remotion project, Remotion template, production run, and artifact repair handoff artifacts.

Required rule:

- Run `context-compaction` after phase boundaries, long handoffs, review-loop iterations, post-run changes, context pressure, and resumes.
- Persist the compact working set in `production-run.context_state`.
- Keep raw large artifacts on disk and record only paths, evidence ids, decisions, blockers, and reload instructions in active context.
- Resume by reading `AGENTS.md`, Director `AGENT.md`, the production run ledger, and only `context_state.artifacts_to_reload_next`.

Acceptance criteria:

- The run ledger can explain current phase, next actions, blockers, open decisions, stale artifacts, and files to reload without relying on conversation memory.
- Snapshot files live under `channels/<channel-slug>/projects/<project-slug>/runs/<run-id>/context/` when detailed sidecars are needed.
- Compaction never marks production work complete without the owning artifact contract and validation evidence.
- New runs can start from the relevant `codex/examples/*.template.json` fixtures after replacing channel, project, request, run, and path placeholders.

### 3. Add Media Manifest Policy To Media-Producing Skills

Required rule:

```text
If this skill creates, downloads, mirrors, renders, samples, transcodes, captures, generates, validates, or consumes a local media artifact, it must update the media asset manifest or return manifest_actions[] with deferred or not_applicable plus a reason.
```

Skills that must report manifest actions:

- Channel Intelligence: `source-corpus-ingestion`, `channel-profile-management`, `reference-video-breakdown`, `web-content-synthesis`, `style-system-extraction`, `channel-format-synthesis`
- Creative Producer: `elevenlabs-voice-selection`, `tts-production-plan`
- Visual Producer: `provider-clip-search`, `freepik-video-search`, `pexels-video-search`, `visual-validation`, `visual-pack-plan` when source asset ids or template/media requirements are set
- InVideo AI Generator: `generation-approval-package`, `generation-iteration-plan`, `generated-clip-qa`
- Remotion Clip Builder: `remotion-scene-plan`, `remotion-template-library`, `remotion-vfx-clip`
- Remotion Video Producer: `subtitle-caption-pipeline`, `timeline-sync-plan`, `remotion-post-production`, `render-release-candidate`, `render-qa`
- Video Critic: `prepare-multimodal-review-package`, `multimodal-video-critique` when prompt/request/raw-response artifacts are written, `artifact-consistency-audit`

Acceptance criteria:

- Media-producing skills include `Media Manifest Policy`.
- Handoff summaries include `manifest_actions[]`.
- Render QA and artifact consistency audit can fail missing manifest coverage explicitly.

Current status: every listed media-producing skill now has local manifest policy or existing `manifest_actions[]` guidance. Remaining Medium skills still need fuller handoff summary shapes as part of later skill hardening.

### 4. Clarify Timeline Helper Authority

Current status: hardened in the current implementation pass.

Required rule:

- Visual Producer owns primary/fallback visual selection.
- Timeline sync consumes selected candidates or marks missing selections as blockers.
- Any helper-chosen visual must be labelled as `repair_default` or equivalent and returned for Director review.
- Timeline sync must not become the creative ranking authority.

Acceptance criteria:

- `timeline-sync-plan` says selected candidates are required inputs.
- Helper fallback behavior is documented and implemented as explicit repair-only behavior.
- Render QA and artifact audit can flag unapproved helper-selected visuals.

### 5. Keep Remotion Template Governance Aligned

Required rule:

- When a reusable Remotion template is selected, created, revised, or promoted, keep these in sync:
  - `codex/contracts/remotion-template.schema.json`
  - `remotion/templates/*.json`
  - `remotion/src/templateRegistry.tsx`
  - `codex/contracts/remotion-project.schema.json`
  - affected `remotion-clip-package` references

Acceptance criteria:

- Template-backed clips carry template id and contract path.
- Render QA checks missing or failed template contracts.
- Project-specific style does not mutate shared template internals unless a new shared version is intentionally created.

## P1: Next Skill Hardening

### Channel Intelligence

| Skill | Current problem | Required hardening |
|---|---|---|
| `source-corpus-ingestion` | Strong after evidence-graph hardening. | Keep `source_ledger[]`, `claim_ledger[]`, rights, reusable scope, evidence refs, missing assets, confidence, invalidation impact, and manifest actions explicit. |
| `channel-profile-management` | Strong after profile-delta hardening. | Keep channel profile delta, project scaffold result, changed/inherited fields, downstream invalidation, manifest status, and QA summary explicit. |
| `reference-video-breakdown` | Strong after evidence-graph hardening. | Keep `reference_beats[]`, transcript/shot/audio/caption evidence, reusable patterns, do-not-copy risks, media asset ids, model limitations, confidence, invalidation impact, and manifest actions explicit. |
| `web-content-synthesis` | Strong after one-page web capture hardening. | Keep direct URL parsing bounded, preserve `web_pages[]`, `claim_ledger[]`, annotations, image candidates, rights/robots gates, and manifest actions. |
| `style-system-extraction` | Strong after tokenized style-system hardening. | Keep style token taxonomy, policy levels, inheritance priority, do-not-copy rules, evidence/confidence, template candidates, invalidation impact, and manifest policy explicit. |
| `channel-format-synthesis` | Strong after version/freshness hardening. | Keep versioned format package, freshness/staleness policy, `must_reuse`/`must_vary`/experimental rules, anti-redundancy thresholds, evidence/confidence, and downstream invalidation explicit. |
| `scenario-alignment-brief` | Strong after scene-finding hardening. | Keep scene-level findings, claim/source coverage, channel-fit state, visual-proof state, owner routing, disposition, and required-change summary explicit. |
| `redundancy-risk-audit` | Strong after scoring/waiver hardening. | Keep redundancy score, factor-level evidence, minimum novelty checks, waiver policy, owner recommendations, and pass/block states explicit. |

### Visual Producer

| Skill | Current problem | Required hardening |
|---|---|---|
| `visual-pack-plan` | Strong after route/manifest/handoff hardening. | Keep scene-pack summary shape with route rationale, primary/fallback route, specialist handoff recommendations, template hints, approval notes, and manifest actions. |
| `visual-research-queries` | Strong after query provenance hardening. | Keep query groups by route/provider, positive/negative criteria, rejected query terms, expected evidence, provider priority, and search stop conditions. |
| `provider-clip-search` | Strong after hardening. | Keep as the general provider-search policy: canonical candidate storage, pre-download checks, scoped approvals, manifest policy, and handoff summary shape. |
| `freepik-video-search` | Strong after hardening. | Keep script flags and provider reference aligned with separate API-search, download-link, and file-download approvals. |
| `pexels-video-search` | Strong after hardening. | Keep script flags and provider reference aligned with secondary-provider policy, API attribution/rate-limit evidence, and separate file-download approval. |
| `ai-video-generation-brief` | Strong after route-brief hardening. | Keep `scene_id`, prompt intent, references, constraints, risk estimate, fallback route, and Director-routable handoff recommendation explicit. |
| `visual-validation` | Strong. | Keep as reference pattern for generated clip QA and artifact audit. |

### InVideo AI Generator

| Skill | Current problem | Required hardening |
|---|---|---|
| `invideo-model-selection` | Strong after route-decision hardening. | Keep quality mode, model, duration/aspect/resolution limits, input types, cost risk, cheaper fallback, non-AI fallback, assumptions, and approval requirement explicit. |
| `ai-video-prompt-builder` | Strong after prompt package hardening. | Keep scene id, model route, positive prompt, negative constraints, prompt guide notes, reference asset ids, settings, blocked terms, and residual risks reproducible. |
| `negative-prompt-guardrails` | Strong after output-shape hardening. | Keep `negative_prompt_mode`, separate field or positive rewrite, unsupported constraints, contradiction check, and residual risk list explicit. |
| `generation-approval-package` | Strong after approval-packet hardening. | Require exact generation dialog fields, credit/cost estimate, approval id/status, expiry/staleness notes, and blocked state when missing approval. |
| `generation-iteration-plan` | Strong after bounded-variant hardening. | Keep max variants, one-variable-change table, QA target per variant, budget ceiling, retry stop conditions, fallback triggers, and version lineage. |

### Remotion Clip Builder

| Skill | Current problem | Required hardening |
|---|---|---|
| `remotion-scene-plan` | Strong after deterministic scene-plan hardening. | Keep implementation mode, composition id, props schema, frame timing map, asset requirements, safe areas, VFX triggers, preview commands, and validation gates explicit. |
| `remotion-template-library` | Strong after template-alignment hardening. | Keep template contract, registry, Remotion project contract, instance clip package, manifest entries, and versioning aligned in one handoff. |
| `remotion-stack-selection` | Strong. | Consider an optional stack-decision artifact only if dependency choices become large. |
| `remotion-ai-component-prompt` | Good guidance but not a contract. | Add generated prompt packet shape, targeted edit plan, forbidden imports checklist, compile-error repair loop, and validation summary. |
| `remotion-vfx-clip` | Output mapping could be stronger. | Add exact `remotion-clip-package` field checklist, transparent/opaque render commands, output media asset ids, and manifest action summary. |

### Remotion Video Producer

| Skill | Current problem | Required hardening |
|---|---|---|
| `subtitle-caption-pipeline` | Strong after caption-pipeline hardening. | Keep source route, normalized Caption JSON, SRT/VTT export policy, burned-in/sidecar decision, caption style, scene ranges, QA checks, and timeline-sync handoff explicit. |
| `timeline-sync-plan` | Strong after hardening. | Keep authority lock aligned: Visual Producer selections only by default; repair fallback requires explicit flag and Director review. |
| `remotion-post-production` | Deliverables are loose. | Add expected timeline source files, composition ids, media normalization report, audio mix report, transition map, render-readiness checklist, and manifest actions. |
| `render-release-candidate` | Strong after hardening. | Keep RC packages immutable and reproducible with version, attempt id, inputs, hashes, commands, logs, metadata, manifest actions, QA, and blockers. |

### Video Critic

| Skill | Current problem | Required hardening |
|---|---|---|
| `prepare-multimodal-review-package` | Review package output should be stricter. | Add video metadata, sampled frame list, checksums if available, artifact paths, frame media asset ids, missing inputs, direct-video eligibility, and limitations. |
| `scene-by-scene-gate-review` | Final JSON shape should be explicit. | Add scene review object, criterion ids, gate results, unknown evidence policy, failed gate ids, and owner mapping. |
| `multimodal-video-critique` | Reproducibility must be mandatory in the skill. | Require prompt path, request preview path, raw response path when executed, model id, review mode, media handling approval id, frame list, and provider limitations. |
| `revision-prioritization` | Rerun dependencies are implicit. | Add affected artifacts, invalidation scope, rerun chain, approval needs, expected impact, stop/waiver recommendation, and next loop action. |

### Creative Producer

These are no longer thin after the latest skill hardening; keep the structured outputs stable:

| Skill | Required hardening |
|---|---|
| `write-scenario` | Strong after dual-layer scenario hardening; keep scene production logic, claim/source coverage, novelty policy, and downstream producibility validation explicit. |
| `scene-breakdown` | Strong; keep as pattern. |
| `voice-casting` | Strong after voice-direction hardening; keep inheritance chain, weighted rubric, rejected styles, pronunciation risks, accessibility notes, rights/consent gates, and provider handoff readiness explicit. |
| `elevenlabs-voice-selection` | Add compact output schema with inventory snapshot path, ranked candidates, selected voice, approval state, continuity risks, and dry-run evidence. |
| `tts-production-plan` | Strong; ensure human narration route still uses the voiceover package. |

## P2: Optional Helpers And Examples

Add these only after prompt/spec hardening, or when real runs show repeated drift:

- Optional `validate_artifact.py`: validate JSON against schemas, check required paths, no API calls, no destructive writes, no creative judgment.
- Optional handoff validator: check persisted `agent-handoff` files for existing skills, allowed paths, output contracts, budget policy, and stop conditions.
- Completed inventory/audit script: `codex/scripts/audit_agent_system.py` generates counts and catches stale script refs, Director handoff drift, approval-gate wording gaps, and section-hardening status.
- Optional Remotion app setup checker: only if checklist-based Remotion setup fails repeatedly.
- Golden prompts and richer fixture artifacts for contracts not covered by the current minimal templates.
- Remotion template override examples for project > channel > shared resolution using real or representative production data.
- Additional golden examples using real channel/project data after the first production run.
- Reviewer prompt archive and raw model response archive policy.
- Run report generation from the production-run ledger.

## First Implementation Batch

Started in the current hardening pass:

1. [x] Update this plan to current inventory and safer priorities.
2. [x] Harden `clip-candidate-ranking`.
3. [x] Harden `generated-clip-qa`.
4. [x] Harden `render-qa`.
5. [x] Harden `artifact-consistency-audit`.

## Second Implementation Batch

Started after provider-candidate storage review:

1. [x] Harden `provider-clip-search`.
2. [x] Harden `freepik-video-search`.
3. [x] Tighten `search_freepik_videos.py` approval flags so API search, download-link retrieval, and file download cannot be authorized accidentally by one broad flag.
4. [x] Document durable candidate storage under `visuals/candidates/` and downloaded provider media under `source-media/provider-clips/`.
5. [x] Add `pexels-video-search` as a secondary/free provider route with API-search approval, attribution/rate-limit evidence, and separate file-download approval.

After the batch:

- Run a section scan for all four critical skills.
- Run a Director handoff-map coverage scan.
- Run duplicate skill-name scan.
- Run contract JSON parse.
- Update the integrated spec count and Freepik row if not already aligned.

## Third Implementation Batch

Started for timeline authority and render reproducibility:

1. [x] Harden `timeline-sync-plan`.
2. [x] Tighten `build_timeline_sync_plan.py` so strict mode consumes Visual Producer selections only.
3. [x] Add explicit `--allow-repair-default` helper fallback that marks visuals as `repair_default` and requires Director review.
4. [x] Harden `render-release-candidate` as an immutable RC attestation package.

## Fourth Implementation Batch

Started for first media manifest propagation:

1. [x] Confirm `timeline-sync-plan` reports `manifest_actions[]`.
2. [x] Confirm `render-release-candidate` reports `manifest_actions[]`.
3. [x] Harden `source-corpus-ingestion` with source ledger fields, evidence requirements, rights/reuse policy, and manifest actions.
4. [x] Harden `reference-video-breakdown` with timecoded evidence, sidecar artifact coverage, do-not-copy risks, and manifest actions.

## Fifth Implementation Batch

Started for Channel Intelligence evidence-graph hardening:

1. [x] Add explicit `source_ledger[]`, `claim_ledger[]`, downstream guidance, and invalidation impact requirements to `source-corpus-ingestion`.
2. [x] Add explicit `reference_beats[]`, beat-level evidence categories, do-not-copy risks, confidence, and invalidation impact requirements to `reference-video-breakdown`.
3. [x] Keep both skills contract-compatible without adding schemas by using additive fields in `reference-analysis` artifacts.

## Sixth Implementation Batch

Started for skill-bundle layout and high-risk routing hardening:

1. [x] Move one-skill Visual Producer provider scripts into skill-local `scripts/` folders.
2. [x] Document script placement rules in `AGENTS.md` and `agent-responsibility-map.md`.
3. [x] Add `codex/scripts/audit_agent_system.py` for skill script refs, Director handoff coverage, frontmatter, approval gates, and hardening status.
4. [x] Harden `visual-research-queries`, `visual-pack-plan`, and `ai-video-generation-brief`.
5. [x] Harden all InVideo AI Generator skills to the local hardening template.
6. [x] Harden `decompose-video-request` with production brief, path map, agent plan, approval gates, and handoff summary.
7. [x] Add missing approval stop language to `redundancy-risk-audit`, `voice-casting`, and `remotion-vfx-clip`.

## Validation Commands

Use local scans before adding new scripts:

```powershell
Get-ChildItem -Path codex\agents -Recurse -Filter SKILL.md
rg -n "## Inputs|## Workflow|## Required Output|## Contract Fields Populated|## Status Policy|## Evidence Required|## Media Manifest Policy|## Approval And Stop Conditions|## Definition Of Done|## Handoff Summary Shape" codex\agents
python codex/scripts/audit_agent_system.py --strict
```

Existing Remotion validation to keep using when Remotion code changes:

```powershell
cd remotion
npm run lint
npm run still:main
```

## Definition Of Done For The Hardening Effort

- No stale architecture counts remain in active planning docs.
- P0 critical skills have structured outputs, status policy, evidence requirements, media manifest policy, stop conditions, and definition of done.
- Handoff map remains complete for all non-Director local skills.
- Media-producing skills report manifest actions.
- Timeline helpers cannot silently become creative visual-selection authority.
- Critique dry runs and executed reviews are reproducible from prompt/request/raw response/review package paths.
- Remotion template contracts, registry, project contract, and clip package refs stay aligned.
- The next production run can be audited from contracts without relying on memory from the main Codex thread.
