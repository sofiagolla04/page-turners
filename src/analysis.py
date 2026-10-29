"""Analytical functions for the Page Turners project."""

import pandas as pd


def summarize_genres(
    books_by_genre: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarise book-level average ratings by genre.

    Parameters
    ----------
    books_by_genre : pandas.DataFrame
        One row per book-genre pair, containing book_id,
        genre, and average_rating.

    Returns
    -------
    pandas.DataFrame
        One row per genre, with the number of books,
        mean rating, median rating, and standard deviation.
        Results are sorted by mean rating in descending order.
    """
    summary = (
        books_by_genre
        .groupby("genre", as_index=False)
        .agg(
            n_books=("book_id", "nunique"),
            mean_rating=("average_rating", "mean"),
            median_rating=("average_rating", "median"),
            std_rating=("average_rating", "std"),
        )
    )

    return (
        summary
        .sort_values("mean_rating", ascending=False)
        .reset_index(drop=True)
    )

def summarize_publication_periods(
    books_by_period: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarise book-level average ratings by publication period.

    Parameters
    ----------
    books_by_period : pandas.DataFrame
        One row per book, with publication_period
        and average_rating columns.

    Returns
    -------
    pandas.DataFrame
        Number of books, mean, median, and standard deviation
        of average ratings for each observed publication period.
        Periods are returned in chronological order.
    """
    summary = (
        books_by_period
        .groupby(
            "publication_period",
            as_index=False,
            observed=True,
        )
        .agg(
            n_books=("book_id", "nunique"),
            mean_rating=("average_rating", "mean"),
            median_rating=("average_rating", "median"),
            std_rating=("average_rating", "std"),
        )
    )

    return (
        summary
        .sort_values("publication_period")
        .reset_index(drop=True)
    )

def summarize_authors(books_by_author: pd.DataFrame) -> pd.DataFrame:
    """
    Summarise book ratings and year availability by first-listed author.

    Parameters
    ----------
    books_by_author : pandas.DataFrame
        Prepared data with one row per book and a first_listed_author column.

    Returns
    -------
    pandas.DataFrame
        Book counts, year availability and unweighted rating statistics.
        Authors are ordered by book count, then alphabetically.
    """
    summary = (
        books_by_author
        .groupby("first_listed_author", as_index=False)
        .agg(
            n_books=("book_id", "nunique"),
            n_books_with_year=("publication_year", "count"),
            n_publication_years=("publication_year", "nunique"),
            mean_rating=("average_rating", "mean"),
            median_rating=("average_rating", "median"),
            std_rating=("average_rating", "std"),
        )
    )

    return (
        summary.sort_values(
            ["n_books", "first_listed_author"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

def prepare_author_timeline(
    books_by_author: pd.DataFrame,
    min_books: int = 5,
    n_authors: int = 3,
) -> pd.DataFrame:
    """
    Select well-represented authors for a publication-year comparison.

    Parameters
    ----------
    books_by_author : pandas.DataFrame
        Prepared data with one row per book.
    min_books : int, default 5
        Minimum number of books with known publication years.
    n_authors : int, default 3
        Maximum number of authors to select.

    Returns
    -------
    pandas.DataFrame
        Dated books for selected authors, ordered by author, year and ID.
        Authors must have at least two distinct publication years.
        Selection uses dated book counts, with alphabetical tie-breaking.
    """
    if min_books < 2 or n_authors < 1:
        raise ValueError(
            "min_books must be at least 2 and n_authors at least 1."
        )

    summary = summarize_authors(books_by_author)

    eligible = summary.loc[
        (summary["n_books_with_year"] >= min_books)
        & (summary["n_publication_years"] >= 2)
    ]

    selected_authors = (
        eligible.sort_values(
            ["n_books_with_year", "first_listed_author"],
            ascending=[False, True],
        )
        .head(n_authors)["first_listed_author"]
    )

    if selected_authors.empty:
        raise ValueError("No authors meet the selection criteria.")

    timeline = books_by_author.loc[
        books_by_author["first_listed_author"].isin(selected_authors)
        & books_by_author["publication_year"].notna(),
        [
            "book_id",
            "title",
            "authors",
            "first_listed_author",
            "publication_year",
            "average_rating",
        ],
    ].copy()

    return (
        timeline.sort_values(
            ["first_listed_author", "publication_year", "book_id"]
        )
        .reset_index(drop=True)
    )

def summarize_popularity_quartiles(
    books_popularity: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarise book-level average ratings by popularity quartile.

    Parameters
    ----------
    books_popularity : pandas.DataFrame
        Output of prepare_popularity_data, with one row per book.

    Returns
    -------
    pandas.DataFrame
        Book counts, observed rating-count ranges and unweighted
        rating statistics, ordered from Q1 to Q4.
    """
    summary = (
        books_popularity
        .groupby(
            "popularity_quartile",
            as_index=False,
            observed=True,
        )
        .agg(
            n_books=("book_id", "nunique"),
            min_ratings_count=("ratings_count", "min"),
            max_ratings_count=("ratings_count", "max"),
            mean_rating=("average_rating", "mean"),
            median_rating=("average_rating", "median"),
            std_rating=("average_rating", "std"),
        )
    )

    return (
        summary.sort_values("popularity_quartile")
        .reset_index(drop=True)
    )

def calculate_popularity_correlation(
    books_popularity: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate the Spearman correlation between popularity and rating.

    Parameters
    ----------
    books_popularity : pandas.DataFrame
        Output of prepare_popularity_data, with one row per book,
        positive finite ratings_count values and valid average_rating
        values.

    Returns
    -------
    pandas.DataFrame
        A one-row summary containing the method, the number of books
        and the Spearman correlation coefficient.

    Raises
    ------
    ValueError
        If book IDs are missing or repeated, either metric contains
        missing values, or either metric has fewer than two distinct
        values.
    """
    if (
        books_popularity["book_id"].isna().any()
        or not books_popularity["book_id"].is_unique
    ):
        raise ValueError(
            "Correlation analysis requires unique, non-missing book IDs."
        )

    values = books_popularity[
        ["ratings_count", "average_rating"]
    ]

    if values.isna().any().any():
        raise ValueError(
            "Use the complete data prepared in the popularity section."
        )

    if values.nunique().lt(2).any():
        raise ValueError(
            "Both variables must contain at least two distinct values."
        )

    rho = values["ratings_count"].corr(
        values["average_rating"],
        method="spearman",
    )

    return pd.DataFrame(
        {
            "method": ["Spearman"],
            "n_books": [len(values)],
            "spearman_rho": [rho],
        }
    )