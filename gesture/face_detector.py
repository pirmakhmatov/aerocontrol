import cv2
import mediapipe as mp

class FaceDetector:
    def __init__(self, min_detection_confidence=0.6):
        base_options = mp.tasks.BaseOptions(model_asset_path='blaze_face_short_range.tflite')
        options = mp.tasks.vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=min_detection_confidence,
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        self.detector = mp.tasks.vision.FaceDetector.create_from_options(options)

    def detect(self, image):
        # Convert BGR to RGB 
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        
        results = self.detector.detect(mp_image)
        
        # Return True if a face is physically visible in frame
        return True if results.detections else False
