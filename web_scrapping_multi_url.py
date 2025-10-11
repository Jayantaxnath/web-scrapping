import requests
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import csv
import time  # Add time for delays
import os  # Add os for file operations

# MAX_PAGES_TO_SCRAPE = 5   # ~255 internships
# MAX_PAGES_TO_SCRAPE = 10  # ~510 internships  
# MAX_PAGES_TO_SCRAPE = 20  # ~1,020 internships
# MAX_PAGES_TO_SCRAPE = 71  # All ~3,600 internships
MAX_PAGES_TO_SCRAPE = 2  # Change this to 5, 10, 20, etc. as needed


try:
    # List of URLs to scrape with separate CSV files for each
    urls = [
        # "https://internshala.com/internships/work-from-home-internships",
        # "https://internshala.com/internships/internship-in-bangalore",
        # "https://internshala.com/internships/internship-in-delhi",
        # "https://internshala.com/internships/internship-in-hyderabad",
        # "https://internshala.com/internships/internship-in-mumbai",
        # "https://internshala.com/internships/internship-in-chennai",
        # "https://internshala.com/internships/internship-in-pune",
        # "https://internshala.com/internships/internship-in-kolkata",
        "https://internshala.com/internships/internship-in-jaipur",
    ]
    
    # Function to extract city name from URL for CSV filename
    def get_csv_filename(url):
        if "work-from-home" in url:
            return "work-from-home.csv"
        elif "internship-in-" in url:
            city = url.split("internship-in-")[-1]
            return f"{city}.csv"
        else:
            return "internships.csv"
    
    # Process each URL separately
    for url_index, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"Processing URL {url_index}/{len(urls)}: {url}")
        print(f"{'='*60}")
        
        # Generate CSV filename for this URL
        csv_filename = get_csv_filename(url)

        # Use requests to get the initial page content
        page_content = requests.get(url)
        page_beautify = bs4(page_content.text, "html.parser")

        # The total pages element has a new structure
        # This selector is now required to find the last page number
        try:
            # Look for pagination_desktop class instead of pagination
            pagination_div = page_beautify.find("div", {"class": "pagination_desktop"})
            if pagination_div:
                # Find all pagination links and get the highest page number
                page_links = pagination_div.find_all("a")
                page_numbers = []
                for link in page_links:
                    text = link.text.strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                
                if page_numbers:
                    total_no_pages = max(page_numbers)
                    # Use the configured maximum pages
                    total_no_pages = min(total_no_pages, MAX_PAGES_TO_SCRAPE)
                else:
                    total_no_pages = MAX_PAGES_TO_SCRAPE
            else:
                total_no_pages = MAX_PAGES_TO_SCRAPE
        except (AttributeError, IndexError):
            total_no_pages = MAX_PAGES_TO_SCRAPE  # Fallback to configured pages if pagination isn't found

        profiles = []

        print(f"Starting to scrape {total_no_pages} pages for {csv_filename}...")

        for i in range(1, total_no_pages + 1):
            print(f"Scraping page {i}/{total_no_pages}...")
            next_page_url = f"{url}/page-{i}"
            next_page_content = requests.get(next_page_url)
            beautify_nextPage = bs4(next_page_content.text, "html.parser")
            
            # Use the correct class for individual internship boxes
            big_boxes = beautify_nextPage.find_all("div", {"class": "individual_internship"})

            for box in big_boxes:
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%d %H:%M:%S")

                try:
                    # Updated selector for profile - it's in h3 with class job-internship-name
                    profile = box.find("h3", {"class": "job-internship-name"}).text.strip()
                except AttributeError:
                    profile = "Nothing"

                try:
                    # Updated selector for company name - clean up the text
                    company_element = box.find("div", {"class": "heading_6 company_name"})
                    if company_element:
                        company = company_element.text.strip().split('\n')[0].strip()
                    else:
                        company = "Nothing"
                except AttributeError:
                    company = "Nothing"
                
                try:
                    # Location - extract from proper location div structure
                    location = "Not Available"
                    
                    # First try to find location in the locations class div
                    location_div = box.find("div", {"class": "row-1-item locations"})
                    if location_div:
                        location_span = location_div.find("span")
                        if location_span:
                            location_link = location_span.find("a")
                            if location_link:
                                location_text = location_link.text.strip()
                                # If multiple locations, take only the first one
                                if ',' in location_text:
                                    location = location_text.split(',')[0].strip()
                                else:
                                    location = location_text
                            else:
                                location_text = location_span.text.strip()
                                # If multiple locations, take only the first one
                                if ',' in location_text:
                                    location = location_text.split(',')[0].strip()
                                else:
                                    location = location_text
                    
                    # Fallback: look for "Work from home" text if not found above
                    if location == "Not Available":
                        work_from_home_span = box.find("span", text="Work from home")
                        if work_from_home_span:
                            location = "Work from home"
                        else:
                            # Try to find any location information in the box text
                            box_text = box.get_text()
                            if 'work from home' in box_text.lower():
                                location = "Work from home"
                            else:
                                # Look for common city names
                                cities = ['Mumbai', 'Delhi', 'Bangalore', 'Bengaluru', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata', 'Ahmedabad', 'Gurgaon', 'Noida']
                                for city in cities:
                                    if city.lower() in box_text.lower():
                                        location = city
                                        break
                except AttributeError:
                    location = "Not Available"

                try:
                    # Start date - look for "Immediately" or specific date patterns
                    start_date = "Not Available"
                    box_text = box.get_text().replace('₹', 'Rs.')
                    if 'immediately' in box_text.lower():
                        start_date = "Immediately"
                    else:
                        # Look for date patterns in detail page later
                        start_date = "Not Available"
                except AttributeError:
                    start_date = "Not Available"

                try:
                    # Stipend - look for rupee symbol or "Unpaid"
                    stipend = "Not Available"
                    box_text = box.get_text()
                    lines = box_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        # Fix encoding issues with rupee symbol
                        line = line.replace('â‚¹', '₹').replace('Rs.', '₹')
                        if "₹" in line and ("month" in line.lower() or "week" in line.lower() or "lump sum" in line.lower()):
                            stipend = line
                            break
                        elif "unpaid" in line.lower() and len(line) < 20:
                            stipend = "Unpaid"
                            break
                except AttributeError:
                    stipend = "Not Available"

                try:
                    # Duration - extract from text, exclude stipend lines
                    duration = "Not Available"
                    box_text = box.get_text().replace('₹', 'Rs.')
                    lines = box_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        # Look for duration patterns that don't contain currency
                        if any(word in line.lower() for word in ['month', 'week']) and 'rs.' not in line.lower():
                            if any(duration_word in line.lower() for duration_word in ['1 month', '2 month', '3 month', '4 month', '5 month', '6 month', '1 week', '2 week', '3 week', '4 week']):
                                duration = line
                                break
                except AttributeError:
                    duration = "Not Available"

                try:
                    # Apply by date - will extract from detail page
                    apply_by_date = "Not Available"
                except AttributeError:
                    apply_by_date = "Not Available"

                offer = "Nothing"

                try:
                    # Detail link is in data-href attribute
                    detail_link = box.get('data-href')
                    if detail_link:
                        # Add delay to avoid being blocked
                        time.sleep(0.5)
                        detail_page_url = "https://internshala.com" + detail_link
                        
                        try:
                            detail_page_content = requests.get(detail_page_url, timeout=10)
                            beautify_detail_page = bs4(detail_page_content.text, "html.parser")
                            
                            # Skills and Perks - look for different sections
                            skills_list = []
                            perks_list = []
                            
                            # Better approach: look for "Skill(s) required" section
                            page_text = beautify_detail_page.get_text()
                            lines = page_text.split('\n')
                            
                            for i, line in enumerate(lines):
                                line = line.strip()
                                if "skill(s) required" in line.lower():
                                    # Look at the next few lines for actual skills
                                    for j in range(1, 10):
                                        if i + j < len(lines):
                                            next_line = lines[i + j].strip()
                                            if next_line and len(next_line) > 2 and len(next_line) < 50:
                                                # Skip common non-skill lines
                                                if not any(skip in next_line.lower() for skip in ['learn', 'earn', 'certificate', 'who can apply', 'other requirements', 'only those', 'candidates']):
                                                    skills_list.append(next_line)
                                            if len(skills_list) >= 8 or "who can apply" in next_line.lower():
                                                break
                                    break
                            
                            # Look for perks separately
                            perk_keywords = ['certificate', 'flexible', 'letter of recommendation', 'mentorship', '5 days a week']
                            for keyword in perk_keywords:
                                if keyword.lower() in page_text.lower():
                                    perks_list.append(keyword.title())
                            
                            # Convert lists to strings for CSV compatibility
                            skills_text = ', '.join(skills_list) if skills_list else "Not Available"
                            perks_text = ', '.join(perks_list) if perks_list else "Not Available"
                            
                            # Better extraction of dates and duration from detail page
                            page_text_clean = page_text.replace('₹', 'Rs.')
                            lines = [line.strip() for line in page_text_clean.split('\n') if line.strip()]
                            
                        except Exception as detail_error:
                            print(f"Error accessing detail page: {detail_error}")
                            skills_text = "Not Available"
                            perks_text = "Not Available"
                            education = "Not Specified"
                        
                        # Improve start date extraction
                        if start_date == "Not Available":
                            for line in lines:
                                if 'immediately' in line.lower() and len(line) < 30:
                                    start_date = "Immediately"
                                    break
                                elif any(month in line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) and 'start' in line.lower():
                                    start_date = line
                                    break
                        
                        # Improve duration extraction
                        if duration == "Not Available":
                            for line in lines:
                                if line.lower().strip() in ['1 month', '2 months', '3 months', '4 months', '5 months', '6 months', '1 week', '2 weeks', '3 weeks', '4 weeks']:
                                    duration = line
                                    break
                                elif 'duration of' in line.lower() and any(word in line.lower() for word in ['month', 'week']):
                                    # Extract duration from "duration of X months" pattern
                                    words = line.split()
                                    for i, word in enumerate(words):
                                        if word.lower() == 'of' and i + 1 < len(words):
                                            duration_part = ' '.join(words[i+1:i+3])
                                            if any(time_word in duration_part.lower() for time_word in ['month', 'week']):
                                                duration = duration_part
                                                break
                        
                        # Extract apply by date
                        for line in lines:
                            if 'apply by' in line.lower() and any(month in line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                                apply_by_date = line.replace('APPLY BY', '').strip()
                                break
                            elif any(month in line for month in ['Oct', 'Nov', 'Dec', 'Jan', 'Feb']) and any(char.isdigit() for char in line) and len(line) < 20:
                                apply_by_date = line
                                break
                        
                        # Education requirements - simplified approach
                        education = "Not Specified"
                        
                        # Only look for very clear, numbered education requirements
                        page_text = beautify_detail_page.get_text()
                        lines = page_text.split('\n')
                        
                        for line in lines:
                            line_clean = line.strip()
                            # Look for numbered education requirements that are clearly educational
                            if (line_clean.startswith(('1.', '2.', '3.', '4.', '5.')) and
                                len(line_clean) > 25 and
                                any(edu_word in line_clean.lower() for edu_word in 
                                    ['bachelor', 'master', 'degree', 'graduate', 'diploma', 'pursuing', 'student', 'mba', 'bba', 'b.tech', 'llb'])):
                                education = line_clean
                                break
                    else:
                        skills_text = "Not Available"
                        perks_text = "Not Available"
                        education = "Not Specified"
                except (AttributeError, KeyError, IndexError):
                    skills_text = "Not Available"
                    perks_text = "Not Available"
                    education = "Not Specified"

                myDict = {
                    "Date Time": date_time,
                    "profile": profile,
                    "company": company,
                    "Location": location,
                    "Start Date": start_date,
                    "Stipend": stipend,
                    'Duration': duration,
                    'Apply by Date': apply_by_date,
                    "Offer": offer,
                    "Education": education,
                    "Skills": skills_text,
                    "Perks": perks_text,
                }
                profiles.append(myDict)

        print(f"Scraped {len(profiles)} internships from {csv_filename}")
        
        # CSV saving - always overwrite existing file for this URL
        if profiles:
            header = profiles[0].keys()
            
            # Try multiple attempts to handle file locks
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Always overwrite the file with new data (UTF-8 with BOM for Excel compatibility)
                    with open(csv_filename, "w", newline="", encoding="utf-8-sig") as file:
                        writer = csv.DictWriter(file, fieldnames=header)
                        writer.writeheader()
                        writer.writerows(profiles)
                    
                    print(f"Data successfully saved in {csv_filename} with {len(profiles)} records")
                    break
                except PermissionError as pe:
                    if attempt < max_attempts - 1:
                        print(f"File is locked, retrying in 2 seconds... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(2)
                    else:
                        print(f"Error: Could not save CSV file after {max_attempts} attempts. Please close {csv_filename} in VS Code and try again.")
                        print(f"Permission error: {pe}")
                except Exception as e:
                    print(f"Unexpected error saving CSV: {e}")
                    break
        else:
            print(f"No data was scraped for {csv_filename}")

except Exception as e:
    print(f"Error: {e}")