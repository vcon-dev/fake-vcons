import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table

def migrate_file(file_path: Path) -> Tuple[Path, List[str]]:
    """Migrate a single file. Returns tuple of (file_path, error_list)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            updated = False
            errors = []
            # Fix "created_at": "2024-09-05T21:22:52.749585+00+00:00" by converting it to "2024-09-05T21:22:52+00:00"
            if "created_at" in data:
                data["created_at"] = data["created_at"].replace("+00+00:00", "+00:00")
                updated = True
                
            
            # Fix "updated_at": "2024-09-05T21:22:52.749585+00+00:00" by converting it to "2024-09-05T21:22:52+00:00"
            if "updated_at" in data:
                data["updated_at"] = data["updated_at"].replace("+00+00:00", "+00:00")
                updated = True
                
            # Remove references to redacted, appended and group
            if "redacted" in data:
                del data["redacted"]
                updated = True
                
            if "appended" in data:
                del data["appended"]
                updated = True
                
            if "group" in data:
                del data["group"]
                updated = True

            if updated:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                     
            return file_path, errors
    except json.JSONDecodeError as e:
        return file_path, [f"Invalid JSON: {str(e)}"]
    except Exception as e:
        return file_path, [f"Unexpected error: {str(e)}"]
    
    
def is_potential_vcon_file(file_path: Path) -> bool:
    """Check if a file might be a vCon file based on its content."""
    try:
        if not file_path.suffix.lower() == '.json':
            return False
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return isinstance(data, dict) and "vcon" in data
    except (json.JSONDecodeError, UnicodeDecodeError, IOError):
        return False


def main():
    parser = argparse.ArgumentParser(description='Validate vCon files in a directory')
    parser.add_argument('directory', help='Directory to scan for vCon files')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads to use')
    args = parser.parse_args()

    console = Console()
    start_time = datetime.now()

    directory = Path(args.directory)
    if not directory.exists():
        console.print(f"[red]Directory not found: {directory}[/red]")
        sys.exit(1)

    console.print(f"[yellow]Scanning directory: {directory}[/yellow]")

    # Find all JSON files that might be vCons
    potential_files = [
        f for f in directory.rglob("*.json") 
        if is_potential_vcon_file(f)
    ]

    if not potential_files:
        console.print("[yellow]No vCon files found[/yellow]")
        return

    console.print(f"[green]Found {len(potential_files)} potential vCon files[/green]")

    # Validate files in parallel
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        results = executor.map(migrate_file, potential_files)
        for file_path, errors in results:
            console.print(f"[yellow]{file_path}[/yellow]")
            for error in errors:
                console.print(f"[red]{error}[/red]")

    console.print(f"[green]Done. Elapsed time: {datetime.now() - start_time}[/green]")
    
    
if __name__ == "__main__":
    main()