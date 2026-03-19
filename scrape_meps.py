import requests
from bs4 import BeautifulSoup
import csv
import time

# 1. This is the main page for the Subcommittee on Human Rights (DROI) members
BASE_URL = "https://www.europarl.europa.eu"
COMMITTEE_URL = "https://www.europarl.europa.eu/committees/en/droi/home/members"

def scrape_meps():
    print("Starting the scraper... please wait.")
    
    # 2. Ask the website for the list of committee members
    try:
        response = requests.get(COMMITTEE_URL)
        response.raise_for_status() # Check if the website is working
    except Exception as e:
        print(f"Error connecting to the website: {e}")
        return

    # 3. Parse the HTML code of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 4. Find all links that lead to MEP profile pages
    # On this specific site, MEP links usually follow a specific pattern
    mep_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if "/meps/en/" in href and "home" not in href:
            # Clean up the link and add it to our list
            full_link = BASE_URL + href if href.startswith('/') else href
            if full_link not in mep_links:
                mep_links.append(full_link)

    print(f"Found {len(mep_links)} MEPs to scrape. Starting individual profile visits...")

    # 5. Prepare a CSV file to save the data (so you can open it in Excel)
    with open('droi_meps_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Country', 'Political Group', 'Profile URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # 6. Visit each individual MEP page
        for link in mep_links:
            try:
                # Add a tiny delay (0.5 seconds) so we don't overwhelm the website
                time.sleep(0.5)
                
                mep_page = requests.get(link)
                mep_soup = BeautifulSoup(mep_page.text, 'html.parser')

                # Extract the Name (usually in a heading)
                name = mep_soup.find('span', class_='sln-member-name')
                name_text = name.get_text(strip=True) if name else "Not Found"

                # Extract the Country
                country = mep_soup.find('span', class_='erpl_title-h3')
                country_text = country.get_text(strip=True) if country else "Not Found"

                # Extract the Political Group
                group = mep_soup.find('span', class_='sln-political-group-name')
                group_text = group.get_text(strip=True) if group else "Not Found"

                # 7. Save the data for this MEP to the file
                writer.writerow({
                    'Name': name_text,
                    'Country': country_text,
                    'Political Group': group_text,
                    'Profile URL': link
                })
                print(f"Successfully scraped: {name_text}")

            except Exception as e:
                print(f"Could not scrape {link}: {e}")

    print("\nAll done! You can now open 'droi_meps_data.csv' in Excel.")

# This line actually runs the script
if __name__ == "__main__":
    scrape_meps()
