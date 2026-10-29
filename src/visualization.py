import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

def plot_ratings_by_publication_period(books_by_period):
    """
    Plot book-level average ratings by publication period.

    Parameters
    ----------
    books_by_period : pandas.DataFrame
        One row per book, with an ordered publication_period
        column and an average_rating column.

    Returns
    -------
    matplotlib.figure.Figure
        A boxplot comparing rating distributions across periods.
    """
    fig, ax = plt.subplots(figsize=(11, 5))

    sns.boxplot(
        data=books_by_period,
        x="publication_period",
        y="average_rating",
        color="#5B7F95",
        fliersize=3,
        ax=ax,
    )

    ax.set_title(
        "Book ratings by original publication period"
    )
    ax.set_xlabel("Original publication period")
    ax.set_ylabel("Average Goodreads rating")
    ax.set_ylim(1, 5)

    ax.tick_params(axis="x", labelrotation=25)
    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()

    return fig
    
def plot_author_ratings_by_year(author_timeline):
    """
    Plot book ratings against original publication year for selected authors.

    Parameters
    ----------
    author_timeline : pandas.DataFrame
        Dated books returned by prepare_author_timeline.

    Returns
    -------
    matplotlib.figure.Figure
        One scatterplot per author, with one point per book
        and a shared rating scale from 1 to 5.
    """
    authors = (
        author_timeline["first_listed_author"]
        .drop_duplicates()
        .tolist()
    )

    if not authors:
        raise ValueError("There are no author records to plot.")

    fig, axes = plt.subplots(
        nrows=1,
        ncols=len(authors),
        figsize=(5 * len(authors), 4.5),
        sharey=True,
        squeeze=False,
    )

    for ax, author in zip(axes[0], authors):
        author_books = author_timeline.loc[
            author_timeline["first_listed_author"] == author
        ]

        ax.scatter(
            author_books["publication_year"],
            author_books["average_rating"],
            color="#5B7F95",
            s=40,
            alpha=0.75,
        )

        ax.set_title(f"{author}\n{len(author_books)} books")
        ax.set_xlabel("Original publication year")
        ax.xaxis.set_major_locator(
            MaxNLocator(integer=True)
        )
        ax.set_ylim(1, 5)
        ax.tick_params(axis="x", labelrotation=30)
        ax.grid(axis="y", alpha=0.2)

    axes[0, 0].set_ylabel("Average Goodreads rating")
    fig.suptitle("Book ratings by author and publication year")
    fig.tight_layout()

    return fig

def plot_popularity_vs_appreciation(books_popularity):
    """
    Plot book ratings against the number of ratings received.

    Parameters
    ----------
    books_popularity : pandas.DataFrame
        Prepared books with positive ratings_count values
        and an average_rating column.

    Returns
    -------
    matplotlib.figure.Figure
        One point per book, with a logarithmic count axis
        and a linear rating axis.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(
        books_popularity["ratings_count"],
        books_popularity["average_rating"],
        s=12,
        alpha=0.2,
        color="#5B7F95",
        edgecolors="none",
    )

    ax.set_xscale("log")
    ax.set_ylim(1, 5)
    ax.set_title("Book popularity and reader appreciation")
    ax.set_xlabel("Number of Goodreads ratings (log scale)")
    ax.set_ylabel("Average Goodreads rating")
    ax.grid(True, which="major", alpha=0.2)

    fig.tight_layout()

    return fig