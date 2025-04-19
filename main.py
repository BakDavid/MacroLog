import tkinter as tk
from tkinter import ttk
import os
import time
import json
from pynput import keyboard, mouse # type: ignore
from tkinter import simpledialog, messagebox
from pynput.keyboard import Controller as KeyboardController, Key # type: ignore
from pynput.mouse import Controller as MouseController, Button # type: ignore

class MacroRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MacroLog")
        self.root.geometry("1000x500")

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

        self.delete_file_button = tk.Button(self.left_frame, text="Delete Selected File", command=self.delete_selected_file)
        self.delete_file_button.pack(pady=5)

        self.details_table.bind("<Delete>", lambda e: self.delete_selected_event())
        self.details_table.bind("<BackSpace>", lambda e: self.delete_selected_event())

        self.recording_listbox.bind("<Delete>", lambda e: self.delete_selected_file())
        self.recording_listbox.bind("<BackSpace>", lambda e: self.delete_selected_file())

        # Buttons inline
        self.button_row = tk.Frame(self.right_frame)
        self.button_row.pack(pady=5)

        self.save_button = tk.Button(self.button_row, text="Save Changes", command=self.save_changes)
        self.save_button.pack(side="left", padx=5)

        self.delete_event_button = tk.Button(self.button_row, text="Delete Selected Event", command=self.delete_selected_event)
        self.delete_event_button.pack(side="left", padx=5)

        self.playback_button = tk.Button(self.button_row, text="Play Macro", command=self.play_macro)
        self.playback_button.pack(side="left", padx=5)



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

        # Prompt only if the user wants to change the value (empty input means skip)
        new_key = simpledialog.askstring("Edit Key/Button", "New Key/Button (leave blank to keep unchanged):", initialvalue=key)
        new_time = simpledialog.askstring("Edit Time", "New Time (leave blank to keep unchanged):", initialvalue=str(time_))
        new_extra = simpledialog.askstring("Edit Extra", "New Extra (optional, leave blank to keep unchanged):", initialvalue=extra)

        # Convert index safely
        index = int(selected)

        # Update values conditionally
        if new_key:
            self.current_data[index]["key" if type_ == "keyboard" else "button"] = new_key
        else:
            new_key = key  # keep old value for display

        if new_time:
            try:
                new_time = float(new_time)
                self.current_data[index]["time"] = new_time
            except ValueError:
                new_time = time_  # fallback to original
        else:
            new_time = time_

        if new_extra and type_ == "mouse":
            try:
                self.current_data[index]["pos"] = eval(new_extra)
            except:
                pass  # leave as-is
        else:
            new_extra = extra

        # Update the table row visually
        self.details_table.item(selected, values=(type_, new_key, new_time, new_extra))


    def save_changes(self):
        if not hasattr(self, "current_file") or not hasattr(self, "current_data"):
            messagebox.showinfo("Info", "No file selected to save.")
            return

        with open(self.current_file, "w") as f:
            json.dump(self.current_data, f, indent=2)

        messagebox.showinfo("Saved", f"Changes saved to {os.path.basename(self.current_file)}.")


    def delete_selected_event(self):
        selected_items = self.details_table.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No events selected.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Delete {len(selected_items)} selected event(s)?")
        if confirm:
            indices = sorted([int(i) for i in selected_items], reverse=True)
            for index in indices:
                self.details_table.delete(index)
                del self.current_data[index]

            # Reindex Treeview iids
            for i, row in enumerate(self.details_table.get_children()):
                self.details_table.item(row, iid=i)

    def delete_selected_file(self):
        selection = self.recording_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "No file selected.")
            return

        filename = self.recording_listbox.get(selection[0])
        filepath = os.path.join(self.macro_folder, filename)

        confirm = messagebox.askyesno("Confirm Delete", f"Delete file '{filename}'?")
        if confirm:
            try:
                os.remove(filepath)
                self.load_recordings_list()
                self.details_table.delete(*self.details_table.get_children())
                messagebox.showinfo("Deleted", f"'{filename}' has been deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")

    def play_macro(self):
        if not hasattr(self, "current_data"):
            messagebox.showinfo("Info", "No macro loaded to play.")
            return

        self.abort_playback = False

        def on_key_press(key):
            if key == Key.f12:
                self.abort_playback = True
                return False  # stop listener

        listener = keyboard.Listener(on_press=on_key_press)
        listener.start()

        keyboard_controller = KeyboardController()
        mouse_controller = MouseController()

        last_time = 0
        for event in self.current_data:
            if self.abort_playback:
                messagebox.showinfo("Aborted", "Playback stopped by user (F12).")
                break

            time.sleep(max(0, event["time"] - last_time))
            last_time = event["time"]

            if event["type"] == "keyboard":
                key = event["key"]
                try:
                    special_keys = {
                        'Key.space': Key.space,
                        'Key.enter': Key.enter,
                        'Key.esc': Key.esc,
                        'Key.tab': Key.tab,
                        'Key.shift': Key.shift,
                        'Key.ctrl': Key.ctrl,
                        'Key.alt': Key.alt,
                        'Key.backspace': Key.backspace,
                        'Key.delete': Key.delete
                    }

                    if key in special_keys:
                        keyboard_controller.press(special_keys[key])
                        keyboard_controller.release(special_keys[key])
                    elif len(key) == 1:
                        keyboard_controller.press(key)
                        keyboard_controller.release(key)
                except Exception as e:
                    print(f"Keyboard error: {e}")

            elif event["type"] == "mouse":
                try:
                    x, y = event["pos"]
                    mouse_controller.position = (x, y)
                    button = Button.left if 'left' in event["button"] else Button.right
                    mouse_controller.press(button)
                    mouse_controller.release(button)
                except Exception as e:
                    print(f"Mouse error: {e}")
        listener.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorderApp(root)
    root.mainloop()
