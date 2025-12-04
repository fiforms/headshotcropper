import os
import shutil
import numpy as np
import face_recognition

HEADSHOT_DIR = "processed"
OUTPUT_DIR = "progressive_similar_faces"
REFERENCE_IMAGE = "reference.jpg"

os.makedirs(OUTPUT_DIR, exist_ok=True)

AGE_WEIGHT = 0.015  # tweak 0.01–0.05 depending on dataset size and variation

# --- Load & encode the reference image ---
ref_img = face_recognition.load_image_file(REFERENCE_IMAGE)
ref_enc_list = face_recognition.face_encodings(ref_img)
if not ref_enc_list:
    raise ValueError("No face found in reference image.")
ref_enc = ref_enc_list[0]

# --- Load and encode all headshots ---
encodings = []   # (filename, enc)
for filename in os.listdir(HEADSHOT_DIR):
    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    path = os.path.join(HEADSHOT_DIR, filename)
    img = face_recognition.load_image_file(path)
    enc_list = face_recognition.face_encodings(img)

    if not enc_list:
        print(f"[SKIP] No encoding for {filename}")
        continue

    encodings.append((filename, enc_list[0]))

print(f"[OK] Loaded {len(encodings)} encodings.")

# --- Initialize greedy chain ---
remaining = encodings.copy()
ordered = []  # (filename, effective_distance)
age = {fn: 0 for fn, enc in remaining}

# --- First pick: closest to reference ---
distances = [(np.linalg.norm(enc - ref_enc), fn, enc) for fn, enc in remaining]
distances.sort(key=lambda x: x[0])
first_dist, first_fn, first_enc = distances[0]

ordered.append((first_fn, first_dist))
remaining = [(fn, enc) for fn, enc in remaining if fn != first_fn]

current_enc = first_enc

# --- Greedy chain with age weighting ---
iteration = 1
while remaining:
    temp = []
    for fn, enc in remaining:
        raw = np.linalg.norm(enc - current_enc)
        effective = raw + AGE_WEIGHT * age[fn]
        temp.append((effective, raw, fn, enc))

    # pick the minimum effective distance
    temp.sort(key=lambda x: x[0])
    eff_dist, raw_dist, fn, enc = temp[0]

    ordered.append((fn, raw_dist))

    # remove picked
    remaining = [(f, e) for f, e in remaining if f != fn]

    # increment age of all remaining faces
    for f, _ in remaining:
        age[f] += 1

    # update chain pointer
    current_enc = enc
    iteration += 1

# --- Output sorted files ---
for i, (fname, dist) in enumerate(ordered):
    src = os.path.join(HEADSHOT_DIR, fname)
    new_name = f"{i:03d}_dist-{dist:.4f}_{fname}"
    dst = os.path.join(OUTPUT_DIR, new_name)
    shutil.copy2(src, dst)
    print(f"[COPY] {fname} → {new_name}")

