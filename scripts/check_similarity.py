#!/usr/bin/env python3
"""
check_similarity.py

Compares every student submission in submissions/*.md against every
other submission using TF-IDF + cosine similarity, and flags pairs
that are suspiciously alike.

This is NOT an "AI detector." It only tells you when two (or more)
students' wording overlaps heavily with each other. That is a much
more reliable signal for a course assignment than trying to guess
whether a single piece of text was AI-written.

Usage (local, from repo root):
    python scripts/check_similarity.py
    python scripts/check_similarity.py --threshold 0.75

Exit code is always 0 (this script informs, it does not block PRs by
itself). Use the GitHub Action to also post the report as a PR comment.
"""

import argparse
import glob
import json
import os
import re
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


HEADER_LINE_RE = re.compile(r"^(name|roll number)\s*:", re.IGNORECASE)


def load_submissions(folder: str) -> dict[str, str]:
    """Read every .md file in `folder`, strip the Name/Roll header
    lines, and return {filename: body_text}. Skips the example file."""
    submissions = {}
    for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
        filename = os.path.basename(path)
        if filename.upper().startswith("EXAMPLE"):
            continue
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        body_lines = [line for line in lines if not HEADER_LINE_RE.match(line.strip())]
        text = "".join(body_lines).strip()
        if text:
            submissions[filename] = text
    return submissions


def compute_similarity_pairs(submissions: dict[str, str], threshold: float):
    """Return a list of (file_a, file_b, score) for every pair whose
    cosine similarity is >= threshold, sorted highest first."""
    filenames = list(submissions.keys())
    if len(filenames) < 2:
        return []

    texts = [submissions[name] for name in filenames]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts)
    sim_matrix = cosine_similarity(tfidf_matrix)

    flagged = []
    for i in range(len(filenames)):
        for j in range(i + 1, len(filenames)):
            score = sim_matrix[i][j]
            if score >= threshold:
                flagged.append((filenames[i], filenames[j], round(float(score), 3)))

    flagged.sort(key=lambda x: x[2], reverse=True)
    return flagged


def build_report(submissions: dict[str, str], flagged: list, threshold: float) -> str:
    lines = []
    lines.append(f"Checked {len(submissions)} submission(s) at similarity threshold {threshold}.\n")

    if not flagged:
        lines.append("No pairs above the threshold. Nothing flagged.")
        return "\n".join(lines)

    lines.append(f"**{len(flagged)} pair(s) flagged for review:**\n")
    for a, b, score in flagged:
        lines.append(f"- `{a}` and `{b}` — similarity **{score}**")

    lines.append(
        "\nA high score means the two answers share a lot of wording, not "
        "necessarily that either is AI-written. Please review the flagged "
        "pairs manually before taking any action."
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check student submissions for text similarity.")
    parser.add_argument(
        "--folder",
        default=os.path.join(os.path.dirname(__file__), "..", "submissions"),
        help="Folder containing submission .md files (default: ../submissions)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Cosine similarity threshold to flag a pair (0.0-1.0, default 0.75)",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional path to also write the report as JSON",
    )
    args = parser.parse_args()

    submissions = load_submissions(args.folder)
    flagged = compute_similarity_pairs(submissions, args.threshold)
    report = build_report(submissions, flagged, args.threshold)

    print(report)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "num_submissions": len(submissions),
                    "threshold": args.threshold,
                    "flagged_pairs": flagged,
                },
                f,
                indent=2,
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
