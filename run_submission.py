#!/usr/bin/env python3
"""
TalentForge AI — Submission Entry Point
Usage:
    python run_submission.py --candidates ./candidates.jsonl --out ./submission.csv
"""

from __future__ import annotations
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rank import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="TalentForge AI — Candidate Ranking Pipeline")
    parser.add_argument(
        "--candidates",
        required=True,
        help="Path to candidates.jsonl (or .json) file",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path for submission CSV output",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=100,
        help="Number of top candidates to include (default: 100)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.candidates):
        print(f"Error: candidates file not found: {args.candidates}")
        sys.exit(1)

    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    run_pipeline(
        candidates_path=args.candidates,
        top_k=args.top_k,
        submission_path=args.out,
    )


if __name__ == "__main__":
    main()
