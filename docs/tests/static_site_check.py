#!/usr/bin/env python3
"""Static checks for the Visibility Nowcasting GitHub Pages site.

The test intentionally uses only Python's standard library so it can run in a
fresh checkout without installing project dependencies.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import urlparse

DOCS = Path(__file__).resolve().parents[1]
REPO = DOCS.parent
INDEX = DOCS / "index.html"
CSS = DOCS / "styles.css"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.ids: set[str] = set()
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        self.tags.append((tag, attr_map))
        if "id" in attr_map:
            self.ids.add(attr_map["id"])

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)


def is_external_or_special(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme in {"http", "https", "mailto", "tel"})


def local_path(value: str) -> Path | None:
    if not value or value.startswith("#") or is_external_or_special(value):
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        return None
    return (DOCS / parsed.path).resolve()



def assert_png_is_publishable(path: Path) -> None:
    png_signature = b"\x89PNG\r\n\x1a\n"
    assert path.read_bytes().startswith(png_signature), f"local PNG is not a valid image: {path.relative_to(DOCS)}"

    repo_relative_path = path.relative_to(REPO).as_posix()
    blob = subprocess.run(
        ["git", "-C", str(REPO), "cat-file", "-p", f":{repo_relative_path}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if blob.returncode == 0:
        assert blob.stdout.startswith(png_signature), (
            "tracked PNG would publish as a non-image blob, likely a Git LFS pointer: "
            f"{repo_relative_path}"
        )

def main() -> None:
    assert INDEX.exists(), "index.html must exist"
    assert CSS.exists(), "styles.css must exist"

    parser = SiteParser()
    parser.feed(INDEX.read_text(encoding="utf-8"))
    text = " ".join(parser.text_parts)
    css = CSS.read_text(encoding="utf-8")

    required_ids = {"top", "abstract", "method", "results", "citation", "bibtex-code"}
    missing_ids = required_ids - parser.ids
    assert not missing_ids, f"missing required sections: {sorted(missing_ids)}"

    required_terms = [
        "SMOTENC",
        "CTGAN",
        "Critical Success Index",
        "SHAP",
        "Wasserstein",
        "temporal distribution shift",
        "10.1007/s00704-026-06219-6",
        "Theoretical and Applied Climatology",
        "Published 10 April 2026",
    ]
    for term in required_terms:
        assert term in text, f"missing scientific/metadata term: {term}"

    figure_imgs = [attrs for tag, attrs in parser.tags if tag == "img" and attrs.get("src", "").startswith("./assets/figure/")]
    assert len(figure_imgs) >= 8, f"expected rich figure usage, found {len(figure_imgs)} figure images"
    for attrs in figure_imgs:
        assert attrs.get("alt", "").strip(), f"missing alt text for {attrs.get('src')}"

    for tag, attrs in parser.tags:
        for attr in ("src", "href"):
          value = attrs.get(attr)
          if value is None:
              continue
          if value.startswith("#"):
              assert value[1:] in parser.ids, f"broken in-page anchor: {value}"
              continue
          path = local_path(value)
          if path is not None:
              assert path.is_relative_to(DOCS), f"local path escapes docs: {value}"
              assert path.exists(), f"missing local asset referenced by {attr}: {value}"
              if path.suffix.lower() == ".png":
                  assert_png_is_publishable(path)

    external_hrefs = {attrs["href"] for tag, attrs in parser.tags if tag == "a" and attrs.get("href", "").startswith("https://")}
    assert "https://doi.org/10.1007/s00704-026-06219-6" in external_hrefs
    assert "https://github.com/Bon99yun/Visibility_Nowcasting" in external_hrefs

    cta_labels = [attrs.get("href") for tag, attrs in parser.tags if tag == "a" and "button" in attrs.get("class", "")]
    assert cta_labels[:2] == [
        "https://doi.org/10.1007/s00704-026-06219-6",
        "https://github.com/Bon99yun/Visibility_Nowcasting",
    ], "hero CTA buttons should be Paper and Code only"

    assert '@media (max-width: 700px)' in css, "responsive mobile media query missing"
    assert "copy-bibtex" in INDEX.read_text(encoding="utf-8"), "BibTeX copy affordance missing"
    assert "image-modal" in INDEX.read_text(encoding="utf-8"), "figure inspection modal missing"
    assert "new analysis" not in text.lower(), "page should not claim new analysis beyond the paper"

    print("PASS static site checks")


if __name__ == "__main__":
    main()
