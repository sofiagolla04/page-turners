"""Validated rating summaries and table merges for Page Turners."""

import pandas as pd


def merge_books_ratings(
    books: pd.DataFrame, ratings: pd.DataFrame
) -> pd.DataFrame:
    """
    Attach rating summaries while retaining one row per book.

    Parameters
    ----------
    books : pandas.DataFrame
        Book metadata with a unique, non-missing book_id.
    ratings : pandas.DataFrame
        Individual ratings with user_id, book_id, and rating.

    Returns
    -------
    pandas.DataFrame
        All input books, plus sample_ratings_count,
        sample_average_rating, and ratings_match.
        Books without observations receive count 0 and a missing mean.

    Raises
    ------
    ValueError
        If required columns, keys, ratings, or relationships are invalid.
    """
    for name, frame, columns in [
        ("books", books, ["book_id"]),
        ("ratings", ratings, ["user_id", "book_id", "rating"]),
    ]:
        missing = sorted(set(columns) - set(frame.columns))
        if missing:
            raise ValueError(f"{name}: missing columns {missing}")
        if frame[columns].isna().any().any():
            raise ValueError(f"{name}: missing identifiers or ratings.")

    if not books["book_id"].is_unique:
        raise ValueError("books.book_id must be unique.")
    if not ratings["rating"].isin([1, 2, 3, 4, 5]).all():
        raise ValueError("Individual ratings must be integers from 1 to 5.")
    if ratings.duplicated(["user_id", "book_id"]).any():
        raise ValueError("Repeated user-book pairs require review.")
    if not ratings["book_id"].isin(books["book_id"]).all():
        raise ValueError("Some ratings refer to books absent from books.")

    rating_summary = ratings.groupby("book_id", as_index=False).agg(
        sample_ratings_count=("rating", "size"),
        sample_average_rating=("rating", "mean"),
    )

    merged = books.merge(
        rating_summary,
        on="book_id",
        how="left",
        validate="one_to_one",
        indicator="ratings_match",
    )

    merged["sample_ratings_count"] = (
        merged["sample_ratings_count"].fillna(0).astype("Int64")
    )

    return merged


def merge_books_tags(
    books: pd.DataFrame,
    book_tags: pd.DataFrame,
    tags: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach tag names and selected book metadata to book-tag records.

    Parameters
    ----------
    books : pandas.DataFrame
        Prepared metadata with both book identifiers, average_rating,
        ratings_count, and publication_year.
    book_tags : pandas.DataFrame
        Source links with goodreads_book_id, tag_id, and count.
    tags : pandas.DataFrame
        Tag dictionary with tag_id and tag_name.

    Returns
    -------
    pandas.DataFrame
        One row per input book-tag record. Repeated pairs are flagged
        by repeated_book_tag_pair. Source count is renamed tag_count.
        tag_match and book_match expose unmatched links.
        No rows are removed and no genre filtering is applied.

    Raises
    ------
    ValueError
        If required columns are missing or keys are missing/duplicated.
    """
    book_columns = [
        "goodreads_book_id", "book_id", "average_rating",
        "ratings_count", "publication_year",
    ]
    link_columns = ["goodreads_book_id", "tag_id", "count"]
    tag_columns = ["tag_id", "tag_name"]

    for name, frame, columns in [
        ("books", books, book_columns),
        ("book_tags", book_tags, link_columns),
        ("tags", tags, tag_columns),
    ]:
        missing = sorted(set(columns) - set(frame.columns))
        if missing:
            raise ValueError(f"{name}: missing columns {missing}")

    for name, frame, keys in [
        ("books", books, ["book_id", "goodreads_book_id"]),
        ("book_tags", book_tags, ["goodreads_book_id", "tag_id"]),
        ("tags", tags, ["tag_id"]),
    ]:
        if frame[keys].isna().any().any():
            raise ValueError(f"{name}: missing merge keys.")

    if not books["book_id"].is_unique:
        raise ValueError("books.book_id must be unique.")
    links = book_tags[link_columns].copy()

    links["repeated_book_tag_pair"] = links.duplicated(
        ["goodreads_book_id", "tag_id"],
        keep=False,
    )

    named_tags = links.rename(
        columns={"count": "tag_count"}
    ).merge(
        tags[tag_columns],
        on="tag_id",
        how="left",
        validate="many_to_one",
        indicator="tag_match",
    )

    return named_tags.merge(
        books[book_columns],
        on="goodreads_book_id",
        how="left",
        validate="many_to_one",
        indicator="book_match",
    )
