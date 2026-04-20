import cv2
import mediapipe as mp

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        base_options = mp.tasks.BaseOptions(model_asset_path='hand_landmarker.task')
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=maxHands,
            min_hand_detection_confidence=float(detectionCon),
            min_hand_presence_confidence=float(detectionCon),
            min_tracking_confidence=float(trackCon),
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        self.detector = mp.tasks.vision.HandLandmarker.create_from_options(options)

    def find_hands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
        result = self.detector.detect(mp_image)
        
        all_lm = []
        if result.hand_landmarks:
            for hand_md in result.hand_landmarks:
                lmList = []
                h, w, c = img.shape
                for lm in hand_md:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append((cx, cy))
                
                if draw:
                    for connection in HAND_CONNECTIONS:
                        p1, p2 = lmList[connection[0]], lmList[connection[1]]
                        cv2.line(img, p1, p2, (0, 255, 0), 2)
                    for lm_pt in lmList:
                        cv2.circle(img, lm_pt, 4, (255, 0, 0), cv2.FILLED)
                        
                all_lm.append(lmList)
                
        return img, all_lm
