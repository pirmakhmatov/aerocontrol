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
from gesture.actions import (next_slide, prev_slide, set_volume_from_pinch, move_laser, click_mouse, execute_voice_command, reset_pinch, handle_scroll, reset_scroll, volume_up, volume_down, toggle_mute, media_play_pause, media_next, media_prev, handle_zoom, stop_subtitles)
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
    
    # Always show camera during calibration so user can position their hand
    while is_running and len(valid_sizes) < calibration_frames:
        ret, frame = cap.read()
        if not ret: continue
        frame = cv2.flip(frame, 1)
        frame, all_lm = detector.find_hands(frame, draw=True)
        
        # Draw calibration progress bar and instructions
        progress = len(valid_sizes) / calibration_frames
        bar_w = int(frame.shape[1] * 0.6)
        bar_x = (frame.shape[1] - bar_w) // 2
        bar_y = frame.shape[0] - 60
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + 30), (50, 50, 50), -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_w * progress), bar_y + 30), (0, 255, 150), -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + 30), (200, 200, 200), 2)
        
        status_text = "Show your open hand to the camera..." if not all_lm else f"Calibrating... {len(valid_sizes)}/{calibration_frames}"
        cv2.putText(frame, status_text, (bar_x, bar_y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 150), 2)
        cv2.putText(frame, "AeroControl Calibration", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 100), 2)
        
        if all_lm:
            wrist = all_lm[0][0]
            middle_tip = all_lm[0][12]
            dist = math.hypot(wrist[0] - middle_tip[0], wrist[1] - middle_tip[1])
            
            # Draw green arrow from wrist to middle fingertip showing measurement
            w_pt = (int(wrist[0]), int(wrist[1]))
            m_pt = (int(middle_tip[0]), int(middle_tip[1]))
            cv2.arrowedLine(frame, w_pt, m_pt, (0, 255, 100), 3, tipLength=0.15)
            cv2.circle(frame, w_pt, 8, (0, 200, 255), -1)
            cv2.circle(frame, m_pt, 8, (0, 200, 255), -1)
            
            # Show size label next to the arrow
            mid_x = (w_pt[0] + m_pt[0]) // 2 + 15
            mid_y = (w_pt[1] + m_pt[1]) // 2
            cv2.putText(frame, f"{dist:.0f} px", (mid_x, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            valid_sizes.append(dist)
            print(f"  [Calibration] Frame {len(valid_sizes)}/{calibration_frames} | Hand Size: {dist:.1f} px")
        
        cv2.imshow("AeroControl Calibration", frame)
        cv2.waitKey(1)
    
    # Close calibration window
    try:
        cv2.destroyWindow("AeroControl Calibration")
        cv2.waitKey(1)
    except:
        pass
            
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
                        print(f"[Gesture] >> Next Slide ({gtype})")
                        next_slide(); swipe_cooldown = 40
                    elif gtype in ["PREV_SLIDE", "PEACE"]:
                        print(f"[Gesture] >> Previous Slide ({gtype})")
                        prev_slide(); swipe_cooldown = 40
                    elif gtype == "VOL_UP":
                        print("[Gesture] >> Volume Up")
                        volume_up(); swipe_cooldown = 4
                    elif gtype == "VOL_DOWN":
                        print("[Gesture] >> Volume Down")
                        volume_down(); swipe_cooldown = 4
                    elif gtype == "MUTE":
                        print("[Gesture] >> Mute Toggle")
                        toggle_mute(); swipe_cooldown = 40
                    elif gtype == "PLAY_PAUSE":
                        print("[Gesture] >> Play/Pause")
                        media_play_pause(); swipe_cooldown = 40
                    elif gtype == "NEXT_TRACK":
                        print("[Gesture] >> Next Track")
                        media_next(); swipe_cooldown = 40
                    elif gtype == "PREV_TRACK":
                        print("[Gesture] >> Previous Track")
                        media_prev(); swipe_cooldown = 40
                        
                if gtype == 'AI_MIC':
                    ai_enabled = settings.get("AI_ASSISTANT_ENABLED", True)
                    if not voice.is_listening:
                        mode = "AI Assistant 🎙️" if ai_enabled else "Command Mode (AI disabled)"
                        print(f"[Voice] >> {mode} ACTIVATED")
                    voice.is_listening = True
                    voice.play_audio = ai_enabled  # Only speak back if AI assistant is ON
                elif gtype == 'FIST':
                    if not voice.is_listening:
                        print("[Voice] >> Command Mode ACTIVATED (Fist)")
                    voice.is_listening = True
                    voice.play_audio = False  # Command-only, no AI voice
                else:
                    if voice.is_listening:
                        print("[Voice] >> Microphone DEACTIVATED")
                    voice.is_listening = False
                    voice.play_audio = False
            else:
                reset_pinch()
                reset_scroll()
                if voice.is_listening:
                    print("[Voice] >> Microphone DEACTIVATED")
                voice.is_listening = False
                voice.play_audio = False
        else:
            reset_pinch()
            reset_scroll()
            if voice.is_listening:
                print("[Voice] >> Microphone DEACTIVATED")
            voice.is_listening = False
            voice.play_audio = False
                    
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
    stop_subtitles()
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
