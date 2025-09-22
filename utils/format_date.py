import re
from datetime import datetime
from typing import List, Union

def convert_iso_date_into_ddmmyyyy(date_input: Union[str, datetime]):

    if isinstance(date_input, datetime):
        return date_input.strftime("%d/%m/%Y")

    date_input = re.sub(r'\s*\(.*?\)\s*', '', date_input)
        # Strip things like "Updated: " or timezone like "IST"
    date_input = re.sub(r'^\s*Updated:\s*', '', date_input)
    date_input = re.sub(r'\s+[A-Z]{2,4}$', '', date_input)  # Remove timezone like IST

    date_formats = [
        "%Y-%m-%dT%H:%M:%SZ",      # ISO format with time
        "%Y-%m-%d",                # ISO format without time
        "%d %B %Y %I:%M %p",       # e.g., '19 May 2025 12:06 PM'
        "%b %d, %Y, %H:%M",        # e.g., 'Mar 27, 2025, 23:20'
        "%m/%d/%Y, %I:%M %p, %z",   # e.g. 06/14/2024, 07:00 AM, +0000
    ]
    cleaned_input = re.sub(r'\s+[A-Z]{2,4}$', '', date_input)
    for fmt in date_formats:
        try:
            dt = datetime.strptime(cleaned_input.strip(), fmt)
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            continue

    raise ValueError(f"Date format not recognized: {date_input}")