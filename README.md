# Virtual Mouse Operation Using Webcam

A Python computer-vision project that lets you control the system mouse using hand movement captured through a webcam. OpenCV detects hands with a Haar-cascade model and PyAutoGUI converts the detected position into mouse movement and click actions.

## Features

- Webcam-based hand detection
- One-hand cursor movement
- Two-hand click gesture
- Left-edge hold → left click
- Right-edge hold → right click
- Cursor smoothing for more stable movement
- Click cooldown to prevent accidental repeated clicks
- PyAutoGUI fail-safe for safer mouse control
- Simple Windows launcher (`run.bat`)

## Project Structure

```text
Virtual-Mouse-Operation-Using-Webcam/
├── models/
│   └── hand.xml                 # OpenCV Haar-cascade hand detector
├── src/
│   └── main.py                  # Main application
├── docs/
│   └── Project_Report.docx      # Original project report
├── .gitignore
├── requirements.txt
├── run.bat
└── README.md
```

## How It Works

1. The webcam captures a live video frame.
2. OpenCV converts the frame to grayscale and applies histogram equalization.
3. `hand.xml` detects hand-shaped regions.
4. With one detected hand, the center of the largest detected hand is mapped to the screen and the cursor follows it.
5. With two detected hands, their average horizontal position is used as a click gesture.
6. Holding both hands near the left edge performs a left click; holding them near the right edge performs a right click.
7. A cooldown prevents the same gesture from producing continuous clicks.

## Requirements

- Windows PC/laptop
- Python 3.9+ recommended
- Working webcam
- Mouse-control permissions for Python/PyAutoGUI

## Installation

Open Command Prompt in the project folder and run:

```bash
python -m pip install -r requirements.txt
```

## Run

### Windows

Double-click:

```text
run.bat
```

### Command line

```bash
python src/main.py
```

Press **Q** or **Esc** to stop the application.

## Controls

| Gesture | Action |
|---|---|
| One hand | Move cursor |
| Two hands held near left edge | Left click |
| Two hands held near right edge | Right click |
| Q / Esc | Exit |

## Important Notes

- The project uses the supplied `models/hand.xml` Haar-cascade model. Haar-cascade detection can be sensitive to lighting, camera quality, hand orientation, and background.
- Keep your hand clearly visible to the webcam and use reasonable lighting.
- The application controls the real system mouse. Test it in a safe application first.
- If the cursor becomes difficult to control, move the physical mouse to a screen corner to trigger PyAutoGUI's fail-safe, then close the program.

## Troubleshooting

### Webcam does not open

- Check Windows camera permissions.
- Close other applications that are using the webcam.
- Change `CAMERA_INDEX = 0` in `src/main.py` to `1` if another camera is required.

### Hands are not detected

- Improve lighting.
- Keep the hand inside the camera frame.
- Use a plain background where possible.
- The supplied Haar cascade is an older detection approach and may not detect every hand pose reliably.

### PyAutoGUI cannot control the mouse

Install/reinstall the dependencies:

```bash
python -m pip install --upgrade opencv-python pyautogui
```

On Windows, also make sure the Python process is allowed to interact with the desktop.

## Improvements Made

The original project contained multiple experimental scripts and inconsistent logic. The repository version consolidates the application into `src/main.py` and fixes the main issues:

- Removed unnecessary `imutils` dependency.
- Replaced webcam-coordinate-to-mouse-coordinate misuse with screen-size mapping.
- Added coordinate clamping so the cursor stays inside the screen.
- Added cursor smoothing.
- Added click cooldown and gesture-hold timing to avoid repeated clicks.
- Removed the broken `count = 1` logic from the original detection loop.
- Removed the incorrect `pyautogui.click(x, y)` behavior used for left-click detection.
- Added proper relative paths for `hand.xml`, so the program can be started from different working directories.
- Added camera-open and model-load validation.
- Added clean shutdown with `try/finally`.
- Added Q/Esc exit controls and status messages.
- Added `requirements.txt`, `.gitignore`, `run.bat`, and this README for GitHub use.

## Limitations

This project is intended as an educational computer-vision demonstration. Haar-cascade hand detection is less robust than modern hand-landmark models such as MediaPipe. For a future version, hand landmarks, gesture recognition, drag-and-drop, scrolling, and configurable gestures could be added.

## License

No license was included in the original project. Add a license file if you plan to distribute or publish the project under specific reuse terms.
