import pandas as pd
import json
from pathlib import Path
import argparse


def convert_excel_to_json(excel_path: Path, json_path: Path, columns: list[str] = None):
    if not excel_path.exists():
        print(f"ERROR: Input file does not exist: {excel_path}")
        return False

    # Read Excel file
    df = pd.read_excel(excel_path, engine="openpyxl")

    # Select columns if specified
    if columns:
        df = df[columns]

    # Convert DataFrame to JSON list of dicts
    data = df.to_dict(orient="records")

    # Write JSON file with UTF-8 encoding and pretty formatting
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Converted {excel_path} to {json_path} with columns {columns}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Excel to JSON with selected columns."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to the input Excel file (e.g. data/raw_data/mini_stock_list.xlsx)",
        required=False,
    )
    parser.add_argument(
        "--out",
        type=str,
        help="Path for the output JSON file (e.g. data/raw_data/mini_stock_list.json)",
        required=False,
    )
    args = parser.parse_args()

    if not args.file:
        excel_file = input(
            "Enter path to Excel file (e.g. data/raw_data/mini_stock_list.xlsx): "
        ).strip()
    else:
        excel_file = args.file

    if not args.out:
        json_file = input(
            "Enter path for output JSON file (e.g. data/raw_data/mini_stock_list.json): "
        ).strip()
    else:
        json_file = args.out

    cols = ["part_number", "title", "manufacturer"]

    convert_excel_to_json(Path(excel_file), Path(json_file), cols)
