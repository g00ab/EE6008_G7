# Project EE6008 for group 7

# 🧊 Rubik's Cube Face Scanner and Solver - OpenMV + Python

This project scans and maps all six faces of a **Rubik’s Cube** using an **OpenMV camera** running object detection and color recognition. It produces a string representation of the cube's state and, if valid, outputs the steps to solve it.

## Project Architecture

.
├── rubiks_square_color.py      # OpenMV color classification and face capture
├── error_handling.py           # Cube string validation and solving
├── fomo.tflite                 # CNN model for color fallback (optional)
├── fomo_labels.txt                 # CNN model for color fallback (optional)
├── screenshots_cube/           # datasets (pictures) of the cube
└── README.md                   # Project documentation
---

## 📷 Overview

The system is designed to detect and classify the **colors of each face** of a Rubik’s Cube using:

- A **bounding box model** (FOMO) to detect the 9 squares on a face
- **LAB color detection** for accurate color classification
- Cube scanning in a fixed **face order**
- String output matching standard cube notation

---

## 🧠 Face Scanning Order

To ensure consistent orientation, scan the cube in the **following order**:

1. **White**
2. **Green**
3. **Yellow**
4. **Red**
5. **Blue**
6. **Orange**

The proper orientation of the cube should be kept in order to capture the sides with the proper orientation

This ensures the resulting cube string uses the standard notation:

UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB

Where:
- U = Up (White)
- R = Right (Red)
- F = Front (Green)
- D = Down (Yellow)
- L = Left (Orange)
- B = Back (Blue)

---

## 🧾 Files & Purpose

### `rubiks_square_color.py`

- Runs on the OpenMV camera
- Detects squares on a cube face using object detection
- Extracts a square region around each bounding box
- Classifies color using **LAB color rules**
- Captures one face per run and maps the 9 colors to a string
- Repeats for all 6 faces, forming a full 54-character cube string

---

### `error_handling.py`

- Takes the cube string output from `rubiks_square_color.py`
- Validates the cube structure and color distribution
- If correct: returns a list of moves to solve the cube
- If incorrect: prompts the user for corrections and generates a corrected string before solving

---

## 💡 How It Works

1. **Start scanning with `rubiks_square_color.py`**
   - Ensure good lighting and stable positioning
   - The script will:
     - Detect 9 squares
     - Force the color of the center and detect the remaining 8
     - Save the face image and print the identified colors

2. **After scanning all 6 faces**, run `error_handling.py`
   - Gives the string ouput to give to the solver (i.e Kociemba)

   Then give this output to **error_handling.py**
   - If valid: solves the cube using a solving library (e.g., `kociemba`) and returns instructions 
   - If errors: prompts the user to give the details of the errors to make the change automatically, then returns the insrtructions with the correct output

---

## 🛠️ Requirements

### Hardware
- [OpenMV Cam](https://openmv.io/)
- Lighting for consistent color detection

### Software
- OpenMV IDE for uploading `rubiks_square_color.py`
- Terminal to run `error_handling.py`
- Python 3.x with:
  - `kociemba` (or any solver library)
  - Standard libraries

---

## 🧪 Example Output

```bash
🔎 LAB → CNN Color classification:

top_left_corner @(90, 48) → blue (1.00)
...
✅ Captured and saved side_1.jpg with center color 'white'

Cube string:
UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB

✅ Cube is valid. Solving...
Moves: R U R' U' R U2 R' ...