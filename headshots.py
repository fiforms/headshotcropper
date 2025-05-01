# Uncomment the following lines and modify as needed if packages aren't installed in the python path.

# import sys
# sys.path.insert(0, '/home/username/.local/share/pipx/venvs/face-recognition/lib/python3.12/site-packages/')

import os
import numpy as np
from PIL import Image
import face_recognition

# --- Configuration ---
INPUT_DIR = 'headshots'
OUTPUT_DIR = 'processed'
OUTPUT_SIZE = 800
INITIAL_MULTIPLIER = 6.1  # Starting multiplier for eye-to-mouth distance
EYE_LINE_RATIO = 0.38     # Eye position from top (e.g. 0.38 = 38%)

# --- Utility function ---
def center_of(points):
    arr = np.array(points)
    return arr.mean(axis=0).astype(int)

# --- Prepare output folder ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    filepath = os.path.join(INPUT_DIR, filename)
    image = face_recognition.load_image_file(filepath)
    landmarks_list = face_recognition.face_landmarks(image)

    if not landmarks_list:
        print(f"[SKIP] No face landmarks found in {filename}")
        continue

    landmarks = landmarks_list[0]
    if not all(k in landmarks for k in ['left_eye', 'right_eye', 'top_lip']):
        print(f"[SKIP] Missing eye or mouth data in {filename}")
        continue

    # --- Calculate key positions ---
    left_eye = center_of(landmarks['left_eye'])
    right_eye = center_of(landmarks['right_eye'])
    mouth = center_of(landmarks['top_lip'])

    eye_center = ((left_eye + right_eye) // 2).tolist()
    eye_to_mouth_dist = np.linalg.norm(eye_center - mouth)

    # --- Calculate initial desired crop size ---
    initial_crop_size = eye_to_mouth_dist * INITIAL_MULTIPLIER
    eye_offset = EYE_LINE_RATIO * initial_crop_size

    # --- Compute max crop size that fits within image bounds ---
    max_top = eye_center[1]
    max_bottom = image.shape[0] - eye_center[1]
    max_vertical = min(max_top / EYE_LINE_RATIO, max_bottom / (1 - EYE_LINE_RATIO))

    max_left = eye_center[0]
    max_right = image.shape[1] - eye_center[0]
    max_horizontal = 2 * min(max_left, max_right)

    max_crop_size = min(max_vertical, max_horizontal)
    final_crop_size = min(initial_crop_size, max_crop_size)
    crop_size = int(final_crop_size)

    # Eye center should be at EYE_LINE_RATIO × crop_size from the top
    top = int(eye_center[1] - (crop_size * EYE_LINE_RATIO))
    left = int(eye_center[0] - (crop_size / 2))
    bottom = top + crop_size
    right = left + crop_size

    # Ensure within bounds just in case
    top = max(0, top)
    left = max(0, left)
    bottom = min(bottom, image.shape[0])
    right = min(right, image.shape[1])

    # Crop and resize
    crop_box = image[top:bottom, left:right]
    pil_image = Image.fromarray(crop_box)
    pil_image = pil_image.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.LANCZOS)

    output_path = os.path.join(OUTPUT_DIR, filename)
    pil_image.save(output_path)
    print(f"[OK] Cropped {filename} (multiplier used: {final_crop_size / eye_to_mouth_dist:.2f})")

