import os
import re
import pytesseract
from PIL import Image
import csv
from datetime import datetime

# Folder to scan
forecast_folder = os.path.expanduser("~/Desktop/Monthly decile/Forecast month 1")
output_csv = os.path.expanduser("~/Desktop/forecast_run_issue_dates_clean.csv")

# Regex patterns
run_re = re.compile(r"model run[:\s]+(\d{1,2}/\d{1,2}/\d{4})", re.IGNORECASE)
issue_re = re.compile(r"issued[:\s]+(\d{1,2}/\d{1,2}/\d{4})", re.IGNORECASE)

def parse_dates(text):
    run_date, issue_date = None, None
    for line in text.splitlines():
        if not run_date:
            m_run = run_re.search(line)
            if m_run:
                try:
                    run_date = datetime.strptime(m_run.group(1), "%d/%m/%Y")
                except:
                    pass
        if not issue_date:
            m_issue = issue_re.search(line)
            if m_issue:
                try:
                    issue_date = datetime.strptime(m_issue.group(1), "%d/%m/%Y")
                except:
                    pass
    return run_date, issue_date

# Process files
rows = []
for file in sorted(os.listdir(forecast_folder)):
    if not file.endswith(".png"):
        continue
    file_path = os.path.join(forecast_folder, file)
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        run_date, issue_date = parse_dates(text)
        if run_date and issue_date:
            span_month = run_date.month != issue_date.month or run_date.year != issue_date.year
            rows.append([file, run_date.strftime("%Y-%m-%d"), issue_date.strftime("%Y-%m-%d"), "YES" if span_month else "NO"])
        else:
            rows.append([file, "", "", "MISSING"])
        print(f"✅ {file}")
    except Exception as e:
        print(f"⚠️ Failed {file}: {e}")
        rows.append([file, "", "", "ERROR"])

# Write to CSV
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "run_date", "issue_date", "spans_month_boundary"])
    writer.writerows(rows)

print(f"📄 Output saved to: {output_csv}")
