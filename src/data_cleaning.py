"""Data-quality checks and cleaning utilities for Page Turners."""

import pandas as pd

GENRE_MAP = {
    "fantasy": "Fantasy",
    "science-fiction": "Science fiction",
    "sci-fi": "Science fiction",
    "romance": "Romance",
    "mystery": "Mystery",
    "thriller": "Thriller",
    "historical-fiction": "Historical fiction",
    "horror": "Horror",
}

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

def prepare_book_genres(books_tags: pd.DataFrame) -> pd.DataFrame:
    """
    Create one row per book and selected genre.

    Parameters
    ----------
    books_tags : pandas.DataFrame
        Merged tag table containing book_id and tag_name.
        Book and tag matches should be checked before calling.

    Returns
    -------
    pandas.DataFrame
        Columns book_id and genre, with unique book-genre pairs.
        Books without a selected genre tag are absent.
        Source tag counts are not used.
    """
    selected = books_tags[["book_id", "tag_name"]].copy()

    selected["genre"] = selected["tag_name"].map(GENRE_MAP)

    selected = selected.dropna(subset=["genre"])

    book_genres = selected[["book_id", "genre"]].drop_duplicates()

    return book_genres.reset_index(drop=True)

def prepare_publication_periods(
    books: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare books for comparison across publication periods.

    Parameters
    ----------
    books : pandas.DataFrame
        Prepared book metadata with unique book_id values
        and a publication_year column.

    Returns
    -------
    pandas.DataFrame
        A copy containing books with known publication years
        and an ordered publication_period column.
        Negative years are retained in the BCE category.
    """
    if not books["book_id"].is_unique:
        raise ValueError(
            "Publication analysis requires one row per book."
        )

    if books["publication_year"].eq(0).any():
        raise ValueError(
            "Publication year 0 requires review."
        )

    prepared = books.dropna(
        subset=["publication_year"]
    ).copy()

    boundaries = [
        float("-inf"),
        0,
        1800,
        1900,
        1950,
        2000,
        2010,
        float("inf"),
    ]

    labels = [
        "BCE",
        "1–1799",
        "1800–1899",
        "1900–1949",
        "1950–1999",
        "2000–2009",
        "2010+",
    ]

    prepared["publication_period"] = pd.cut(
        prepared["publication_year"],
        bins=boundaries,
        labels=labels,
        right=False,
        ordered=True,
    )

    prepared["publication_period"] = (
        prepared["publication_period"]
        .cat.remove_unused_categories()
    )

    return prepared

def prepare_book_authors(books: pd.DataFrame) -> pd.DataFrame:
    """
    Assign each book to the first name listed in authors.

    Parameters
    ----------
    books : pandas.DataFrame
        Prepared book metadata with unique, non-missing book_id values.

    Returns
    -------
    pandas.DataFrame
        A copy with a first_listed_author column.
        Books without a usable author name are excluded.
        Missing publication years are retained.
    """
    if books["book_id"].isna().any() or not books["book_id"].is_unique:
        raise ValueError(
            "Author analysis requires unique, non-missing book IDs."
        )

    prepared = books.copy()

    prepared["first_listed_author"] = (
        prepared["authors"]
        .astype("string")
        .str.split(",", n=1)
        .str[0]
        .str.strip()
        .replace("", pd.NA)
    )

    return (
        prepared.dropna(subset=["first_listed_author"])
        .reset_index(drop=True)
    )

def prepare_popularity_data(books: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare book metadata for a popularity-appreciation comparison.

    Parameters
    ----------
    books : pandas.DataFrame
        One row per book, with numeric ratings_count and average_rating.

    Returns
    -------
    pandas.DataFrame
        Book ID, title, rating count, average rating and an ordered
        popularity_quartile column. Missing metrics and zero counts
        are excluded from this analysis.

    Raises
    ------
    ValueError
        If book IDs are missing or repeated, numeric values are invalid,
        no usable rows remain, or quartile boundaries are not distinct.
    """
    if books["book_id"].isna().any() or not books["book_id"].is_unique:
        raise ValueError(
            "Popularity analysis requires unique, non-missing book IDs."
        )

    columns = [
        "book_id",
        "title",
        "ratings_count",
        "average_rating",
    ]

    prepared = (
        books[columns]
        .dropna(subset=["ratings_count", "average_rating"])
        .copy()
    )

    counts = prepared["ratings_count"]

    if not (counts.ge(0) & counts.mod(1).eq(0)).all():
        raise ValueError(
            "Rating counts must be finite, non-negative integers."
        )

    if not prepared["average_rating"].between(1, 5).all():
        raise ValueError("Average ratings must be between 1 and 5.")

    prepared = prepared.loc[counts.gt(0)].copy()

    if prepared.empty:
        raise ValueError(
            "No books have usable popularity and rating data."
        )

    prepared["popularity_quartile"] = pd.qcut(
        prepared["ratings_count"],
        q=4,
        labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"],
        duplicates="raise",
    )

    return prepared.reset_index(drop=True)
    