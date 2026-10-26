# CSV Cleaner & Sales Report Generator

A beginner-friendly Python project for cleaning sales CSV files and generating reports.

## Requirements
- Windows 10/11
- Python 3.10 or newer
- Internet only for the one-time pandas installation

## Setup (Windows)

1. Extract the ZIP file to a folder, for example:
   `C:\Users\YourName\Documents\csv_cleaner_demo`
2. Open that folder in File Explorer.
3. Click the address bar, type `cmd`, and press Enter.
4. In the Command Prompt, run:

   ```bat
   py -m pip install pandas
   ```

   If `py` is not recognized, try `python -m pip install pandas`.

5. Run the demo:

   ```bat
   py csv_cleaner.py messy_sales.csv
   ```

   If `py` is not recognized, use:

   ```bat
   python csv_cleaner.py messy_sales.csv
   ```

6. Open the `output` folder created beside the script.

## Output files
- `output/cleaned_sales.csv` — cleaned and sorted data with a calculated `line_total`
- `output/product_summary.csv` — order count, units sold, and revenue by product
- `output/sales_summary.txt` — readable summary and data-quality counts

## Expected behavior
The sample file deliberately includes an exact duplicate, extra spaces, mixed capitalization, a bad date, a missing customer, and a zero quantity. The program removes duplicate rows and rows that cannot be used safely in the report.

## Use with another CSV
Your CSV must have these columns (column names are case-insensitive and spaces are converted to underscores):
- `order_id`
- `date`
- `customer`
- `product`
- `quantity`
- `unit_price`

For real client work, agree on the rules before cleaning. Keep an untouched backup, never silently delete ambiguous records, and show the client a before/after summary. This demo removes invalid rows, so adapt that behavior to the client's requirements.

## Suggested portfolio description
"Built a Python/pandas utility that validates sales CSV files, removes exact duplicates, standardizes text, flags/removes invalid records, calculates line totals, and exports product-level revenue summaries."
