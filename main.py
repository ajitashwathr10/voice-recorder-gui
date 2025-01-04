import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyaudio
import wave
import os

ORANGE_THEME = "#FFA500"
DARK_MODE = "#2E2E2E"
LIGHT_MODE = "#FFFFFF"
AUDIO_QUALITY = {"Low": 8000, "Medium": 16000, "High": 44100}

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

class VoiceRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Recorder")
        self.root.geometry("500x300")
        self.root.configure(bg = ORANGE_THEME)
        self.is_recording = False
        self.is_playing = False
        self.audio_frames = []
        self.audio_quality = tk.StringVar(value = "Medium")
        self.dark_mode = tk.BooleanVar(value = False)
        self.create_widgets()
        self.apply_theme()
    
    def create_widgets(self):
        self.record_button = ttk.Button(self.root, text = "Record", command = self.toggle_recording)
        self.record_button.pack(pady = 10)

        self.play_button = ttk.Button(self.root, text = "Play", command = self.play_audio, state = tk.DISABLED)
        self.play_button.pack(pady = 5)


        settings_frame = ttk.LabelFrame(self.root, text = "Settings")
        settings_frame.pack(pady = 10, fill = "x", padx = 10)

        ttk.Label(settings_frame, text = "Audio Quality: ").grid(row = 0, column = 0, padx = 5, pady = 5)
        self.quality_menu = ttk.Combobox(settings_frame, textvariable = self.audio_quality, values = list(AUDIO_QUALITY.keys()), state = "readonly")
        self.quality_menu.grid(row = 0, column = 1, padx = 5, pady = 5)

        self.dark_mode_toggle = ttk.Checkbutton(settings_frame, text = "Dark Mode", variable = self.dark_mode, command = self.apply_theme)
        self.dark_mode_toggle.grid(row = 1, column = 0, columnspan = 2, padx = 5, pady = 5)

        self.status_label = ttk.Label(self.root, text = "Status: Idle", foreground = "green")
        self.status_label.pack(pady = 10)
    def create_styles(self):
        style = ttk.Style()
        style.configure("TFrame", background=ORANGE_THEME)
        style.configure("TLabel", background=ORANGE_THEME, foreground=DARK_MODE)
        style.configure("TButton", background=ORANGE_THEME, foreground=DARK_MODE)
    def apply_theme(self):
        theme_color = DARK_MODE if self.dark_mode.get() else LIGHT_MODE
        text_color = LIGHT_MODE if self.dark_mode.get() else DARK_MODE

        self.root.configure(bg = theme_color)
        for widget in self.root.winfo_children():
            widget.configure(style = "TFrame" if isinstance(widget, ttk.LabelFrame) else "TLabel" if isinstance(widget, ttk.Label) else "TButton")
            if isinstance(widget, ttk.Label):
                widget.configure(background = theme_color, foreground = text_color)
        
    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.record_button.config(text = "Stop Recording")
            self.status_label.config(text = "Status: Recording", foreground = "red")
            self.audio_frames = []
            self.start_recording()
        else:
            self.is_recording = False
            self.record_button.config(text = "Record")
            self.status_label.config(text = "Status: Idle", foreground = "green")
            self.stop_recording()
            self.play_button.config(state = tk.NORMAL)
        
    def start_recording(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = FORMAT, channels = CHANNELS, rate = AUDIO_QUALITY[self.audio_quality.get()], input = True, frames_per_buffer = CHUNK)
        print("Recording...")
        self.record_audio()

    def record_audio(self):
        if self.is_recording:
            data = self.stream.read(CHUNK)
            self.audio_frames.append(data)
            self.root.after(10, self.record_audio)
    
    def stop_recording(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        print("Recording stopped")
    
    def play_audio(self):
        if not self.is_playing:
            self.is_playing = True
            self.play_button.config(text = "Stop Playing")
            self.status_label.config(text = "Status: Playing", foreground = "blue")
            self.play_audio_frames()
        else:
            self.is_playing = False
            self.play_button.config(text = "Play")
            self.status_label.config(text = "Status: Idle", foreground = "green")
            self.stop_playing()
        
    def play_audio_frames(self):
        if self.is_playing:
            p = pyaudio.PyAudio()
            stream = p.open(format = FORMAT, channels = CHANNELS, rate = AUDIO_QUALITY[self.audio_quality.get()], output = True)
            for frame in self.audio_frames:
                stream.write(frame)
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.is_playing = False
            self.play_button.config(text = "Play")
            self.status_label.config(text = "Status: Idle", foreground = "green")
    
    def save_audio(self):
        file_path = filedialog.asksaveasfilename(defaultextension = ".wav", filetypes = [("WAV files", "*.wav")])
        if file_path:
            wf = wave.open(file_path, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(AUDIO_QUALITY[self.audio_quality.get()])
            wf.writeframes(b"".join(self.audio_frames))
            wf.close()
            messagebox.showinfo("Saved", f"File saved as {os.path.basename(file_path)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceRecorder(root)
    root.mainloop()
