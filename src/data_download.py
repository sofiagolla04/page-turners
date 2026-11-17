"""Download only the public goodbooks-10k CSVs used by the dashboard.

The Jupyter workflow continues to use download_data.sh for all four CSVs.
Streamlit Community Cloud does not include Git-ignored data/raw CSV files,
so the dashboard downloads its three required sources on first launch.
"""

from pathlib import Path
from urllib.request import Request, urlopen

from src.data_loading import RAW_DATA_DIR

SOURCE = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master"
DASHBOARD_FILES = ("books.csv", "tags.csv", "book_tags.csv")


def ensure_dashboard_datasets() -> None:
    """Download missing source CSVs to data/raw without replacing local copies."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for filename in DASHBOARD_FILES:
        target = RAW_DATA_DIR / filename

        # Reuse existing local files, including those downloaded by
        # download_data.sh. Never overwrite the user's original data.
        if target.is_file() and target.stat().st_size > 0:
            continue

        temporary = Path(str(target) + ".download")
        request = Request(
            f"{SOURCE}/{filename}",
            headers={"User-Agent": "PageTurners-Streamlit/1.0"},
        )

        try:
            with urlopen(request, timeout=120) as response, temporary.open("wb") as out:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)

            if temporary.stat().st_size == 0:
                raise OSError(f"Downloaded file {filename} is empty.")

            # A completed download becomes visible only after it succeeds.
            temporary.replace(target)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
