import os
import random
from pathlib import Path

def create_dummy_files(target_dir="test_folder", count=20):
    target = Path(target_dir)
    target.mkdir(exist_ok=True)
    
    extensions = ['.jpg', '.png', '.txt', '.pdf', '.docx', '.zip', '.mp3', '.mp4', '.py', '.unknown']
    
    print(f"Creating {count} dummy files in '{target_dir}'...")
    
    for i in range(count):
        ext = random.choice(extensions)
        filename = f"file_{i}{ext}"
        content = f"This is dummy file {i}".encode()
        
        # Chance to create a duplicate
        if i > 0 and random.random() < 0.2:
            prev_file = random.choice(list(target.glob("*")))
            if prev_file.is_file():
                filename = f"duplicate_{i}{prev_file.suffix}"
                with open(prev_file, 'rb') as f:
                    content = f.read()

        with open(target / filename, 'wb') as f:
            f.write(content)
            
    print("Done.")

if __name__ == "__main__":
    create_dummy_files()
