"""
intake_runner.py — Shared intake orchestration logic.

Contains process_file(), prompt helpers, inbox scanning, and main().
Used by both scripts/intake.py and the CLI intake subcommand.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.ingestion.capture import SourceCapture
from oil_painting_rag.ingestion.intake_classifier import (
    IntakeClassifier,
    build_intake_filename,
    next_source_id,
)
from oil_painting_rag.ingestion.source_registry import SourceRegistry
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)


def _prompt(label: str, default: Optional[str] = None) -> str:
    """Prompt user for input with optional default."""
    if default:
        raw = input(f"  {label} [{default}]: ").strip()
        return raw if raw else default
    while True:
        raw = input(f"  {label}: ").strip()
        if raw:
            return raw
        print("    (required)")


def _prompt_pick(label: str, options: list[str], default: Optional[str] = None) -> str:
    """Prompt user to pick from a numbered list."""
    print(f"  {label}:")
    for i, opt in enumerate(options, 1):
        marker = " *" if opt == default else ""
        print(f"    {i}. {opt}{marker}")
    while True:
        raw = input(f"  Pick [1-{len(options)}]: ").strip()
        if not raw and default:
            return default
        try:
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            # Allow typing the value directly
            if raw in options:
                return raw
        print(f"    (enter 1-{len(options)})")


def _collect_inbox_files() -> list[tuple[Path, str]]:
    """Scan inbox subdirectories for files. Returns (path, subfolder_name) pairs."""
    inbox_subdirs = {
        "pdf": cfg.INBOX_PDF_DIR,
        "html": cfg.INBOX_HTML_DIR,
        "markdown": cfg.INBOX_MARKDOWN_DIR,
        "text": cfg.INBOX_TEXT_DIR,
        "other": cfg.INBOX_OTHER_DIR,
    }
    files: list[tuple[Path, str]] = []
    for label, inbox_path in inbox_subdirs.items():
        if not inbox_path.exists():
            continue
        for fpath in sorted(inbox_path.iterdir()):
            if fpath.is_file() and fpath.name != ".gitkeep" and not fpath.name.startswith("."):
                files.append((fpath, label))
    return files


def _load_vocab_values(key: str) -> list[str]:
    """Load valid values for a vocabulary key from controlled_vocabulary.json."""
    import json

    vocab_path = cfg.VOCAB_DIR / "controlled_vocabulary.json"
    with vocab_path.open("r", encoding="utf-8") as fh:
        vocab = json.load(fh)
    return vocab.get(key, {}).get("values", [])


def process_file(
    filepath: Path,
    inbox_subfolder: Optional[str],
    classifier: IntakeClassifier,
    registry: SourceRegistry,
    capture: SourceCapture,
) -> Optional[str]:
    """
    Process a single file through intake. Returns source_id on success, None on skip.
    Returns "QUIT" if user wants to stop batch processing.
    """
    print(f"\n{'─' * 60}")
    print(f"  Intake: {filepath.name}")
    print(f"{'─' * 60}")

    # --- Inference ---
    content = classifier.read_content_preview(filepath)
    family_result = classifier.infer_source_family(filepath.name, content)
    domain_result = classifier.infer_domain(filepath.name, content)
    capture_method = classifier.infer_capture_method(inbox_subfolder or "other")

    # Get family code and next source_id
    family_codes = classifier.family_codes
    family_code = family_codes.get(family_result.value)

    if family_code:
        existing_ids = registry.list_ids()
        source_id = next_source_id(family_code, existing_ids)
    else:
        source_id = "SRC-???-001"

    # --- Display inferred values ---
    print(f"\n  Inferred:")
    print(f"    source_family : {family_result.value}  (confidence: {family_result.confidence})")
    print(f"    domain        : {domain_result.value}  (confidence: {domain_result.confidence})")
    print(f"    capture_method: {capture_method}")
    print(f"    source_id     : {source_id}")
    print()

    # --- Accept/override inferred values ---
    raw = input("  [Enter] to accept inferred, 'skip' to skip, 'quit' to stop: ").strip().lower()
    if raw == "quit":
        return "QUIT"
    if raw == "skip":
        print("  Skipped.")
        return None

    # Allow overriding inferred values
    if raw:
        if family_result.confidence == "low" or raw == "source_family":
            families = list(family_codes.keys())
            family_result_value = _prompt_pick("source_family", families)
            family_code = family_codes[family_result_value]
            existing_ids = registry.list_ids()
            source_id = next_source_id(family_code, existing_ids)
        if raw == "domain":
            domains = _load_vocab_values("domain")
            domain_result_value = _prompt_pick("domain", domains, domain_result.value)
    else:
        # If family was unknown, must pick
        if family_result.value == "unknown":
            families = list(family_codes.keys())
            family_result_value = _prompt_pick("source_family", families)
            family_code = family_codes[family_result_value]
            family_result = type(family_result)(value=family_result_value, confidence="manual", hits=0)
            existing_ids = registry.list_ids()
            source_id = next_source_id(family_code, existing_ids)

    # --- Prompt for required fields ---
    # Source type — filtered by family
    source_types = classifier.source_type_by_family.get(family_result.value, [])
    if not source_types:
        source_types = _load_vocab_values("source_type")
    source_type = _prompt_pick("source_type", source_types)

    title = _prompt("Title")
    short_title = _prompt("Short title")
    institution = _prompt("Institution/publisher")

    access_types = _load_vocab_values("access_type")
    access_type = _prompt_pick("access_type", access_types)

    # Optional fields
    author = input("  Author (optional): ").strip() or None
    pub_year_raw = input("  Publication year (optional): ").strip()
    publication_year = int(pub_year_raw) if pub_year_raw.isdigit() else None
    source_url = input("  Source URL (optional): ").strip() or None

    # --- File operations ---
    extension = filepath.suffix
    dest_dir = cfg.RAW_DIR / source_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    new_filename = build_intake_filename(source_id, short_title, extension, dest_dir=dest_dir)
    dest_path = dest_dir / new_filename

    # Move file
    original_path = filepath
    shutil.move(str(filepath), str(dest_path))
    print(f"\n  Moved: {filepath.name} → data/raw/{source_id}/{new_filename}")

    # Register — rollback file move on failure
    try:
        capture.register_source(
            source_id=source_id,
            title=title,
            short_title=short_title,
            source_family=family_result.value,
            source_type=source_type,
            institution_or_publisher=institution,
            domain=domain_result.value,
            capture_method=capture_method,
            access_type=access_type,
            raw_file_name=new_filename,
            author=author,
            publication_year=publication_year,
            source_url=source_url,
        )
        # Set raw_captured flag
        registry.update_field(source_id, "raw_captured", True)
        print(f"  Registered: {source_id} — {short_title}")
        return source_id

    except Exception as exc:
        # Rollback: move file back to original location
        logger.error("Registration failed for %s: %s", source_id, exc)
        print(f"  [ERROR] Registration failed: {exc}")
        try:
            shutil.move(str(dest_path), str(original_path))
            # Clean up empty dest dir
            if dest_dir.exists() and not any(dest_dir.iterdir()):
                dest_dir.rmdir()
            print(f"  Rolled back file move.")
        except Exception as rollback_exc:
            logger.error("Rollback failed: %s", rollback_exc)
            print(f"  [ERROR] Rollback also failed: {rollback_exc}")
        return None


def main() -> None:
    """Entry point for the intake script."""
    import argparse

    parser = argparse.ArgumentParser(description="Oil Painting RAG — Source Intake")
    parser.add_argument("--file", type=Path, help="Process a single file (skip inbox scan)")
    args = parser.parse_args()

    cfg.ensure_data_dirs()
    classifier = IntakeClassifier()
    registry = SourceRegistry()
    capture = SourceCapture()

    if args.file:
        # Single file mode
        if not args.file.exists():
            print(f"File not found: {args.file}")
            sys.exit(1)
        result = process_file(args.file, None, classifier, registry, capture)
        if result and result != "QUIT":
            print(f"\nDone: registered {result}")
    else:
        # Batch mode — scan inbox
        files = _collect_inbox_files()
        if not files:
            print("No files found in data/inbox/")
            return

        print(f"Found {len(files)} file(s) in inbox:")
        for fpath, label in files:
            print(f"  [{label}] {fpath.name}")
        print()

        registered: list[str] = []
        skipped = 0

        for fpath, label in files:
            result = process_file(fpath, label, classifier, registry, capture)
            if result == "QUIT":
                print("\nStopped by user.")
                break
            elif result:
                registered.append(result)
            else:
                skipped += 1

        print(f"\nDone: {len(registered)} registered, {skipped} skipped, {len(files)} total")
        if registered:
            print("Registered IDs:")
            for sid in registered:
                print(f"  {sid}")


if __name__ == "__main__":
    main()
