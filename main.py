"""Virtual Mouse Operation Using Webcam.

Uses an OpenCV Haar cascade to detect hands from a webcam and PyAutoGUI to
control the system mouse. One detected hand controls cursor movement; two
hands can trigger a left/right click when held near the corresponding side.
"""

from __future__ import annotations

import time
from collections import deque
from pathlib import Path

import cv2
import pyautogui


BASE_DIR = Path(__file__).resolve().parent.parent
CASCADE_PATH = BASE_DIR / "models" / "hand.xml"

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DETECTION_SCALE = 1.15
MIN_NEIGHBORS = 5
MIN_HAND_SIZE = (50, 50)
SMOOTHING_POINTS = 5
CLICK_COOLDOWN = 1.0
CLICK_HOLD_TIME = 0.45
EDGE_ZONE = 0.25


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def load_detector() -> cv2.CascadeClassifier:
    if not CASCADE_PATH.exists():
        raise FileNotFoundError(f"Hand cascade not found: {CASCADE_PATH}")

    detector = cv2.CascadeClassifier(str(CASCADE_PATH))
    if detector.empty():
        raise RuntimeError("OpenCV could not load models/hand.xml")
    return detector


def map_to_screen(x: int, y: int, frame_width: int, frame_height: int,
                  screen_width: int, screen_height: int) -> tuple[int, int]:
    """Map webcam coordinates to the full screen with bounds checking."""
    screen_x = int(clamp(x / frame_width * screen_width, 0, screen_width - 1))
    screen_y = int(clamp(y / frame_height * screen_height, 0, screen_height - 1))
    return screen_x, screen_y


def main() -> None:
    detector = load_detector()
    screen_width, screen_height = pyautogui.size()

    camera = cv2.VideoCapture(CAMERA_INDEX)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not camera.isOpened():
        raise RuntimeError("Unable to open webcam. Check camera permissions.")

    pyautogui.PAUSE = 0.03
    pyautogui.FAILSAFE = True

    positions: deque[tuple[int, int]] = deque(maxlen=SMOOTHING_POINTS)
    last_click = 0.0
    zone_start = None
    zone = None

    print("Virtual Mouse started. Press Q or ESC to exit.")
    print("One hand: move the cursor. Two hands: hold left/right edge to click.")

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Could not read a frame from the webcam.")
                break

            # Mirror the webcam so movement feels natural.
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            hands = detector.detectMultiScale(
                gray,
                scaleFactor=DETECTION_SCALE,
                minNeighbors=MIN_NEIGHBORS,
                minSize=MIN_HAND_SIZE,
            )
            hands = sorted(hands, key=lambda r: r[2] * r[3], reverse=True)

            for x, y, w, h in hands[:2]:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            now = time.monotonic()

            if len(hands) == 1:
                x, y, w, h = hands[0]
                center_x, center_y = x + w // 2, y + h // 2
                positions.append(map_to_screen(
                    center_x, center_y, width, height, screen_width, screen_height
                ))

                avg_x = sum(p[0] for p in positions) / len(positions)
                avg_y = sum(p[1] for p in positions) / len(positions)
                pyautogui.moveTo(int(avg_x), int(avg_y), duration=0)

                zone = None
                zone_start = None
                status = "1 hand - cursor movement"

            elif len(hands) >= 2:
                # Two hands are treated as a click gesture. The average X
                # position determines whether it is a left or right click.
                centers = [x + w // 2 for x, y, w, h in hands[:2]]
                avg_hand_x = sum(centers) / len(centers)
                normalized_x = avg_hand_x / width

                new_zone = "left" if normalized_x <= EDGE_ZONE else (
                    "right" if normalized_x >= 1 - EDGE_ZONE else None
                )

                if new_zone != zone:
                    zone = new_zone
                    zone_start = now if zone else None
                elif zone and zone_start is not None:
                    held_long_enough = now - zone_start >= CLICK_HOLD_TIME
                    cooled_down = now - last_click >= CLICK_COOLDOWN
                    if held_long_enough and cooled_down:
                        pyautogui.click(button=zone)
                        last_click = now
                        zone_start = now

                status = "2 hands - hold left/right edge to click"
                positions.clear()

            else:
                positions.clear()
                zone = None
                zone_start = None
                status = "No hand detected"

            cv2.putText(
                frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2, cv2.LINE_AA
            )
            cv2.putText(
                frame, "Q / ESC: Exit", (10, height - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA
            )

            cv2.imshow("Virtual Mouse Operation", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except pyautogui.FailSafeException:
        print("PyAutoGUI fail-safe triggered. Exiting safely.")
    except Exception as exc:
        print(f"Error: {exc}")
