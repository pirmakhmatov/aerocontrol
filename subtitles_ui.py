import sys
import tkinter as tk
import threading
import queue

class SubtitleOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AeroControl Subtitles")
        
        # Transparent UI
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        if sys.platform.startswith('linux'):
            # wait_visibility is needed on some linux WMs before alpha can be set
            self.root.wait_visibility(self.root)
            self.root.attributes('-alpha', 0.8)
        else:
            self.root.attributes("-transparentcolor", "black")
            
        self.root.configure(bg="black")
            
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        w = int(screen_width * 0.8)
        h = 100
        x = (screen_width - w) // 2
        y = screen_height - h - 50
        
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        self.label = tk.Label(self.root, text="", font=("Helvetica", 36, "bold"), 
                              fg="#00FF99", bg="black", wraplength=w-20, justify="center")
        self.label.pack(expand=True, fill="both")
        
        self.hide()
        self.timeout_id = None
        
        self.q = queue.Queue()
        self.reader_thread = threading.Thread(target=self.read_stdin, daemon=True)
        self.reader_thread.start()
        
        self.check_queue()
        
    def show_text(self, text):
        if text == 'CMD:HIDE' or not text:
            self.hide()
            return
            
        self.root.deiconify()
        self.label.config(text=text)
        
        if self.timeout_id:
            self.root.after_cancel(self.timeout_id)
        # Hide after 5 seconds of silence
        self.timeout_id = self.root.after(5000, self.hide)
        
    def hide(self):
        self.root.withdraw()
        
    def read_stdin(self):
        # We read continuously from stdin which is piped from main.py
        for line in sys.stdin:
            self.q.put(line.strip())
            
    def check_queue(self):
        try:
            while True:
                line = self.q.get_nowait()
                if line:
                    self.show_text(line)
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SubtitleOverlay()
    app.run()
