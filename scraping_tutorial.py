import requests
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

# ==============================================================================
# HOW TO INSPECT HTML & IDENTIFY SELECTORS (Educational Guide)
# ==============================================================================
# To scrape a webpage, you must inspect the HTML elements of the website in your browser:
# 1. Open the webpage (https://realpython.github.io/fake-jobs/) in your browser.
# 2. Right-click on any element you want to scrape (e.g., a job title) and select "Inspect".
# 3. Look for unique identifiers in the HTML panel:
#    - Tag Name: e.g., <div>, <h2>, <p>
#    - Class Attribute: e.g., class="card-content", class="location"
#    - ID Attribute: e.g., id="job-1" (highly unique)
#    - Nesting/Hierarchies: Identify a container that wraps each individual item.
#
# From inspecting this mock website, we identified:
# - Individual Job Card: <div class="card-content">
# - Job Title: <h2> inside the card with class "title is-5"
# - Company Name: <h3> inside the card with class "subtitle is-6 company"
# - City/Location: <p> inside the card with class "location"
# ==============================================================================

url = "https://realpython.github.io/fake-jobs/"
print(f"Fetching job listings from {url}...")
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 1. Find all job card container elements
    # Instead of find(), which returns only the first match, we use find_all()
    # to retrieve a list of all matching tags.
    job_cards = soup.find_all("div", class_="card-content")
    print(f"Found {len(job_cards)} job cards on the page.\n")
    
    # List to hold our scraped job dictionaries
    scraped_jobs = []
    
    # 2. Loop through each job card and extract details
    for card in job_cards:
        # Find elements inside the scope of the current card container
        title_element = card.find("h2", class_="title is-5")
        company_element = card.find("h3", class_="subtitle is-6 company")
        location_element = card.find("p", class_="location")
        
        # Check if the elements exist before extracting their text to prevent AttributeError
        if title_element and company_element and location_element:
            job_info = {
                "title": title_element.text.strip(),
                "company": company_element.text.strip(),
                # Cleaning up location text since it might contain commas/whitespace
                "city": location_element.text.strip(),
            }
            scraped_jobs.append(job_info)
            
    # 3. Display the structured data
    print(f"Successfully scraped {len(scraped_jobs)} jobs into a list of dictionaries:")
    for idx, job in enumerate(scraped_jobs[:5], 1):  # Display first 5 jobs as sample
        print(f"\nScraped Job #{idx}:")
        print(f"  Title:   {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  City:    {job['city']}")
        
    if len(scraped_jobs) > 5:
        print(f"\n... and {len(scraped_jobs) - 5} more jobs.")
else:
    print(f"Failed to fetch page. Status code: {response.status_code}")
