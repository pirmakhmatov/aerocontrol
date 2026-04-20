import customtkinter as ctk
import cv2
import json
import os
import math
from PIL import Image
from config import CAM_INDEX, CAM_WIDTH, CAM_HEIGHT
from gesture.detector import HandDetector

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AeroSettings(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AeroControl Configuration")
        self.geometry("1100x700")
        
        self.cap = cv2.VideoCapture(CAM_INDEX)
        self.detector = HandDetector()
        
        self.custom_db = {}
        if os.path.exists("custom_gestures.json"):
            try:
                with open("custom_gestures.json", "r") as f:
                    self.custom_db = json.load(f)
            except:
                pass
                
        self.current_recording = None
        self.actions = [
            ('0', 'SCROLL', 'Jedi Scroll'),
            ('1', 'NEXT_SLIDE', 'Next Slide'),
            ('2', 'PREV_SLIDE', 'Prev Slide'),
            ('3', 'VOL_UP', 'Volume Up'),
            ('4', 'VOL_DOWN', 'Volume Down'),
            ('5', 'MUTE', 'Mute Toggle'),
            ('6', 'PLAY_PAUSE', 'Play/Pause Media'),
            ('7', 'NEXT_TRACK', 'Next Track'),
            ('8', 'PREV_TRACK', 'Prev Track'),
            ('9', 'AI_MIC', 'AI Voice (Default=FIST)')
        ]
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar Menu
        self.sidebar = ctk.CTkScrollableFrame(self, width=350, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="AeroControl Actions", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 20), padx=20, anchor="w")
        
        self.buttons = {}
        for hotkey, action_id, name in self.actions:
            status = "✓ Bound" if action_id in self.custom_db else "Unbound"
            color = "#1f6aa5" if action_id in self.custom_db else "transparent"
            btn = ctk.CTkButton(self.sidebar, text=f"[{hotkey}] {name} - {status}", 
                                anchor="w", fg_color=color, border_width=1,
                                command=lambda a=action_id: self.start_recording(a))
            btn.pack(pady=5, padx=20, fill="x")
            self.buttons[action_id] = btn
            
        ctk.CTkLabel(self.sidebar, text="System Toggles", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 10), padx=20, anchor="w")
        
        self.notif_var = ctk.BooleanVar(value=self.custom_db.get("NOTIFICATIONS_ENABLED", True))
        ctk.CTkSwitch(self.sidebar, text="Desktop Notifications", variable=self.notif_var, command=self.update_toggles).pack(pady=10, padx=20, anchor="w")
        
        self.debug_var = ctk.BooleanVar(value=self.custom_db.get("DEBUG_WINDOW_ENABLED", False))
        ctk.CTkSwitch(self.sidebar, text="Daemon CV2 Debug Window", variable=self.debug_var, command=self.update_toggles).pack(pady=10, padx=20, anchor="w")
        
        self.sub_var = ctk.BooleanVar(value=self.custom_db.get("SUBTITLES_ENABLED", True))
        ctk.CTkSwitch(self.sidebar, text="Live English Subtitles", variable=self.sub_var, command=self.update_toggles).pack(pady=10, padx=20, anchor="w")
        
        self.ai_var = ctk.BooleanVar(value=self.custom_db.get("AI_ASSISTANT_ENABLED", True))
        ctk.CTkSwitch(self.sidebar, text="AI Voice Assistant", variable=self.ai_var, command=self.update_toggles).pack(pady=10, padx=20, anchor="w")
        
        # Proper slider for notification time
        self.time_var = ctk.IntVar(value=self.custom_db.get("NOTIFICATIONS_TIME", 2000))
        ctk.CTkLabel(self.sidebar, text="Notification Time (ms)").pack(pady=(20, 0), padx=20, anchor="w")
        
        slider = ctk.CTkSlider(self.sidebar, from_=500, to=5000, number_of_steps=9, variable=self.time_var, command=self.update_slider)
        slider.pack(pady=10, padx=20, fill="x")
        self.time_lbl = ctk.CTkLabel(self.sidebar, text=f"{self.time_var.get()} ms")
        self.time_lbl.pack(pady=0, padx=20, anchor="w")
        
        ctk.CTkButton(self.sidebar, text="Save & Exit", fg_color="green", hover_color="darkgreen", command=self.save_and_quit).pack(pady=(40, 10), padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Clear All Gestures", fg_color="#a83232", hover_color="#802121", command=self.clear_db).pack(pady=5, padx=20, fill="x")
        
        # Video Frame
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.status_lbl = ctk.CTkLabel(self.video_frame, text="Select an action on the left to record its shape", font=ctk.CTkFont(size=20), text_color="#aaaaaa")
        self.status_lbl.pack(pady=20)
        
        self.video_lbl = ctk.CTkLabel(self.video_frame, text="")
        self.video_lbl.pack(expand=True)
        
        self.update_video()
        
    def start_recording(self, action_id):
        self.current_recording = action_id
        action_name = dict([(a[1], a[2]) for a in self.actions]).get(action_id, "")
        self.status_lbl.configure(text=f"HOLD STILL! Recording: {action_name}", text_color="#ff5555")
        
    def update_toggles(self):
        self.custom_db["NOTIFICATIONS_ENABLED"] = self.notif_var.get()
        self.custom_db["DEBUG_WINDOW_ENABLED"] = self.debug_var.get()
        self.custom_db["SUBTITLES_ENABLED"] = self.sub_var.get()
        self.custom_db["AI_ASSISTANT_ENABLED"] = self.ai_var.get()
        
    def update_slider(self, value):
        val = int(value)
        self.time_lbl.configure(text=f"{val} ms")
        self.custom_db["NOTIFICATIONS_TIME"] = val
        
    def clear_db(self):
        self.custom_db.clear()
        self.refresh_buttons()
        
    def refresh_buttons(self):
        for hotkey, action_id, name in self.actions:
            status = "✓ Bound" if action_id in self.custom_db else "Unbound"
            color = "#1f6aa5" if action_id in self.custom_db else "transparent"
            self.buttons[action_id].configure(text=f"[{hotkey}] {name} - {status}", fg_color=color)

    def normalize_landmarks(self, lmList):
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

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame, all_lm = self.detector.find_hands(frame, draw=True)
            
            if self.current_recording and all_lm:
                normalized = self.normalize_landmarks(all_lm[0])
                self.custom_db[self.current_recording] = normalized
                self.status_lbl.configure(text=f"Successfully Saved!", text_color="#55ff55")
                self.current_recording = None
                self.refresh_buttons()
                
            # Convert CV2 Frame to Tkinter CTkImage natively
            cv2data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2data)
            
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 480))
            
            self.video_lbl.configure(image=imgtk)
            self.video_lbl.image = imgtk
            
        self.after(15, self.update_video)
        
    def save_and_quit(self):
        with open("custom_gestures.json", "w") as f:
            json.dump(self.custom_db, f, indent=4)
        self.cap.release()
        self.destroy()

def main():
    app = AeroSettings()
    app.mainloop()

if __name__ == "__main__":
    main()
