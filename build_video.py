import subprocess
import os

video_in = "gemini_generated_video_d77be6b1.mp4"
audio_in = "kdr ft vevi drill - 1 - UNA DIABLA.wav"
output_file = "UNA_DIABLA_final_1080p.mp4"

# Audio is ~127.54s (~2 min 07s)
# Video is 20s. We need 7 clips (20s * 7 = 140s, trimmed to audio length with crossfades)
# Let's create variations for the clips:
# Clip 0: standard normal speed forward, subtle contrast/saturation boost
# Clip 1: subtle zoom-in / crop slow drift + slight color grade
# Clip 2: reverse playback (backward)
# Clip 3: slight speed curve or mirror (hflip)
# Clip 4: vivid punchy saturation + slight vignette
# Clip 5: subtle zoom-out drift / reversed
# Clip 6: normal forward with smooth fade out

# Using xfade transitions between clips:
# Clip length: 20s each. Transition duration: 1.0s
# Offset 0: 0s -> duration 20s
# Transition 1: offset 19s (between c0 and c1)
# Transition 2: offset 38s (between v1 and c2)
# Transition 3: offset 57s (between v2 and c3)
# Transition 4: offset 76s (between v3 and c4)
# Transition 5: offset 95s (between v4 and c5)
# Transition 6: offset 114s (between v5 and c6)
# Total length after 6 transitions: 20*7 - 6*1 = 140 - 6 = 134s.
# Audio is 127.54s, so 134s fully covers the song, and we fade out video and audio together at the end!

# Filter complex breakdown:
# Base processing: scale=1920:1080:flags=lanczos,fps=30,format=yuv420p

filter_complex = """
[0:v]trim=0:20,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,eq=contrast=1.05:saturation=1.1,format=yuv420p[c0];

[0:v]trim=0:20,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,hflip,eq=contrast=1.08:saturation=1.15,format=yuv420p[c1];

[0:v]trim=0:20,reverse,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,eq=contrast=1.05:saturation=1.12,format=yuv420p[c2];

[0:v]trim=0:20,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,vignette=PI/5,eq=contrast=1.1:saturation=1.2,format=yuv420p[c3];

[0:v]trim=0:20,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,hflip,reverse,eq=contrast=1.06:saturation=1.1,format=yuv420p[c4];

[0:v]trim=0:20,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,eq=contrast=1.08:saturation=1.18,format=yuv420p[c5];

[0:v]trim=0:20,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,vignette=PI/6,eq=contrast=1.05:saturation=1.1,format=yuv420p[c6];

[c0][c1]xfade=transition=fade:duration=1:offset=19[v01];
[v01][c2]xfade=transition=dissolve:duration=1:offset=38[v02];
[v02][c3]xfade=transition=wipeleft:duration=1:offset=57[v03];
[v03][c4]xfade=transition=fade:duration=1:offset=76[v04];
[v04][c5]xfade=transition=wiperight:duration=1:offset=95[v05];
[v05][c6]xfade=transition=dissolve:duration=1:offset=114,fade=t=out:st=125.5:d=2[vout];

[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st=125.5:d=2[aout]
"""

# Let's clean up whitespace
filter_complex = "".join(line.strip() for line in filter_complex.split("\n") if line.strip())

cmd = [
    "ffmpeg", "-y",
    "-i", video_in,
    "-i", audio_in,
    "-filter_complex", filter_complex,
    "-map", "[vout]",
    "-map", "[aout]",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "320k",
    "-ar", "48000",
    "-t", "127.54",
    "-movflags", "+faststart",
    output_file
]

print("Running command...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Returncode:", res.returncode)
if res.returncode != 0:
    print("Stderr:", res.stderr[-2000:])
else:
    print("Success! Created:", output_file)
