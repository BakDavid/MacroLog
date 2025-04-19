import tkinter as tk
from tkinter import ttk
import os
import time
import json
from pynput import keyboard, mouse # type: ignore
from tkinter import simpledialog, messagebox

class MacroRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MacroLog")
        self.root.geometry("1000x400")

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

        self.details_table = ttk.Treeview(self.right_frame, columns=("type", "key", "time", "extra"), show="headings")
        self.details_table.heading("type", text="Type")
        self.details_table.heading("key", text="Key/Button")
        self.details_table.heading("time", text="Time")
        self.details_table.heading("extra", text="Extra")

        self.details_table.pack(expand=True, fill="both")

        self.macro_folder = "macro-records"
        os.makedirs(self.macro_folder, exist_ok=True)

        self.load_recordings_list()

        self.details_table.bind("<Double-1>", self.edit_event_popup)

        self.save_button = tk.Button(self.right_frame, text="Save Changes", command=self.save_changes)
        self.save_button.pack(pady=5)


    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.toggle_button.config(text="Stop Recording")
            self.start_recording()
        else:
            self.toggle_button.config(text="Start Recording")
            self.stop_recording()
            self.load_recordings_list()


    def load_recording_details(self, event):
        selection = self.recording_listbox.curselection()
        if selection:
            filename = self.recording_listbox.get(selection[0])
            filepath = os.path.join(self.macro_folder, filename)
            with open(filepath, 'r') as f:
                try:
                    self.current_data = json.load(f)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Failed to parse the recording file.")
                    return

            # Clear table
            for row in self.details_table.get_children():
                self.details_table.delete(row)

            # Populate table
            for i, entry in enumerate(self.current_data):
                type_ = entry.get("type")
                key = entry.get("key") or entry.get("button")
                time_ = entry.get("time")
                extra = str(entry.get("pos", "")) if entry["type"] == "mouse" else ""
                self.details_table.insert("", "end", iid=i, values=(type_, key, time_, extra))

            self.current_file = filepath


    def load_recordings_list(self):
        self.recording_listbox.delete(0, tk.END)
        for file in os.listdir(self.macro_folder):
            if file.endswith(".json"):
                self.recording_listbox.insert(tk.END, file)


    def start_recording(self):
        self.recording_data = []
        self.start_time = time.time()

        # Set up listeners
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener = mouse.Listener(on_click=self.on_click)

        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop_recording(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()

        # Prompt for filename
        name = simpledialog.askstring("Save Recording", "Enter a name for this recording:")
        if not name:
            messagebox.showinfo("Cancelled", "Recording not saved.")
            return

        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{self.macro_folder}/{safe_name}.json"

        with open(filename, "w") as f:
            json.dump(self.recording_data, f, indent=2)

        print(f"Saved recording: {filename}")


    def get_elapsed_time(self):
        return round(time.time() - self.start_time, 4)

    def on_key_press(self, key):
        try:
            key_str = key.char if hasattr(key, 'char') and key.char else str(key)
        except AttributeError:
            key_str = str(key)

        event = {
            "type": "keyboard",
            "key": key_str,
            "time": self.get_elapsed_time()
        }
        self.recording_data.append(event)

    def on_click(self, x, y, button, pressed):
        if pressed:
            event = {
                "type": "mouse",
                "button": str(button),
                "action": "click",
                "pos": [x, y],
                "time": self.get_elapsed_time()
            }
            self.recording_data.append(event)

    def edit_event_popup(self, event):
        selected = self.details_table.focus()
        if not selected:
            return

        current = self.details_table.item(selected)["values"]
        type_, key, time_, extra = current

        new_key = simpledialog.askstring("Edit Key/Button", "New Key/Button:", initialvalue=key)
        new_time = simpledialog.askfloat("Edit Time", "New Time:", initialvalue=float(time_))
        new_extra = simpledialog.askstring("Edit Extra", "New Extra (optional):", initialvalue=extra)

        # Update data structure
        index = int(selected)
        self.current_data[index]["key" if type_ == "keyboard" else "button"] = new_key
        self.current_data[index]["time"] = new_time
        if type_ == "mouse":
            try:
                self.current_data[index]["pos"] = eval(new_extra)
            except:
                pass

        # Update UI
        self.details_table.item(selected, values=(type_, new_key, new_time, new_extra))

    def save_changes(self):
        if not hasattr(self, "current_file") or not hasattr(self, "current_data"):
            messagebox.showinfo("Info", "No file selected to save.")
            return

        with open(self.current_file, "w") as f:
            json.dump(self.current_data, f, indent=2)

        messagebox.showinfo("Saved", f"Changes saved to {os.path.basename(self.current_file)}.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorderApp(root)
    root.mainloop()
