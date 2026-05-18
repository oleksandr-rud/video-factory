# Shared Scripts

These helpers are reusable across agents. Agent-specific scripts remain in each agent folder when they need contract-aware behavior.

## OpenRouter Video Request

`openrouter_video_request.py` sends a generic prompt plus a video to OpenRouter. It can optionally attach still images. By default it writes a dry-run request preview and does not call the API.

Dry run:

```powershell
python codex/scripts/openrouter_video_request.py `
  --prompt "Describe the video scene by scene." `
  --video "C:\path\video.mp4" `
  --output "tmp\openrouter-request-preview.json"
```

Execute after approval:

```powershell
python codex/scripts/openrouter_video_request.py `
  --prompt-file "prompt.txt" `
  --video "C:\path\video.mp4" `
  --image "C:\path\frame-001.jpg" `
  --output "tmp\openrouter-response.json" `
  --execute `
  --approved
```

Use `codex/agents/video-critic/scripts/run_openrouter_video_critique.py` for production critique reports because it loads review assets, production artifacts, sampled frames, and writes `critique-report.schema.json`.

## Agent System Audit

`codex/scripts/audit_agent_system.py` checks the project-internal skill inventory, Director handoff coverage, skill script references, approval-gate wording for API/paid-looking skills, and the local hardening section template.

Run:

```powershell
python codex/scripts/audit_agent_system.py
```

Use `--json` for a machine-readable report and `--strict` in CI-style checks when missing script references, handoff drift, missing frontmatter, or missing approval-gate wording should fail the command.

## Reference Video Analysis

`codex/agents/channel-intelligence/scripts/analyze_reference_video.py` prepares deterministic reference-video evidence for Channel Intelligence. It writes `reference-analysis.schema.json`-shaped output plus sidecars such as `probe.json`, `scenes.json`, `frame-samples.json`, and `keyframes/`. It does not call paid or cloud models by default.

Dry local run:

```powershell
python codex/agents/channel-intelligence/scripts/analyze_reference_video.py `
  --video "C:\path\reference.mp4" `
  --source-id "source-ref-001" `
  --work-dir "channels/demo/projects/sample/source-media/reference-analysis/source-ref-001" `
  --output "channels/demo/projects/sample/source-media/reference-analysis/source-ref-001/reference-analysis.json"
```

With manifest update:

```powershell
python codex/agents/channel-intelligence/scripts/analyze_reference_video.py `
  --video "C:\path\reference.mp4" `
  --source-id "source-ref-001" `
  --work-dir "channels/demo/projects/sample/source-media/reference-analysis/source-ref-001" `
  --output "channels/demo/projects/sample/source-media/reference-analysis/source-ref-001/reference-analysis.json" `
  --media-asset-manifest "channels/demo/projects/sample/media-asset-manifest.json" `
  --update-media-asset-manifest
```

Optional tools:

- `ffprobe` and `ffmpeg` enable metadata and keyframe extraction.
- PySceneDetect improves scene boundary detection; without it the script uses fallback time segments.
- `tesseract` is used only when `--enable-ocr` or `REFERENCE_ANALYSIS_ENABLE_OCR=true` is set.
- WhisperX, CLIP embeddings, and direct-video model observations are not executed by this local MVP script. Run those externally or through an approved provider path, then pass `--transcript-path`, `--embedding-index-path`, or `--model-observation-path`.

## Web Content Parsing

`codex/agents/channel-intelligence/scripts/parse_web_content.py` prepares deterministic one-page evidence for supplied article/blog/news/product/source URLs. It writes a `reference-analysis.schema.json`-shaped fragment plus `raw.html`, `extracted.json`, `extracted.md`, `source-report.json`, `source-report.md`, `annotations.json`, and `images/image-manifest.json`. It does not crawl related pages by default.

Dry local page capture:

```powershell
python codex/agents/channel-intelligence/scripts/parse_web_content.py `
  --url "https://example.com/post" `
  --source-id "source-web-001" `
  --work-dir "channels/demo/projects/sample/source-media/web-content/source-web-001" `
  --output "channels/demo/projects/sample/source-media/web-content/source-web-001/reference-analysis.json"
```

With manifest update:

```powershell
python codex/agents/channel-intelligence/scripts/parse_web_content.py `
  --url "https://example.com/post" `
  --source-id "source-web-001" `
  --work-dir "channels/demo/projects/sample/source-media/web-content/source-web-001" `
  --output "channels/demo/projects/sample/source-media/web-content/source-web-001/reference-analysis.json" `
  --media-asset-manifest "channels/demo/projects/sample/media-asset-manifest.json" `
  --update-media-asset-manifest
```

Approved image downloads:

```powershell
python codex/agents/channel-intelligence/scripts/parse_web_content.py `
  --url "https://example.com/post" `
  --source-id "source-web-001" `
  --work-dir "channels/demo/projects/sample/source-media/web-content/source-web-001" `
  --output "channels/demo/projects/sample/source-media/web-content/source-web-001/reference-analysis.json" `
  --download-images `
  --approved-downloads
```
