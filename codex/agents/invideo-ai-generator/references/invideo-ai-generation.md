# InVideo AI Generation Reference

Use this reference when preparing InVideo AI or model-backed AI video clip generation packages.

## InVideo Routes

- Agent One is a conversational AI filmmaker that thinks through a brief, builds scene by scene, and edits through back-and-forth context. Use it for full InVideo-managed creative workflows or when the brief needs script, visuals, subtitles, voice, and music assembled together.
- Prompt Guides are standing instructions for models. InVideo exposes defaults for Nano Banana, Veo, Sora, Kling, and ElevenLabs Voice Design. Use project prompt guides for repeated brand, camera, lighting, character, or voice constraints.
- Basic uses stock library media and is cheap. Use for simple background visuals or when generated performances are unnecessary.
- Pro generates every pixel with more natural acting and movement at higher credit cost. Use for important clips where realism matters but Ultra is not justified.
- Ultra uses flagship models for higher realism and brand/product integration at the highest credit cost. Use only when quality risk justifies the spend.

## Model Notes

- Sora 2 in InVideo:
  - Use Ultra for full story videos.
  - Use Sora 2 Pro under Agents & Models for 4-12 second clips.
  - You can write "use Sora 2" for full videos using Sora visuals, but still preserve approval before spend.
- Veo 3.1 in InVideo:
  - Duration: 4-8 seconds.
  - Resolution: 720p-4K.
  - Aspect ratios: 16:9 and 9:16.
  - Inputs: text or up to 3 images.
  - Prompt formula: Camera/Lens -> Subject -> Action -> Environment -> Lighting -> Style -> Audio.
  - Use first and last frames for transition continuity when available.
- Kling 3.0 in InVideo:
  - Duration: 3-15 seconds.
  - Resolution: 720p-1080p.
  - Aspect ratios: 16:9 and 9:16.
  - Inputs: text, image, or video.
  - Prompt structure: scene, characters, action, and camera in one structured statement.
  - Strong fit for native audio, multi-shot sequencing, consistent multi-character scenes, and lip sync.

## Positive Prompt Structure

Use the shortest prompt that fully specifies the shot:

1. Shot/camera/lens: close-up, wide tracking shot, handheld, locked camera, dolly, crane, macro, over-the-shoulder.
2. Subject: the person, product, character, object, or environment.
3. Action: one primary physical action for a short clip.
4. Environment: location, era, weather, background motion.
5. Lighting/style: dawn, neon, softbox, cinematic, documentary, UGC, premium product ad.
6. Audio: ambience, dialogue, music tone, native sound, or silent.
7. Constraints: aspect ratio, duration, reference asset usage, brand/product visibility.

For image-to-video, focus on motion rather than re-describing everything in the image. Mention subject motion, environmental motion, camera motion, timing, direction, and speed.

## Negative Prompt Policy

Keep an explicit negative constraint list for internal planning, but adapt it to the target model:

- For models with negative prompt support, provide a comma-separated list of unwanted visible elements or artifacts. Do not write command phrases such as "no" or "do not".
- For routes that perform better with positive phrasing, rewrite negatives as the desired state. Example: replace "no camera movement" with "locked camera, camera remains still".
- Avoid contradictions between the positive prompt and negative constraints.
- Common negative constraints: warped hands, extra fingers, distorted faces, unreadable text, random logos, watermark, brand mismatch, flicker, low-resolution blur, overexposed highlights, sudden style change, unwanted subtitles, unwanted camera shake.

## Generation Checklist

Before approval:

- Scene id, candidate id, duration, aspect ratio, resolution, platform, and route are set.
- Model choice and quality mode match the scene risk and budget.
- Positive prompt is concrete and not overloaded.
- Negative constraints are separated or converted correctly for the target model.
- Reference assets have local paths, labels, rights notes, and intended use.
- Credit/cost estimate and approval status are recorded.

After generation:

- Output path or URL is captured.
- Prompt/version, model, duration, aspect ratio, and credit use are recorded.
- Visual fit, motion, artifacts, audio, continuity, rights, and editability are scored.
- Best output becomes a clip candidate; failed variants keep rejection reasons.
