# Headshot Auto-Cropper

This script automatically detects faces in headshot photos, aligns them based on facial landmarks (specifically the eyes and mouth), and outputs uniformly cropped and resized images for use in directories, ID photos, thumbnails, or facial datasets.

---

## ✨ Features

- Uses facial landmarks to precisely detect eyes and mouth.
- Crops a square region around the face, keeping the eyes at a consistent vertical position.
- Resizes all output images to 800×800 pixels.
- Skips images with no detectable face landmarks.

---

## ⚙️ Configuration Variables (inside script)

| Variable        | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `INPUT_DIR`     | Folder containing input images (.jpg, .jpeg, .png)                         |
| `OUTPUT_DIR`    | Folder where processed 800×800 headshots are saved                         |
| `OUTPUT_SIZE`   | Final size of each square-cropped image (in pixels)                        |
| `MULTIPLIER`    | Determines how much of the face to include: eye-to-mouth distance × this factor |
| `EYE_LINE_RATIO`| Vertical position (0–1) where the midpoint between the eyes should appear, relative to the top of the cropped square (e.g. 0.38 = 38% down) |

---

## 🧪 How It Works

1. Detect facial landmarks using `face_recognition`.
2. Calculate the midpoint between the eyes and the position of the mouth.
3. Use the vertical distance between the eyes and mouth, scaled by `MULTIPLIER`, to define a square crop region.
4. Align the midpoint between the eyes so it appears at `EYE_LINE_RATIO` from the top of the cropped image.
5. Resize to 800×800 and save to the output folder.

---

## 🐧 Installation (Linux)

### 1. Create a virtual environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install system dependencies (for `dlib` and `face_recognition`)

```bash
sudo apt update
sudo apt install cmake build-essential libboost-all-dev python3-dev
```

If you don’t have `sudo` access, try using a machine with dev tools or install via [conda](https://docs.conda.io/en/latest/).

### 3. Install Python packages

```bash
pip install face_recognition pillow numpy
```

Note: `face_recognition` depends on `dlib`, which compiles during install. This can take a few minutes.

---

## 🚀 Running the Script

Place all input headshot images into the `headshots/` folder, then run:

```bash
python headshots.py
```

Cropped and resized headshots will be saved in the `processed/` folder.

---

## 🤡 Goofy Morphing Video

The project has two goofy scripts that can make a video of faces morphing into each other. After processing the faces, 
choose one as a starting image. Copy it from processed/ into the root and rename it as "reference.jpg"
Then run

```bash
python similar_faces.py
```

This will build a folder called progressive_similar_faces with each shot sorted based on a progressive similarty algorithm. The next step will create the morphing video (requires ffmpeg)

```bash
python similar_faces_morph.py
```

## 📝 Notes

- Only the **first face** found in each image is processed.
- Images without detectable eyes and mouth landmarks are skipped with a warning.
- The script assumes front-facing headshots for best results.

---

## 📃 License

Written by Pastor Daniel McFeeters with assistance from ChatGPT. 
MIT License

