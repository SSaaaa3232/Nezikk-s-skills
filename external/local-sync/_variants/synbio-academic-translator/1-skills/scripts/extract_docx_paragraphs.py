#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from zipfile import ZipFile


W_PARAGRAPH_RE = re.compile(r"<w:p[\s\S]*?</w:p>")
TEXT_RE = re.compile(r"<w:t[^>]*>(.*?)</w:t>")
TAG_RE = re.compile(r"<[^>]+>")
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]")


def extract_paragraphs(docx_path: Path) -> list[str]:
    if not docx_path.exists():
        raise FileNotFoundError(f"{docx_path} does not exist")
    if docx_path.suffix.lower() != ".docx":
        raise ValueError(f"{docx_path} is not a .docx file")

    with ZipFile(docx_path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", "ignore")

    paragraphs = []
    for raw_paragraph in W_PARAGRAPH_RE.findall(xml):
        matches = TEXT_RE.findall(raw_paragraph)
        if matches:
            text = "".join(matches).strip()
        else:
            text = TAG_RE.sub("", raw_paragraph).strip()
        text = re.sub(r"\s+", " ", text)
        if text:
            paragraphs.append(text)
    return paragraphs


def keep_paragraph(text: str, include_english: bool) -> bool:
    if not text.strip():
        return False
    if include_english:
        return True
    if CHINESE_RE.search(text):
        return True
    if ASCII_WORD_RE.search(text):
        return False
    return True


def build_output(paragraphs: list[str], include_english: bool) -> list[str]:
    return [paragraph for paragraph in paragraphs if keep_paragraph(paragraph, include_english)]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Extract ordered paragraphs from a DOCX file for translation workflows."
    )
    parser.add_argument("docx_path", help="Path to the .docx manuscript file")
    parser.add_argument(
        "--include-english",
        action="store_true",
        help="Keep English-only paragraphs such as English titles",
    )
    args = parser.parse_args(argv)

    path = Path(args.docx_path).expanduser().resolve()

    try:
        paragraphs = extract_paragraphs(path)
        filtered = build_output(paragraphs, include_english=args.include_english)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    for paragraph in filtered:
        print(paragraph)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
