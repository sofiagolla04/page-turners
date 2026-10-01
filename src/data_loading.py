"""Functions for loading the Page Turners datasets."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def load_csv(filename: str) -> pd.DataFrame:
    """
    Load a CSV file from the project's raw data directory.

    Parameters
    ----------
    filename : str
        Name of the CSV file, for example "books.csv".

    Returns
    -------
    pandas.DataFrame
        The loaded dataset.

    Raises
    ------
    FileNotFoundError
        If the requested file does not exist.
    ValueError
        If the file cannot be read as a CSV.
    """
    file_path = RAW_DATA_DIR / filename

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}. "
            "Run 'bash download_data.sh' from the project folder."
        )

    try:
        return pd.read_csv(file_path)
    except (
        OSError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as error:
        raise ValueError(
            f"Could not read {file_path.name}: {error}"
        ) from error
