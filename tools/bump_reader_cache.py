import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    changed = 0
    for path in ROOT.glob("pg*_sec001.html"):
        original = path.read_text(encoding="utf-8")
        updated = re.sub(r"pdf-word-highlight\.js\?v=\d+", "pdf-word-highlight.js?v=15", original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"changed={changed}")


if __name__ == "__main__":
    main()
