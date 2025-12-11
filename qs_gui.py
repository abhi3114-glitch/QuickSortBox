import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import json
from pathlib import Path
from qs_core import QuickSortBox

# --- Dark Theme Colors ---
BG_COLOR = "#2e2e2e"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#007acc"
ACCENT_HOVER = "#005f9e"
SECONDARY_BG = "#3e3e3e"

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=ACCENT_COLOR, 
            fg=FG_COLOR, 
            activebackground=ACCENT_HOVER, 
            activeforeground=FG_COLOR, 
            relief='flat', 
            font=("Segoe UI", 10, "bold"),
            padx=15, 
            pady=8
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['bg'] = ACCENT_HOVER

    def on_leave(self, e):
        self['bg'] = ACCENT_COLOR

class QuickSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickSortBox Pro")
        self.root.geometry("700x550")
        self.root.configure(bg=BG_COLOR)
        
        # Configure Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Dark Theme for TTK
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10))
        self.style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=SECONDARY_BG, foreground=FG_COLOR, padding=[15, 5])
        self.style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", "#ffffff")])
        self.style.configure("Horizontal.TProgressbar", troughcolor=SECONDARY_BG, background=ACCENT_COLOR, bordercolor=BG_COLOR, lightcolor=ACCENT_COLOR, darkcolor=ACCENT_COLOR)

        # Main Layout
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.notebook.add(self.tab_settings, text="Settings")

        self.setup_dashboard()
        self.setup_settings()
        
        self.qs = None # Instance placeholder

    def setup_dashboard(self):
        # Path Selection
        frame_top = tk.Frame(self.tab_dashboard, bg=BG_COLOR)
        frame_top.pack(pady=20, padx=20, fill='x')
        
        tk.Label(frame_top, text="Target Folder:", bg=BG_COLOR, fg=FG_COLOR, font=("Segoe UI", 11)).pack(anchor='w')
        
        self.path_var = tk.StringVar(value=str(Path.home() / 'Downloads'))
        path_entry = tk.Entry(frame_top, textvariable=self.path_var, width=50, bg=SECONDARY_BG, fg=FG_COLOR, insertbackground='white', relief='flat', font=("Consolas", 10))
        path_entry.pack(side='left', fill='x', expand=True, ipady=5, padx=(0, 10))
        
        btn_browse = tk.Button(frame_top, text="Browse", command=self.browse_folder, bg=SECONDARY_BG, fg=FG_COLOR, relief='flat', padx=10)
        btn_browse.pack(side='left')

        # Control Panel
        frame_controls = tk.Frame(self.tab_dashboard, bg=BG_COLOR)
        frame_controls.pack(pady=10)
        
        self.dry_run_var = tk.BooleanVar(value=True)
        self.chk_dry = tk.Checkbutton(frame_controls, text="Dry Run (Simulate only)", variable=self.dry_run_var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=SECONDARY_BG, activebackground=BG_COLOR, activeforeground=FG_COLOR, font=("Segoe UI", 10))
        self.chk_dry.pack(side='left', padx=10)
        
        tk.Label(frame_controls, text="(Uncheck to actually move files)", bg=BG_COLOR, fg="#aaaaaa", font=("Segoe UI", 8)).pack(side='left', padx=(0, 20))
        
        self.btn_run = ModernButton(frame_controls, text="🚀 Sort Files", command=self.start_sort)
        self.btn_run.pack(side='left', padx=10)
        
        self.btn_undo = tk.Button(frame_controls, text="↩ Undo Last", command=self.start_undo, bg="#D32F2F", fg="white", relief='flat', font=("Segoe UI", 10, "bold"), padx=15, pady=8)
        self.btn_undo.pack(side='left', padx=10)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.tab_dashboard, variable=self.progress_var, maximum=100, style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill='x', padx=40, pady=(20, 5))
        
        self.status_label = tk.Label(self.tab_dashboard, text="Ready", bg=BG_COLOR, fg="#aaaaaa", font=("Segoe UI", 9))
        self.status_label.pack(pady=(0, 10))

        # Log Area
        tk.Label(self.tab_dashboard, text="Activity Log:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w', padx=20)
        self.log_area = scrolledtext.ScrolledText(self.tab_dashboard, height=10, bg=SECONDARY_BG, fg=FG_COLOR, insertbackground='white', relief='flat', font=("Consolas", 9))
        self.log_area.pack(fill='both', expand=True, padx=20, pady=(5, 20))
        self.log_area.tag_config("info", foreground="#4CAF50")
        self.log_area.tag_config("dup", foreground="#FF9800")
        self.log_area.tag_config("err", foreground="#F44336")

    def setup_settings(self):
        # Provide a text area to edit JSON config
        tk.Label(self.tab_settings, text="Edit Category Rules (JSON)", bg=BG_COLOR, fg=FG_COLOR, font=("Segoe UI", 12)).pack(pady=10)
        tk.Label(self.tab_settings, text="Modify extensions and click Save.", bg=BG_COLOR, fg="#aaaaaa").pack()
        
        self.txt_config = scrolledtext.ScrolledText(self.tab_settings, bg=SECONDARY_BG, fg=FG_COLOR, insertbackground='white', font=("Consolas", 10))
        self.txt_config.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Load initial config
        self.refresh_config_view()
        
        btn_save = ModernButton(self.tab_settings, text="Save Settings", command=self.save_settings)
        btn_save.pack(pady=20)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def refresh_config_view(self):
        # Just create a dummy instance to load config
        temp_qs = QuickSortBox(".")
        config_str = json.dumps(temp_qs.config, indent=4)
        self.txt_config.delete('1.0', tk.END)
        self.txt_config.insert(tk.END, config_str)

    def save_settings(self):
        try:
            new_config = json.loads(self.txt_config.get('1.0', tk.END))
            # Validate basic structure
            if 'EXTENSIONS' not in new_config:
                 raise ValueError("Missing 'EXTENSIONS' key")
            
            # Save via QuickSortBox instance
            qs = QuickSortBox(".")
            qs.config = new_config
            qs.save_config()
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Invalid JSON", f"Error parsing config: {e}")

    def log(self, message, tag=None):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n", tag)
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def progress_update(self, current, total, msg):
        pct = (current / total) * 100
        self.progress_var.set(pct)
        self.status_label.config(text=f"{msg} ({int(pct)}%)")
        self.root.update_idletasks()

    def start_sort(self):
        target = self.path_var.get()
        if not target: return
        
        self.log("-" * 40)
        self.log(f"Started processing...", "info")
        self.btn_run.config(state='disabled')
        threading.Thread(target=self._run_thread, args=(target,), daemon=True).start()

    def _run_thread(self, target):
        try:
            self.qs = QuickSortBox(target)
            moves, stats = self.qs.sort_files(
                dry_run=self.dry_run_var.get(),
                progress_callback=self.thread_safe_progress
            )
            
            self.root.after(0, self.finish_sort, moves, stats)
        except Exception as e:
            self.root.after(0, self.log, f"Error: {e}", "err")
            self.root.after(0, lambda: self.btn_run.config(state='normal'))

    def thread_safe_progress(self, current, total, msg):
        self.root.after(0, self.progress_update, current, total, msg)

    def finish_sort(self, moves, stats):
        self.progress_var.set(100)
        self.status_label.config(text="Completed")
        
        if not moves:
            self.log("No files needed sorting.")
        else:
            count = len(moves)
            self.log(f"Processed {count} files.", "info")
            # Summarize stats
            self.log("--- Stats ---")
            for k, v in stats.items():
                if v > 0: self.log(f"  {k}: {v}")
        
        self.btn_run.config(state='normal')

    def start_undo(self):
        target = self.path_var.get()
        if messagebox.askyesno("Undo", "Revert last operation?"):
            self.log("Undoing last operation...", "info")
            threading.Thread(target=self._undo_thread, args=(target,), daemon=True).start()

    def _undo_thread(self, target):
        try:
            self.qs = QuickSortBox(target)
            success = self.qs.undo_last_run(progress_callback=self.thread_safe_progress)
            if success:
                self.root.after(0, self.log, "Undo successful.", "info")
            else:
                self.root.after(0, self.log, "Nothing to undo.", "err")
        except Exception as e:
            self.root.after(0, self.log, f"Undo Error: {e}", "err")
        
        self.root.after(0, lambda: self.status_label.config(text="Ready"))
        self.root.after(0, lambda: self.progress_var.set(0))


if __name__ == "__main__":
    root = tk.Tk()
    app = QuickSortApp(root)
    root.mainloop()
