"""Interactive dashboard built on the Page Turners analysis functions.

Run from the repository root with: streamlit run app.py
The source CSV files must first be downloaded with: bash download_data.sh
"""

import html

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


st.set_page_config(
    page_title="Page Turners | Book Insights",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

ACCENT = "#1A7A7A"


def apply_design():
    """Style the dashboard; the analytical data and results are unchanged."""
    st.markdown(
        """
        <style>
        :root {
            --pt-ink: #163844;
            --pt-muted: #627983;
            --pt-teal: #1A7A7A;
            --pt-edge: #DFE8E4;
        }
        [data-testid="stAppViewContainer"] {
            background: #F8FAF7;
        }
        [data-testid="stHeader"] {
            background: rgba(248, 250, 247, 0.94);
        }
        [data-testid="stSidebar"] {
            background: #EDF3F0;
            border-right: 1px solid #DCE8E2;
        }
        .block-container {
            max-width: 1290px;
            padding-top: 1.6rem;
            padding-bottom: 3.5rem;
        }
        .pt-hero {
            position: relative;
            overflow: hidden;
            border-radius: 26px;
            background:
                radial-gradient(circle at 84% 15%, rgba(91, 178, 166, .32), transparent 31%),
                linear-gradient(120deg, #163844 0%, #205965 65%, #23716E 100%);
            padding: 42px 48px 39px;
            color: #FFFFFF;
            margin-bottom: 1.45rem;
            box-shadow: 0 18px 40px rgba(22, 56, 68, 0.13);
        }
        .pt-hero:after {
            content: "";
            position: absolute;
            right: -20px;
            bottom: -85px;
            width: 230px;
            height: 230px;
            border: 32px solid rgba(255, 255, 255, .08);
            border-radius: 50%;
            pointer-events: none;
        }
        .pt-kicker {
            font-size: 11px;
            font-weight: 750;
            letter-spacing: 2.4px;
            text-transform: uppercase;
            color: #E5C594;
        }
        .pt-hero h1 {
            margin: 0.55rem 0 0.45rem;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(40px, 5vw, 68px);
            letter-spacing: -2.3px;
            line-height: 1.03;
            color: #FFFFFF;
            font-weight: 650;
        }
        .pt-hero h1 em {
            color: #F5CC8C;
            font-style: italic;
            font-weight: 500;
        }
        .pt-hero p {
            margin: 0 0 1.35rem;
            font-size: 16px;
            line-height: 1.55;
            color: #E2EFED;
            max-width: 630px;
        }
        .pt-tags {
            display: flex;
            gap: 9px;
            flex-wrap: wrap;
        }
        .pt-tag {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 99px;
            background: rgba(255, 255, 255, .11);
            border: 1px solid rgba(255, 255, 255, .20);
            color: #F7FAF8;
            font-size: 12px;
            letter-spacing: .1px;
        }
        .pt-section {
            margin: 1.55rem 0 1.15rem;
        }
        .pt-section .pt-kicker {
            color: #167472;
        }
        .pt-section h2 {
            font-family: Georgia, "Times New Roman", serif;
            color: #163844;
            font-size: clamp(27px, 3vw, 37px);
            line-height: 1.16;
            font-weight: 600;
            margin: .35rem 0 .4rem;
            letter-spacing: -.55px;
        }
        .pt-section p {
            color: #647B83;
            font-size: 14px;
            max-width: 820px;
            line-height: 1.6;
            margin: 0;
        }
        .pt-note {
            border: 1px solid #DFE8E4;
            border-left: 4px solid #1A7A7A;
            border-radius: 14px;
            background: #FFFFFF;
            padding: 18px 20px;
            margin: 10px 0 18px;
        }
        .pt-note-label {
            color: #167472;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.8px;
            text-transform: uppercase;
            margin: 0 0 7px;
        }
        .pt-note-copy {
            margin: 0;
            font-size: 14px;
            line-height: 1.6;
            color: #314F58;
        }
        .pt-mini-card {
            border: 1px solid #DFE8E4;
            border-radius: 17px;
            background: #FFFFFF;
            min-height: 161px;
            padding: 19px 19px 17px;
            box-shadow: 0 4px 14px rgba(22, 56, 68, .035);
        }
        .pt-mini-card strong {
            display: block;
            color: #163844;
            font-size: 17px;
            margin-bottom: 7px;
        }
        .pt-mini-card p {
            font-size: 13px;
            color: #627983;
            line-height: 1.55;
            margin: 0;
        }
        [data-testid="stMetric"] {
            border: 1px solid #DFE8E4;
            background: #FFFFFF;
            border-radius: 17px;
            padding: 17px 19px;
            box-shadow: 0 4px 14px rgba(22, 56, 68, .035);
        }
        [data-testid="stMetricLabel"] {
            color: #627983;
        }
        [data-testid="stMetricValue"] {
            color: #163844;
        }
        button[data-baseweb="tab"] {
            border-radius: 11px 11px 0 0;
            padding-left: 13px;
            padding-right: 13px;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #126A6D;
            background: #E5F2ED;
        }
        [data-testid="stExpander"] {
            background: #FFFFFF;
            border-radius: 14px;
        }
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }
        @media (max-width: 700px) {
            .block-container { padding-top: 1.1rem; }
            .pt-hero { padding: 29px 23px 27px; border-radius: 20px; }
            .pt-hero h1 { letter-spacing: -1.2px; }
            .pt-mini-card { min-height: 0; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_heading(number, title, description):
    """Consistent headings across all interactive views."""
    st.markdown(
        '<div class="pt-section">'
        f'<span class="pt-kicker">{html.escape(number)}</span>'
        f'<h2>{html.escape(title)}</h2>'
        f'<p>{html.escape(description)}</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def insight(label, message):
    st.markdown(
        '<div class="pt-note">'
        f'<div class="pt-note-label">{html.escape(label)}</div>'
        f'<p class="pt-note-copy">{html.escape(message)}</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def mini_card(title, body):
    st.markdown(
        '<div class="pt-mini-card">'
        f'<strong>{html.escape(title)}</strong>'
        f'<p>{html.escape(body)}</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def display_figure(fig):
    """Give existing Matplotlib plots consistent chrome without changing data."""
    fig.patch.set_facecolor("#FFFFFF")
    for ax in fig.axes:
        ax.set_facecolor("#FFFFFF")
        ax.tick_params(colors="#526A75")
        ax.xaxis.label.set_color("#526A75")
        ax.yaxis.label.set_color("#526A75")
        ax.title.set_color("#163844")
        for side, spine in ax.spines.items():
            if side in ("top", "right"):
                spine.set_visible(False)
            else:
                spine.set_color("#DFE8E4")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


apply_design()


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


st.markdown(
    """
    <div class="pt-hero">
      <div class="pt-kicker">Coding for Data Science &nbsp; / &nbsp; Data exploration</div>
      <h1>Page <em>Turners.</em></h1>
      <p>What makes a book loved by readers? Explore the story behind
      genres, authors, publication years, and popularity.</p>
      <div class="pt-tags">
        <span class="pt-tag">10,000 books</span>
        <span class="pt-tag">Goodreads ratings</span>
        <span class="pt-tag">Interactive research</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
    st.markdown("### 📚 Page Turners")
    st.caption("AN INTERACTIVE READING OF DATA")
    st.divider()
    st.markdown("**Explore the collection**")
    st.write("Select a tab to compare genres, periods, authors, or popularity — or search for a book.")
    st.divider()
    st.markdown("**How to interpret results**")
    st.caption("Each book has equal weight in group averages. Genre groups overlap, and associations do not establish causation.")
    st.caption("The dataset is a historical goodbooks-10k snapshot, not live Goodreads data.")
    st.markdown("[View source code on GitHub](https://github.com/sofiagolla04/page-turners)")

overview, genres_tab, periods_tab, authors_tab, popularity_tab, discover_tab = st.tabs(
    ["✦ Overview", "▥ Genres", "◷ Periods", "✎ Authors", "↗ Popularity", "⌕ Explore books"]
)

with overview:
    section_heading(
        "01 / OVERVIEW", "The story in the numbers",
        "A snapshot of the goodbooks-10k collection and the patterns behind reader appreciation.",
    )
    a, b, c, d = st.columns(4)
    a.metric("Books analyzed", f"{len(books):,}")
    b.metric("Genre-classified", f"{data['book_genres']['book_id'].nunique():,}")
    c.metric("Books with dated entries", f"{len(data['periods']):,}")
    d.metric("Spearman rho", f"{all_correlation:.4f}")
    st.markdown("#### Three things worth noticing")
    left, center, right = st.columns(3)
    with left:
        mini_card("Genres tell different stories", "Fantasy has the highest mean rating among the seven mapped genre groups, but the differences are small.")
    with center:
        mini_card("Time is not a simple explanation", "Ratings do not consistently rise or fall across publication periods.")
    with right:
        mini_card("Popular ≠ most appreciated", "Rating counts and average ratings show only a very weak positive association.")
    insight(
        "Research note",
        "These results describe this selected collection of books. They are exploratory, not causal, and should not be generalized to all published books.",
    )

with genres_tab:
    section_heading(
        "02 / GENRE EXPLORER", "Which genres do readers rate most highly?",
        "Compare average book-level ratings across selected user-generated genre tags.",
    )
    genre_options = summarize_genres(data["genres"])["genre"].tolist()
    selected_genres = st.multiselect(
        "Choose genres", genre_options, default=genre_options,
        help="A book can belong to multiple genres."
    )
    if selected_genres:
        subset = data["genres"].loc[data["genres"]["genre"].isin(selected_genres)]
        genre_summary = summarize_genres(subset)
        a, b, c = st.columns(3)
        a.metric("Genres selected", len(genre_summary))
        b.metric("Books represented", f"{subset['book_id'].nunique():,}")
        c.metric("Highest mean rating", f"{genre_summary['mean_rating'].max():.3f}")
        st.bar_chart(
            genre_summary, x="genre", y="mean_rating", color=ACCENT,
            height=380, sort=False, y_label="Mean Goodreads rating",
        )
        insight(
            "Read the chart",
            "Each book is given equal weight within its genre. Overlapping genre categories mean that totals across genres should not be added together.",
        )
        with st.expander("View the full genre statistics"):
            st.dataframe(genre_summary.round(3), hide_index=True, use_container_width=True)
    else:
        st.info("Choose at least one genre to display the comparison.")

with periods_tab:
    section_heading(
        "03 / THROUGH THE YEARS", "How do ratings vary across eras?",
        "Explore medians, quartiles, and outliers, not just the mean rating of each period.",
    )
    period_options = data["periods"]["publication_period"].cat.categories.tolist()
    selected_periods = st.multiselect(
        "Publication periods", period_options, default=period_options
    )
    if selected_periods:
        subset = data["periods"].loc[
            data["periods"]["publication_period"].isin(selected_periods)
        ].copy()
        subset["publication_period"] = subset["publication_period"].cat.remove_unused_categories()
        period_summary = summarize_publication_periods(subset)
        a, b = st.columns(2)
        a.metric("Books included", f"{len(subset):,}")
        b.metric("Periods shown", len(period_summary))
        fig = plot_ratings_by_publication_period(subset)
        display_figure(fig)
        insight(
            "Read the boxplot",
            "The middle line shows the median, the box shows the middle half of ratings, and points beyond the whiskers indicate potential outliers. Periods have unequal durations.",
        )
        with st.expander("View the publication-period statistics"):
            st.dataframe(period_summary.round(3), hide_index=True, use_container_width=True)
    else:
        st.info("Choose at least one publication period.")

with authors_tab:
    section_heading(
        "04 / AUTHOR STUDY", "A closer look at authors",
        "Compare individual books across publication years, using a shared rating scale.",
    )
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
        "Choose up to three authors",
        author_options, default=default_authors, max_selections=3,
        help="Authors are ranked by the number of books with known publication years.",
    )
    if selected_authors:
        timeline = data["authors"].loc[
            data["authors"]["first_listed_author"].isin(selected_authors)
            & data["authors"]["publication_year"].notna()
        ].copy()
        a, b = st.columns(2)
        a.metric("Books in comparison", f"{len(timeline):,}")
        b.metric("Authors shown", len(selected_authors))
        fig = plot_author_ratings_by_year(timeline)
        display_figure(fig)
        insight(
            "An important limitation",
            "Books are assigned to the first-listed author. Each point is a different book, not the changing rating of one book over time.",
        )
        with st.expander("View author statistics"):
            st.dataframe(
                author_summary.loc[
                    author_summary["first_listed_author"].isin(selected_authors)
                ].round(3),
                hide_index=True, use_container_width=True,
            )
    else:
        st.info("Choose at least one author.")

with popularity_tab:
    section_heading(
        "05 / POPULARITY VS APPRECIATION", "Do more ratings mean better ratings?",
        "Investigate the relationship between the number of ratings and their average score.",
    )
    quartile_options = ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]
    selected_quartiles = st.multiselect(
        "Popularity quartiles", quartile_options, default=quartile_options,
        help="Quartiles split the dataset into groups with approximately equal numbers of books.",
    )
    if selected_quartiles:
        subset = books_popularity.loc[
            books_popularity["popularity_quartile"].isin(selected_quartiles)
        ].copy()
        subset_rho = calculate_popularity_correlation(subset)["spearman_rho"].iat[0]
        a, b, c = st.columns(3)
        a.metric("Selected books", f"{len(subset):,}")
        b.metric("Selected Spearman rho", f"{subset_rho:.4f}")
        c.metric("Full dataset rho", f"{all_correlation:.4f}")
        fig = plot_popularity_vs_appreciation(subset)
        display_figure(fig)
        insight(
            "Read the scatterplot",
            "Each point represents one book. The horizontal axis is logarithmic to accommodate the large range of rating counts. A weak association does not imply causation.",
        )
        with st.expander("View the quartile statistics"):
            st.dataframe(
                summarize_popularity_quartiles(subset).round(3),
                hide_index=True, use_container_width=True,
            )
    else:
        st.info("Choose at least one popularity quartile.")

with discover_tab:
    section_heading(
        "06 / BOOK DISCOVERY", "Find your next data-driven read",
        "Discover books combining strong ratings and popularity, or build your own filtered shortlist.",
    )
    rating_cutoff = books["average_rating"].quantile(0.75)
    count_cutoff = books["ratings_count"].quantile(0.75)
    standouts = books.loc[
        books["average_rating"].ge(rating_cutoff)
        & books["ratings_count"].ge(count_cutoff)
    ].sort_values(["average_rating", "ratings_count"], ascending=False)

    a, b, c = st.columns(3)
    a.metric("Books meeting both criteria", f"{len(standouts):,}")
    b.metric("Minimum average rating", f"{rating_cutoff:.2f}")
    c.metric("Minimum rating count", f"{count_cutoff:,.0f}")
    insight(
        "How the shortlist works",
        "These are books in the top 25% of this dataset for both average rating and number of ratings. This is an exploratory rule, not an objective ranking of literary quality.",
    )
    st.markdown("#### The standout shelf")
    st.dataframe(
        standouts[["title", "authors", "average_rating", "ratings_count"]].head(30),
        hide_index=True, use_container_width=True,
    )
    st.divider()
    st.markdown("#### Build your own bookshelf")
    first, second = st.columns(2)
    with first:
        query = st.text_input("Search by title", placeholder="Try The Hobbit")
        minimum_rating = st.slider("Minimum average rating", 1.0, 5.0, 4.0, 0.05)
    with second:
        chosen_genres = st.multiselect(
            "Genre filter (any selected)",
            sorted(data["book_genres"]["genre"].unique().tolist()),
        )
        minimum_count = st.select_slider(
            "Minimum number of ratings",
            options=[0, 5000, 10000, 25000, 50000, 100000, 500000],
            value=0,
        )
    filtered = books.loc[
        books["average_rating"].ge(minimum_rating)
        & books["ratings_count"].ge(minimum_count)
    ].copy()
    if query.strip():
        filtered = filtered.loc[
            filtered["title"].str.contains(
                query.strip(), case=False, regex=False, na=False
            )
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
    st.caption(f"{len(filtered):,} matching books — showing the first 100.")
    st.dataframe(filtered[columns].head(100), hide_index=True, use_container_width=True)
    st.download_button(
        "↓ Download filtered books as CSV",
        data=filtered[columns].to_csv(index=False).encode("utf-8"),
        file_name="page_turners_filtered_books.csv",
        mime="text/csv",
        disabled=filtered.empty,
    )
