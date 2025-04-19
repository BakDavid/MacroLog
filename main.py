import tkinter as tk
from tkinter import ttk
import os

class MacroRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MacroLog")
        self.root.geometry("700x400")

        self.recording = False

        # Setup layout frames
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=10)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Toggle button
        self.toggle_button = tk.Button(self.top_frame, text="Start Recording", command=self.toggle_recording)
        self.toggle_button.pack()

        # Left: Recording list
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side='left', fill='y', padx=(0, 10))

        self.recordings_label = tk.Label(self.left_frame, text="Saved Recordings")
        self.recordings_label.pack()

        self.recording_listbox = tk.Listbox(self.left_frame, width=30)
        self.recording_listbox.pack(expand=True, fill='y')
        self.recording_listbox.bind('<<ListboxSelect>>', self.load_recording_details)

        # Right: Recording details
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side='left', expand=True, fill='both')

        self.details_label = tk.Label(self.right_frame, text="Recording Details")
        self.details_label.pack()

        self.details_text = tk.Text(self.right_frame, wrap='none')
        self.details_text.pack(expand=True, fill='both')

        self.macro_folder = "macro-records"
        os.makedirs(self.macro_folder, exist_ok=True)

        self.load_recordings_list()

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.toggle_button.config(text="Stop Recording")
            # TODO: Start recording inputs
        else:
            self.toggle_button.config(text="Start Recording")
            # TODO: Stop recording and save file
            self.load_recordings_list()

    def load_recordings_list(self):
        self.recording_listbox.delete(0, tk.END)
        for file in os.listdir(self.macro_folder):
            if file.endswith(".json"):
                self.recording_listbox.insert(tk.END, file)

    def load_recording_details(self, event):
        selection = self.recording_listbox.curselection()
        if selection:
            filename = self.recording_listbox.get(selection[0])
            filepath = os.path.join(self.macro_folder, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, content)

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorderApp(root)
    root.mainloop()
