import sqlite3
import requests
from bs4 import BeautifulSoup
import random
import os
from telegram_notifier import send_telegram_job

DB_FILE = "jobs.db"

# Replace these placeholder values with your real Telegram Bot Token and Chat ID.
# Best practice is to read them from environment variables.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        city TEXT,
        salary INTEGER,
        url TEXT UNIQUE NOT NULL,
        date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def is_job_new(url):
    """Returns True if the URL is not in the database, False otherwise."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM jobs WHERE url = ?", (url,))
    row = cursor.fetchone()
    conn.close()
    return row is None

def insert_job(title, company, city, salary, url):
    """Inserts job details into SQLite."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO jobs (title, company, city, salary, url)
    VALUES (?, ?, ?, ?, ?)
    """, (title, company, city, salary, url))
    conn.commit()
    conn.close()

def run_scraper_and_notify():
    init_db()
    
    url = "https://realpython.github.io/fake-jobs/"
    print(f"Scraping {url}...")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching page: {response.status_code}")
        return
        
    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("div", class_="card-content")
    
    new_jobs_count = 0
    
    for idx, card in enumerate(job_cards):
        title_el = card.find("h2", class_="title is-5")
        company_el = card.find("h3", class_="subtitle is-6 company")
        location_el = card.find("p", class_="location")
        links = card.find_all("a")
        apply_url = links[1]["href"] if len(links) > 1 else f"https://example.com/job/{idx}"
        
        if title_el and company_el and location_el:
            title = title_el.text.strip()
            company = company_el.text.strip()
            city = location_el.text.strip()
            
            # Check if this listing is new to the database
            if is_job_new(apply_url):
                # Assign a mock salary for demo purposes
                salary = random.randint(8, 32) * 5000
                
                # 1. Save it in SQLite so we don't notify next time
                insert_job(title, company, city, salary, apply_url)
                
                # 2. Trigger Telegram Notification
                # (Will print skipped/placeholder error if credentials are not configured yet)
                if TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" and TELEGRAM_CHAT_ID != "YOUR_CHAT_ID_HERE":
                    send_telegram_job(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, title, company, city, salary, apply_url)
                else:
                    print(f"[Placeholder Notifier] Found new job: '{title}' at '{company}'. Connect your Telegram Bot Token to send alerts!")
                
                new_jobs_count += 1
                
    print(f"\nCompleted! Processed {len(job_cards)} jobs, found {new_jobs_count} new listings.")

if __name__ == "__main__":
    run_scraper_and_notify()
