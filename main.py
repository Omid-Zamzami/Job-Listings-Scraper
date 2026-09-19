import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://realpython.github.io/fake-jobs/"


def fetch_html():
    try:
        response = requests.get(url=BASE_URL, timeout=10)

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


def parse_jobs(html):
    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    job_cards = soup.select(".card-content")

    for job in job_cards:
        title_element = job.select_one(".title.is-5")
        company_element = job.select_one(".subtitle.is-6.company")
        location_element = job.select_one(".location")
        link_element = job.find("a", string="Apply")

        title = title_element.get_text(strip=True) if title_element else ""
        company = company_element.get_text(strip=True) if company_element else ""
        location = location_element.get_text(strip=True) if location_element else ""
        href = link_element.get("href") if link_element else ""

        url = urljoin(BASE_URL, href) if href else ""

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "url": url
            }
        )

    return jobs


def main():
    data = fetch_html()

    jobs = parse_jobs(data)
    print(jobs)


if __name__ == "__main__":
    main()