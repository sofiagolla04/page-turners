"""Data-quality checks and cleaning utilities for Page Turners."""

import pandas as pd


def check_books_quality(books: pd.DataFrame) -> pd.DataFrame:
    """
    Summarise initial data-quality checks without modifying the input.

    Parameters
    ----------
    books : pandas.DataFrame
        The original books dataset.

    Returns
    -------
    pandas.DataFrame
        A table with check names and row counts. Duplicate-ID counts
        exclude the first occurrence and ignore missing IDs.
        Non-positive years are flagged for review, not deletion.

    Raises
    ------
    ValueError
        If a required column is missing.
    """
    required_columns = [
        "book_id",
        "goodreads_book_id",
        "title",
        "authors",
        "original_publication_year",
        "average_rating",
        "ratings_count",
    ]

    missing_columns = sorted(set(required_columns) - set(books.columns))

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    book_ids = books["book_id"]
    goodreads_ids = books["goodreads_book_id"]

    titles = books["title"].astype("string").str.strip()
    authors = books["authors"].astype("string").str.strip()

    years = pd.to_numeric(
        books["original_publication_year"], errors="coerce"
    )
    averages = pd.to_numeric(books["average_rating"], errors="coerce")
    counts = pd.to_numeric(books["ratings_count"], errors="coerce")

    checks = {
        "total_rows": len(books),
        "exact_duplicate_rows": books.duplicated().sum(),
        "missing_book_ids": book_ids.isna().sum(),
        "extra_duplicate_book_ids": book_ids.dropna().duplicated().sum(),
        "missing_goodreads_book_ids": goodreads_ids.isna().sum(),
        "extra_duplicate_goodreads_book_ids": (
            goodreads_ids.dropna().duplicated().sum()
        ),
        "missing_or_blank_titles": (titles.isna() | titles.eq("")).sum(),
        "missing_or_blank_authors": (authors.isna() | authors.eq("")).sum(),
        "missing_or_non_numeric_years": years.isna().sum(),
        "non_positive_years_to_review": years.le(0).sum(),
        "missing_or_non_numeric_average_ratings": averages.isna().sum(),
        "average_ratings_outside_1_to_5": (
            averages.notna() & ~averages.between(1, 5)
        ).sum(),
        "missing_or_non_numeric_rating_counts": counts.isna().sum(),
        "negative_rating_counts": counts.lt(0).sum(),
    }

    return pd.DataFrame(checks.items(), columns=["check", "count"])


def clean_books(books: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare book metadata without removing rows or imputing dates.

    Parameters
    ----------
    books : pandas.DataFrame
        Book metadata with title, authors, and original_publication_year.

    Returns
    -------
    pandas.DataFrame
        A copy with trimmed text fields and three additional columns:
        publication_year, publication_year_missing, and is_bce.
        The original publication-year column is preserved.
        is_bce remains missing when the publication year is unknown.

    Raises
    ------
    ValueError
        If required columns are absent or years are non-numeric,
        non-integer, infinite, or zero.
    """
    required_columns = {"title", "authors", "original_publication_year"}
    missing_columns = sorted(required_columns - set(books.columns))

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    cleaned = books.copy()

    years = pd.to_numeric(
        cleaned["original_publication_year"], errors="raise"
    )

    if not years.dropna().mod(1).eq(0).all():
        raise ValueError("Publication years must be finite whole numbers.")

    if years.eq(0).any():
        raise ValueError("Zero publication years require manual review.")

    for column in ["title", "authors"]:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    cleaned["publication_year"] = years.astype("Int64")
    cleaned["publication_year_missing"] = cleaned["publication_year"].isna()
    cleaned["is_bce"] = cleaned["publication_year"].lt(0)

    return cleaned
