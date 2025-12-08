import argparse
import sys
from pathlib import Path
from qs_core import QuickSortBox

def main():
    parser = argparse.ArgumentParser(description="QuickSortBox — Fast Desktop File Organizer")
    parser.add_argument('--path', type=str, help='Directory to sort', default=str(Path.home() / 'Downloads'))
    parser.add_argument('--dry-run', action='store_true', help='Show what will happen without moving files')
    parser.add_argument('--undo', action='store_true', help='Undo the last sorting operation using the log file')
    
    args = parser.parse_args()
    
    target_path = args.path
    if not Path(target_path).exists():
        print(f"Error: Path '{target_path}' does not exist.")
        sys.exit(1)
        
    qs = QuickSortBox(target_path)
    
    if args.undo:
        if qs.undo_last_run():
            print("Undo successful.")
        else:
            print("Nothing to undo or log file missing.")
    else:
        log, stats = qs.sort_files(dry_run=args.dry_run)
        
        # Print summary
        if args.dry_run:
            print("\n[Dry Run Summary]")
        else:
            print("\n[Sort Summary]")
            
        for cat, count in stats.items():
            if count > 0:
                print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()
