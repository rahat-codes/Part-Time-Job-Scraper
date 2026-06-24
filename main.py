# Job listings database stored as a list of dictionaries.
# Each dictionary represents a job with keys: 'title', 'company', 'city', and 'salary'.
job_listings = [
    {"title": "Software Engineer", "company": "Tech Corp", "city": "New York", "salary": 95000},
    {"title": "Data Analyst", "company": "Data Solutions", "city": "San Francisco", "salary": 85000},
    {"title": "Web Developer", "company": "Creative Agency", "city": "New York", "salary": 70000},
    {"title": "Product Manager", "company": "Innovate LLC", "city": "Boston", "salary": 110000},
    {"title": "QA Engineer", "company": "Quality First", "city": "Boston", "salary": 65000}
]

def display_jobs(jobs):
    """Prints a formatted list of jobs."""
    if not jobs:
        print("\nNo jobs found matching the criteria.")
        return
    
    print(f"\n{'#' * 60}")
    # Iterate through the list of jobs and display each job's details
    for idx, job in enumerate(jobs, 1):
        print(f"Job #{idx}:")
        print(f"  Title:      {job['title']}")
        print(f"  Company:    {job['company']}")
        print(f"  City:       {job['city']}")
        print(f"  Salary:     ${job['salary']:,}")
        print("-" * 30)
    print(f"{'#' * 60}")

def search_by_city(city_name):
    """Filters and returns jobs matching a specific city (case-insensitive)."""
    # Use list comprehension to filter jobs by checking if the input city is in the job's city key.
    # .strip().lower() is used to ensure a case-insensitive, whitespace-trimmed comparison.
    matching_jobs = [
        job for job in job_listings 
        if job['city'].strip().lower() == city_name.strip().lower()
    ]
    return matching_jobs

def search_by_min_salary(min_salary):
    """Filters and returns jobs with a salary greater than or equal to min_salary."""
    # Use list comprehension to filter jobs that meet or exceed the specified minimum salary.
    matching_jobs = [
        job for job in job_listings 
        if job['salary'] >= min_salary
    ]
    return matching_jobs

def add_job():
    """Prompts the user for job details and appends it to the listings."""
    print("\n--- Add a New Job Listing ---")
    title = input("Enter Job Title: ").strip()
    company = input("Enter Company Name: ").strip()
    city = input("Enter City: ").strip()
    
    # Input validation loop for the salary to ensure the user enters a valid number
    while True:
        salary_str = input("Enter Annual Salary: ").strip()
        try:
            salary = int(salary_str)
            if salary < 0:
                print("Salary cannot be negative. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid salary format. Please enter a valid number (e.g., 75000).")
            
    # Create the job dictionary and append it to our in-memory list
    new_job = {
        "title": title,
        "company": company,
        "city": city,
        "salary": salary
    }
    job_listings.append(new_job)
    print(f"\nJob listing for '{title}' at '{company}' added successfully!")

def main():
    """Main loop for the console application menu."""
    while True:
        print("\n=== Job Board Console Application ===")
        print("1. View All Job Listings")
        print("2. Search Jobs by City")
        print("3. Search Jobs by Minimum Salary")
        print("4. Add a New Job Listing")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            display_jobs(job_listings)
        elif choice == '2':
            city = input("Enter the city to search for: ")
            results = search_by_city(city)
            print(f"\nSearch results for jobs in '{city}':")
            display_jobs(results)
        elif choice == '3':
            # Input validation to ensure a valid numeric minimum salary
            while True:
                min_salary_str = input("Enter the minimum salary to filter by: ").strip()
                try:
                    min_salary = int(min_salary_str)
                    break
                except ValueError:
                    print("Please enter a valid number for the salary.")
            results = search_by_min_salary(min_salary)
            print(f"\nSearch results for jobs with salary >= ${min_salary:,}:")
            display_jobs(results)
        elif choice == '4':
            add_job()
        elif choice == '5':
            print("\nThank you for using the Job Board Console Application. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")

# Standard Python boilerplate to run the main function when script is executed directly
if __name__ == "__main__":
    main()