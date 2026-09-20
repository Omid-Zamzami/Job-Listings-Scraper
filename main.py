import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

# Base URL of the Fake Python Jobs website for scraping
BASE_URL: str = "https://realpython.github.io/fake-jobs/"


def fetch_html(url: str = BASE_URL) -> str:
    """Fetch the raw HTML content from the specified URL.

    Args:
        url (str): The target URL to fetch HTML from. Defaults to BASE_URL.

    Returns:
        str: The raw HTML content if successful, or an empty string on failure.
    """

    try:
        # Send HTTP GET request with a 10-second timeout
        response = requests.get(url=url, timeout=10)
        # Raise HTTPError if status code indicates an error
        response.raise_for_status()

        return response.text

    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        return ""
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        return ""
    except requests.exceptions.HTTPError as error:
        print(f"HTTP Error occurred: {error}")
        return ""
    except requests.exceptions.RequestException as error:
        print(f"An unexpected network error occurred: {error}")
        return ""


def parse_jobs(html: str) -> list[dict[str, str]]:
    """Parse job listings from raw HTML content using BeautifulSoup.

    Extracts job title, company name, location, and the apply URL.

    Args:
        html (str): Raw HTML content of the job listings page.

    Returns:
        list[dict[str, str]]: A list of dictionaries containing job details.
    """

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    jobs: list[dict[str, str]] = []

    # Select all job posting card elements from the page
    job_cards = soup.select(".card-content")

    for job in job_cards:
        # Extract individual HTML elements for each field
        title_element = job.select_one(".title.is-5")
        company_element = job.select_one(".subtitle.is-6.company")
        location_element = job.select_one(".location")
        link_element = job.find("a", string="Apply")

        # Extract text content safely or fallback to empty string
        title: str = title_element.get_text(strip=True) if title_element else ""
        company: str = company_element.get_text(strip=True) if company_element else ""
        location: str = location_element.get_text(strip=True) if location_element else ""
        href: str = link_element.get("href") if link_element else ""

        # Resolve relative URLs to absolute URLs
        url: str = urljoin(BASE_URL, href) if href else ""

        # Construct job data dictionary
        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "url": url
            }
        )

    return jobs


def save_jobs_to_csv(jobs: list[dict[str, str]], filename: str = "jobs.csv") -> None:
    """Save a list of job dictionaries to a CSV file.

    Args:
        jobs (list[dict[str, str]]): List of job listing dictionaries.
        filename (str): Name of the target CSV file. Defaults to 'jobs.csv'.
    """

    if not jobs:
        print("No job listings found to save.")
        return

    # Define the header column names for the CSV file
    fieldnames: list[str] = ["title", "company", "location", "url"]

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(jobs)

    print(f"Successfully saved {len(jobs)} job listings to '{filename}'.")


def main() -> None:
    """Execute the job listings scraper workflow."""

    print("Fetching HTML content...")
    html_data: str = fetch_html()

    if not html_data:
        print("Failed to retrieve web content. Exiting execution.")
        return

    print("Parsing job listings...")
    jobs: list[dict[str, str]] = parse_jobs(html_data)

    print("Saving job listings to CSV...")
    save_jobs_to_csv(jobs)


if __name__ == "__main__":
    main()