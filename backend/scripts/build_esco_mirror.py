import argparse
import json

from services.esco_mirror_service import build_from_extracted_csv_folder


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True, help="Path to extracted ESCO CSV package folder")
    args = ap.parse_args()

    result = build_from_extracted_csv_folder(args.folder)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

