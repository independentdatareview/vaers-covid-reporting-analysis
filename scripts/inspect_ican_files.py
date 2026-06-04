from pathlib import Path
import pandas as pd

ICAN_DIR = Path(r".\data\ICANN")

files = sorted(list(ICAN_DIR.glob("*.xlsx")))

print(f"Found {len(files)} Excel files\n")

for file in files:
    print("=" * 80)
    print(file.name)
    print("=" * 80)

    try:
        xls = pd.ExcelFile(file)
        print("Sheets:", xls.sheet_names)

        for sheet in xls.sheet_names:
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(file, sheet_name=sheet, nrows=5)
            print("Columns:")
            for col in df.columns:
                print(f"  - {col}")
            print("\nPreview:")
            print(df.head().to_string(index=False))

    except Exception as e:
        print(f"ERROR reading {file.name}: {e}")

    print("\n")
