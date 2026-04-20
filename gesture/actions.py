import os
import sys
import pyautogui
import json

def _notify(msg):
    settings = {}
    if os.path.exists("custom_gestures.json"):
        try:
            with open("custom_gestures.json", "r") as f:
                settings = json.load(f)
        except Exception:
            pass
            
    if not settings.get("NOTIFICATIONS_ENABLED", True):
        return
        
    t_state = settings.get("NOTIFICATIONS_TIME", 2000)
    
    if sys.platform.startswith('linux'):
        os.system(f'notify-send "AeroControl" "{msg}" -t {t_state} > /dev/null 2>&1')

last_pinch_y = None
last_scroll_y = None

def reset_pinch():
    global last_pinch_y
    last_pinch_y = None

def reset_scroll():
    global last_scroll_y
    last_scroll_y = None

def handle_scroll(y_pos):
    global last_scroll_y
    if last_scroll_y is None:
        last_scroll_y = y_pos
        return
        
    diff = last_scroll_y - y_pos
    if abs(diff) > 5:  # Scroll Deadzone constraint
        # Positive diff (hand went up relative to frame origin top-left) means scrolling UP
        scroll_ticks = int(diff * 0.75) 
        if scroll_ticks != 0:
            pyautogui.scroll(scroll_ticks)
            last_scroll_y = y_pos

def next_slide():
    _notify("Next Slide")
    pyautogui.press('right')

def prev_slide():
    _notify("Previous Slide")
    pyautogui.press('left')

def volume_up():
    _notify("Volume Up")
    if sys.platform.startswith('linux'):
        os.system("amixer -D pulse sset Master unmute > /dev/null 2>&1")
        os.system("amixer -D pulse sset Master 2%+ > /dev/null 2>&1")
    else:
        pyautogui.press('volumeup')

def volume_down():
    _notify("Volume Down")
    if sys.platform.startswith('linux'):
        os.system("amixer -D pulse sset Master unmute > /dev/null 2>&1")
        os.system("amixer -D pulse sset Master 2%- > /dev/null 2>&1")
    else:
        pyautogui.press('volumedown')

def toggle_mute():
    _notify("Toggle Mute")
    if sys.platform.startswith('linux'):
        os.system("amixer -D pulse sset Master toggle > /dev/null 2>&1")
    else:
        pyautogui.press('volumemute')

def set_volume_from_pinch(midpoint, max_h=720):
    global last_pinch_y
    if last_pinch_y is None:
        last_pinch_y = midpoint[1]
        return
        
    diff = last_pinch_y - midpoint[1]
    steps = int(abs(diff) / 25)  # 25 pixels per volume step
    
    if steps > 0:
        vol_change = steps * 5
        if diff > 0: # moved up
            if sys.platform.startswith('linux'):
                os.system("amixer -D pulse sset Master unmute > /dev/null 2>&1")
                os.system(f"amixer -D pulse sset Master {vol_change}%+ > /dev/null 2>&1")
            else:
                for _ in range(steps): pyautogui.press('volumeup')
            last_pinch_y -= steps * 25
        else: # moved down
            if sys.platform.startswith('linux'):
                os.system("amixer -D pulse sset Master unmute > /dev/null 2>&1")
                os.system(f"amixer -D pulse sset Master {vol_change}%- > /dev/null 2>&1")
            else:
                for _ in range(steps): pyautogui.press('volumedown')
            last_pinch_y += steps * 25

def move_laser(x, y, screen_w, screen_h, cam_w=1280, cam_h=720, ema_x=None, ema_y=None, alpha=0.35):
    # Define an active inner bounding box so the user doesn't have to reach to the camera edges to hit the monitors edges.
    pad_x = cam_w * 0.15
    pad_y = cam_h * 0.15
    active_w = cam_w - 2 * pad_x
    active_h = cam_h - 2 * pad_y
    
    # Map from active box to screen
    screen_x = int(((x - pad_x) / active_w) * screen_w)
    screen_y = int(((y - pad_y) / active_h) * screen_h)
    
    if ema_x is None:
        ema_x, ema_y = screen_x, screen_y
    else:
        ema_x = alpha * screen_x + (1.0 - alpha) * ema_x
        ema_y = alpha * screen_y + (1.0 - alpha) * ema_y
        
    final_x = max(0, min(screen_w - 2, int(ema_x)))
    final_y = max(0, min(screen_h - 2, int(ema_y)))
    pyautogui.moveTo(final_x, final_y, _pause=False)
    return ema_x, ema_y

def click_mouse():
    pyautogui.click()
    
def media_play_pause():
    _notify("Play/Pause")
    if sys.platform.startswith('linux'):
        if os.system("playerctl play-pause > /dev/null 2>&1") != 0:
            if os.system("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause > /dev/null 2>&1") != 0:
                if os.system("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.vlc /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause > /dev/null 2>&1") != 0:
                    pyautogui.press('playpause')
    else:
        pyautogui.press('playpause')

def media_next():
    _notify("Next Track")
    if sys.platform.startswith('linux'):
        if os.system("playerctl next > /dev/null 2>&1") != 0:
            if os.system("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next > /dev/null 2>&1") != 0:
                if os.system("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.vlc /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next > /dev/null 2>&1") != 0:
                    pyautogui.press('nexttrack')
    else:
        pyautogui.press('nexttrack')

def media_prev():
    _notify("Previous Track")
    if sys.platform.startswith('linux'):
        if os.system("playerctl previous > /dev/null 2>&1") != 0:
            if os.system("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Previous > /dev/null 2>&1") != 0:
                if os.system("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.vlc /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Previous > /dev/null 2>&1") != 0:
                    pyautogui.press('prevtrack')
    else:
        pyautogui.press('prevtrack')

def handle_zoom(dist, last_zoom_dist):
    if last_zoom_dist is None:
        return dist
        
    diff = dist - last_zoom_dist
    if abs(diff) > 30: # Fire a zoom event every 30 pixels distance change
        if diff > 0:
            pyautogui.hotkey('ctrl', '+') # zoom in
        else:
            pyautogui.hotkey('ctrl', '-') # zoom out
        return dist # reset baseline after zooming
    return last_zoom_dist

subtitle_proc = None

def get_subtitle_proc():
    global subtitle_proc
    if subtitle_proc is None:
        try:
            import subprocess
            subtitle_proc = subprocess.Popen(["python", "subtitles_ui.py"], stdin=subprocess.PIPE, text=True, bufsize=1)
        except Exception as e:
            print("Failed to start subtitles_ui:", e)
    return subtitle_proc

def stop_subtitles():
    global subtitle_proc
    if subtitle_proc:
        subtitle_proc.terminate()
        subtitle_proc = None

def execute_voice_command(text):
    original_text = text
    text = text.lower()
    
    if text.startswith("subtitle: "):
        sub_text = original_text[10:].strip() # preserve original casing for neat subtitles
        settings = {}
        if os.path.exists("custom_gestures.json"):
            try:
                with open("custom_gestures.json", "r") as f:
                    settings = json.load(f)
            except Exception:
                pass
        
        proc = get_subtitle_proc()
        if settings.get("SUBTITLES_ENABLED", True):
            if proc and proc.stdin:
                try:
                    proc.stdin.write(sub_text + "\n")
                    proc.stdin.flush()
                except:
                    pass
        else:
             if proc and proc.stdin:
                  try:
                      proc.stdin.write("CMD:HIDE\n")
                      proc.stdin.flush()
                  except:
                      pass
        print(f"Action: Subtitle Displayed -> {sub_text}")
        return
        
    print(f"Voice Command Detected: {text}")
    
    import re
    # Check for direct volume setting (e.g., "set volume to 15", "volume 80")
    vol_match = re.search(r'(?:volume|set).*?(\d+)', text)
    if vol_match:
        try:
            vol = int(vol_match.group(1))
            vol = max(0, min(100, vol)) # Clamp 0-100
            if sys.platform.startswith('linux'):
                os.system(f"amixer -D pulse sset Master {vol}% > /dev/null 2>&1")
            else:
                # On windows/mac absolute volume via pyautogui isn't possible, we fallback
                print(f"Absolute volume {vol} not fully supported on this OS via pyautogui.")
            print(f"Action: Set Volume to {vol}% (VOICE)")
            return
        except (ValueError, IndexError):
            pass

    if 'next slide' in text:
        next_slide()
        print("Action: Next Slide (VOICE)")
    elif 'previous slide' in text or 'go back' in text:
        prev_slide()
        print("Action: Previous Slide (VOICE)")
    elif 'next track' in text or 'new track' in text or 'skip track' in text:
        media_next()
        print("Action: Next Track (VOICE)")
    elif 'previous track' in text or 'go back track' in text:
        media_prev()
        print("Action: Previous Track (VOICE)")
    elif 'play' in text or 'pause' in text or 'stop music' in text:
        media_play_pause()
        print("Action: Play/Pause Media (VOICE)")
    elif 'unmute' in text:
        if sys.platform.startswith('linux'):
            os.system("amixer -D pulse sset Master unmute > /dev/null 2>&1")
        else:
            pyautogui.press('volumemute')
        print("Action: Unmute (VOICE)")
    elif 'mute' in text:
        if sys.platform.startswith('linux'):
            os.system("amixer -D pulse sset Master mute > /dev/null 2>&1")
        else:
            pyautogui.press('volumemute')
        print("Action: Mute (VOICE)")
    elif 'volume up' in text or 'louder' in text:
        if sys.platform.startswith('linux'):
            os.system("amixer -D pulse sset Master 20%+ > /dev/null 2>&1")
        else:
            for _ in range(5): pyautogui.press('volumeup')
        print("Action: Volume Up (VOICE)")
    elif 'volume down' in text or 'quieter' in text:
        if sys.platform.startswith('linux'):
            os.system("amixer -D pulse sset Master 20%- > /dev/null 2>&1")
        else:
            for _ in range(5): pyautogui.press('volumedown')
        print("Action: Volume Down (VOICE)")
    elif 'full screen' in text or 'start presentation' in text:
        pyautogui.press('f5')
        print("Action: Full Screen (VOICE)")
    elif 'escape' in text or 'exit' in text:
        pyautogui.press('esc')
        print("Action: Escape (VOICE)")
