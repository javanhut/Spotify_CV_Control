from cvzone.HandTrackingModule import HandDetector
import cv2 as cv
from functools import partial
import time


class GestureControl:
    def __init__(self, gesture_callback=None):
        self.cap_vid = cv.VideoCapture(0)
        self.cap_vid.set(cv.CAP_PROP_FRAME_WIDTH, 720)
        self.cap_vid.set(cv.CAP_PROP_FRAME_HEIGHT, 486)
        self.detector = HandDetector(
            staticMode=False,
            maxHands=2,
            modelComplexity=1,
            detectionCon=0.5,
            minTrackCon=0.5,
        )
        self.gesture_callback = gesture_callback
        self.previous_x = None
        self.swipe_threshold_horizontal = 20
        self.frame_skip = 5
        self.frame_count = 0
        self.pattern_play_start = None
        self.pattern_stop_start = None
        self.hold_duration = 1.3

    def recognize_gesture(
        self, hand: dict, finger_up_array: list
    ) -> tuple[str | None, int | None]:
        gesture = None
        volume_level = None
        current_time = time.time()
        if finger_up_array == [1, 1, 1, 1, 1] and hand["type"].lower() == "right":
            current_y = hand["center"][1]
            frame_height = self.cap_vid.get(cv.CAP_PROP_FRAME_HEIGHT)
            volume_level = (current_y / frame_height) * 100
            volume_level = 100 - volume_level
            volume_level = max(0, min(100, volume_level))
            gesture = f"Volume: {volume_level:.0f}%"
        elif finger_up_array == [0, 1, 1, 0, 0] and hand["type"].lower() == "right":
            current_x = hand["lmList"][0][0]
            if self.previous_x is not None:
                dx = self.previous_x - current_x
                if dx > self.swipe_threshold_horizontal:
                    gesture = "Swipe Right"
                elif dx < -self.swipe_threshold_horizontal:
                    gesture = "Swipe Left"
            self.previous_x = current_x
        elif hand["type"].lower() == "left":
            if finger_up_array == [1, 1, 1, 1, 1]:
                if self.pattern_play_start is None:
                    self.pattern_play_start = current_time
                    self.pattern_stop_start = None
                elif current_time - self.pattern_play_start >= self.hold_duration:
                    gesture = "Play"
            elif finger_up_array == [0, 0, 0, 0, 0]:
                if self.pattern_stop_start is None:
                    self.pattern_stop_start = current_time
                    self.pattern_play_start = None
                elif current_time - self.pattern_stop_start >= self.hold_duration:
                    gesture = "Stop"
            else:
                self.pattern_play_start = None
                self.pattern_stop_start = None

        return gesture, volume_level

    def run_hands(self, token: str = None):
        while True:
            success, img = self.cap_vid.read()
            if not success:
                break
            self.frame_count += 1
            if self.frame_count % self.frame_skip != 0:
                continue
            img = cv.resize(img, (640, 480))
            hands, img = self.detector.findHands(img=img, draw=True, flipType=True)
            if hands:
                hand = hands[0]
                finger_up_array = self.detector.fingersUp(hand)
                gesture, volume_level = self.recognize_gesture(hand, finger_up_array)
                if self.gesture_callback:
                    self.gesture_callback(
                        gesture=gesture,
                        hand=hand,
                        finger_array=finger_up_array,
                        token=token,
                        volume_level=volume_level,
                    )

            cv.imshow("Image", img)
            if cv.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap_vid.release()
        cv.destroyAllWindows()
