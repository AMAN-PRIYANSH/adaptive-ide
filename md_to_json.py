#!/usr/bin/env python3
"""
md_to_json.py
=============
Converts the human-review .md question bank files into the canonical
JSON format used by the Adaptive Quiz Engine.

Input  : one or more .md files (c_review.md, python_review.md, dsa_review.md)
Output : one JSON file per subject  (c_questions.json, python_questions.json,
         dsa_questions.json) written to ./data/

The script also writes enriched .md files alongside the originals with
the new `type` and `estimated_time` fields inserted so human reviewers
can verify and override them before the next JSON regeneration.

Usage:
    python md_to_json.py                        # processes all three defaults
    python md_to_json.py python_review.md       # single file
    python md_to_json.py --outdir ./data        # custom output dir

Type classification heuristic (override in MANUAL_OVERRIDES below):
    program  - question text is "What will be the output …" or contains
               a code snippet reference; estimated_time 55–90 s
    logic    - requires reasoning / ordering / rule application;
               estimated_time 40–70 s
    direct   - pure recall / definition / identification;
               estimated_time 20–35 s
"""

import re, json, sys, os, argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# MANUAL OVERRIDES
# If the heuristic mis-classifies a question, add its ID here.
# Format:  "ID": {"type": "...", "estimated_time": N}
# ---------------------------------------------------------------------------
MANUAL_OVERRIDES = {
    # Python
    "PY-0007":  {"type": "logic",   "estimated_time": 50},
    "PY-0011":  {"type": "program", "estimated_time": 60},
    "PY-0014":  {"type": "logic",   "estimated_time": 45},
    "PY-0015":  {"type": "program", "estimated_time": 65},
    "PY-0018":  {"type": "logic",   "estimated_time": 55},
    "PY-0020":  {"type": "program", "estimated_time": 70},
    "PY-0023":  {"type": "program", "estimated_time": 65},
    "PY-0024":  {"type": "program", "estimated_time": 70},
    "PY-0026":  {"type": "logic",   "estimated_time": 40},
    "PY-0028":  {"type": "program", "estimated_time": 55},
    "PY-0029":  {"type": "program", "estimated_time": 60},  # code missing
    "PY-0031":  {"type": "program", "estimated_time": 65},
    "PY-0032":  {"type": "program", "estimated_time": 45},
    "PY-0033":  {"type": "program", "estimated_time": 60},
    "PY-0035":  {"type": "program", "estimated_time": 70},
    "PY-0036":  {"type": "program", "estimated_time": 65},
    "PY-0038":  {"type": "program", "estimated_time": 65},
    "PY-0040":  {"type": "program", "estimated_time": 55},
    "PY-0042":  {"type": "program", "estimated_time": 75},
    "PY-0044":  {"type": "program", "estimated_time": 55},
    "PY-0045":  {"type": "program", "estimated_time": 60},
    "PY-0047":  {"type": "logic",   "estimated_time": 45},
    "PY-0049":  {"type": "program", "estimated_time": 60},  # code missing
    "PY-0050":  {"type": "program", "estimated_time": 55},
    "PY-0052":  {"type": "program", "estimated_time": 65},
    "PY-0054":  {"type": "program", "estimated_time": 55},
    "PY-0055":  {"type": "logic",   "estimated_time": 40},
    "PY-0057":  {"type": "program", "estimated_time": 60},
    "PY-0060":  {"type": "program", "estimated_time": 70},
    "PY-0062":  {"type": "program", "estimated_time": 70},
    # C
    "C-0034":  {"type": "program", "estimated_time": 65},
    "C-0035":  {"type": "program", "estimated_time": 65},
    "C-0036":  {"type": "program", "estimated_time": 70},
    "C-0037":  {"type": "program", "estimated_time": 70},
    "C-0038":  {"type": "program", "estimated_time": 65},
    "C-0039":  {"type": "program", "estimated_time": 60},
    "C-0040":  {"type": "program", "estimated_time": 65},
    "C-0041":  {"type": "program", "estimated_time": 65},
    "C-0042":  {"type": "program", "estimated_time": 70},
    "C-0043":  {"type": "program", "estimated_time": 65},
    "C-0044":  {"type": "program", "estimated_time": 70},
    "C-0045":  {"type": "program", "estimated_time": 65},
    "C-0046":  {"type": "logic",   "estimated_time": 50},
    "C-0047":  {"type": "program", "estimated_time": 65},
    "C-0048":  {"type": "program", "estimated_time": 70},
    "C-0049":  {"type": "program", "estimated_time": 65},
    "C-0050":  {"type": "logic",   "estimated_time": 50},
    "C-0051":  {"type": "program", "estimated_time": 70},
    "C-0052":  {"type": "program", "estimated_time": 65},
    "C-0053":  {"type": "logic",   "estimated_time": 50},
    "C-0054":  {"type": "logic",   "estimated_time": 50},
    "C-0055":  {"type": "logic",   "estimated_time": 45},
    "C-0056":  {"type": "logic",   "estimated_time": 50},
    "C-0057":  {"type": "program", "estimated_time": 65},
    "C-0058":  {"type": "logic",   "estimated_time": 55},
    "C-0059":  {"type": "logic",   "estimated_time": 50},  # code missing
    "C-0060":  {"type": "program", "estimated_time": 65},
    "C-0061":  {"type": "program", "estimated_time": 60},
    "C-0062":  {"type": "program", "estimated_time": 65},
    "C-0063":  {"type": "program", "estimated_time": 60},
    "C-0064":  {"type": "program", "estimated_time": 65},
    # DSA
    "DSA-0007": {"type": "logic",   "estimated_time": 60},
    "DSA-0011": {"type": "logic",   "estimated_time": 65},
    "DSA-0023": {"type": "program", "estimated_time": 65},
    "DSA-0024": {"type": "logic",   "estimated_time": 55},
    "DSA-0026": {"type": "logic",   "estimated_time": 55},
    "DSA-0030": {"type": "program", "estimated_time": 65},
    "DSA-0036": {"type": "program", "estimated_time": 60},
}

# Difficulty overrides (the .md files all have 0.50; this is your starter set)
# Scale: 0.0 easy recall → 1.0 expert
DIFFICULTY_OVERRIDES = {
    # Python - basic recall easy
    "PY-0001": 0.10, "PY-0002": 0.15, "PY-0003": 0.15, "PY-0004": 0.10,
    "PY-0005": 0.20, "PY-0006": 0.30, "PY-0007": 0.45, "PY-0008": 0.15,
    "PY-0009": 0.10, "PY-0010": 0.15, "PY-0011": 0.55, "PY-0012": 0.30,
    "PY-0013": 0.35, "PY-0014": 0.30, "PY-0015": 0.55, "PY-0016": 0.20,
    "PY-0017": 0.25, "PY-0018": 0.65, "PY-0019": 0.25, "PY-0020": 0.60,
    "PY-0021": 0.20, "PY-0022": 0.25, "PY-0023": 0.65, "PY-0024": 0.70,
    "PY-0025": 0.25, "PY-0026": 0.40, "PY-0027": 0.20, "PY-0028": 0.35,
    "PY-0029": 0.45, "PY-0030": 0.40, "PY-0031": 0.45, "PY-0032": 0.20,
    "PY-0033": 0.60, "PY-0034": 0.30, "PY-0035": 0.65, "PY-0036": 0.65,
    "PY-0037": 0.30, "PY-0038": 0.55, "PY-0039": 0.25, "PY-0040": 0.45,
    "PY-0041": 0.30, "PY-0042": 0.75, "PY-0043": 0.15, "PY-0044": 0.55,
    "PY-0045": 0.55, "PY-0046": 0.15, "PY-0047": 0.40, "PY-0048": 0.20,
    "PY-0049": 0.50, "PY-0050": 0.35, "PY-0051": 0.15, "PY-0052": 0.55,
    "PY-0053": 0.20, "PY-0054": 0.40, "PY-0055": 0.35, "PY-0056": 0.25,
    "PY-0057": 0.55, "PY-0058": 0.25, "PY-0059": 0.20, "PY-0060": 0.70,
    "PY-0061": 0.35, "PY-0062": 0.70,
    # C
    "C-0001": 0.10, "C-0002": 0.20, "C-0003": 0.15, "C-0004": 0.20,
    "C-0005": 0.20, "C-0006": 0.25, "C-0007": 0.30, "C-0008": 0.25,
    "C-0009": 0.20, "C-0010": 0.25, "C-0011": 0.30, "C-0012": 0.45,
    "C-0013": 0.50, "C-0014": 0.15, "C-0015": 0.30, "C-0016": 0.35,
    "C-0017": 0.40, "C-0018": 0.35, "C-0019": 0.15, "C-0020": 0.35,
    "C-0021": 0.20, "C-0022": 0.15, "C-0023": 0.40, "C-0024": 0.35,
    "C-0025": 0.40, "C-0026": 0.35, "C-0027": 0.35, "C-0028": 0.30,
    "C-0029": 0.35, "C-0030": 0.25, "C-0031": 0.40, "C-0032": 0.20,
    "C-0033": 0.30, "C-0034": 0.55, "C-0035": 0.55, "C-0036": 0.65,
    "C-0037": 0.65, "C-0038": 0.60, "C-0039": 0.55, "C-0040": 0.60,
    "C-0041": 0.60, "C-0042": 0.65, "C-0043": 0.55, "C-0044": 0.60,
    "C-0045": 0.55, "C-0046": 0.45, "C-0047": 0.55, "C-0048": 0.65,
    "C-0049": 0.65, "C-0050": 0.50, "C-0051": 0.60, "C-0052": 0.60,
    "C-0053": 0.55, "C-0054": 0.55, "C-0055": 0.50, "C-0056": 0.55,
    "C-0057": 0.60, "C-0058": 0.65, "C-0059": 0.60, "C-0060": 0.60,
    "C-0061": 0.55, "C-0062": 0.60, "C-0063": 0.55, "C-0064": 0.55,
    # DSA
    "DSA-0001": 0.10, "DSA-0002": 0.20, "DSA-0003": 0.20, "DSA-0004": 0.30,
    "DSA-0005": 0.35, "DSA-0006": 0.35, "DSA-0007": 0.55, "DSA-0008": 0.35,
    "DSA-0009": 0.20, "DSA-0010": 0.30, "DSA-0011": 0.60, "DSA-0012": 0.40,
    "DSA-0013": 0.15, "DSA-0014": 0.40, "DSA-0015": 0.30, "DSA-0016": 0.50,
    "DSA-0017": 0.35, "DSA-0018": 0.25, "DSA-0019": 0.45, "DSA-0020": 0.40,
    "DSA-0021": 0.45, "DSA-0022": 0.40, "DSA-0023": 0.50, "DSA-0024": 0.55,
    "DSA-0025": 0.35, "DSA-0026": 0.65, "DSA-0027": 0.35, "DSA-0028": 0.45,
    "DSA-0029": 0.20, "DSA-0030": 0.50, "DSA-0031": 0.55, "DSA-0032": 0.35,
    "DSA-0033": 0.45, "DSA-0034": 0.30, "DSA-0035": 0.30, "DSA-0036": 0.45,
    "DSA-0037": 0.50,
}

OUTPUT_KEYWORDS = re.compile(
    r"(what will be the output|what is the output|what will be output"
    r"|what is output|what will happen|what will be the final|"
    r"what will be the value|what will be the result)",
    re.IGNORECASE,
)

LOGIC_KEYWORDS = re.compile(
    r"(order of|precedence|which of the following is not|which is not|"
    r"which of the following (are|is) (not|true|false|correct|incorrect)|"
    r"evaluate|postfix|prefix|complexity|difference between|"
    r"how many|convert|notation)",
    re.IGNORECASE,
)


def classify(qid: str, question: str):
    if qid in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[qid]["type"], MANUAL_OVERRIDES[qid]["estimated_time"]
    q = question.lower()
    if OUTPUT_KEYWORDS.search(q):
        return "program", 65
    if LOGIC_KEYWORDS.search(q):
        return "logic", 50
    return "direct", 25


def subject_from_id(qid: str) -> str:
    prefix = qid.split("-")[0].upper()
    return {"PY": "Python", "C": "C", "DSA": "Data Structures"}.get(prefix, prefix)


def clean_option(opt: str) -> str:
    """Strip leading A) B) C) D) and '4) View Answer' lines."""
    opt = opt.strip()
    if re.match(r"^[0-9]\)", opt):
        return None
    opt = re.sub(r"^[A-D]\)\s*", "", opt)
    return opt if opt else None


def parse_correct_answer(raw: str) -> str:
    """Extract just the answer text from 'C) Guido van Rossum'."""
    raw = raw.strip()
    # Handle '?) D' style (malformed scrape)
    m = re.match(r"^\??\)\s*[A-D]$", raw)
    if m:
        return raw  # keep as-is, human must fix
    raw = re.sub(r"^[A-D\?]\)\s*", "", raw)
    return raw


def parse_md(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    blocks = re.split(r"^---$", text, flags=re.MULTILINE)
    questions = []

    for block in blocks:
        qid_match = re.search(r"##\s+Question ID\s*:\s*(\S+)", block)
        if not qid_match:
            continue
        qid = qid_match.group(1).strip()

        def extract(label: str) -> str:
            pattern = rf"\*\*{re.escape(label)}\*\*\s*\n+(.*?)(?=\n\*\*|\Z)"
            m = re.search(pattern, block, re.DOTALL)
            return m.group(1).strip() if m else ""

        question_text = extract("Question")
        options_raw   = extract("Options")
        correct_raw   = extract("Correct Answer")
        explanation   = extract("Explanation")
        difficulty_raw = extract(r"Difficulty \(0\.0 – 1\.0\)")

        # Parse options list
        opts_lines = [l.strip() for l in options_raw.splitlines() if l.strip()]
        options = []
        for l in opts_lines:
            c = clean_option(l)
            if c:
                options.append(c)

        difficulty = DIFFICULTY_OVERRIDES.get(qid, float(difficulty_raw) if difficulty_raw else 0.50)
        q_type, est_time = classify(qid, question_text)
        subject = subject_from_id(qid)

        questions.append({
            "id":             qid,
            "subject":        subject,
            "question":       question_text,
            "options":        options,
            "correct_answer": parse_correct_answer(correct_raw),
            "explanation":    explanation,
            "difficulty":     round(difficulty, 2),
            "type":           q_type,
            "estimated_time": est_time,
        })

    return questions


def write_json(questions: list[dict], outdir: Path, subject: str):
    slug = subject.lower().replace(" ", "_")
    out = outdir / f"{slug}_questions.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {len(questions)} questions → {out}")


def write_enriched_md(questions: list[dict], outdir: Path, original_stem: str):
    """Write an enriched .md alongside with type + estimated_time injected."""
    out = outdir / f"{original_stem}_enriched.md"
    lines = []
    for q in questions:
        lines.append(f"## Question ID : {q['id']}\n")
        lines.append(f"**Question**\n\n{q['question']}\n\n")
        lines.append("**Options**\n\n")
        for i, o in enumerate(q["options"]):
            lines.append(f"{chr(65+i)}) {o}\n")
        lines.append(f"\n**Correct Answer**\n\n{q['correct_answer']}\n\n")
        lines.append(f"**Explanation**\n\n{q['explanation']}\n\n")
        lines.append(f"**Difficulty (0.0 – 1.0)**\n\n{q['difficulty']}\n\n")
        lines.append(f"**Type**\n\n{q['type']}\n\n")
        lines.append(f"**Estimated Time (seconds)**\n\n{q['estimated_time']}\n\n")
        lines.append("---\n\n")
    out.write_text("".join(lines), encoding="utf-8")
    print(f"  Enriched md → {out}")


DEFAULT_FILES = [
    Path("/mnt/user-data/uploads/python_review.md"),
    Path("/mnt/user-data/uploads/c_review.md"),
    Path("/mnt/user-data/uploads/dsa_review.md"),
]


def main():
    parser = argparse.ArgumentParser(description="Convert review .md → JSON dataset")
    parser.add_argument("files", nargs="*", type=Path, help=".md files to process")
    parser.add_argument("--outdir", type=Path, default=Path("data"), help="output directory")
    parser.add_argument("--no-enriched-md", action="store_true")
    args = parser.parse_args()

    files = args.files or DEFAULT_FILES
    args.outdir.mkdir(parents=True, exist_ok=True)

    for f in files:
        if not f.exists():
            print(f"  SKIP (not found): {f}")
            continue
        print(f"\nParsing {f.name} …")
        questions = parse_md(f)
        if not questions:
            print("  No questions found, skipping.")
            continue
        subject = questions[0]["subject"]
        write_json(questions, args.outdir, subject)
        if not args.no_enriched_md:
            write_enriched_md(questions, args.outdir, f.stem)

    print("\nDone.")


if __name__ == "__main__":
    main()
