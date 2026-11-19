---
name: fable-director
description: Produce a finished vertical 2D fable from a script or an uploaded example. Install or check the Linux toolchain, direct a Kokoro Hindi narrator, animate a recurring prop, and deliver a verified MP4 and editable project.
---

# Direct and render the episode

For the PaperBoat kit, open the folder containing `README.md` and `scripts/setup.sh`. Read `docs/production-guide.md`. Run `bash scripts/setup.sh`. Check the actual output. The included demo has a completed MP4, Hindi SRT, timing manifest and clean voice stem.

For a new episode, start with the approved script or use the fable-script workflow. Work in a sibling copy so the existing episode can be replayed. If an uploaded reference is present, run `python3 scripts/inspect_reference.py INPUT.mp4 OUTPUT_DIR`. Record its measured technical settings and visible storytelling decisions before choosing which to preserve.

1. Block the change in the prop through at least three states. Specify its position, scale, which hand supports it, release frame and final state. Draw a distinct silhouette for each character. Plan a wide for geography, a close shot for the decision and an insert for the physical consequence.
2. Generate the voice before locking the edit. For Hindi use clean Devanagari, Kokoro hm_omega and the hi phonemizer. Give the question a lift through punctuation and give the answer room through the post-line pause. Keep performance notes out of the spoken string. For a different language choose an appropriate model voice and test the actual words. Preserve the clean WAV.
3. Measure each generated line. Put start, speech end and scene end in the manifest. Use those intervals for subtitles and frame boundaries. New dialogue requires regenerated timing.
4. For new material, edit `assets/story.json`, add shot dispatches and poses in `src/scenes.py`, draw props and rigs in `src/art.py`, and update shot-keyed Foley in `src/mix.py`. Check the final title, any baked lettering, filenames and verification targets. Reusing only the old animation with unrelated dialogue fails the brief.
5. Render a 3–5 second test of the hardest handoff, release or turn. Inspect at phone size and at contact frames. Check eyelines, open hands, readable expressions, caption spacing, screen edges and the position of the prop across cuts. Use anticipation and settling on the decisive gesture; hold the reaction.
6. Render the complete edit and review its beginning, every cut and its final image. Run the full decode and measure loudness. Output H.264, yuv420p, AAC, 9:16, 30 fps. Reference scale is 720×1280; 1080×1920 is the larger delivery preset. Offer selectable subtitles or a separate SRT. Re-compose text if the creator asks for burned-in captions.
7. Return the actual MP4, editable source, script, measured subtitles and a short validation report. Identify any blocked installation, missed listening check or rendering failure accurately. Keep the scope to production unless publication is requested.

If this skill is imported without the project, obtain or extract the accompanying kit for the executable commands. The directing workflow can also guide another renderer when the user supplies one.
