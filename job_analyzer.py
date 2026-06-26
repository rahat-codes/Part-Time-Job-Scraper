from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
import os
import json

# Define the structured output format using Pydantic
class JobAnalysis(BaseModel):
    skills: list[str] = Field(description="Key technical or soft skills extracted from the description.")
    experience_level: str = Field(description="Expected experience level (e.g., Entry-level, Mid-level, Senior-level).")
    suitability_for_students: str = Field(description="Is this job suitable for college/university students? Yes/No/Maybe with a brief reason.")

def analyze_job_url(url):
    """Fetches job description from URL and uses Gemini API to perform structured analysis."""
    # 1. Fetch the description text from the job details page
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching page ({response.status_code})")
            return None
    except Exception as e:
        print(f"Network error fetching job page: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find(class_="content")
    if not content_div:
        print("Error: Could not find job description element on page.")
        return None

    # Extract clean description text (splitting before the Location/Posted metadata)
    raw_desc = content_div.text.split("Location:")[0].strip()
    
    # 2. Check for Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[Warning] GEMINI_API_KEY is not set. Using mock Gemini analysis output.")
        # Provide fallback/mock data for demo if API key isn't provided
        return {
            "skills": ["Python", "CSS", "Agile/SCRUM", "Django"],
            "experience_level": "Entry-level (willingness to learn mentioned)",
            "suitability_for_students": "Yes - suitable due to entry-level requirements and supportive educational environment."
        }

    # 3. Call the Gemini API with Structured Outputs (gemini-2.5-flash)
    print("Sending job description to Gemini (gemini-2.5-flash)...")
    client = genai.Client()
    
    prompt = f"""
    Please analyze this job description and extract structured information:
    
    Job Description:
    {raw_desc}
    """
    
    try:
        result = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobAnalysis,
            ),
        )
        # The result.text is guaranteed to match the JobAnalysis schema exactly
        return json.loads(result.text)
    except Exception as e:
        print(f"Gemini API execution error: {e}")
        return None

# ==============================================================================
# Demonstration Loop
# ==============================================================================
if __name__ == "__main__":
    test_url = "https://realpython.github.io/fake-jobs/jobs/senior-python-developer-0.html"
    print(f"Testing Job Analyzer on URL: {test_url}\n")
    
    analysis = analyze_job_url(test_url)
    if analysis:
        print("\n--- Extracted Analysis Results ---")
        print(json.dumps(analysis, indent=4))
