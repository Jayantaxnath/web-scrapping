# Internshala Web Scraper & Data Analysis

A comprehensive web scraping project for collecting and analyzing internship data from Internshala across multiple Indian cities.

## Project Overview

This project scrapes internship listings from Internshala and performs detailed exploratory data analysis (EDA) to uncover insights about the internship market in India. The scraper collects data from major cities and remote work opportunities.

## Features

- **Multi-city Web Scraping**: Automated data collection from 8+ major Indian cities
- **Remote Opportunities**: Work-from-home internship data collection  
- **Data Processing**: Clean and merge datasets from multiple sources
- **Comprehensive EDA**: Statistical analysis and visualizations
- **Robust Scraping**: Retry mechanisms and error handling for reliable data collection

## Dataset Coverage

### Cities Covered:
- Bangalore, Chennai, Delhi, Hyderabad, Jaipur, Kolkata, Mumbai, Pune, Work-from-home positions

### Data Fields:
- Internship Profile | Company Name | Location | Stipend Range | Duration | Start Date | Application Deadline | Required Skills | Educational Requirements | Perks & Benefits

## Technology Stack 🛠️

- **Python 3.x**
- **BeautifulSoup4**: HTML parsing and web scraping
- **Requests**: HTTP requests with retry mechanisms
- **Pandas**: Data manipulation and analysis
- **Matplotlib & Seaborn**: Data visualization
- **NumPy**: Numerical computations

## Project Structure

```
├── web_scrapping.py              # Main scraping script
├── web_scrapping_multi_url.py    # Multi-URL batch scraper
├── eda_internship_data.ipynb     # Comprehensive data analysis
├── preprocess.ipynb              # Data preprocessing pipeline
├── merged_internships_dataset.csv # Final consolidated dataset
├── requirements.txt              # Python dependencies
├── internship/                   # Individual city datasets
│   ├── bangalore.csv
│   ├── delhi.csv
│   ├── mumbai.csv
│   └── ...
└── url.txt                       # Target URLs for scraping
```

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Web Scraper
```python
python web_scrapping.py
```

### 4. Data Analysis
Open and run `eda_internship_data.ipynb` in Jupyter Notebook

The analysis reveals trends in:
- Stipend distributions across cities
- Most in-demand skills
- Company hiring patterns
- Seasonal internship availability
- Remote vs. on-site opportunities

## Configuration ⚙️

Modify scraping parameters in the scripts:
- `MAX_PAGES_TO_SCRAPE`: Control data volume
- `urls`: Target specific cities or regions
- `timeout`: Adjust request timeout settings

## Features

- Exponential backoff retry mechanism
- Request timeout handling
- Error logging and recovery
- Automatic CSV generation per city
- Data merging and consolidation
- Duplicate handling and cleaning

## Contributing 🤝

Feel free to submit issues, fork the repository, and create pull requests for improvements.

---

*For questions or collaboration opportunities, feel free to reach out!*