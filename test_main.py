from pathlib import Path
from unittest.mock import Mock
import csv
import pytest
import requests
import main


# Sample HTML containing one complete job listing.
SAMPLE_HTML: str = """
<div class="card-content">
    <h2 class="title is-5">Python Developer</h2>
    <h3 class="subtitle is-6 company">Example Company</h3>
    <p class="location">Amsterdam, NL</p>
    <a href="jobs/python-developer-1.html">Apply</a>
</div>
"""


def test_fetch_html_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that fetch_html returns the response text on success."""

    mock_response: Mock = Mock()
    mock_response.text = "<html>Test page</html>"
    mock_response.raise_for_status.return_value = None

    mock_get: Mock = Mock(return_value=mock_response)
    monkeypatch.setattr(main.requests, "get", mock_get)

    result: str = main.fetch_html()

    assert result == "<html>Test page</html>"
    mock_get.assert_called_once_with(
        url=main.BASE_URL,
        timeout=10,
    )
    mock_response.raise_for_status.assert_called_once()


def test_fetch_html_with_custom_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that fetch_html uses a custom URL when provided."""

    custom_url: str = "https://example.com/jobs"

    mock_response: Mock = Mock()
    mock_response.text = "<html>Custom page</html>"
    mock_response.raise_for_status.return_value = None

    mock_get: Mock = Mock(return_value=mock_response)
    monkeypatch.setattr(main.requests, "get", mock_get)

    result: str = main.fetch_html(custom_url)

    assert result == "<html>Custom page</html>"
    mock_get.assert_called_once_with(
        url=custom_url,
        timeout=10,
    )


def test_fetch_html_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that fetch_html handles request timeouts."""

    mock_get: Mock = Mock(
        side_effect=requests.exceptions.Timeout
    )
    monkeypatch.setattr(main.requests, "get", mock_get)

    result: str = main.fetch_html()

    assert result == ""


def test_fetch_html_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that fetch_html handles connection errors."""

    mock_get: Mock = Mock(
        side_effect=requests.exceptions.ConnectionError
    )
    monkeypatch.setattr(main.requests, "get", mock_get)

    result: str = main.fetch_html()

    assert result == ""


def test_fetch_html_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that fetch_html handles HTTP errors."""

    mock_response: Mock = Mock()
    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("404 Not Found")
    )

    mock_get: Mock = Mock(return_value=mock_response)
    monkeypatch.setattr(main.requests, "get", mock_get)

    result: str = main.fetch_html()

    assert result == ""
    mock_response.raise_for_status.assert_called_once()


def test_fetch_html_request_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that fetch_html handles unexpected request exceptions."""

    mock_get: Mock = Mock(
        side_effect=requests.exceptions.RequestException(
            "Unexpected request error"
        )
    )
    monkeypatch.setattr(main.requests, "get", mock_get)

    result: str = main.fetch_html()

    assert result == ""


def test_parse_jobs_empty_html() -> None:
    """Test that parse_jobs returns an empty list for empty HTML."""

    result: list[dict[str, str]] = main.parse_jobs("")

    assert result == []


def test_parse_jobs_without_job_cards() -> None:
    """Test that parse_jobs returns an empty list when no jobs exist."""

    html: str = """
    <html>
        <body>
            <h1>No jobs</h1>
        </body>
    </html>
    """

    result: list[dict[str, str]] = main.parse_jobs(html)

    assert result == []


def test_parse_jobs_single_job() -> None:
    """Test parsing a complete single job listing."""

    result: list[dict[str, str]] = main.parse_jobs(SAMPLE_HTML)

    expected: list[dict[str, str]] = [
        {
            "title": "Python Developer",
            "company": "Example Company",
            "location": "Amsterdam, NL",
            "url": (
                "https://realpython.github.io/fake-jobs/"
                "jobs/python-developer-1.html"
            ),
        }
    ]

    assert result == expected


def test_parse_jobs_multiple_jobs() -> None:
    """Test parsing multiple job listings."""

    html: str = """
    <div class="card-content">
        <h2 class="title is-5">Python Developer</h2>
        <h3 class="subtitle is-6 company">Company One</h3>
        <p class="location">Amsterdam, NL</p>
        <a href="jobs/python-developer.html">Apply</a>
    </div>

    <div class="card-content">
        <h2 class="title is-5">Data Engineer</h2>
        <h3 class="subtitle is-6 company">Company Two</h3>
        <p class="location">Rotterdam, NL</p>
        <a href="jobs/data-engineer.html">Apply</a>
    </div>
    """

    result: list[dict[str, str]] = main.parse_jobs(html)

    assert len(result) == 2

    assert result[0]["title"] == "Python Developer"
    assert result[0]["company"] == "Company One"
    assert result[0]["location"] == "Amsterdam, NL"
    assert result[0]["url"] == (
        "https://realpython.github.io/fake-jobs/"
        "jobs/python-developer.html"
    )

    assert result[1]["title"] == "Data Engineer"
    assert result[1]["company"] == "Company Two"
    assert result[1]["location"] == "Rotterdam, NL"
    assert result[1]["url"] == (
        "https://realpython.github.io/fake-jobs/"
        "jobs/data-engineer.html"
    )


@pytest.mark.parametrize(
    ("missing_selector", "expected_key"),
    [
        (".title.is-5", "title"),
        (".subtitle.is-6.company", "company"),
        (".location", "location"),
    ],
)
def test_parse_jobs_missing_text_field(
    missing_selector: str,
    expected_key: str,
) -> None:
    """Test that missing text fields are replaced with empty strings."""

    html: str = """
    <div class="card-content">
        <h2 class="title is-5">Python Developer</h2>
        <h3 class="subtitle is-6 company">Example Company</h3>
        <p class="location">Amsterdam, NL</p>
        <a href="jobs/python-developer.html">Apply</a>
    </div>
    """

    elements: dict[str, str] = {
        ".title.is-5": (
            '<h2 class="title is-5">Python Developer</h2>'
        ),
        ".subtitle.is-6.company": (
            '<h3 class="subtitle is-6 company">'
            "Example Company"
            "</h3>"
        ),
        ".location": '<p class="location">Amsterdam, NL</p>',
    }

    soup_html: str = html.replace(
        elements[missing_selector],
        "",
    )

    result: list[dict[str, str]] = main.parse_jobs(soup_html)

    assert len(result) == 1
    assert result[0][expected_key] == ""


def test_parse_jobs_missing_apply_link() -> None:
    """Test that a missing Apply link produces an empty URL."""

    html: str = """
    <div class="card-content">
        <h2 class="title is-5">Python Developer</h2>
        <h3 class="subtitle is-6 company">Example Company</h3>
        <p class="location">Amsterdam, NL</p>
    </div>
    """

    result: list[dict[str, str]] = main.parse_jobs(html)

    assert len(result) == 1
    assert result[0]["url"] == ""


def test_parse_jobs_relative_url() -> None:
    """Test that relative job URLs are converted to absolute URLs."""

    html: str = """
    <div class="card-content">
        <h2 class="title is-5">Python Developer</h2>
        <h3 class="subtitle is-6 company">Example Company</h3>
        <p class="location">Amsterdam, NL</p>
        <a href="jobs/python-developer.html">Apply</a>
    </div>
    """

    result: list[dict[str, str]] = main.parse_jobs(html)

    assert result[0]["url"] == (
        "https://realpython.github.io/fake-jobs/"
        "jobs/python-developer.html"
    )


def test_parse_jobs_empty_apply_href() -> None:
    """Test that an Apply link without href produces an empty URL."""

    html: str = """
    <div class="card-content">
        <h2 class="title is-5">Python Developer</h2>
        <h3 class="subtitle is-6 company">Example Company</h3>
        <p class="location">Amsterdam, NL</p>
        <a>Apply</a>
    </div>
    """

    result: list[dict[str, str]] = main.parse_jobs(html)

    assert len(result) == 1
    assert result[0]["url"] == ""


def test_save_jobs_to_csv(tmp_path: Path) -> None:
    """Test that job listings are correctly written to a CSV file."""

    jobs: list[dict[str, str]] = [
        {
            "title": "Python Developer",
            "company": "Example Company",
            "location": "Amsterdam, NL",
            "url": "https://example.com/python-developer",
        },
        {
            "title": "Data Engineer",
            "company": "Data Company",
            "location": "Rotterdam, NL",
            "url": "https://example.com/data-engineer",
        },
    ]

    csv_file: Path = tmp_path / "jobs.csv"

    main.save_jobs_to_csv(jobs, str(csv_file))

    assert csv_file.exists()

    with csv_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        rows: list[dict[str, str]] = list(reader)

    assert reader.fieldnames == [
        "title",
        "company",
        "location",
        "url",
    ]

    assert rows == jobs


def test_save_jobs_to_csv_with_empty_list(
    tmp_path: Path,
) -> None:
    """Test that no CSV file is created when there are no jobs."""

    csv_file: Path = tmp_path / "jobs.csv"

    main.save_jobs_to_csv([], str(csv_file))

    assert not csv_file.exists()


def test_save_jobs_to_csv_overwrites_existing_file(
    tmp_path: Path,
) -> None:
    """Test that an existing CSV file is overwritten."""

    csv_file: Path = tmp_path / "jobs.csv"

    csv_file.write_text(
        "old,data,should,disappear\n",
        encoding="utf-8",
    )

    jobs: list[dict[str, str]] = [
        {
            "title": "New Job",
            "company": "New Company",
            "location": "New Location",
            "url": "https://example.com/new-job",
        }
    ]

    main.save_jobs_to_csv(jobs, str(csv_file))

    with csv_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        rows: list[dict[str, str]] = list(reader)

    assert rows == jobs


def test_main_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that main executes the complete scraping workflow."""

    mock_jobs: list[dict[str, str]] = [
        {
            "title": "Python Developer",
            "company": "Example Company",
            "location": "Amsterdam, NL",
            "url": "https://example.com/python-developer",
        }
    ]

    mock_fetch_html: Mock = Mock(
        return_value="<html>test</html>"
    )
    mock_parse_jobs: Mock = Mock(return_value=mock_jobs)
    mock_save_jobs_to_csv: Mock = Mock()

    monkeypatch.setattr(
        main,
        "fetch_html",
        mock_fetch_html,
    )
    monkeypatch.setattr(
        main,
        "parse_jobs",
        mock_parse_jobs,
    )
    monkeypatch.setattr(
        main,
        "save_jobs_to_csv",
        mock_save_jobs_to_csv,
    )

    main.main()

    mock_fetch_html.assert_called_once_with()
    mock_parse_jobs.assert_called_once_with(
        "<html>test</html>"
    )
    mock_save_jobs_to_csv.assert_called_once_with(mock_jobs)


def test_main_stops_when_fetch_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that main stops without parsing or saving when fetching fails."""

    mock_fetch_html: Mock = Mock(return_value="")
    mock_parse_jobs: Mock = Mock()
    mock_save_jobs_to_csv: Mock = Mock()

    monkeypatch.setattr(
        main,
        "fetch_html",
        mock_fetch_html,
    )
    monkeypatch.setattr(
        main,
        "parse_jobs",
        mock_parse_jobs,
    )
    monkeypatch.setattr(
        main,
        "save_jobs_to_csv",
        mock_save_jobs_to_csv,
    )

    main.main()

    mock_fetch_html.assert_called_once_with()
    mock_parse_jobs.assert_not_called()
    mock_save_jobs_to_csv.assert_not_called()