import requests
from bs4 import BeautifulSoup
import csv
import time

# 1. This is the main page for the Subcommittee on Human Rights (DROI) members
BASE_URL = "https://www.europarl.europa.eu"
COMMITTEE_URL = "https://www.europarl.europa.eu/committees/en/droi/home/members"

def scrape_meps():
    print("Starting the scraper... please wait.")
    
    try:
        response = requests.get(COMMITTEE_URL)
        response.raise_for_status()
    except Exception as e:
        print(f"Error connecting to the website: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all MEP profile links
    mep_links = []
    for link in soup.find_all('a', href=True):
        if "/meps/en/" in link['href'] and "home" not in link['href']:
            full_url = BASE_URL + link['href'] if link['href'].startswith('/') else link['href']
            if full_url not in mep_links:
                mep_links.append(full_url)

    print(f"Found {len(mep_links)} MEP profile links. Starting extraction...")

    with open('droi_meps_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Country', 'Political Group', 'Profile URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for url in mep_links:
            try:
                time.sleep(0.3)
                r = requests.get(url)
                s = BeautifulSoup(r.text, 'html.parser')

                # Extract Name
                name = s.select_one('.sln-member-name')
                name_text = name.get_text(strip=True) if name else "Unknown"

                # Extract Country (Found in 'es_title-h3')
                country_text = "Not Found"
                country_el = s.select_one('.es_title-h3')
                if country_el:
                    # The text often contains ' - Party Name', so we'll just take the first part
                    full_text = country_el.get_text(strip=True)
                    country_text = full_text.split('-')[0].strip()

                # Extract Political Group
                group = s.select_one('.sln-political-group-name, .erpl_political-group-name')
                group_text = group.get_text(strip=True) if group else "Not Found"

                writer.writerow({
                    'Name': name_text,
                    'Country': country_text,
                    'Political Group': group_text,
                    'Profile URL': url
                })
                print(f"Scraped: {name_text} | {country_text} | {group_text}")
            except Exception as e:
                print(f"Error on {url}: {e}")


    print("\nAll done! You can now open 'droi_meps_data.csv' in Excel.")

# This line actually runs the script
if __name__ == "__main__":
    scrape_meps()
