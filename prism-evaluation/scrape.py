import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup


def fetch_sic_mapping():
    with open("a.html") as f:
        text = f.read()
    soup = BeautifulSoup(text, "html.parser")

    sic_mapping = {}

    # This example assumes the page contains a table with at least two columns:
    # first column for SIC code and second for the office/industry description.
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        # Skip header row (if present)
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                sic_code = cols[0].get_text(strip=True)
                office = cols[1].get_text(strip=True)
                # Optionally convert the SIC code to an integer if possible
                try:
                    sic_code = int(sic_code)
                except ValueError:
                    pass
                sic_mapping[sic_code] = office
    else:
        print("No table found on the page—please check the page structure.")
    return sic_mapping


def standardize_name(name: str, mapping: dict) -> str:
    """
    Standardize the industry name using a mapping.
    For example, replace "Office of Energy & Transportation" with "Office of Energy and Transportation".
    """
    name = name.strip()
    name = name.replace("Office of ", "")
    name = name.replace("&", "and")
    name = name.replace("\xa0", " ")
    return mapping.get(name, name)


def clean_sic_json(data: dict) -> dict:
    """
    Clean up the SIC JSON mapping:
      - Trim whitespace.
      - Split values containing ' or ' into a list.
      - Standardize industry names using a predefined mapping.
    """
    # Mapping for standardizing industry names.
    # Adjust these replacements as needed.
    standard_mapping = {
        "Office of Energy & Transportation": "Office of Energy and Transportation",
        "Office of Real Estate & Construction": "Office of Real Estate and Construction",
        "Office of Trade & Services": "Office of Trade and Services",
        "Office of International Corp Fin": "Office of International Corporate Finance",
    }

    cleaned = {}
    for sic, industry in data.items():
        # Trim extra whitespace
        industry = industry.strip()

        # Check if the industry string contains ' or '
        if " or " in industry:
            # Split on ' or ', trim each part, and standardize it
            parts = [
                standardize_name(part, standard_mapping)
                for part in industry.split(" or ")
            ]
            # Optional: Remove duplicate names (if any)
            parts = list(dict.fromkeys(parts))
            cleaned[sic] = parts
        else:
            cleaned[sic] = [standardize_name(industry, standard_mapping)]
    return cleaned


if __name__ == "__main__":
    mapping = fetch_sic_mapping()
    cleaned_data = clean_sic_json(mapping)
    # print(json.dumps(set(*zip(*[v for k, v in cleaned_data.items()]))))
    print(json.dumps(cleaned_data))
