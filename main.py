import cv2
import math
import pyautogui
import threading
import subprocess
import time
import pystray
from PIL import Image, ImageDraw

from gesture.detector import HandDetector
from gesture.classifier import GestureClassifier
from gesture.face_detector import FaceDetector
from gesture.actions import (next_slide, prev_slide, set_volume_from_pinch, move_laser, click_mouse, execute_voice_command, reset_pinch, handle_scroll, reset_scroll, volume_up, volume_down, toggle_mute, media_play_pause, media_next, media_prev, handle_zoom)
from voice.realtime_client import RealtimeVoiceClient
from config import CAM_INDEX, CAM_WIDTH, CAM_HEIGHT

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

is_running = True
is_paused = False

def load_settings():
    try:
        import json, os
        if os.path.exists("custom_gestures.json"):
            with open("custom_gestures.json", "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def create_image():
    # Clean system tray icon rendering
    image = Image.new('RGB', (64, 64), color=(30, 30, 30))
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill=(0, 255, 150))
    return image

def _opencv_thread_internal(voice):
    global is_running, is_paused
    
    screen_w, screen_h = pyautogui.size()
    detector = HandDetector()
    classifier = GestureClassifier()
    face_detector = FaceDetector()
    
    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    
    swipe_cooldown = 0
    click_cooldown = 0
    last_zoom_dist = None
    
    print("Starting background calibration... locking onto hand shape.")
    enrolled_hand_size = None
    
    calibration_frames = 20
    valid_sizes = []
    
    # Fully invisible bootstrap calibration
    while is_running and len(valid_sizes) < calibration_frames:
        ret, frame = cap.read()
        if not ret: continue
        frame = cv2.flip(frame, 1)
        frame, all_lm = detector.find_hands(frame, draw=False)
        if all_lm:
            wrist = all_lm[0][0]
            middle_tip = all_lm[0][12]
            dist = math.hypot(wrist[0] - middle_tip[0], wrist[1] - middle_tip[1])
            valid_sizes.append(dist)
            
    if valid_sizes:
        enrolled_hand_size = sum(valid_sizes) / len(valid_sizes)
    else:
        enrolled_hand_size = 150
        
    print(f"Calibration Complete. Hand Size: {enrolled_hand_size}")
    print("AeroControl Daemon Active! (Check System Tray)")
    
    frame_counter = 0
    settings = load_settings()
    
    while is_running:
        ret, frame = cap.read()
        if not ret: continue
            
        frame_counter += 1
        if frame_counter % 30 == 0:
            settings = load_settings()
            classifier.reload_db()
            
        if is_paused:
            time.sleep(0.01)
            continue
            
        frame = cv2.flip(frame, 1)
        
        draw_debug = settings.get("DEBUG_WINDOW_ENABLED", False)
        frame, all_lm = detector.find_hands(frame, draw=draw_debug)
        
        valid_hand = None
        if all_lm:
            for lm_list in all_lm:
                wrist = lm_list[0]
                middle_tip = lm_list[12]
                h_size = math.hypot(wrist[0] - middle_tip[0], wrist[1] - middle_tip[1])
                
                if enrolled_hand_size * 0.4 < h_size < enrolled_hand_size * 1.6:
                    valid_hand = lm_list
                    break
        
        # Audience Proofing
        face_detected = face_detector.detect(frame)
        if not face_detected:
            valid_hand = None
            if voice.is_listening:
                voice.is_listening = False
        
        # Two-Handed Zoom Logic
        if face_detected and all_lm and len(all_lm) >= 2:
            left_index = all_lm[0][8]
            right_index = all_lm[1][8]
            dist = math.hypot(left_index[0]-right_index[0], left_index[1]-right_index[1])
            last_zoom_dist = handle_zoom(dist, last_zoom_dist)
            valid_hand = None
        else:
            last_zoom_dist = None

        if valid_hand:
            result = classifier.classify(valid_hand)
            if result:
                gtype, data = result
                if gtype == 'PINCH':
                    set_volume_from_pinch(data)
                else:
                    reset_pinch()
                    
                if gtype == 'SCROLL':
                    handle_scroll(data[0][1])
                else:
                    reset_scroll()
                    
                if swipe_cooldown == 0:
                    if gtype in ["NEXT_SLIDE", "OPEN_PALM"]:
                        next_slide(); swipe_cooldown = 40
                    elif gtype in ["PREV_SLIDE", "PEACE"]:
                        prev_slide(); swipe_cooldown = 40
                    elif gtype == "VOL_UP":
                        volume_up(); swipe_cooldown = 4
                    elif gtype == "VOL_DOWN":
                        volume_down(); swipe_cooldown = 4
                    elif gtype == "MUTE":
                        toggle_mute(); swipe_cooldown = 40
                    elif gtype == "PLAY_PAUSE":
                        media_play_pause(); swipe_cooldown = 40
                    elif gtype == "NEXT_TRACK":
                        media_next(); swipe_cooldown = 40
                    elif gtype == "PREV_TRACK":
                        media_prev(); swipe_cooldown = 40
                        
                if gtype in ('AI_MIC', 'FIST'):
                    voice.is_listening = True
                else:
                    voice.is_listening = False
            else:
                reset_pinch()
                reset_scroll()
                voice.is_listening = False
        else:
            reset_pinch()
            reset_scroll()
            voice.is_listening = False
                    
        if swipe_cooldown > 0: swipe_cooldown -= 1
        if click_cooldown > 0: click_cooldown -= 1
        
        if draw_debug:
            cv2.putText(frame, "AeroControl BACKGROUND DAEMON", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 100), 2)
            cv2.imshow("AeroControl Debug", frame)
            cv2.waitKey(1)
        else:
            try:
                if cv2.getWindowProperty("AeroControl Debug", 0) >= 0:
                    cv2.destroyWindow("AeroControl Debug")
            except:
                pass
            
    cap.release()


def opencv_thread(voice):
    try:
        _opencv_thread_internal(voice)
    except Exception as e:
        import traceback
        print("\n\n=== A FATAL ERROR OCCURRED IN THE BACKGROUND COMPUTE DAEMON ===")
        traceback.print_exc()
        print("=================================================================\n\n")
        global is_running
        is_running = False

def on_quit(icon, item):
    global is_running
    is_running = False
    icon.stop()

def on_toggle(icon, item):
    global is_paused
    is_paused = not is_paused

def on_settings(icon, item):
    subprocess.Popen(["python", "settings.py"])

def main():
    voice = RealtimeVoiceClient(on_command_cb=execute_voice_command)
    voice.start()
    
    vision_t = threading.Thread(target=opencv_thread, args=(voice,), daemon=True)
    vision_t.start()
    
    menu = pystray.Menu(
        pystray.MenuItem('Settings...', on_settings),
        pystray.MenuItem(lambda text: 'Resume Tracking' if is_paused else 'Pause Gestures', on_toggle),
        pystray.MenuItem('Quit AeroControl', on_quit)
    )
    
    print("AeroControl initializing in system taskbar tray...")
    icon = pystray.Icon("aerocontrol", create_image(), "AeroControl Daemon", menu=menu)
    icon.run()
    
    # Wait for cleanly closing the voice client when icon is stopped
    voice.stop()

if __name__ == "__main__":
    main()
