# Artifact Problem Handoff Routing

This is the Director reference for turning cross-artifact problems into formal `agent-handoff` records. Use it for findings from agent boundary checks, `scene-artifact-sync`, Remotion visual debugging, render QA, Video Critic, and post-run user changes.

## Codex References

Load these local references before routing a repair:

- `AGENTS.md`: ownership model, production-agent boundaries, pipeline, and base subagent instruction.
- `codex/agents/director/AGENT.md`: Director local skills, handoff skill map, inputs, outputs, and rules.
- `codex/contracts/agent-handoff.schema.json`: executable handoff shape.
- `codex/contracts/production-run.schema.json`: review loop, invalidation graph, handoff ledger, blockers, and change requests.
- `codex/contracts/scene-artifact-sync.schema.json`: scene lineage status and repair-owner fields.
- `codex/agents/director/skills/scene-artifact-sync/SKILL.md`: scene identity, props lineage, stale artifact detection, and repair routing.
- `codex/agents/director/skills/autonomous-production-run/SKILL.md`: canonical handoff fields, run loop, invalidation rules, and post-run change handling.
- `codex/agents/director/skills/quality-gated-review-loop/SKILL.md`: revision dependency rules after Video Critic findings.
- `codex/agents/video-critic/skills/artifact-consistency-audit/SKILL.md`: final artifact consistency findings and owner mapping.
- `codex/specs/agent-system-integrated-spec.md`: shared relation rules, evidence rules, and handoff rules.
- `codex/architecture/agent-responsibility-map.md`: per-agent ownership, runtime paths, feeds, and handoff relations.

## Routing Policy

Agents may cross-review only the inputs they must consume safely. They must not silently mutate another production agent's authoritative artifact.

When an agent finds an upstream or cross-artifact problem, it should return a structured finding or handoff recommendation. The Director then:

1. Runs or refreshes `scene-artifact-sync` when scene-linked artifacts may have drifted.
2. Maps the finding to the artifact owner below.
3. Marks affected downstream artifacts stale or invalidated in `production-run.invalidation_graph` when the dependency chain is non-trivial.
4. Creates a formal `agent-handoff` with exact inputs, allowed paths, local skills, output contract, budget policy, stop conditions, and definition of done.
5. Re-runs downstream sync, timeline, render, and critique only for affected scope unless the scenario or channel format changed globally.

Use `Director` as the repair owner only for approvals, waivers, conflicting valid repairs, cross-agent path/ledger integration, or final release decisions.

## Finding Shape

Normalize findings before routing:

```json
{
  "problem_id": "string",
  "finding_source": "boundary_check | scene_artifact_sync | remotion_visual_debugging | render_qa | video_critic | user_change",
  "severity": "blocker | major | minor | note",
  "problem_type": "string",
  "scene_id": "string",
  "scene_index": 0,
  "timestamp_seconds": 0,
  "source_artifact": "repo-relative path",
  "affected_artifacts": ["repo-relative path"],
  "evidence_refs": ["string"],
  "current_owner": "agent-name",
  "recommended_action": "string"
}
```

## Owner Routing Matrix

| Problem type | Correct owner | Skills to read | Output contract |
|---|---|---|---|
| Missing source evidence, weak claim ledger, stale reference analysis, source rights ambiguity, reusable channel rule drift, channel format/VFX rule drift, redundancy risk | `channel-intelligence` | `source-corpus-ingestion`, `reference-video-breakdown`, `web-content-synthesis`, `style-system-extraction`, `channel-format-synthesis`, `scenario-alignment-brief`, or `redundancy-risk-audit` as applicable | `reference-analysis.schema.json`, `channel-profile.schema.json`, or `channel-format.schema.json` |
| Scenario scene ids, scene order, scene timing, narration, claims, on-screen text, source claim use, voice direction, TTS plan | `creative-producer` | `write-scenario`, `scene-breakdown`, `voice-casting`, `elevenlabs-voice-selection`, or `tts-production-plan` as applicable | `scenario.schema.json` or `voiceover-package.schema.json` |
| Scene visual pack missing/stale, duplicate scene pack, visual route conflict, candidate requirements conflict, selected candidate/ranking issue, provider search insufficiency, visual rights route issue | `visual-producer` | `visual-pack-plan`, `visual-research-queries`, `provider-clip-search`, provider-specific search skill, `visual-validation`, or `clip-candidate-ranking` as applicable | `scene-visual-pack.schema.json` or `clip-candidate.schema.json` |
| AI generation prompt/package mismatch, model/settings mismatch, negative prompt issue, approval packet stale, generated output QA failure, reroll/variant planning | `invideo-ai-generator` | `invideo-model-selection`, `ai-video-prompt-builder`, `negative-prompt-guardrails`, `generation-approval-package`, `generation-iteration-plan`, or `generated-clip-qa` as applicable | `ai-video-generation-package.schema.json` or `clip-candidate.schema.json` |
| Remotion props stale, short clip does not match scene pack, reusable template mismatch, VFX overlay issue, component code defect, clip-level dense layout, ugly/broken clip animation | `remotion-clip-builder` | `remotion-scene-plan`, `remotion-template-library`, `remotion-stack-selection`, `remotion-ai-component-prompt`, `remotion-vfx-clip`, or `vfx-quality-performance-hardening` as applicable | `remotion-clip-package.schema.json`, `remotion-template.schema.json`, or `clip-candidate.schema.json` |
| Timeline scene order/frame range mismatch, caption/subtitle placement, audio mix, transition timing, assembled-scene alignment, dense-region overlap in the full timeline, render/export failure, release-candidate package issue | `remotion-video-producer` | `subtitle-caption-pipeline`, `timeline-sync-plan`, `remotion-post-production`, `remotion-visual-debugging`, `render-release-candidate`, or `render-qa` as applicable | `timeline-sync-plan.schema.json` or `render-package.schema.json` |
| Missing review evidence, scene-by-scene critique gap, final viewer-experience problem, artifact consistency audit, revision priority or rerun-scope uncertainty after render | `video-critic` | `prepare-multimodal-review-package`, `scene-by-scene-gate-review`, `artifact-consistency-audit`, `multimodal-video-critique`, or `revision-prioritization` as applicable | `critique-report.schema.json` |
| Approval, spend, license, waiver, conflicting valid repairs, or cross-artifact graph decision | `director` | `producer-criteria-prompt`, `scene-artifact-sync`, `quality-gated-review-loop`, `context-compaction`, or `autonomous-production-run` as applicable | `producer-criteria.schema.json`, `scene-artifact-sync.schema.json`, `production-run.schema.json`, or `agent-handoff.schema.json` |

## Handoff Construction Checklist

Every repair handoff must include:

- `handoff_id`, `run_id`, `request_id`, `from_agent`, `to_agent`, `phase`, and `status`
- `project_path`, `producer_criteria_path`, `media_asset_manifest_path`, and `scene_artifact_sync_report_path` when available
- exact `scene_id`, `scene_index`, `scene_pack_id`, `scenario_scene_fingerprint`, source scenario path, visual pack path, and props requirements for scene-linked repairs
- source finding ids, timestamps, sampled frames, screenshots, console logs, render logs, or artifact fields that prove the problem
- allowed paths limited to the target agent's owned artifacts plus required input paths
- only target-agent local `skills_to_read`, plus explicitly approved built-in skills
- output contract and expected artifacts
- definition of done that names the repaired artifact and validation evidence
- stop conditions for approvals, missing source, rights, repeated failure, or impossible technical blockers
- budget policy that blocks paid APIs, generation credits, licensed downloads, external critique, or paid templates until approval

## Handoff Templates

Use these as templates, filling in concrete paths and ids.

### Scene Visual Pack Repair

```json
{
  "to_agent": "visual-producer",
  "phase": "repair_visual_pack",
  "objective": "Repair stale or missing scene visual pack rows for the listed scene ids without changing scenario scene identity.",
  "skills_to_read": [
    "codex/agents/visual-producer/skills/visual-pack-plan/SKILL.md",
    "codex/agents/visual-producer/skills/visual-validation/SKILL.md",
    "codex/agents/visual-producer/skills/clip-candidate-ranking/SKILL.md"
  ],
  "output_contract": "codex/contracts/scene-visual-pack.schema.json",
  "definition_of_done": [
    "Exactly one current scene pack exists for every affected scenario scene.",
    "Scene ids, scene indexes, timings, fingerprints, and prop requirements match the current scenario.",
    "Route and candidate requirements are current and downstream handoff recommendations are Director-routable."
  ]
}
```

### Remotion Props Or Clip Repair

```json
{
  "to_agent": "remotion-clip-builder",
  "phase": "repair_remotion_clip",
  "objective": "Repair the affected Remotion props, template instance, short clip, or VFX overlay so it matches the current scenario scene and scene visual pack.",
  "skills_to_read": [
    "codex/agents/remotion-clip-builder/skills/remotion-scene-plan/SKILL.md",
    "codex/agents/remotion-clip-builder/skills/remotion-template-library/SKILL.md",
    "codex/agents/remotion-clip-builder/skills/remotion-vfx-clip/SKILL.md",
    "codex/agents/remotion-clip-builder/skills/vfx-quality-performance-hardening/SKILL.md"
  ],
  "output_contract": "codex/contracts/remotion-clip-package.schema.json",
  "definition_of_done": [
    "Clip package records current source scenario, scene visual pack, scene pack id, scene fingerprint, and props sync status.",
    "Preview/still/render evidence is analyzed, not only generated.",
    "Broken or ugly animation is repaired or replaced with a deterministic route and evidence."
  ]
}
```

### Timeline Or Render Repair

```json
{
  "to_agent": "remotion-video-producer",
  "phase": "repair_timeline_or_render",
  "objective": "Repair timeline, caption, audio, alignment, dense-region overlap, animation readability, or render package defects without changing upstream scene/visual ownership.",
  "skills_to_read": [
    "codex/agents/remotion-video-producer/skills/timeline-sync-plan/SKILL.md",
    "codex/agents/remotion-video-producer/skills/remotion-visual-debugging/SKILL.md",
    "codex/agents/remotion-video-producer/skills/render-release-candidate/SKILL.md",
    "codex/agents/remotion-video-producer/skills/render-qa/SKILL.md"
  ],
  "output_contract": "codex/contracts/render-package.schema.json",
  "definition_of_done": [
    "Timeline sync consumes only current scene-linked artifacts.",
    "Dense scenes have sampled-frame and browser/DOM evidence when inspectable.",
    "Render package is reproducible and records scene artifact sync provenance."
  ]
}
```

### Final Critique Or Evidence Repair

```json
{
  "to_agent": "video-critic",
  "phase": "repair_review_evidence_or_recritique",
  "objective": "Prepare missing review evidence or rerun independent critique for the updated render candidate.",
  "skills_to_read": [
    "codex/agents/video-critic/skills/prepare-multimodal-review-package/SKILL.md",
    "codex/agents/video-critic/skills/scene-by-scene-gate-review/SKILL.md",
    "codex/agents/video-critic/skills/artifact-consistency-audit/SKILL.md",
    "codex/agents/video-critic/skills/revision-prioritization/SKILL.md"
  ],
  "output_contract": "codex/contracts/critique-report.schema.json",
  "definition_of_done": [
    "Every required scene has review status or an explicit evidence limitation.",
    "Findings include owner agent, affected artifacts, timestamps or frame refs, and delivery-blocking status.",
    "Revision priorities are Director-routable without hidden production edits."
  ]
}
```

## Downstream Rerun Rules

- Channel/source, channel format, or scenario repairs usually invalidate visual pack, specialist outputs, timeline, render, and critique.
- Visual pack or candidate repairs invalidate affected AI/Remotion specialist outputs, timeline, render, and critique.
- AI generation or Remotion clip repairs invalidate affected timeline scenes, render, and critique.
- Timeline/render repairs usually invalidate only render and critique unless they reveal stale upstream scene-linked artifacts.
- Critic evidence repairs do not invalidate production artifacts unless the new critique finds a production defect.

