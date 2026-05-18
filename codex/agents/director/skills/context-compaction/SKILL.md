---
name: context-compaction
description: Compact Video Factory autonomous run state into a durable resume summary. Use when the Director finishes a phase, handoff, review-loop iteration, or post-run change; when context is growing; before or after /compact-style resumes; and whenever the next step should reload only a small authoritative working set from project artifacts.
---

# Context Compaction

Use this as a Director skill. The goal is not to summarize everything; the goal is to preserve enough state for the Director to resume autonomous work from files without relying on chat history.

## Inputs

- Current user request and any post-run change request.
- `production_run_path` matching `codex/contracts/production-run.schema.json`.
- `project_path`, `channel_profile_path`, `channel_format_path`, `producer_criteria_path`, `media_asset_manifest_path`, `remotion_project_contract_path`, and other known artifact paths.
- Latest handoff results, approvals, blockers, review loops, validation results, and changed files.
- Current phase, next intended phase, and any context-risk reason such as long research output, large tool output, review-loop iteration, or expected resume.

## Workflow

1. Treat persisted artifacts as authoritative. Prefer contract paths, artifact ids, hashes, statuses, and evidence refs over conversational recollection.
2. Read the run ledger and only the artifact indexes needed to understand current status. Do not bulk-load large transcripts, raw critique responses, videos, frame sets, generated media, or full source documents unless they are needed for the immediate next decision.
3. Classify information into:
   - `pinned`: user intent, acceptance criteria, approval decisions, current blockers, current phase, active handoffs, selected artifact paths, gate decisions, and next actions.
   - `reload_next`: exact files the next phase must read.
   - `summarized`: completed phase results, validation outcomes, assumptions, risks, and why artifacts are trusted or stale.
   - `archived`: raw tool outputs, full research notes, frame samples, media files, raw provider responses, render logs, and old critique reports that can be found by path.
   - `dropped`: duplicate prose, stale intermediate reasoning, rejected options that are already represented by a decision record, and noisy terminal output with no current diagnostic value.
4. Update `production-run.context_state` with a compact state summary, current phase summary, reload list, open decisions, blockers, recent changes, invalidated artifacts, and next actions.
5. Append a `context_snapshots[]` entry when crossing a phase boundary, after a review-loop iteration, after user changes, before a likely context reset, or after large research/tool output. Put snapshot files under `channels/<channel-slug>/projects/<project-slug>/runs/<run-id>/context/` when a run folder exists.
6. Keep recent working context small. The next Director step should load `AGENTS.md`, Director `AGENT.md`, this run ledger, and only the files listed in `context_state.artifacts_to_reload_next`.
7. If compaction reveals missing required paths, stale artifacts, or unresolved approvals, mark them in the run ledger instead of hiding them in a prose summary.

## Required Output

Update the run ledger with this shape:

```json
{
  "context_state": {
    "status": "fresh | compacted | needs_compaction | stale | resume_required",
    "working_set_summary": "short summary of what matters now",
    "current_phase_summary": "phase, completed work, and immediate objective",
    "last_resume_summary": "what a resumed Director must know first",
    "context_snapshot_path": "repo-relative path or empty when not written",
    "important_open_decisions": ["string"],
    "active_blockers": ["string"],
    "recent_user_requests": ["string"],
    "recent_changes": ["string"],
    "stale_or_invalidated_artifacts": ["repo-relative path"],
    "artifacts_to_reload_next": [
      {
        "kind": "contract | skill | spec | media_manifest | qa | render | critique | source",
        "path": "repo-relative path",
        "reason": "why the next step needs this file"
      }
    ],
    "next_actions": ["string"],
    "context_budget_policy": "keep only the current phase, next handoff, approvals, blockers, and reload paths in active context",
    "last_compacted_at": "ISO-like timestamp or run-local timestamp"
  },
  "context_snapshots": [
    {
      "snapshot_id": "string",
      "path": "repo-relative path",
      "phase": "string",
      "reason": "phase_boundary | review_loop | user_change | context_pressure | resume | manual",
      "summary": "short snapshot summary",
      "created_at": "ISO-like timestamp or run-local timestamp"
    }
  ]
}
```

When a separate snapshot file is written, use the same fields plus `source_artifacts[]`, `preserved_decisions[]`, `reload_instructions[]`, and `discarded_context_notes[]`.

## Contract Fields Populated

- `production-run.context_state.status`
- `production-run.context_state.working_set_summary`
- `production-run.context_state.current_phase_summary`
- `production-run.context_state.last_resume_summary`
- `production-run.context_state.context_snapshot_path`
- `production-run.context_state.important_open_decisions[]`
- `production-run.context_state.active_blockers[]`
- `production-run.context_state.recent_user_requests[]`
- `production-run.context_state.recent_changes[]`
- `production-run.context_state.stale_or_invalidated_artifacts[]`
- `production-run.context_state.artifacts_to_reload_next[]`
- `production-run.context_state.next_actions[]`
- `production-run.context_state.context_budget_policy`
- `production-run.context_state.last_compacted_at`
- `production-run.context_snapshots[]`

## Status Policy

- `fresh`: no compaction needed; current ledger already has a usable working set.
- `compacted`: state was compressed and the next reload list is current.
- `needs_compaction`: large outputs or long phase history exist and should be summarized before more work.
- `stale`: resume state points to superseded or invalidated artifacts.
- `resume_required`: a resumed Director must read the reload list before continuing.

Use run status `blocked` only when compaction finds missing required artifacts, approvals, or impossible recovery gaps that prevent the next phase.

## Evidence Required

- Every important decision must point to a producer criteria path, handoff id, artifact path, approval id, blocker, critique finding id, or validation result when available.
- Every reload item must have a reason tied to the next action.
- Every stale artifact must include why it is stale or what invalidated it.
- Do not preserve raw long outputs in the active summary. Preserve their paths and the specific lines, ids, timestamps, or findings that matter.

## Approval And Stop Conditions

Stop and ask the user only when the next step cannot be determined because the user intent changed, a paid/rights approval is missing, required source media is absent, or the run ledger cannot identify the authoritative project/run artifacts.

Do not ask approval merely because context is large. Compact, write the reload list, and continue.

## Definition Of Done

- The run ledger contains an up-to-date `context_state`.
- The next step can be executed by reading only the reload list plus required repo instructions.
- Open decisions, blockers, approvals, stale artifacts, and next actions are explicit.
- Large raw context is represented by artifact paths, evidence ids, timestamps, checksums, or summaries.
- No production artifact is treated as complete solely because the compact summary says so; completion comes from the owning artifact contract and validation evidence.

## Handoff Summary Shape

Return this summary to the Director:

```json
{
  "status": "complete | blocked | needs_revision",
  "artifact_paths": ["production-run path", "context snapshot path when written"],
  "changed_files": ["repo-relative paths"],
  "populated_contracts": ["codex/contracts/production-run.schema.json"],
  "validation_performed": ["checked authoritative artifact paths", "updated reload list"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```

## Resume Prompt Shape

When resuming after compaction, the Director should start with:

```text
You are the Director for the Video Factory project. Read AGENTS.md, codex/agents/director/AGENT.md, the production run ledger, and only the files listed in production-run.context_state.artifacts_to_reload_next. Treat persisted artifacts as authoritative, preserve existing ids, continue from production-run.context_state.next_actions, and stop only for the approval or blocker conditions recorded in the run ledger.
```
