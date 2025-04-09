import requests
from bs4 import BeautifulSoup


def scrape_table(url, table_class, header_match=None, is_rebate=False):
    """
    Scrapes a specific table from the webpage based on its class and header match.

    :param url: URL of the page to scrape.
    :param table_class: Class name of the target table.
    :param header_match: Text in the header to identify the specific table.
    :param is_rebate: Set to True for rebate table processing.
    :return: List of dictionaries containing table data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all("table", {"class": table_class})
        if not tables:
            raise ValueError("No tables found with the specified class!")

        for table in tables:
            header = table.find("tr").get_text(strip=True)
            if header_match and header_match in header:
                return extract_table_data(table, is_rebate=is_rebate)

        raise ValueError(f"No table found with header matching '{header_match}'!")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except ValueError as ve:
        print(str(ve))
        return None

def extract_table_data(table, is_rebate=False):
    """
    Extracts table data into a structured list of dictionaries.
    Splits tax_rate column into tax_on_previous_bracket and tax_percentage for tax tables.
    Converts currency values in rebate tables to integers.

    :param table: HTML table element.
    :param is_rebate: Set to True if processing a rebate table.
    :return: List of dictionaries with the table's rows.
    """
    rows = table.find_all("tr")
    table_data = []

    for index, row in enumerate(rows[1:]):  # Skip the header row
        cols = row.find_all("td")
        if cols:
            if is_rebate:
                # Handle rebate table rows
                age_group = cols[0].get_text(strip=True)
                if not age_group:  # Skip rows with empty age_group
                    continue

                # Sanitize currency values
                def sanitize_currency(value):
                    if value and value.startswith("R"):
                        return int(value.replace("R", "").replace(",", "").replace(" ", "").strip())
                    return None

                table_data.append({
                    "age_group": age_group,
                    "2026": sanitize_currency(cols[1].get_text(strip=True)) if len(cols) > 1 else None,
                    "2025": sanitize_currency(cols[1].get_text(strip=True)) if len(cols) > 1 else None,
                    "2024": sanitize_currency(cols[2].get_text(strip=True)) if len(cols) > 2 else None
                })
            else:
                # Handle tax table rows
                income_range = cols[0].get_text(strip=True)
                if "–" in income_range:
                    min_income, max_income = map(
                        lambda x: int(x.replace(" ", "").replace("\xa0", "")),
                        income_range.split("–")
                    )
                elif "and above" in income_range:
                    min_income = 1817001
                    max_income = 9999999999
                else:
                    continue

                tax_rate = cols[1].get_text(strip=True) if len(cols) > 1 else None

                # Split tax_rate into tax_on_previous_bracket and tax_percentage
                tax_on_previous_bracket, tax_percentage = None, None
                if tax_rate:
                    if "+" in tax_rate:
                        parts = tax_rate.split("+")
                        tax_on_previous_bracket = int(parts[0].strip().replace(" ", "").replace(",", ""))
                        if "%" in parts[1]:
                            tax_percentage = int(parts[1].strip().split("%")[0])
                    elif "%" in tax_rate:  # Special case for percentages without '+'
                        tax_on_previous_bracket = 0
                        tax_percentage = int(tax_rate.strip().split("%")[0])

                table_data.append({
                    "min_income": min_income,
                    "max_income": max_income,
                    "tax_on_previous_bracket": tax_on_previous_bracket,
                    "tax_percentage": tax_percentage
                })

    return table_data

def validate_tax_table_data(tax_table):
    """
    Validates the tax table data.

    :param tax_table: List of dictionaries containing tax table data.
    :return: Validated list of tax table entries.
    """
    validated_table = []
    for entry in tax_table:
        if entry["min_income"] >= 0 and entry["max_income"] >= entry["min_income"]:
            validated_table.append(entry)
    return validated_table


def validate_rebate_table_data(rebate_table):
    """
    Validates the rebate table data.

    :param rebate_table: List of dictionaries containing rebate table data.
    :return: Validated list of rebate table entries.
    """
    validated_table = []
    for entry in rebate_table:
        if entry["age_group"] and entry["2026"] and entry["2025"] and entry["2024"]:
            validated_table.append(entry)
    return validated_table


def scrape_tax_table_2024(url):
    """
    Scrapes and validates the tax table for 2024.

    :param url: URL of the page to scrape.
    :return: Validated list of dictionaries containing processed tax table data.
    """
    tax_table = scrape_table(url, "ms-rteTable-default", "Taxable income")
    if tax_table:
        return validate_tax_table_data(tax_table)
    return None


def scrape_rebate_table(url):
    """
    Scrapes and validates the rebate table.

    :param url: URL of the page to scrape.
    :return: Validated list of dictionaries containing rebate table data.
    """
    rebate_table = scrape_table(url, "ms-rteTable-default", "Tax Rebate", is_rebate=True)
    if rebate_table:
        return validate_rebate_table_data(rebate_table)
    return None


if __name__ == "__main__":
    url = "https://www.sars.gov.za/tax-rates/income-tax/rates-of-tax-for-individuals/"

    print("Scraping Tax Table for 2024...")
    tax_table_2024 = scrape_tax_table_2024(url)
    if tax_table_2024:
        print("Tax Table for 2024:")
        for entry in tax_table_2024:
            print(entry)

    print("\nScraping Rebate Table...")
    rebate_table = scrape_rebate_table(url)
    if rebate_table:
        print("Rebate Table:")
        for entry in rebate_table:
            print(entry)
            
