# scripts/ingest.py
import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ingestion.yaml_ingestor import ingest_yaml_file


def main():
    parser = argparse.ArgumentParser(description="Ingest product YAML into Neo4j")
    parser.add_argument("--file", required=True, help="Path to YAML file")
    args = parser.parse_args()

    ingest_yaml_file(args.file)


if __name__ == "__main__":
    main()
