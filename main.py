import requests


URL = "https://realpython.github.io/fake-jobs/"


def fetch_html():
    try:
    
        response = requests.get(url=URL, timeout=10)

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


def main():
    print(fetch_html())


if __name__ == "__main__":
    main()