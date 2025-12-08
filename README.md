# QuickSortBox

QuickSortBox is a robust desktop utility designed to organize files into categorized directories based on their file extensions. It simplifies file management by automatically moving items such as images, documents, and archives into dedicated folders. The application also lists detailed statistics and includes deduplication capabilities using MD5 hashing to ensure data integrity.

## Features

- **Automated Categorization**: Sorts files into predefined categories like Images, Documents, Archives, Audio, Video, Code, and Executables.
- **Deduplication**: Identifies duplicate files by content (not just name) using MD5 hashing and moves them to a separate "Duplicates" folder.
- **Safety First**:
    - **Non-Destructive**: Files are moved, not deleted.
    - **Collision Handling**: Automatically renames files if a file with the same name already exists in the destination (e.g., `file_1.txt`).
    - **Undo Capability**: Reverts the last operation completely using a persistent transaction log.
- **Dual Interfaces**:
    - **GUI**: A modern, dark-themed graphical interface with a dashboard, progress tracking, and settings manager.
    - **CLI**: A command-line interface for headless operation or automation scripts.
- **Customizable**: Users can modify file classification rules via the Settings tab in the GUI or by editing the `config.json` file.
- **Portable**: Available as a standalone single-file executable.

## Installation

### Running form Source
1. Ensure Python 3.8+ is installed.
2. Clone the repository:
   ```bash
   git clone https://github.com/abhi3114-glitch/QuickSortBox.git
   cd QuickSortBox
   ```
3. Install dependencies (Tkinter is usually included with Python):
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The project uses standard library modules `tkinter`, `shutil`, `hashlib`, `pathlib`, `json`. `pyinstaller` is only needed for building the executable.)*

### Running the Executable
1. Download `QuickSortBox.exe` from the releases page (or build it yourself).
2. Double-click to run. No installation required.

## Usage

### Graphical Interface
Run the application using Python:
```bash
python qs_gui.py
```
1. **Target Folder**: Click "Browse" to select the directory you wish to organize.
2. **Dry Run**: Keep the "Dry Run" option checked to simulate the process. The log will show proposed moves without creating folders or moving files. Uncheck it to perform the actual sort.
3. **Sort Files**: Click the button to begin. A progress bar will indicate the status.
4. **Undo**: If you make a mistake, click "Undo Last" to revert the changes.
5. **Settings**: Switch to the "Settings" tab to add or remove file extensions from categories.

### Command Line Interface
Run the tool from a terminal:
```bash
# Dry run verification (default)
python quicksortbox.py --path "C:/Users/User/Downloads" --dry-run

# Actual execution
python quicksortbox.py --path "C:/Users/User/Downloads"

# Undo previous operation
python quicksortbox.py --path "C:/Users/User/Downloads" --undo
```

## Configuration

The application generates a `config.json` file in the working directory (or the executable's directory) to store categorization rules. You can edit this file manually or through the GUI.

Example structure:
```json
{
    "EXTENSIONS": {
        "Images": [".jpg", ".png", ".webp"],
        "Documents": [".pdf", ".docx", ".txt"]
    }
}
```

## Build Instructions

To create a standalone executable:
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run the build command:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --name "QuickSortBox" --clean qs_gui.py
   ```
3. The output file will be in the `dist/` directory.

## License

This project is open source.
