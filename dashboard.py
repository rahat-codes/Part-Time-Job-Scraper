import streamlit as st
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import os

DB_FILE = "jobs.db"

# Page config for high-end look
st.set_page_config(
    page_title="Apex Careers | Premium Job Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using CSS injection
st.markdown("""
<style>
    /* Main body background & color adjustment */
    .stApp {
        background-color: #0e1117;
        color: #e2e8f0;
    }
    
    /* Header typography */
    h1 {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.8em !important;
        margin-bottom: 5px !important;
    }
    
    h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #ffffff;
    }
    
    /* Sidebar styled container */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Metric Card Styling */
    div[data-testid="metric-container"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        padding: 15px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    }
    
    /* Custom job card layout styling */
    .job-card {
        border-radius: 12px;
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
        border: 1px solid #374151;
        border-left: 6px solid #4facfe;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .job-card:hover {
        transform: translateY(-3px);
        border-color: #00f2fe;
    }
    .job-title {
        color: #ffffff;
        font-size: 1.35em;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .job-company {
        color: #00f2fe;
        font-weight: 600;
        font-size: 1.05em;
        margin: 0 0 12px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .job-meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #9ca3af;
        font-size: 0.95em;
        margin-top: 10px;
    }
    .job-salary {
        color: #34d399;
        font-weight: bold;
        font-size: 1.15em;
    }
    .job-tag {
        background-color: #374151;
        color: #9ca3af;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# Database & Scraping Integration Helper Functions
# ==============================================================================
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

def get_job_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def scrape_and_populate_db():
    """Scrapes 100 jobs and populates DB if it is empty."""
    st.info("Populating database with jobs from realpython.github.io...")
    
    url = "https://realpython.github.io/fake-jobs/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("div", class_="card-content")
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            for idx, card in enumerate(job_cards):
                title_el = card.find("h2", class_="title is-5")
                company_el = card.find("h3", class_="subtitle is-6 company")
                location_el = card.find("p", class_="location")
                
                # Fetch apply link
                links = card.find_all("a")
                apply_url = links[1]["href"] if len(links) > 1 else f"https://example.com/job/{idx}"
                
                if title_el and company_el and location_el:
                    title = title_el.text.strip()
                    company = company_el.text.strip()
                    city = location_el.text.strip()
                    # Generate a random realistic salary ($40,000 - $160,000)
                    salary = random.randint(8, 32) * 5000 
                    
                    cursor.execute("""
                    INSERT OR IGNORE INTO jobs (title, company, city, salary, url)
                    VALUES (?, ?, ?, ?, ?)
                    """, (title, company, city, salary, apply_url))
            
            conn.commit()
            conn.close()
            st.success("Successfully populated database with 100 jobs!")
    except Exception as e:
        st.error(f"Error scraping initial job listings: {e}")

# ==============================================================================
# Dashboard Main Application Flow
# ==============================================================================
init_db()

# Check if we need to pre-fill jobs in the DB
if get_job_count() == 0:
    scrape_and_populate_db()

# Connect to database and retrieve data
conn = sqlite3.connect(DB_FILE)
df = pd.read_sql_query("SELECT * FROM jobs", conn)
conn.close()

# App Header
st.markdown("<h1>APEX CAREERS</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af; font-size: 1.2em; margin-bottom: 30px;'>Scraped Job Listings Real-time Intelligence Dashboard</p>", unsafe_allow_html=True)

# ----------------- SIDEBAR FILTERS -----------------
st.sidebar.markdown("<h3 style='margin-top:0;'>🔍 Filter Listings</h3>", unsafe_allow_html=True)

# Text Search
search_term = st.sidebar.text_input("Search Title or Company", "").strip()

# Location Filter
cities_available = sorted(df['city'].dropna().unique())
selected_cities = st.sidebar.multiselect("Select Cities", options=cities_available)

# Salary Filter
min_sal_db = int(df['salary'].min()) if not df.empty else 0
max_sal_db = int(df['salary'].max()) if not df.empty else 200000
salary_threshold = st.sidebar.slider(
    "Minimum Salary ($)", 
    min_value=min_sal_db, 
    max_value=max_sal_db, 
    value=min_sal_db,
    step=5000
)

# Apply filters to dataframe
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(search_term, case=False, na=False) |
        filtered_df['company'].str.contains(search_term, case=False, na=False)
    ]

if selected_cities:
    filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]

filtered_df = filtered_df[filtered_df['salary'] >= salary_threshold]

# ----------------- METRICS ROW -----------------
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric("Total Jobs Listed", len(df))
with m_col2:
    st.metric("Matching Filters", len(filtered_df))
with m_col3:
    avg_salary = int(filtered_df['salary'].mean()) if not filtered_df.empty else 0
    st.metric("Average Salary of Matches", f"${avg_salary:,}" if avg_salary else "N/A")

st.markdown("---")

# ----------------- MAIN DISPLAY -----------------
if filtered_df.empty:
    st.warning("No job listings match your current filters. Try relaxing them in the sidebar.")
else:
    # Split into 2 columns for card layout grid
    grid_col1, grid_col2 = st.columns(2)
    
    # Iterate through matching jobs and render as beautiful custom cards
    for idx, row in enumerate(filtered_df.itertuples()):
        # Determine column placing
        target_col = grid_col1 if idx % 2 == 0 else grid_col2
        
        with target_col:
            # Styled Card using injected html/css
            st.markdown(f"""
            <div class="job-card">
                <div class="job-title">{row.title}</div>
                <div class="job-company">🏢 {row.company}</div>
                <div class="job-meta-row">
                    <span>📍 {row.city}</span>
                    <span class="job-salary">${row.salary:,}</span>
                </div>
                <div class="job-meta-row" style="margin-top: 15px;">
                    <span class="job-tag">SQLite ID: {row.id}</span>
                    <a href="{row.url}" target="_blank" style="text-decoration: none; color: #4facfe; font-weight:600;">Apply Now ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
