import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import vlc

class MotionTrackerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Modern & MOG2 Tracker")
        root.configure(bg='#2e2e2e')
        # Top controls frame
        top = tk.Frame(root, bg='#2e2e2e')
        top.pack(fill='x', padx=10, pady=5)
        btn_conf = dict(bg='#444444', fg='white', activebackground='#555555', activeforeground='white', bd=0)

        self.btn_open = tk.Button(top, text="Open Video", command=self.open_video, **btn_conf)
        self.btn_open.pack(side='left', padx=5)
        self.btn_toggle = tk.Button(top, text="Show Mask", command=self.toggle_mode, **btn_conf)
        self.btn_toggle.pack(side='left', padx=5)
        self.btn_pause = tk.Button(top, text="Pause", command=self.toggle_pause, state='disabled', **btn_conf)
        self.btn_pause.pack(side='left', padx=5)
        self.btn_quit = tk.Button(top, text="Quit", command=self.on_quit, **btn_conf)
        self.btn_quit.pack(side='right', padx=5)

        # Video display panel
        self.video_panel = tk.Label(root, bg='black')
        self.video_panel.pack(fill='both', expand=True, padx=10, pady=5)

        # Bottom controls frame
        bottom = tk.Frame(root, bg='#2e2e2e')
        bottom.pack(fill='x', padx=10, pady=5)
        scale_conf = dict(bg='#2e2e2e', fg='white', troughcolor='#555555', highlightthickness=0, bd=0)

        # Mask threshold slider
        tk.Label(bottom, text="Mask Thresh", bg='#2e2e2e', fg='white').grid(row=0, column=0, padx=5)
        self.mask_slider = tk.Scale(bottom, from_=0, to=255, orient='horizontal', length=150, **scale_conf)
        self.mask_slider.set(16)
        self.mask_slider.grid(row=1, column=0, padx=5)

        # Area threshold slider
        tk.Label(bottom, text="Area Thresh", bg='#2e2e2e', fg='white').grid(row=0, column=1, padx=5)
        self.area_slider = tk.Scale(bottom, from_=0, to=5000, orient='horizontal', length=150, **scale_conf)
        self.area_slider.set(500)
        self.area_slider.grid(row=1, column=1, padx=5)

        # Volume slider
        tk.Label(bottom, text="Volume", bg='#2e2e2e', fg='white').grid(row=0, column=2, padx=5)
        self.vol_slider = tk.Scale(bottom, from_=0, to=100, orient='horizontal', length=150, command=self.set_volume, **scale_conf)
        self.vol_slider.set(100)
        self.vol_slider.grid(row=1, column=2, padx=5)

        # Speed slider
        tk.Label(bottom, text="Speed", bg='#2e2e2e', fg='white').grid(row=0, column=3, padx=5)
        self.speed_slider = tk.Scale(bottom, from_=0.25, to=2.0, resolution=0.05, orient='horizontal', length=150, command=self.set_speed, **scale_conf)
        self.speed_slider.set(1.0)
        self.speed_slider.grid(row=1, column=3, padx=5)

        # State variables
        self.cap = None
        self.backSub = None
        self.show_mask = False
        self.running = False
        self.video_path = None
        self.playback_delay = 30  # ms base frame delay

        # VLC audio-only instance
        self.vlc_instance = vlc.Instance('--no-xlib', '--no-video')
        self.audio_player = None

    def open_video(self):
        path = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if not path:
            return
        # Stop existing playback
        self.running = False
        if self.cap:
            self.cap.release()
        if self.audio_player:
            self.audio_player.stop()
        self.btn_pause.config(state='disabled')

        # Initialize new video
        self.video_path = path
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot open video.")
            return
        self.backSub = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=int(self.mask_slider.get()),
            detectShadows=True
        )

        # Setup audio
        media = self.vlc_instance.media_new(self.video_path)
        self.audio_player = self.vlc_instance.media_player_new()
        self.audio_player.set_media(media)
        self.audio_player.audio_set_volume(self.vol_slider.get())
        events = self.audio_player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self._audio_loop)

        # Enable pause and start playback
        self.btn_pause.config(state='normal', text='Pause')
        self.running = True
        self.set_speed(self.speed_slider.get())
        self.audio_player.play()
        self.process_frame()

    def toggle_pause(self):
        if self.running:
            self.running = False
            self.btn_pause.config(text='Play')
            if self.audio_player:
                self.audio_player.pause()
        else:
            self.running = True
            self.btn_pause.config(text='Pause')
            if self.audio_player:
                self.audio_player.play()
            self.process_frame()

    def _audio_loop(self, event):
        if self.running and self.audio_player:
            self.audio_player.stop()
            self.audio_player.play()

    def set_volume(self, val):
        if self.audio_player:
            self.audio_player.audio_set_volume(int(float(val)))

    def set_speed(self, val):
        speed = float(val)
        self.playback_delay = max(1, int(30 / speed))
        if self.audio_player:
            try:
                self.audio_player.set_rate(speed)
            except Exception:
                pass

    def toggle_mode(self):
        self.show_mask = not self.show_mask
        self.btn_toggle.config(text="Show Boxes" if self.show_mask else "Show Mask")

    def process_frame(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if not ret:
            # Loop video
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                return

        # Motion detection
        thr = int(self.mask_slider.get())
        self.backSub.setVarThreshold(thr)
        mask = self.backSub.apply(frame)
        _, mask = cv2.threshold(mask, thr, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

        if self.show_mask:
            disp = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        else:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            area_min = self.area_slider.get()
            for cnt in contours:
                if cv2.contourArea(cnt) < area_min:
                    continue
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
            disp = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(disp)
        imgtk = ImageTk.PhotoImage(img)
        self.video_panel.imgtk = imgtk
        self.video_panel.config(image=imgtk)

        self.root.after(self.playback_delay, self.process_frame)

    def on_quit(self):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.audio_player:
            self.audio_player.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MotionTrackerGUI(root)
    root.mainloop()
