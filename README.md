# Meera ki 23 Naavein

A Hindi animated fable about a father who keeps his daughter's paper boats behind glass. One rainy day she asks which one is fastest.

**Watch** `output/Meera_ki_23_Naavein.mp4`. The archive already includes the finished film, selectable Hindi captions, clean narration and both Kokoro model files.

## Use with Claude

**Claude Code on Linux or WSL.** Extract the full archive, open the `PaperBoat` directory in Claude Code and paste the prompt in `CLAUDE_PROMPT.md`. Two project skills live in `.claude/skills/`. You can invoke them as `/fable-script` and `/fable-director`.

**Claude chat with file execution.** If your Claude account supports custom skills, import the two individual skill ZIPs in `claude-import/` and enable them. Give Claude the project files and `CLAUDE_PROMPT.md`. If your upload surface has a small attachment limit, use `claude-import/PaperBoat_light.zip` as the executable project. The light kit includes source and the existing voice stem. It fetches the two verified models during setup. The full kit already contains those model files. The execution environment must allow the required package installations or already have those packages. Opening a ZIP alone does not run its installer.

## Rebuild

From the extracted project root, in a Bash shell:

```bash
bash scripts/setup.sh
bash scripts/build.sh
```

The installer checks Debian/Ubuntu rendering dependencies, installs missing system packages when privileges allow, and creates a project-local voice environment when needed. It checks both model hashes, synthesizes a real Hindi phrase, tests Devanagari shaping, and checks the encoders. The build regenerates the narration, measured cues and SRT, synthesizes the score, streams frames to FFmpeg, muxes the movie and decodes it for verification. Rebuilding replaces the files in `output/` in that project copy.

| Requirement | Function |
| --- | --- |
| Bash and Python | Setup and orchestration. Voice Python supports 3.10–3.13. Set VOICE_PYTHON to choose the interpreter. |
| FFmpeg and ffprobe | Read the reference, encode H.264 and AAC, mux subtitles, measure loudness and verify the export. |
| Pycairo / Cairo, NumPy, Pillow with RAQM | Vector artwork, per-frame animation, grain and shaped Devanagari lettering. The default drawing interpreter is /usr/bin/python3. |
| Noto Serif Devanagari | The final handwritten-style note. Override the path with DEVANAGARI_FONT if needed. |
| kokoro-onnx, ONNX Runtime, eSpeak NG phonemizer, SoundFile | CPU inference, Hindi pronunciation and 24 kHz PCM voice export. Python dependencies are in requirements-voice.txt. |
| Quantized Kokoro v1.0 model and voices-v1.0.bin | Included in models/ with their checksums, provenance and license. |

If the sandbox blocks apt or pip, use the finished film immediately or run in Debian/Ubuntu with the packages above. No model download is needed for the full ZIP. The included setup and build were exercised in the creation workspace with available Linux dependencies. The target Claude session is a separate environment.

## Editing

- Read `docs/reference-analysis.md` and its timestamped frame sheet for the source breakdown.
- Read `docs/script-and-shots.md` for the final script and timed storyboard. `assets/story.json` is the editable script.
- Edit `src/art.py` for character and prop drawing, `src/scenes.py` for staging and camera, `src/voice.py` for narration and `src/mix.py` for music and Foley. Shot IDs connect all four.
- Use `bash scripts/build.sh --reuse-voice` for visual-only changes. The clean stem and its original timing must still match the story.
- Use `WIDTH=1080 bash scripts/build.sh --reuse-voice` for 1080 × 1920 encoding. The supplied movie matches the reference canvas at 720 × 1280.
- For an excerpt after setup, use `source .runtime/tools.sh` then `"$RENDER_PYTHON" src/render.py --start 32 --seconds 4 --out preview.mp4`. The excerpt is picture-only.
- To inspect a new reference, use `"$RENDER_PYTHON" scripts/inspect_reference.py input.mp4 review/`. It writes metadata and a timestamped contact sheet.
- `output/verification.json` records technical checks. `output/hindi.srt` is the standalone subtitle file for uploads. The finished film includes the same text as a selectable track.
