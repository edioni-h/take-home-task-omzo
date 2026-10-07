#run all repository, encoding, unit-test, and evaluation checks

from __future__ import annotations

import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import evaluate


ROOT = Path(__file__).resolve().parent
EXPECTED_FILES = {
    "DESIGN.md",
    "DESIGN.pdf",
    "NOTES.md",
    "README.md",
    "architecture.svg",
    "evaluate.py",
    "evaluation_cases.py",
    "router.py",
    "tests/test_router.py",
    "verify.py",
}
TEXT_FILES = EXPECTED_FILES - {"DESIGN.pdf"}
CORRUPTION_MARKERS = (
    "\ufffd",
    "\u00c3",
    "\u00c2",
    "\u00e2\u20ac",
)


def _submission_files() -> set[str]:
    return {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def validate_repository() -> list[str]:
    errors: list[str] = []
    actual_files = _submission_files()

    missing = EXPECTED_FILES - actual_files
    unexpected = actual_files - EXPECTED_FILES
    if missing:
        errors.append("Missing files: " + ", ".join(sorted(missing)))
    if unexpected:
        errors.append("Unexpected files: " + ", ".join(sorted(unexpected)))

    for relative_path in sorted(TEXT_FILES & actual_files):
        path = ROOT / relative_path
        try:
            text = path.read_bytes().decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            errors.append(f"{relative_path} is not valid UTF-8: {error}")
            continue

        for marker in CORRUPTION_MARKERS:
            if marker in text:
                errors.append(
                    f"{relative_path} contains a likely encoding-corruption marker"
                )
                break

    architecture_path = ROOT / "architecture.svg"
    if architecture_path.is_file():
        try:
            svg_root = ET.fromstring(architecture_path.read_text(encoding="utf-8"))
            if not svg_root.tag.endswith("svg"):
                errors.append("architecture.svg does not have an SVG root element")
        except ET.ParseError as error:
            errors.append(f"architecture.svg is not valid XML: {error}")

    design_path = ROOT / "DESIGN.md"
    if design_path.is_file():
        design_text = design_path.read_text(encoding="utf-8")
        if "![Omzo Air production architecture" not in design_text:
            errors.append("DESIGN.md does not embed architecture.svg")

    pdf_path = ROOT / "DESIGN.pdf"
    if pdf_path.is_file():
        pdf_bytes = pdf_path.read_bytes()
        if not pdf_bytes.startswith(b"%PDF-"):
            errors.append("DESIGN.pdf does not have a valid PDF header")
        page_count = len(re.findall(rb"/Type\s*/Page(?!s)\b", pdf_bytes))
        if page_count != 2:
            errors.append(
                f"DESIGN.pdf must contain exactly 2 pages; found {page_count}"
            )

    return errors


def main() -> int:
    print("== Repository and UTF-8 validation ==")
    repository_errors = validate_repository()
    if repository_errors:
        for error in repository_errors:
            print(f"FAIL: {error}")
        return 1
    print(
        f"PASS: {len(EXPECTED_FILES)} expected files; text is strict UTF-8; "
        "DESIGN.pdf is valid and 2 pages"
    )

    print("\n== Unit tests ==")
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(ROOT / "tests"),
        pattern="test_*.py",
    )
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1

    print("\n== Required evaluation ==")
    return evaluate.run_evaluation()


if __name__ == "__main__":
    raise SystemExit(main())
