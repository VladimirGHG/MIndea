import time
import json
import os
import datetime
import tkinter as tk
from tkinter import messagebox, font as tkFont
import piecharts

TASK_FILE = "tasks.json"
custom_font = ("Pixelify Sans", 20, "bold")

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("MINDEA")
        self.root.geometry("600x500")
        self.root.configure(bg="#202A44")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(5, weight=1)

        self.custom_font = tkFont.Font(family="Helvetica", size=12)

        self.tasks = {}
        self.timers = {}
        self.task_frames = {}
        self.selected_task = None
        self.show_today_only = False
        self.show_previous_only = False

        self.buttons_frame = tk.Frame(root, bg="#202A44")
        self.buttons_frame.grid(row=0, column=0, sticky="ew", padx=10)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)

        self.today_btn = self.make_button(self.buttons_frame, "📅 Today's Tasks", self.toggle_today_tasks)
        self.today_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.previous_btn = self.make_button(self.buttons_frame, "🕒 Previous Tasks", self.toggle_previous_tasks)
        self.previous_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.entry = tk.Entry(root, font=custom_font, bg="#141B30", fg="white")
        self.entry.grid(row=1, column=0, sticky="ew", padx=20, pady=10, ipady=10)

        self.add_btn = self.make_button(root, "➕ Add Task", self.add_task)
        self.add_btn.grid(row=2, column=0, sticky="ew", padx=20)

        # Scrollable canvas for tasks
        self.canvas_frame = tk.Frame(root, bg="#202A44")
        self.canvas_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=10)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#202A44", highlightthickness=0, height=1000)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.configure(yscrollcommand=lambda *args: None)  # Disable visible scrollbar

        self.tasks_container = tk.Frame(self.canvas, bg="#202A44")
        self.canvas.create_window((0, 0), window=self.tasks_container, anchor="nw")

        self.tasks_container.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)    # Linux scroll up
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)    # Linux scroll down


        self.show_btn = self.make_button(root, "📊 See Piecharts", piecharts.show_piechart)
        self.show_btn.grid(row=4, column=0, sticky="e", padx=20, pady=5)

        self.load_tasks()
        self.update_task_display()
        self.update_timers()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def btn_style(self, bg="#141B30", active="#ffffff"):
        return {
            "font": custom_font,
            "bg": bg,
            "fg": "white",
            "activebackground": active,
            "bd": 0,
            "relief": tk.FLAT,
            "width": 15,
            "height": 2
        }
    
    def make_button(self, parent, text, command, bg="#141B30", active="#ffffff"):
        btn = tk.Button(parent, text=text, command=command, **self.btn_style(bg, active))
        self.add_hover_animation(btn, normal_bg=bg, hover_bg="#1F2B47")
        return btn

    def add_hover_animation(self, button, normal_bg="#141B30", hover_bg="#1F2B47"):
        def on_enter(e): button.config(bg=hover_bg)
        def on_leave(e): button.config(bg=normal_bg)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def flash_add_button(self):
        original_color = "#141B30"
        highlight_color = "#4CAF50"
        self.add_btn.config(bg=highlight_color)
        self.root.after(150, lambda: self.add_btn.config(bg=original_color))

    def load_tasks(self):
        if os.path.exists(TASK_FILE):
            with open(TASK_FILE, "r") as f:
                loaded_tasks = json.load(f)
                for task, info in loaded_tasks.items():
                    if isinstance(info, dict):
                        self.tasks[task] = info
                    else:
                        self.tasks[task] = {"time": info, "date": datetime.datetime.now().date().isoformat()}
        for task in self.tasks:
            self.timers[task] = {"running": False, "start_time": None}

    def save_tasks(self):
        with open(TASK_FILE, "w") as f:
            json.dump(self.tasks, f)

    def update_task_display(self):
        for widget in self.tasks_container.winfo_children():
            widget.destroy()

        self.task_frames.clear()

        today_date = datetime.datetime.now().date().isoformat()

        for task, task_info in self.tasks.items():
            task_date = task_info.get("date", today_date)

            if self.show_today_only and task_date != today_date:
                continue
            if self.show_previous_only and task_date == today_date:
                continue

            mins, secs = divmod(int(task_info["time"]), 60)
            frame = tk.Frame(self.tasks_container, bg="#1A223A", pady=7, padx=10, width=2520, height=100)
            frame.pack_propagate(False)
            frame.pack(fill=tk.X, padx=10, pady=2)

            task_label = tk.Label(frame, text=f"{task} — {mins:02d}:{secs:02d}", fg="white", bg="#1A223A", font=custom_font)
            task_label.pack(side=tk.LEFT, padx=10)

            select_btn = tk.Button(
                frame,
                text="✅ Select",
                command=lambda t=task: self.select_task(t),
                **self.btn_style("#4CAF50", "#388E3C")
            )
            self.add_hover_animation(select_btn)
            select_btn.pack(side=tk.RIGHT, padx=5, pady=2)


            self.task_frames[task] = frame

    def add_task(self):
        task = self.entry.get().strip()
        if task and task not in self.tasks:
            self.tasks[task] = {"time": 0, "date": datetime.datetime.now().strftime("%Y-%m-%d")}
            self.timers[task] = {"running": False, "start_time": None}
            self.entry.delete(0, tk.END)
            self.save_tasks()
            self.update_task_display()

    def select_task(self, task):
        self.selected_task = task
        frame = self.task_frames.get(task)
        if frame:
            for widget in frame.winfo_children():
                widget.destroy()

            mins, secs = divmod(int(self.tasks[task]["time"]), 60)
            label = tk.Label(frame, text=f"{task} — {mins:02d}:{secs:02d}", fg="white", bg="#1A223A", font=custom_font)
            label.pack(side=tk.LEFT, padx=10)

            start_btn = tk.Button(frame, text="Start", command=self.start_timer, **self.btn_style("#2196F3", "#1976D2"))
            start_btn.config(width=6, height=1)
            start_btn.pack(side=tk.RIGHT, padx=5)

            pause_btn = tk.Button(frame, text="Pause", command=self.pause_timer, **self.btn_style("#607D8B", "#455A64"))
            pause_btn.config(width=6, height=1)
            pause_btn.pack(side=tk.RIGHT, padx=5)

            del_btn = tk.Button(frame, text="Delete", command=self.delete_task, **self.btn_style("#f44336", "#d32f2f"))
            del_btn.config(width=6, height=1)
            del_btn.pack(side=tk.RIGHT, padx=5)

    def delete_task(self):
        task = self.selected_task
        if task:
            del self.tasks[task]
            del self.timers[task]
            self.selected_task = None
            self.save_tasks()
            self.update_task_display()

    def start_timer(self):
        task = self.selected_task
        if task and not self.timers[task]["running"]:
            self.timers[task]["running"] = True
            self.tasks[task]["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
            self.timers[task]["start_time"] = time.time()

    def pause_timer(self):
        task = self.selected_task
        if task and self.timers[task]["running"]:
            elapsed = time.time() - self.timers[task]["start_time"]
            self.tasks[task]["time"] += elapsed
            self.timers[task]["running"] = False
            self.timers[task]["start_time"] = None
            self.save_tasks()
            self.update_task_display()

    def update_timers(self):
        for task in self.timers:
            if self.timers[task]["running"]:
                elapsed = time.time() - self.timers[task]["start_time"]
                total = self.tasks[task]["time"] + elapsed
                mins, secs = divmod(int(total), 60)
                frame = self.task_frames.get(task)
                if frame:
                    for widget in frame.winfo_children():
                        widget.destroy()

                    label = tk.Label(frame, text=f"{task} — {mins:02d}:{secs:02d}", fg="white", bg="#1A223A", font=custom_font)
                    label.pack(side=tk.LEFT, padx=10)

                    if self.selected_task == task:
                        start_btn = tk.Button(frame, text="Start", command=self.start_timer, **self.btn_style("#2196F3", "#1976D2"))
                        start_btn.config(width=6, height=1)
                        start_btn.pack(side=tk.RIGHT, padx=5)

                        pause_btn = tk.Button(frame, text="Pause", command=self.pause_timer, **self.btn_style("#607D8B", "#455A64"))
                        pause_btn.config(width=6, height=1)
                        pause_btn.pack(side=tk.RIGHT, padx=5)

                        del_btn = tk.Button(frame, text="Delete", command=self.delete_task, **self.btn_style("#f44336", "#d32f2f"))
                        del_btn.config(width=6, height=1)
                        del_btn.pack(side=tk.RIGHT, padx=5)
                    else:
                        select_btn = tk.Button(frame, text="Select", command=lambda t=task: self.select_task(t), **self.btn_style("#4CAF50", "#388E3C"))
                        select_btn.config(width=8, height=1)
                        select_btn.pack(side=tk.RIGHT, padx=5)
        self.root.after(1000, self.update_timers)

    def toggle_today_tasks(self):
        self.show_today_only = not self.show_today_only
        self.show_previous_only = False
        self.update_task_display()

    def toggle_previous_tasks(self):
        self.show_previous_only = not self.show_previous_only
        self.show_today_only = False
        self.update_task_display()

    def on_close(self):
        for task in self.timers:
            if self.timers[task]["running"]:
                elapsed = time.time() - self.timers[task]["start_time"]
                self.tasks[task]["time"] += elapsed
                self.timers[task]["running"] = False
        self.save_tasks()
        self.root.destroy()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:
            # Windows / macOS
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# ---- Run App ----
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
