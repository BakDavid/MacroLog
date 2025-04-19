import tkinter as tk

class MacroRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MacroLog")
        self.root.geometry("300x150")

        self.recording = False

        self.record_button = tk.Button(root, text="Start Recording", command=self.start_recording)
        self.record_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # Status label
        self.status = tk.Label(root, text="Status: Idle")
        self.status.pack(pady=5)

    def start_recording(self):
        self.recording = True
        self.status.config(text="Status: Recording...")
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # TODO: Start keyboard & mouse listeners here

    def stop_recording(self):
        self.recording = False
        self.status.config(text="Status: Stopped")
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        # TODO: Stop listeners & save file

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorderApp(root)
    root.mainloop()
