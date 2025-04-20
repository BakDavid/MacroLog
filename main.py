import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import time
import json
from pynput import keyboard, mouse  # type: ignore
from pynput.keyboard import Controller as KeyboardController, Key  # type: ignore
from pynput.mouse import Controller as MouseController, Button  # type: ignore

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

        listbox_frame = tk.Frame(self.left_frame)
        listbox_frame.pack(expand=True, fill='both')

        self.recording_listbox = tk.Listbox(listbox_frame, width=30)
        self.recording_listbox.pack(side='left', expand=True, fill='both')

        listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.recording_listbox.yview)
        listbox_scrollbar.pack(side='right', fill='y')

        self.recording_listbox.config(yscrollcommand=listbox_scrollbar.set)
        self.recording_listbox.bind('<<ListboxSelect>>', self.load_recording_details)

        # Right: Recording details
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side='left', expand=True, fill='both')

        self.details_label = tk.Label(self.right_frame, text="Recording Details")
        self.details_label.pack()

        # Treeview + Scrollbar wrapper
        table_frame = tk.Frame(self.right_frame)
        table_frame.pack(expand=True, fill="both")

        # Vertical scrollbar - always visible by reserving space
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.details_table = ttk.Treeview(table_frame, columns=("type", "key", "time", "extra"), show="headings", yscrollcommand=scrollbar.set)
        self.details_table.heading("type", text="Type")
        self.details_table.heading("key", text="Key/Button")
        self.details_table.heading("time", text="Time")
        self.details_table.heading("extra", text="Extra")

        self.details_table.pack(side="left", expand=True, fill="both")

        scrollbar.config(command=self.details_table.yview)

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

        self.delete_event_button = tk.Button(self.button_row, text="Delete Selected Event", command=self.delete_selected_event)
        self.delete_event_button.pack(side="left", padx=5)

        self.playback_button = tk.Button(self.button_row, text="Play Macro", command=self.play_macro)
        self.playback_button.pack(side="left", padx=5)

        # Interval Entry and Checkbox
        self.interval_label = tk.Label(self.button_row, text="Interval (s):")
        self.interval_label.pack(side="left", padx=5)

        self.interval_entry = tk.Entry(self.button_row, width=8)  # Adjusted width
        self.interval_entry.insert(0, "0.01")  # Default value
        self.interval_entry.pack(side="left", padx=5)

        # Create a BooleanVar for Apply Interval checkbox
        self.apply_interval_var = tk.BooleanVar()
        self.apply_interval_checkbox = tk.Checkbutton(self.button_row, text="Apply Interval", variable=self.apply_interval_var)
        self.apply_interval_checkbox.pack(side="left", padx=5)

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
            filename = self.recording_listbox.get(selection[0]) + ".json"
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
                display_name = file[:-5]  # remove ".json"
                self.recording_listbox.insert(tk.END, display_name)

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
        index = int(selected)

        popup = tk.Toplevel(self.root)
        popup.title("Edit Event")
        popup.geometry("300x200")
        popup.transient(self.root)
        popup.grab_set()

        # Center the popup relative to the root window
        self.root.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        popup_width = 300
        popup_height = 200
        x = root_x + (root_width // 2) - (popup_width // 2)
        y = root_y + (root_height // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        tk.Label(popup, text="Key/Button:").pack(pady=5)
        key_entry = tk.Entry(popup)
        key_entry.insert(0, key)
        key_entry.pack()

        tk.Label(popup, text="Time:").pack(pady=5)
        time_entry = tk.Entry(popup)
        time_entry.insert(0, str(time_))
        time_entry.pack()

        tk.Label(popup, text="Extra (pos):").pack(pady=5)
        extra_entry = tk.Entry(popup)
        extra_entry.insert(0, str(extra))
        extra_entry.pack()

        def save_and_close():
            new_key = key_entry.get().strip()
            new_time = time_entry.get().strip()
            new_extra = extra_entry.get().strip()

            # Update internal data
            if new_key:
                self.current_data[index]["key" if type_ == "keyboard" else "button"] = new_key
            if new_time:
                try:
                    self.current_data[index]["time"] = float(new_time)
                except ValueError:
                    pass
            if new_extra and type_ == "mouse":
                try:
                    self.current_data[index]["pos"] = eval(new_extra)
                except:
                    pass

            # Write updated data to JSON immediately
            if hasattr(self, "current_file"):
                with open(self.current_file, "w") as f:
                    json.dump(self.current_data, f, indent=2)

            # Refresh the table row
            updated_key = self.current_data[index].get("key") or self.current_data[index].get("button")
            updated_time = self.current_data[index]["time"]
            updated_extra = str(self.current_data[index].get("pos", "")) if type_ == "mouse" else ""

            self.details_table.item(selected, values=(type_, updated_key, updated_time, updated_extra))
            popup.destroy()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Save", command=save_and_close).pack(side="left", padx=10)

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

        filename = self.recording_listbox.get(selection[0]) + ".json"
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

        # Check if Apply Interval checkbox is checked
        apply_interval = self.apply_interval_var.get()  # Use the updated variable
        interval = 0.01  # Default interval

        # Get the interval from the entry if the checkbox is checked
        if apply_interval:
            try:
                interval = float(self.interval_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Interval", "Please enter a valid interval value.")
                return

            # Adjust the time of each event in the macro
            last_time = 0
            for event in self.current_data:
                event["time"] = last_time
                last_time += interval

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

        # Notify that playback is complete
        messagebox.showinfo("Playback Complete", "The macro has finished executing.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorderApp(root)
    root.mainloop()
