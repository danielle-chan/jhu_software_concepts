import json
from scrape import scrape_data  # assuming scrape_data is in scrape.py
import re

def clean_data(raw_data):
    cleaned = []

    for entry in raw_data:
        cleaned_entry = {}

        # University
        cleaned_entry["university"] = entry.get("university", "N/A")

        # Program
        cleaned_entry["program"] = entry.get("program", "N/A")

        # Degree type
        cleaned_entry["degree_type"] = entry.get("degree_type", "N/A")

        # Comments
        cleaned_entry["comments"] = entry.get("comment", "N/A")

        # Date added 
        cleaned_entry["date_added"] = entry.get("date_added", "N/A")

        # Applicant status
        cleaned_entry['status'] = entry.get("applicant_status", "N/A")

        # URL
        cleaned_entry["url"] = entry.get("url", "N/A")

        # GPA 
        cleaned_entry["GPA"] = entry.get("gpa", "N/A")

        # GRE G
        cleaned_entry["GRE_G"] = entry.get("gre_general", "N/A")

        # GRE V
        cleaned_entry["GRE_V"] = entry.get("gre_verbal", "N/A")

        # GRE AW
        cleaned_entry["GRE_AW"] = entry.get("gre_aw", "N/A")

        # Semester Start
        cleaned_entry["term"] = entry.get("semester_start", "N/A")

        # International status
        cleaned_entry["US/International"] = entry.get("international_status", "N/A")

        cleaned.append(cleaned_entry)

    return cleaned

