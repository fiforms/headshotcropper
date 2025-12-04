import os
from PIL import Image
import numpy as np

INPUT_DIR = "progressive_similar_faces"
OUTPUT_DIR = "flow_ready_frames"
STILL_FRAMES = 2
BLEND_FRAMES = 2   # minimum needed for optical flow to work

os.makedirs(OUTPUT_DIR, exist_ok=True)

files = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".jpg")])

def blend(a, b, t):
    a = np.array(a).astype(float)
    b = np.array(b).astype(float)
    c = (1 - t) * a + t * b
    return Image.fromarray(c.astype(np.uint8))

frame_index = 0

for i in range(len(files) - 1):
    imgA = Image.open(os.path.join(INPUT_DIR, files[i])).convert("RGB")
    imgB = Image.open(os.path.join(INPUT_DIR, files[i+1])).convert("RGB")

    # 1) Still frames (identical)
    for _ in range(STILL_FRAMES):
        imgA.save(os.path.join(OUTPUT_DIR, f"{frame_index:05}.jpg"))
        frame_index += 1

    # 2) Tiny blends (very small transition)
    for f in range(1, BLEND_FRAMES + 1):
        t = f / (BLEND_FRAMES + 1)   # small fractional steps
        blended = blend(imgA, imgB, t)
        blended.save(os.path.join(OUTPUT_DIR, f"{frame_index:05}.jpg"))
        frame_index += 1

# Final still
last = Image.open(os.path.join(INPUT_DIR, files[-1])).convert("RGB")
for _ in range(STILL_FRAMES):
    last.save(os.path.join(OUTPUT_DIR, f"{frame_index:05}.jpg"))
    frame_index += 1

print("Frames generated:", frame_index)

import subprocess

# --- FFmpeg configuration ---
FFMPEG_PATH = "ffmpeg"  # or full path if needed
INPUT_FRAMERATE = 1     # your source rate (1 fps for duplicate frames)
OUTPUT_FRAMERATE = 30   # desired final fps

cmd = [
    FFMPEG_PATH,
    "-y",
    "-framerate", str(INPUT_FRAMERATE),
    "-i", "flow_ready_frames/%05d.jpg",
    "-vf", (
        "minterpolate=fps={}:"
        "mi_mode=mci:"
        "mc_mode=aobmc:"
        "me_mode=bidir:"
        "vsbmc=1"
    ).format(OUTPUT_FRAMERATE),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "morph_output.mp4"
]

print("Running ffmpeg…")
subprocess.run(cmd, check=True)
print("Video created: morph_output.mp4")

