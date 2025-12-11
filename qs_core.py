import os
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime

# Default Configuration
DEFAULT_CONFIG = {
    'EXTENSIONS': {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        'Video': ['.mp4', '.mkv', '.avi', '.mov', '.wmv'],
        'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.json', '.xml'],
        'Executables': ['.exe', '.msi', '.bat', '.sh', '.app']
    }
}

CONFIG_FILE = Path("config.json")

class QuickSortBox:
    def __init__(self, target_dir):
        self.target_dir = Path(target_dir).resolve()
        self.log_file = self.target_dir / "quicksortbox.log"
        self.duplicates_dir = self.target_dir / "Duplicates"
        self.config = self.load_config()

    def load_config(self):
        """Load config from file or use defaults."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        """Save current config to file."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_category(self, file_path):
        """Determine category based on extension using current config."""
        ext = os.path.splitext(file_path)[1].lower()
        for category, extensions in self.config['EXTENSIONS'].items():
            if ext in extensions:
                return category
        return 'Others'

    def calculate_md5(self, file_path):
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, PermissionError):
            return None

    def scan_files(self):
        """Yield files in the directory (skipping directories)."""
        if not self.target_dir.exists():
            return

        try:
            for entry in os.scandir(self.target_dir):
                if entry.is_file() and entry.name != "quicksortbox.log" and entry.name != "config.json":
                    yield Path(entry.path)
        except PermissionError:
            print(f"Permission denied accessing {self.target_dir}")

    def sort_files(self, dry_run=False, progress_callback=None):
        """Sort files into categories with progress updates."""
        moved_log = []
        stats = {cat: 0 for cat in self.config['EXTENSIONS'].keys()}
        stats['Others'] = 0
        stats['Duplicates'] = 0
        
        # 1. Scan first to get total count
        print(f"Scanning {self.target_dir}...")
        files_to_process = list(self.scan_files())
        total_files = len(files_to_process)
        
        seen_hashes = {}

        for params in enumerate(files_to_process, 1):
             i, file_path = params
             
             if progress_callback:
                 progress_callback(i, total_files, f"Processing {file_path.name}...")

             try:
                file_hash = self.calculate_md5(file_path)
                
                # --- Deduplication Logic ---
                if file_hash and file_hash in seen_hashes:
                    dest = self.duplicates_dir / file_path.name
                    action = "duplicate"
                    stats['Duplicates'] += 1
                    
                    if not dry_run:
                        self.duplicates_dir.mkdir(exist_ok=True)
                        self._move_safe(file_path, dest)
                        self._log_action(file_path, dest, "duplicate")
                    
                    moved_log.append((str(file_path), str(dest), "duplicate"))
                    continue
                else:
                    if file_hash:
                        seen_hashes[file_hash] = file_path

                # --- Sorting Logic ---
                category = self.get_category(file_path)
                dest_dir = self.target_dir / category
                dest_file = dest_dir / file_path.name
                
                if category in stats:
                    stats[category] += 1
                else:
                    stats['Others'] += 1
                
                if not dry_run:
                    dest_dir.mkdir(exist_ok=True)
                    target_path = self._move_safe(file_path, dest_file)
                    self._log_action(file_path, target_path, "move")
                
                moved_log.append((str(file_path), str(dest_file), "move"))
                
             except Exception as e:
                 print(f"Error processing {file_path.name}: {e}")

        return moved_log, stats

    def _move_safe(self, src, dst):
        """Move file, handling name collisions by renaming."""
        target = dst
        counter = 1
        while target.exists():
            stem = dst.stem
            suffix = dst.suffix
            target = dst.parent / f"{stem}_{counter}{suffix}"
            counter += 1
        
        try:
            shutil.move(str(src), str(target))
        except OSError as e:
             print(f"Error moving {src} to {target}: {e}")
        return target

    def _log_action(self, src, dst, action):
        """Append action to log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "src": str(src),
            "dst": str(dst)
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def undo_last_run(self, progress_callback=None):
        """Undo logic with progress."""
        if not self.log_file.exists():
            return False

        with open(self.log_file, "r") as f:
            lines = f.readlines()
        
        total = len(lines)
        for i, line in enumerate(reversed(lines), 1):
            if progress_callback:
                progress_callback(i, total, "Undoing...")
            try:
                entry = json.loads(line)
                src = Path(entry['src'])
                dst = Path(entry['dst'])
                
                if dst.exists():
                    if not src.parent.exists():
                        src.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dst), str(src))
            except Exception:
                pass
        
        try:
            os.remove(self.log_file)
            # Cleanup empty dirs? (Optional, maybe too risky to automate blindly)
        except OSError:
            pass
            
        return True
