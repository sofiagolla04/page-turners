"""Interactive dashboard built on the Page Turners analysis functions.

Run from the repository root with: streamlit run app.py
The source CSV files must first be downloaded with: bash download_data.sh
"""

import matplotlib.pyplot as plt
import streamlit as st

from src.analysis import (
    calculate_popularity_correlation,
    summarize_authors,
    summarize_genres,
    summarize_popularity_quartiles,
    summarize_publication_periods,
    prepare_author_timeline,
)
from src.data_cleaning import (
    GENRE_MAP,
    clean_books,
    prepare_book_authors,
    prepare_book_genres,
    prepare_popularity_data,
    prepare_publication_periods,
)
from src.data_loading import load_csv
from src.data_merging import merge_books_genres, merge_books_tags
from src.visualization import (
    plot_author_ratings_by_year,
    plot_popularity_vs_appreciation,
    plot_ratings_by_publication_period,
)


st.set_page_config(page_title="Page Turners | Explore the data", page_icon="📚", layout="wide")


@st.cache_data(show_spinner="Preparing Page Turners datasets...")
def prepare_dashboard_data():
    """Reuse the project workflow; keep only mapped tags to speed up the dashboard."""
    books = clean_books(load_csv("books.csv"))
    tags = load_csv("tags.csv")
    mapped_tags = tags.loc[tags["tag_name"].isin(GENRE_MAP)].copy()
    book_tags = load_csv("book_tags.csv")
    mapped_links = book_tags.loc[
        book_tags["tag_id"].isin(mapped_tags["tag_id"])
    ].copy()

    # Only selected genre tags are needed for this interface. This produces
    # the same mapped book/genre memberships as the notebook's full tag merge.
    books_tags = merge_books_tags(books, mapped_links, mapped_tags)
    if not books_tags["tag_match"].eq("both").all():
        raise ValueError("Some selected tag identifiers are missing from the tag dictionary.")
    if not books_tags["book_match"].eq("both").all():
        raise ValueError("Some selected book-tag links do not match the books dataset.")

    book_genres = prepare_book_genres(books_tags)
    return {
        "books": books,
        "book_genres": book_genres,
        "genres": merge_books_genres(books, book_genres),
        "periods": prepare_publication_periods(books),
        "authors": prepare_book_authors(books),
        "popularity": prepare_popularity_data(books),
    }


st.title("📚 Page Turners")
st.write("Explore how book ratings differ across genres, publication periods, authors, and popularity.")
st.caption("Source: goodbooks-10k | Ratings and popularity are historical dataset values, not live Goodreads data.")

try:
    data = prepare_dashboard_data()
except (FileNotFoundError, OSError, KeyError, ValueError) as error:
    st.error("The project datasets could not be loaded or validated.")
    st.write("From the repository directory, download the CSVs and restart the app:")
    st.code("bash download_data.sh", language="bash")
    st.caption(f"Details: {error}")
    st.stop()

books = data["books"]
books_popularity = data["popularity"]
all_correlation = calculate_popularity_correlation(books_popularity)["spearman_rho"].iat[0]

with st.sidebar:
    st.header("About the project")
    st.write("This interactive interface reuses the cleaning, merging, analysis, and visualization modules in src/.")
    st.caption("Each book has equal weight in group-level mean ratings. Associations do not imply causation.")
    st.write("Run the notebook for the complete methodology and research limitations.")

overview, genres_tab, periods_tab, authors_tab, popularity_tab, discover_tab = st.tabs(
    ["Overview", "Genres", "Publication periods", "Authors", "Popularity", "Discover books"]
)

with overview:
    st.subheader("Project at a glance")
    a, b, c, d = st.columns(4)
    a.metric("Books", f"{len(books):,}")
    b.metric("Genre-classified books", f"{data['book_genres']['book_id'].nunique():,}")
    c.metric("Books with publication years", f"{len(data['periods']):,}")
    d.metric("Spearman rho", f"{all_correlation:.4f}")
    st.write("The main finding is that books with more ratings tend to be rated only slightly more highly. Popularity and reader appreciation are distinct dimensions.")
    st.info("This is an exploratory dashboard for the selected goodbooks-10k collection, not a representative sample of all published books.")

with genres_tab:
    st.subheader("Ratings across selected genres")
    genre_options = summarize_genres(data["genres"])["genre"].tolist()
    selected_genres = st.multiselect("Genres to compare", genre_options, default=genre_options)
    if selected_genres:
        subset = data["genres"].loc[data["genres"]["genre"].isin(selected_genres)]
        genre_summary = summarize_genres(subset)
        st.bar_chart(genre_summary.set_index("genre")["mean_rating"])
        st.dataframe(genre_summary.round(3), hide_index=True, use_container_width=True)
        st.caption("Genre groups overlap. Each book is counted once within each selected genre, without weighting by rating count.")
    else:
        st.info("Choose at least one genre.")

with periods_tab:
    st.subheader("Ratings by original publication period")
    period_options = data["periods"]["publication_period"].cat.categories.tolist()
    selected_periods = st.multiselect("Publication periods", period_options, default=period_options)
    if selected_periods:
        subset = data["periods"].loc[
            data["periods"]["publication_period"].isin(selected_periods)
        ].copy()
        subset["publication_period"] = subset["publication_period"].cat.remove_unused_categories()
        period_summary = summarize_publication_periods(subset)
        fig = plot_ratings_by_publication_period(subset)
        st.pyplot(fig)
        plt.close(fig)
        st.dataframe(period_summary.round(3), hide_index=True, use_container_width=True)
        st.caption("Books without a known publication year are excluded here only. Periods cover unequal time spans.")
    else:
        st.info("Choose at least one publication period.")

with authors_tab:
    st.subheader("Selected authors: ratings across publication years")
    author_summary = summarize_authors(data["authors"])
    eligible = author_summary.loc[
        (author_summary["n_books_with_year"] >= 5)
        & (author_summary["n_publication_years"] >= 2)
    ]
    author_options = eligible["first_listed_author"].head(25).tolist()
    default_authors = prepare_author_timeline(
        data["authors"], min_books=5, n_authors=3
    )["first_listed_author"].drop_duplicates().tolist()
    selected_authors = st.multiselect(
        "Choose up to three authors", author_options, default=default_authors, max_selections=3
    )
    if selected_authors:
        timeline = data["authors"].loc[
            data["authors"]["first_listed_author"].isin(selected_authors)
            & data["authors"]["publication_year"].notna()
        ].copy()
        fig = plot_author_ratings_by_year(timeline)
        st.pyplot(fig)
        plt.close(fig)
        st.dataframe(
            author_summary.loc[
                author_summary["first_listed_author"].isin(selected_authors)
            ].round(3),
            hide_index=True, use_container_width=True,
        )
        st.caption("Books are attributed to their first-listed author; each point represents a book, not changes in one book's rating over time.")
    else:
        st.info("Choose at least one author.")

with popularity_tab:
    st.subheader("Popularity versus appreciation")
    quartile_options = ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]
    selected_quartiles = st.multiselect(
        "Popularity quartiles", quartile_options, default=quartile_options
    )
    if selected_quartiles:
        subset = books_popularity.loc[
            books_popularity["popularity_quartile"].isin(selected_quartiles)
        ].copy()
        subset_rho = calculate_popularity_correlation(subset)["spearman_rho"].iat[0]
        a, b = st.columns(2)
        a.metric("Selected books", f"{len(subset):,}")
        b.metric("Spearman rho (selection)", f"{subset_rho:.4f}")
        fig = plot_popularity_vs_appreciation(subset)
        st.pyplot(fig)
        plt.close(fig)
        st.dataframe(
            summarize_popularity_quartiles(subset).round(3),
            hide_index=True, use_container_width=True,
        )
        st.caption("The X-axis uses a logarithmic scale. Changing quartiles recalculates rho on the selected books; the full-dataset coefficient is shown in Overview.")
    else:
        st.info("Choose at least one popularity quartile.")

with discover_tab:
    st.subheader("Books combining high ratings and popularity")
    rating_cutoff = books["average_rating"].quantile(0.75)
    count_cutoff = books["ratings_count"].quantile(0.75)
    standouts = books.loc[
        books["average_rating"].ge(rating_cutoff)
        & books["ratings_count"].ge(count_cutoff)
    ].sort_values(["average_rating", "ratings_count"], ascending=False)
    st.caption(
        f"Exploratory definition: at least {rating_cutoff:.2f} average stars and "
        f"{count_cutoff:,.0f} ratings (upper quartile of each variable in this dataset)."
    )
    st.dataframe(
        standouts[["title", "authors", "average_rating", "ratings_count"]].head(30),
        hide_index=True, use_container_width=True,
    )

    st.divider()
    st.subheader("Search and filter books")
    query = st.text_input("Search a title", placeholder="e.g. The Hobbit")
    chosen_genres = st.multiselect(
        "Has at least one of these selected genres",
        sorted(data["book_genres"]["genre"].unique().tolist()),
    )
    minimum_rating = st.slider("Minimum average rating", 1.0, 5.0, 4.0, 0.05)
    minimum_count = st.select_slider(
        "Minimum rating count", options=[0, 5000, 10000, 25000, 50000, 100000, 500000],
        value=0,
    )
    filtered = books.loc[
        books["average_rating"].ge(minimum_rating)
        & books["ratings_count"].ge(minimum_count)
    ].copy()
    if query.strip():
        filtered = filtered.loc[
            filtered["title"].str.contains(query.strip(), case=False, regex=False, na=False)
        ]
    if chosen_genres:
        eligible_ids = data["book_genres"].loc[
            data["book_genres"]["genre"].isin(chosen_genres), "book_id"
        ]
        filtered = filtered.loc[filtered["book_id"].isin(eligible_ids)]
    filtered = filtered.sort_values(
        ["average_rating", "ratings_count"], ascending=False
    )
    columns = ["title", "authors", "average_rating", "ratings_count", "publication_year"]
    st.write(f"{len(filtered):,} matching books (first 100 shown)")
    st.dataframe(filtered[columns].head(100), hide_index=True, use_container_width=True)
    st.download_button(
        "Download all matching books (CSV)",
        data=filtered[columns].to_csv(index=False).encode("utf-8"),
        file_name="page_turners_filtered_books.csv",
        mime="text/csv",
        disabled=filtered.empty,
    )
