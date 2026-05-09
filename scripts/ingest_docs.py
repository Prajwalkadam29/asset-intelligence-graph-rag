# scripts/ingest_docs.py
import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ingestion.docs_ingestor import ingest_docs_for_root


def main():
    parser = argparse.ArgumentParser(description="Ingest docs for parts")
    parser.add_argument("--root", required=True, help="Root folder for part docs")
    args = parser.parse_args()

    ingest_docs_for_root(args.root)


if __name__ == "__main__":
    main()
