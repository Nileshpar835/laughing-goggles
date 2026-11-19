# Production guide for a narrated vertical fable

## Scope and scale

| Decision | This episode | How to scale a new episode |
| --- | --- | --- |
| Runtime | 58.9 s, one narrator, one question, one payoff | For 30–40 s use one decision and its consequence. For the reference's 90–105 s add a second situation that changes how the viewer reads the first. |
| Picture | 720 × 1280, 30 fps, 360 × 640 layout coordinates | Set WIDTH=1080 for a 1080 × 1920 encode. For a sharper large-format close-up, raise the cached background resolution in scenes.py as well. |
| Staging | Two rigs, an indoor room and an outdoor lane, with cabinet, water and photo inserts | Reuse a location from another angle. Budget new artwork for the consequential action or object. |
| Art | Warm wood and ochre cloth indoors, slate water, one red focal prop | Keep silhouettes distinct. Reserve the highest contrast for the object that answers this beat's question. |
| Sound | Hindi male Kokoro hm_omega, 24 kHz voice stem, original score and Foley, 48 kHz stereo AAC delivery | Test difficult words as a short phrase. Record new durations whenever text, speed or voice changes. |
| Text | Selectable Hindi subtitles, on-screen Hindi note | Review at phone size. Use fully shaped Devanagari. For another platform, supply SRT separately when its player ignores MP4 subtitle tracks. |
| Compute | CPU-only Linux; no API key or GPU for this implementation | Stream frames to FFmpeg. Allow roughly 2 GB free disk and a few GB of RAM as a planning estimate. Runtimes vary by host. |

## How the sample earns the next shot

1. **The contradiction.** Twenty-three boats have never touched water. The cabinet answers how that is possible but leaves the viewer wondering whether the boats will ever sail.
2. **The question.** Meera asks which boat is fastest. Papa's pause gives the viewer time to reach the answer with him.
3. **The choice.** Papa offers the red boat. That choice makes his later impulse to rescue it recognizable.
4. **The reversal.** The red boat starts well, then catches a leaf. The story would feel predictable if it sailed perfectly the first time.
5. **The action.** Meera folds up the wet corner. The camera stays on her hand, the leaf and the boat so the solution is visible with the sound off.
6. **The ending.** A photo takes the boat's place. The note says who learned from whom. Leave a final hold long enough for it to be read.

Use the measured `output/timing.json` for timecodes, clean lines, purposes, shot descriptions and pauses. `docs/script-and-shots.md` presents them for reading. Hindi is the spoken master. The Romanization is a reading aid.

## Drawing and motion

Characters use connected upper and lower arms with a palm endpoint for the held boat. The faces have gaze, blink, brows, mouth shapes and small head tilts. Match a reaching hand's screen direction when cutting to the insert. Start and finish a transfer with a clear hold. Animate a change in the prop itself, such as the bow folding, as well as the position of the hand. In this renderer, every frame is computed from its timestamp, so re-rendered excerpts use the same motion as the final film.

Direct the camera with a single reason per move. The opening pullback reveals the number of boats. The later push into the same shelf reveals the photograph. The photograph turns over once, then holds. The note and spoken quote carry the same idea.

## Voice and mix

Feed Hindi text in Devanagari to the hi phonemizer. Keep directions in separate fields. This episode varies synthesis speed from 0.96 to 1.05. Each phrase is trimmed around active audio with a short margin and a tiny de-click fade. The authored pause is added before snapping the scene end to the next frame. Subtitles cover the measured voice interval, excluding the added hold. These are phrase timings.

The mix places the centered voice over a quiet plucked motif, a filtered rain bed and brief contact sounds. Water and paper cues are generated in code. The finalizer measures the mix, applies a two-pass loudness adjustment and attaches the selectable Hindi track. Rerun verification after changing speech or score.

## Pre-release checks

- Watch the first two seconds muted. Describe what is unusual before reading the script.
- Read only the shot actions. A viewer should be able to reconstruct the character's decision and its consequence.
- Inspect three consecutive poses around a pickup, contact or release. Check hand direction and whether the prop jumps across a cut.
- Read the final handwritten line on a phone. Listen to the Hindi quote against the printed words. Check vowel lengths, names and rests at full speed.
- Validate frame rate, resolution, complete decoding, subtitle duration, loudness and audio/video end times with the included verifier.
- When actual analytics exist, compare where viewers swipe with the corresponding shots. An opening exit suggests testing another first image; a dip before the reveal suggests shortening repeated information. Change one thing per version and record what changed. Treat conclusions from a small audience as tentative.
