#!/usr/bin/env python3

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

def validate_vcon(vcon: Dict[str, Any]) -> List[str]:
    """Validates a vCon object. Returns a list of error messages."""
    errors = []

    # Check required top-level fields
    required_fields = ["vcon", "uuid", "created_at"]
    for field in required_fields:
        if field not in vcon:
            errors.append(f"Missing required field: {field}")

    # Validate vcon version
    if "vcon" in vcon and vcon["vcon"] != "0.0.1":
        errors.append("Invalid vcon version. Expected '0.0.1'")

    # Validate UUID format (basic check)
    if "uuid" in vcon and not isinstance(vcon["uuid"], str):
        errors.append("UUID must be a string")

    # Validate created_at format
    if "created_at" in vcon:
        try:
            datetime.fromisoformat(vcon["created_at"])
        except ValueError:
            errors.append("Invalid created_at date format")

    # Validate updated_at format if present
    if "updated_at" in vcon:
        try:
            datetime.fromisoformat(vcon["updated_at"])
        except ValueError:
            errors.append("Invalid updated_at date format")

    # Validate parties array
    if "parties" in vcon:
        if not isinstance(vcon["parties"], list):
            errors.append("parties must be an array")
        else:
            for i, party in enumerate(vcon["parties"]):
                errors.extend(validate_party(party, i))

    # Validate dialog array
    if "dialog" in vcon:
        if not isinstance(vcon["dialog"], list):
            errors.append("dialog must be an array")
        else:
            for i, dialog in enumerate(vcon["dialog"]):
                errors.extend(validate_dialog(dialog, i))

    # Validate analysis array if present
    if "analysis" in vcon:
        if not isinstance(vcon["analysis"], list):
            errors.append("analysis must be an array")
        else:
            for i, analysis in enumerate(vcon["analysis"]):
                errors.extend(validate_analysis(analysis, i))

    # Validate attachments array if present
    if "attachments" in vcon:
        if not isinstance(vcon["attachments"], list):
            errors.append("attachments must be an array")
        else:
            for i, attachment in enumerate(vcon["attachments"]):
                errors.extend(validate_attachment(attachment, i))

    # Validate redacted, appended, and group are mutually exclusive
    if sum(key in vcon for key in ["redacted", "appended", "group"]) > 1:
        errors.append("redacted, appended, and group are mutually exclusive")

    return errors

def validate_party(party: Dict[str, Any], index: int) -> List[str]:
    """Validates a party object. Returns a list of error messages."""
    errors = []
    
    # Check for at least one identifier
    identifiers = ["tel", "mailto", "name"]
    if not any(identifier in party for identifier in identifiers):
        errors.append(f"Party {index} must have at least one identifier (tel, mailto, or name)")

    # Validate tel format if present
    if "tel" in party and not party["tel"].startswith("+"):
        errors.append(f"Party {index}: tel must start with '+'")

    # Validate mailto format if present
    if "mailto" in party and "@" not in party["mailto"]:
        errors.append(f"Party {index}: invalid mailto format")

    return errors

def validate_dialog(dialog: Dict[str, Any], index: int) -> List[str]:
    """Validates a dialog object. Returns a list of error messages."""
    errors = []

    required_fields = ["type", "start", "parties"]
    for field in required_fields:
        if field not in dialog:
            errors.append(f"Dialog {index}: Missing required field: {field}")

    # Validate type
    valid_types = ["recording", "text", "transfer", "incomplete"]
    if "type" in dialog and dialog["type"] not in valid_types:
        errors.append(f"Dialog {index}: Invalid type. Must be one of {valid_types}")

    # Validate start format
    if "start" in dialog:
        try:
            datetime.fromisoformat(dialog["start"])
        except ValueError:
            errors.append(f"Dialog {index}: Invalid start date format")

    # Validate parties
    if "parties" in dialog:
        if not isinstance(dialog["parties"], (int, list)):
            errors.append(f"Dialog {index}: parties must be an integer or an array of integers")

    # Validate duration if present
    if "duration" in dialog and not isinstance(dialog["duration"], (int, float)):
        errors.append(f"Dialog {index}: duration must be a number")

    return errors

def validate_analysis(analysis: Dict[str, Any], index: int) -> List[str]:
    """Validates an analysis object. Returns a list of error messages."""
    errors = []

    required_fields = ["type"]
    for field in required_fields:
        if field not in analysis:
            errors.append(f"Analysis {index}: Missing required field: {field}")

    return errors

def validate_attachment(attachment: Dict[str, Any], index: int) -> List[str]:
    """Validates an attachment object. Returns a list of error messages."""
    errors = []

    return errors

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

def validate_file(file_path: Path) -> Tuple[Path, List[str]]:
    """Validate a single file. Returns tuple of (file_path, error_list)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            errors = validate_vcon(data)
            return file_path, errors
    except json.JSONDecodeError as e:
        return file_path, [f"Invalid JSON: {str(e)}"]
    except Exception as e:
        return file_path, [f"Unexpected error: {str(e)}"]

def main():
    parser = argparse.ArgumentParser(description='Validate vCon files in a directory')
    parser.add_argument('directory', help='Directory to scan for vCon files')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads to use')
    args = parser.parse_args()

    console = Console()
    start_time = datetime.now()

    # Find all potential vCon files
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
    results = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        results = list(executor.map(lambda f: validate_file(f), potential_files))

    # Create results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Errors")

    valid_count = 0
    invalid_count = 0

    for file_path, errors in results:
        relative_path = file_path.relative_to(directory)
        if errors:
            status = "[red]Invalid[/red]"
            error_text = "\n".join(errors)
            invalid_count += 1
        else:
            status = "[green]Valid[/green]"
            error_text = ""
            valid_count += 1
        
        table.add_row(str(relative_path), status, error_text)

    # Print results
    console.print("\n[bold]Validation Results:[/bold]")
    console.print(table)

    duration = datetime.now() - start_time
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"Total files: {len(potential_files)}")
    console.print(f"Valid: [green]{valid_count}[/green]")
    console.print(f"Invalid: [red]{invalid_count}[/red]")
    console.print(f"Time taken: {duration.total_seconds():.2f} seconds")

if __name__ == "__main__":
    main()