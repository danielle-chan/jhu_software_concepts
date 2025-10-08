"""Clean and normalize scraped GradCafe applicant data."""
import json

from worker.etl.incremental_scraper import scrape_data

def clean_data(raw_data):
    """Normalize raw scraped applicant records into a consistent dictionary list."""
    cleaned = []

    for entry in raw_data:
        cleaned_entry = {}

        # Clean university
        cleaned_entry["university"] = entry.get("university", "N/A")

        # Clean program
        cleaned_entry["program"] = entry.get("program", "N/A")

        # Clean degree type
        cleaned_entry["degree_type"] = entry.get("degree_type", "N/A")

        # Clean comments
        cleaned_entry["comments"] = entry.get("comment", "N/A")

        # Clean date added
        cleaned_entry["date_added"] = entry.get("date_added", "N/A")

        # Clean applicant status
        cleaned_entry['status'] = entry.get("applicant_status", "N/A")

        # Clean URL
        cleaned_entry["url"] = entry.get("url", "N/A")

        # Clean GPA
        cleaned_entry["GPA"] = entry.get("gpa", "N/A")

        # Clean GRE G
        cleaned_entry["GRE_G"] = entry.get("gre_general", "N/A")

        # Clean GRE V
        cleaned_entry["GRE_V"] = entry.get("gre_verbal", "N/A")

        # Clean GRE AW
        cleaned_entry["GRE_AW"] = entry.get("gre_aw", "N/A")

        # Clean semester start
        cleaned_entry["term"] = entry.get("semester_start", "N/A")

        # Clean international status
        cleaned_entry["US/International"] = entry.get("international_status", "N/A")

        cleaned.append(cleaned_entry)

    return cleaned


def save_data(cleaned_data, filename="cleaned_applicant_data.json"):
    """Save cleaned data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)


def load_data(filename="cleaned_applicant_data.json"):
    """Load cleaned data from a JSON file."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    scraped = scrape_data(pages=1500)  # scrape first 1500 pages
    structured_data = clean_data(scraped)

    save_data(structured_data)  # save to JSON
    loaded_data = load_data()   # load back

    print(f"Saved and loaded {len(loaded_data)} entries")
    print(json.dumps(loaded_data[:1], indent=4))
