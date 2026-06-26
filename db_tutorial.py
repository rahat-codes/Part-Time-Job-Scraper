import sqlite3
import os

DB_FILE = "jobs.db"

def init_db():
    """Connects to SQLite and creates the jobs table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Modify Schema: Add 'url' column with 'UNIQUE NOT NULL' constraint.
    # This prevents any two records in the database from sharing the same URL.
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
    print("Database and 'jobs' table initialized successfully.")

def insert_job(title, company, city, salary, url):
    """Inserts a new job listing. If the URL already exists, the insert is ignored."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # INSERT OR IGNORE prevents sqlite3.IntegrityError if the 'url' constraint is violated
        cursor.execute("""
        INSERT OR IGNORE INTO jobs (title, company, city, salary, url)
        VALUES (?, ?, ?, ?, ?)
        """, (title, company, city, salary, url))
        conn.commit()
        
        # Check if a row was actually inserted
        if cursor.rowcount > 0:
            print(f"Inserted: '{title}' at '{company}' (URL: {url})")
        else:
            print(f"Skipped duplicate URL: {url}")
            
    except sqlite3.Error as e:
        print(f"Error inserting job: {e}")
    finally:
        conn.close()

def update_job_salary_by_url(url, new_salary):
    """Updates the salary of an existing job matching the unique URL."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        UPDATE jobs
        SET salary = ?
        WHERE url = ?
        """, (new_salary, url))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Updated: Job at URL '{url}' to new salary: ${new_salary:,}")
        else:
            print(f"No match found to update for URL '{url}'")
            
    except sqlite3.Error as e:
        print(f"Error updating job: {e}")
    finally:
        conn.close()

def query_jobs_by_city(city):
    """Queries and prints jobs in a specific city."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, title, company, city, salary, url, date_scraped
    FROM jobs
    WHERE city LIKE ?
    """, (f"%{city}%",))
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n--- Jobs in '{city}' ({len(rows)} found) ---")
    for row in rows:
        job_id, title, company, job_city, salary, url, date_scraped = row
        salary_str = f"${salary:,}" if salary else "N/A"
        print(f"ID {job_id} | {title} | {company} | {job_city} | {salary_str} | URL: {url}")

# ==============================================================================
# Demonstration Loop
# ==============================================================================
if __name__ == "__main__":
    # Clean up any database from previous runs
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    init_db()
    
    print("\n--- Inserting Jobs ---")
    insert_job("Software Engineer", "Tech Corp", "New York", 95000, "https://example.com/job/1")
    insert_job("Data Analyst", "Data Solutions", "San Francisco", 85000, "https://example.com/job/2")
    insert_job("Web Developer", "Creative Agency", "New York", 70000, "https://example.com/job/3")
    
    # Try inserting duplicate URL with a different title/salary
    # This should be skipped because of the UNIQUE(url) constraint
    insert_job("Senior Engineer", "Tech Corp", "New York", 120000, "https://example.com/job/1")
    
    print("\n--- Querying Jobs ---")
    query_jobs_by_city("New York")
    
    print("\n--- Updating Job ---")
    update_job_salary_by_url("https://example.com/job/1", 105000)
    
    print("\n--- Querying Jobs After Update ---")
    query_jobs_by_city("New York")
