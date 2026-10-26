#!/usr/bin/env python3
"""
CSV Cleaner & Sales Report Generator
Beginner-friendly demo project.

Usage:
    python csv_cleaner.py messy_sales.csv

Outputs are written to an output/ folder next to this script:
    cleaned_sales.csv
    sales_summary.txt
    product_summary.csv
"""

from pathlib import Path
import sys
import pandas as pd


REQUIRED_COLUMNS = {"order_id", "date", "customer", "product", "quantity", "unit_price"}


def clean_text(series: pd.Series) -> pd.Series:
    """Trim extra spaces and turn empty strings into missing values."""
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.replace("", pd.NA)
    return cleaned


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python csv_cleaner.py <input_csv_path>")
        return 2

    input_path = Path(sys.argv[1]).expanduser()

    if not input_path.exists() or not input_path.is_file():
        print(f"ERROR: Input file not found: {input_path}")
        return 1

    if input_path.suffix.lower() != ".csv":
        print("ERROR: Please provide a .csv file.")
        return 1

    try:
        df = pd.read_csv(input_path)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(input_path, encoding="latin-1")
        except Exception as exc:
            print(f"ERROR: Could not read CSV: {exc}")
            return 1
    except pd.errors.EmptyDataError:
        print("ERROR: The CSV file is empty.")
        return 1
    except Exception as exc:
        print(f"ERROR: Could not read CSV: {exc}")
        return 1

    if df.empty:
        print("ERROR: The CSV has headers but no data rows.")
        return 1

    # Normalize column names to make common variations easier to handle.
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        print("ERROR: The CSV is missing required columns:")
        print("  " + ", ".join(sorted(missing_columns)))
        print("Expected columns: " + ", ".join(sorted(REQUIRED_COLUMNS)))
        return 1

    original_rows = len(df)

    # Clean text columns.
    for column in ["order_id", "customer", "product"]:
        df[column] = clean_text(df[column])

    # Standardize customer/product capitalization without changing order IDs.
    df["customer"] = df["customer"].str.replace(r"\s+", " ", regex=True).str.title()
    df["product"] = df["product"].str.replace(r"\s+", " ", regex=True).str.title()

    # Parse dates and numeric fields; invalid values become missing.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # Remove exact duplicate records.
    exact_duplicates_removed = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Remove rows missing essential fields or with invalid/non-positive values.
    essential = ["order_id", "date", "customer", "product", "quantity", "unit_price"]
    missing_essential_rows = int(df[essential].isna().any(axis=1).sum())
    df = df.dropna(subset=essential).copy()

    invalid_value_mask = (df["quantity"] <= 0) | (df["unit_price"] < 0)
    invalid_value_rows_removed = int(invalid_value_mask.sum())
    df = df.loc[~invalid_value_mask].copy()

    if df.empty:
        print("ERROR: No valid rows remain after cleaning. Check your input data.")
        return 1

    # Calculate line totals and produce consistent output.
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].round(2)
    df["line_total"] = (df["quantity"] * df["unit_price"]).round(2)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Sort output so it is easier to review.
    df = df.sort_values(["date", "order_id"], kind="stable").reset_index(drop=True)

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    cleaned_path = output_dir / "cleaned_sales.csv"
    product_path = output_dir / "product_summary.csv"
    report_path = output_dir / "sales_summary.txt"

    df.to_csv(cleaned_path, index=False, encoding="utf-8-sig")

    product_summary = (
        df.groupby("product", dropna=False)
        .agg(
            orders=("order_id", "nunique"),
            units_sold=("quantity", "sum"),
            revenue=("line_total", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    product_summary["revenue"] = product_summary["revenue"].round(2)
    product_summary.to_csv(product_path, index=False, encoding="utf-8-sig")

    total_revenue = float(df["line_total"].sum())
    total_units = int(df["quantity"].sum())
    unique_orders = int(df["order_id"].nunique())
    unique_customers = int(df["customer"].nunique())
    date_min = df["date"].min()
    date_max = df["date"].max()

    report_lines = [
        "CSV CLEANING & SALES SUMMARY",
        "=" * 32,
        f"Input file: {input_path.name}",
        f"Rows before cleaning: {original_rows}",
        f"Rows after cleaning: {len(df)}",
        f"Rows removed: {original_rows - len(df)}",
        "",
        "DATA QUALITY",
        "-" * 32,
        f"Exact duplicate rows removed: {exact_duplicates_removed}",
        f"Rows with missing/invalid essential fields removed: {missing_essential_rows}",
        f"Rows with non-positive quantity or negative price removed: {invalid_value_rows_removed}",
        "",
        "SALES SUMMARY",
        "-" * 32,
        f"Date range: {date_min} to {date_max}",
        f"Unique orders: {unique_orders}",
        f"Unique customers: {unique_customers}",
        f"Units sold: {total_units}",
        f"Total revenue: Rs. {total_revenue:,.2f}",
        "",
        "TOP PRODUCTS BY REVENUE",
        "-" * 32,
    ]

    for _, row in product_summary.head(5).iterrows():
        report_lines.append(
            f"{row['product']}: Rs. {row['revenue']:,.2f} "
            f"({int(row['units_sold'])} units)"
        )

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("\nSUCCESS — CSV cleaning finished.")
    print(f"Input rows: {original_rows}")
    print(f"Output rows: {len(df)}")
    print(f"Rows removed: {original_rows - len(df)}")
    print(f"Total revenue: Rs. {total_revenue:,.2f}")
    print("\nFiles created:")
    print(f"  Cleaned data:   {cleaned_path}")
    print(f"  Product report: {product_path}")
    print(f"  Summary report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
