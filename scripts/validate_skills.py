"""Validate the skills in this repository. Run: python3 -I scripts/validate_skills.py

Checks every skills/*/SKILL.md: only the allowed frontmatter keys, name equals the
folder, description at most 1024 characters, body at most 500 lines. Fails when the
absolute URL in SKILL.md, references, README.md, AGENTS.md, .mcp.json or .claude-plugin/*.json
is not https or names a host outside the allowlist. Also fails on banned wording (copy lint) in the README, AGENTS.md, SKILL.md files, references, manifests
and script docstrings. Run the self-test: python3 -I scripts/validate_skills.py --self-test
"""

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_KEYS = {"name", "description", "license", "metadata"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_HOSTS = {
    "klaracase.de",
    "agentskills.io",
    "modelcontextprotocol.io",
    "docs.anthropic.com",
    "code.claude.com",
}
URL_PATTERN = re.compile(r"https?://[^\s)>\]\"'`<,]+")
URL_FILES = ("README.md", "AGENTS.md", ".mcp.json", ".claude-plugin/*.json", "skills/**/*.md")
BANNED_COPY = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"hallucinat",
        r"halluzin",
        r"fabricat",
        r"fabrizier",
        r"\bfake\b",
        r"official source",
        r"offizielle quelle",
        r"amtlich",
    )
]
# The required disclaimer says "fabricated" once. Only this exact sentence is exempt.
ALLOWED_SENTENCE = re.compile(r"it is not a claim that the citation is fabricated\.", re.IGNORECASE)
COPY_FILES = ("README.md", "AGENTS.md", "tools/*.json", ".claude-plugin/*.json", ".mcp.json")
COPY_GLOBS = ("skills/**/*.md", "scripts/anthropic-tools.py")


def split_frontmatter(text: str):
    match = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    return (match.group(1), match.group(2)) if match else (None, text)


def top_level_values(frontmatter: str) -> dict:
    values: dict = {}
    for line in frontmatter.split("\n"):
        key = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if key and not line.startswith((" ", "\t")):
            values[key.group(1)] = key.group(2).strip().strip("\"'")
    return values


def check_skill(skill_file: Path) -> list:
    errors = []
    frontmatter, body = split_frontmatter(skill_file.read_text(encoding="utf-8"))
    if frontmatter is None:
        return [f"{skill_file}: no frontmatter"]
    values = top_level_values(frontmatter)
    extra = set(values) - ALLOWED_KEYS
    missing = {"name", "description"} - set(values)
    if extra:
        errors.append(f"{skill_file}: keys not allowed: {sorted(extra)}")
    if missing:
        errors.append(f"{skill_file}: keys missing: {sorted(missing)}")
    name = values.get("name", "")
    if name != skill_file.parent.name:
        errors.append(f"{skill_file}: name '{name}' is not the folder '{skill_file.parent.name}'")
    if not NAME_PATTERN.match(name) or len(name) > 64:
        errors.append(f"{skill_file}: name '{name}' breaks the name rules")
    if len(values.get("description", "")) > 1024:
        errors.append(f"{skill_file}: description is over 1024 characters")
    if len(body.splitlines()) > 500:
        errors.append(f"{skill_file}: body is over 500 lines")
    return errors


def url_problem(url: str) -> str | None:
    parts = urlsplit(url.rstrip(".;:"))
    if parts.scheme != "https":
        return "is not https"
    host = (parts.hostname or "").lower()
    if host == "github.com":
        path = parts.path.rstrip("/")
        return None if path == "/klaracase" or path.startswith("/klaracase/") else "is a github.com path outside /klaracase/"
    return None if host in ALLOWED_HOSTS else f"names host '{host}' outside the allowlist"


def check_urls() -> list:
    paths = set()
    for pattern in URL_FILES:
        paths.update(ROOT.glob(pattern))
    errors = []
    for path in sorted(paths):
        for url in URL_PATTERN.findall(path.read_text(encoding="utf-8")):
            problem = url_problem(url)
            if problem:
                errors.append(f"{path.relative_to(ROOT)}: URL {url} {problem}")
    return errors


def find_banned_copy(text: str) -> list:
    flat = ALLOWED_SENTENCE.sub("", " ".join(text.split()))
    return [pattern.pattern for pattern in BANNED_COPY if pattern.search(flat)]


def check_copy() -> list:
    paths = set()
    for pattern in COPY_FILES + COPY_GLOBS:
        paths.update(ROOT.glob(pattern))
    errors = []
    for path in sorted(paths):
        for pattern in find_banned_copy(path.read_text(encoding="utf-8")):
            errors.append(f"{path.relative_to(ROOT)}: banned wording '{pattern}'")
    return errors


def self_test() -> int:
    flagged = [
        "This stops hallucinations.",
        "Das verhindert Halluzinationen.",
        "The citation is Fabricated.",
        "Das ist fabriziert.",
        "A fake case.",
        "The official source of law.",
        "Die offizielle Quelle.",
        "Der amtliche Leitsatz.",
        "A `not_found` verdict means it was not found; it is not a claim that the citation is "
        "fabricated. It is fabricated.",
    ]
    allowed = [
        "A `not_found` verdict means the citation was not found in the corpus; it is not a claim\n"
        "that the citation is fabricated."
    ]
    bad_urls = [
        "http://klaracase.de/mcp",
        "https://example.test/x",
        "https://github.com/other/repo",
        "https://klaracase.de.evil.test/x",
        "http://127.0.0.1:7000/mcp",
    ]
    good_urls = [
        "https://klaracase.de/mcp",
        "https://github.com/klaracase/skills.",
        "https://github.com/klaracase",
        "https://agentskills.io/specification",
    ]
    failures = [text for text in flagged if not find_banned_copy(text)]
    failures += [url for url in bad_urls if url_problem(url) is None]
    failures += [url for url in good_urls if url_problem(url) is not None]
    failures += [text for text in allowed if find_banned_copy(text)]
    for text in failures:
        print(f"self-test failed: {text!r}")
    print(f"copy lint self-test: {len(failures)} failures")
    return 1 if failures else 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    errors = [] if skill_files else ["no skills/*/SKILL.md found"]
    for skill_file in skill_files:
        errors += check_skill(skill_file)
    errors += check_urls()
    errors += check_copy()
    for error in errors:
        print(error)
    print(f"{len(skill_files)} skills checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
