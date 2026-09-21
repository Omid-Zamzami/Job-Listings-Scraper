# Python Job Listings Scraper

A lightweight Python web scraper that collects job listings from the [Fake Python Jobs](https://realpython.github.io/fake-jobs/) website and exports the extracted data to a CSV file.

The scraper demonstrates a simple, maintainable workflow for fetching HTML, parsing structured content, handling missing fields, resolving relative URLs, and saving the results as CSV. The project also includes a comprehensive pytest test suite covering the main scraping workflow and common edge cases.

## Features

- Fetch job listing pages with `requests`
- Parse HTML with Beautiful Soup
- Extract:
  - Job title
  - Company name
  - Location
  - Job detail page URL
- Convert relative job URLs into absolute URLs
- Handle missing HTML fields gracefully
- Handle common network errors and HTTP errors
- Export job listings to `jobs.csv`
- Prevent creation of an empty CSV when no jobs are available
- Test scraping, error handling, CSV output, and the main workflow with `pytest`

## Tech Stack

- **Python**
- **Requests** — HTTP requests and webpage retrieval
- **Beautiful Soup 4** — HTML parsing and element selection
- **CSV** — CSV file generation
- **Pytest** — automated testing

## Project Structure

```text
Job-Listings-Scraper/
├── main.py
├── test_main.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

### Main Components

- `fetch_html()` — retrieves the webpage HTML and handles request-related errors.
- `parse_jobs()` — parses job cards and extracts the required job information.
- `save_jobs_to_csv()` — writes the extracted listings to a CSV file.
- `main()` — runs the complete scraping workflow.
- `test_main.py` — contains tests for successful operations, error handling, missing fields, URL handling, CSV output, and workflow control.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Omid-Zamzami/Job-Listings-Scraper.git
cd Job-Listings-Scraper
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Run the scraper with:

```bash
python main.py
```

The program will:

1. Fetch the job listings page.
2. Parse the HTML.
3. Extract the job title, company, location, and application URL for each listing.
4. Save the results to `jobs.csv`.

A successful run prints progress messages similar to:

```text
Fetching HTML content...
Parsing job listings...
Saving job listings to CSV...
Successfully saved 100 job listings to 'jobs.csv'.
```

The exact number of listings may change as the target website's content changes.

## Output

The generated `jobs.csv` file contains the following columns:

| Column | Description |
|---|---|
| `title` | Job title |
| `company` | Company name |
| `location` | Job location |
| `url` | Absolute URL to the job detail/application page |

Example:

```csv
title,company,location,url
Python Developer,Example Company,"Amsterdam, NL",https://realpython.github.io/fake-jobs/jobs/python-developer.html
```

`jobs.csv` is intentionally excluded from version control because it is generated project output.

## Error Handling

The scraper handles several common request failures:

- Request timeout
- Connection error
- HTTP error
- Other `requests` exceptions

If fetching the page fails, the scraper stops before attempting to parse or save data.

The parser also handles incomplete job cards. Missing title, company, location, or application URL fields are represented by empty strings rather than causing the scraper to fail.

## Testing

Run the complete test suite with:

```bash
pytest
```

The tests cover:

- Successful HTTP requests
- Custom URLs
- Request timeouts
- Connection errors
- HTTP errors
- Unexpected request exceptions
- Empty HTML
- Pages without job cards
- Parsing single and multiple job listings
- Missing job fields
- Missing or empty application links
- Relative-to-absolute URL conversion
- CSV creation and contents
- Empty job lists
- Overwriting existing CSV files
- Successful end-to-end workflow execution
- Stopping the workflow when fetching fails

The tests use `pytest`, `monkeypatch`, mocks, and temporary paths so that network requests and filesystem operations can be tested without relying on the live website.

## Repository

**GitHub:** [Omid-Zamzami/Job-Listings-Scraper](https://github.com/Omid-Zamzami/Job-Listings-Scraper)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Omid Zamzami**

- GitHub: [@Omid-Zamzami](https://github.com/Omid-Zamzami)
