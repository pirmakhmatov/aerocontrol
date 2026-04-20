import math
import collections
import json
import os

def normalize_landmarks(lmList):
    wrist = lmList[0]
    middle_mcp = lmList[9]
    scale = math.hypot(wrist[0] - middle_mcp[0], wrist[1] - middle_mcp[1])
    if scale == 0: scale = 1.0
    normalized = []
    for x, y in lmList:
        nx = (x - wrist[0]) / scale
        ny = (y - wrist[1]) / scale
        normalized.append((nx, ny))
    return normalized

class GestureClassifier:
    def __init__(self, pinch_threshold=0.08, swipe_velocity_threshold=0.03):
        # We normalize thresholds to pixels based on width (approx 1280) for this simple logic
        self.pinch_threshold = pinch_threshold * 1280
        self.swipe_velocity_threshold = swipe_velocity_threshold * 1280
        self.wrist_history = collections.deque(maxlen=5)
        self.reload_db()

    def reload_db(self):
        self.custom_db = {}
        if os.path.exists("custom_gestures.json"):
            try:
                with open("custom_gestures.json", "r") as f:
                    self.custom_db = json.load(f)
            except:
                pass
        
    def classify(self, lmList):
        if not lmList or len(lmList) < 21:
            return None
            
        # 0. Check against custom DB first
        if self.custom_db:
            normalized = normalize_landmarks(lmList)
            best_match = None
            min_dist = float('inf')
            
            for action, template in self.custom_db.items():
                if not isinstance(template, list):
                    continue
                    
                total_dist = 0
                for i in range(21):
                    dx = normalized[i][0] - template[i][0]
                    dy = normalized[i][1] - template[i][1]
                    total_dist += math.hypot(dx, dy)
                avg_dist = total_dist / 21.0
                
                if avg_dist < min_dist:
                    min_dist = avg_dist
                    best_match = action
                    
            # 0.28 is our custom gesture match threshold. 
            if min_dist < 0.28:
                return (best_match, lmList)
            elif min_dist < 0.45:
                # ANTI-TWIST DEADZONE
                return None
            
        wrist = lmList[0]
        self.wrist_history.append(wrist[0]) # store x coord
        
        # Golden standard scaling: distance from wrist to middle MCP
        palm_length = math.hypot(lmList[9][0] - wrist[0], lmList[9][1] - wrist[1])
        if palm_length == 0: palm_length = 1.0
        
        def is_curled(tip_idx):
            tip_dist = math.hypot(lmList[tip_idx][0] - wrist[0], lmList[tip_idx][1] - wrist[1])
            # If the fingertip is closer to the wrist than 1.4x the palm length, it's curled.
            # An extended finger is typically 1.7x to 2.0x the palm length.
            return (tip_dist / palm_length) < 1.4
            
        def is_extended(tip_idx):
            tip_dist = math.hypot(lmList[tip_idx][0] - wrist[0], lmList[tip_idx][1] - wrist[1])
            return (tip_dist / palm_length) > 1.5

            
        index_curled = is_curled(8)
        middle_curled = is_curled(12)
        ring_curled = is_curled(16)
        pinky_curled = is_curled(20)
        
        is_open_palm = not index_curled and not middle_curled and not ring_curled and not pinky_curled
        
        # Check Swipes (wrist horizontal delta over 5 frames)
        if len(self.wrist_history) == 5 and is_open_palm:
            delta_x = self.wrist_history[-1] - self.wrist_history[0]
            if delta_x > self.swipe_velocity_threshold * 3:
                # Swipe Right
                self.wrist_history.clear()
                return ('SWIPE_RIGHT', None)
            elif delta_x < -self.swipe_velocity_threshold * 3:
                # Swipe Left
                self.wrist_history.clear()
                return ('SWIPE_LEFT', None)
        
        # 1. Fist (4 fingers curled)
        if index_curled and middle_curled and ring_curled and pinky_curled:
            return ('FIST', None)
            
        # 2. Open Palm (4 fingers open)
        if is_open_palm:
            return ('OPEN_PALM', None)
            
        # 2.5 Peace Sign (Index and Middle open, ring and pinky curled)
        if is_extended(8) and is_extended(12) and ring_curled and pinky_curled:
            return ('PEACE', None)
            
        # 3. Pointer removed (Skipped for now)
        # Thumb Up
        if lmList[4][1] < lmList[3][1] and self.is_fist_except_thumb(index_curled, middle_curled, ring_curled, pinky_curled):
            return ('THUMB_UP', None)
            
        # Thumb Down
        if lmList[4][1] > lmList[3][1] and self.is_fist_except_thumb(index_curled, middle_curled, ring_curled, pinky_curled):
            return ('THUMB_DOWN', None)
                
        # 4. Pinch (Thumb and Index touching, others must be extended to form "OK sign")
        pinch_dist = math.hypot(lmList[4][0]-lmList[8][0], lmList[4][1]-lmList[8][1])
        if pinch_dist < self.pinch_threshold:
            # Check if other three fingers are reasonably extended
            if not middle_curled and not ring_curled and not pinky_curled:
                # calculate midpoint for volume slider logic
                midpoint = ((lmList[4][0]+lmList[8][0])//2, (lmList[4][1]+lmList[8][1])//2)
                return ('PINCH', midpoint)
            
        return None

    def is_fist_except_thumb(self, index_curled, middle_curled, ring_curled, pinky_curled):
        return index_curled and middle_curled and ring_curled and pinky_curled
