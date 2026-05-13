import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATHS = [
    ROOT / "README.md",
    *sorted((ROOT / "docs").glob("*.md")),
    *sorted((ROOT / "examples").glob("*.md")),
]

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _iter_local_links(markdown_path):
    text = markdown_path.read_text(encoding="utf-8")
    for match in MARKDOWN_LINK_RE.finditer(text):
        href = match.group(1).strip()
        if not href:
            continue
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if href.startswith("sandbox:"):
            continue
        href_without_anchor = href.split("#", 1)[0]
        if not href_without_anchor:
            continue
        yield href, href_without_anchor


def test_local_markdown_links_point_to_existing_files():
    broken_links = []

    for markdown_path in DOC_PATHS:
        for original_href, href_without_anchor in _iter_local_links(markdown_path):
            target = (markdown_path.parent / href_without_anchor).resolve()
            if not target.exists():
                relative_doc = markdown_path.relative_to(ROOT)
                broken_links.append(f"{relative_doc}: {original_href}")

    assert broken_links == []