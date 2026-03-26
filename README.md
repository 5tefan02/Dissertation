# Romanian Real Estate ETL Pipeline

## Project Overview
This project is an end-to-end ETL (Extract, Transform, Load) pipeline designed to automate the collection, processing, and storage of real estate listings from major Romanian property platforms (OLX, Imobiliare.ro, Storia). 

Built with Python, the pipeline extracts raw unstructured web data, cleans and formats it, and loads it into a fully normalized PostgreSQL relational database using SQLAlchemy. This project demonstrates practical skills in web scraping, data engineering, relational database architecture, and query optimization.

## Key Features

* **Data Extraction (Web Scraping):** Automated scrapers built using Selenium WebDriver (headless mode) and BeautifulSoup. Bypasses dynamic content loading to fetch accurate listing details (price, area, rooms, location, floor, etc.).
* **Data Transformation (Cleaning & Processing):** Cleans messy web data using Pandas and Regex. Handles missing values, standardizes area metrics (e.g., stripping "m²"), and cleans monetary values.
* **Data Loading & Database Architecture:** Uses SQLAlchemy ORM and raw SQL queries to insert data into a PostgreSQL database. Implements a robust `ON CONFLICT DO NOTHING` strategy to manage duplicate listings. A custom normalization script automatically maps raw flat data into a highly structured relational schema (separating tables for Counties, Cities, Property Types, Transaction Types, etc.).

## Technology Stack

* **Language:** Python 3.12
* **Database:** PostgreSQL
* **ORM & Database Management:** SQLAlchemy, psycopg2
* **Web Scraping:** Selenium, BeautifulSoup4, WebDriver Manager
* **Data Manipulation:** Pandas

## Project Structure

```text

├── Database/
│   ├── db_manager.py          # PostgreSQL connection & SessionLocal setup
│   ├── db_tabels.py           # SQLAlchemy ORM definitions (Base, Tables, Foreign Keys)
│   ├── insert_estates.py      # Logic for bulk inserting raw scraped data
│   └── nomalize_db.py         # SQL transaction script that normalizes raw data into structured tables
├── Scraping/
│   ├── scraper_OLX.py         # Selenium/BS4 scraper for OLX
│   ├── scraper_imobiliarero.py# Selenium/BS4 scraper for Imobiliare.ro
│   └── scraper_storia.py      # Selenium/BS4 scraper for Storia.ro
├── Main.py                    # Main orchestrator (runs scraping -> loading -> normalization)
└── requirements.txt           # Python project dependencies
```

## Database Schema 

The PostgreSQL database is fully normalized to ensure data integrity and avoid redundancy. Key tables include:
* `raw_data`: Temporary landing table for scraped unstructured listings.
* **Reference Tables (Dimensions):** `judete` (Counties), `localitati` (Cities), `tipuri_imobil` (Property Types), `tipuri_tranzactie` (Transaction Types), `compartimentare` (Layouts).
* **Fact Tables:** `anunturi` (Core listing attributes mapped via foreign keys), `istoric_anunturi` (Tracks price drops/increases and listing activity over time).

## Setup & Execution

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd <repo-name>
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure the Database:**
* Ensure PostgreSQL is running on `localhost:5432`.
* Update the credentials in `Database/db_manager.py` (username, password, DB name).

4. **Run the ETL Pipeline:**
```bash
python Main.py
```
*(This will initialize the database schema, scrape the latest listings, insert them into the raw_data table, and automatically execute the normalization script.)*
