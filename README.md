# Page Turners

## Project Overview

Page Turners is a Python data analysis project exploring the relationship between book ratings, genres, publication periods, authors, and popularity. It is developed for the Coding for Data Science course.

The project distinguishes **popularity** (the number of ratings a book receives) from **reader appreciation** (its average rating). It uses a Jupyter notebook for the analysis narrative, an interactive Streamlit dashboard in `app.py`, and reusable functions in the `src/` directory for data preparation, validation, analysis, and plotting. The dashboard is prepared for free deployment on Streamlit Community Cloud.

## Research Questions

1. How do average book ratings vary across selected genres?
2. How do rating distributions differ across original publication periods?
3. Is the number of ratings associated with a book's average rating?
4. How do ratings vary among books by the same author and over publication years?
5. Which books combine relatively high ratings with high popularity?

## Dataset

Source: [goodbooks-10k](https://github.com/zygmuntz/goodbooks-10k) by zygmuntz.

| File | Purpose |
| --- | --- |
| `books.csv` | Book metadata, publication years, aggregate ratings, and rating counts |
| `ratings.csv` | Individual user–book ratings |
| `tags.csv` | Tag IDs and names |
| `book_tags.csv` | Book–tag relationships and associated counts |

The raw CSV files are not stored in this repository. Run `download_data.sh` to download them from the source. Book IDs and Goodreads book IDs serve different purposes and are used with the appropriate join keys.

## Project Structure

| Path | Purpose |
| --- | --- |
| `page_turners_analysis.ipynb` | Main analysis and presentation notebook |
| `app.py` | Interactive Streamlit dashboard reusing the src modules |
| `src/data_download.py` | Automatically downloads the three CSVs used by the cloud dashboard |
| `.streamlit/config.toml` | Coordinated light theme and application colors |
| `src/data_loading.py` | Load CSV files and report loading errors |
| `src/data_cleaning.py` | Data-quality checks, metadata preparation, genre mapping, and analysis-specific subsets |
| `src/data_merging.py` | Validated merges of ratings, tags, genres, and book metadata |
| `src/analysis.py` | Genre, publication-period, author, and popularity summaries; Spearman correlation |
| `src/visualization.py` | Plots for publication periods, author timelines, and popularity versus appreciation |
| `data/raw/` | Downloaded source CSV files |
| `data/processed/` | Location reserved for intermediate datasets |
| `outputs/figures/` | Location for exported figures |
| `outputs/tables/` | Location for exported tables |
| `download_data.sh` | Data download script |
| `requirements.txt` | Pinned cross-platform dependencies for analysis and Streamlit Cloud |
| `requirements-notebook.txt` | Additional pinned dependencies for Jupyter and the notebook |

## Methodology

### 1. Data inspection and quality checks

Inspect the dataset structure, missing values, duplicate records, and key fields. Validate book identifiers, rating ranges, rating counts, and publication-year values before analysis.

### 2. Data cleaning

Standardize title and author strings, prepare nullable integer publication years, and preserve information about missing years and BCE dates. Missing publication years are not automatically imputed. Map a selected set of tags to broader genre labels; a book may belong to multiple selected genres.

### 3. Data integration

- Summarize individual ratings by `book_id` and merge them with the book table while retaining one row per book.
- Join book tags to tag names through `tag_id`, then to book metadata through `goodreads_book_id`.
- Check key uniqueness, missing join keys, and unmatched records. Repeated book–tag pairs are flagged for review.
- Keep the source's aggregate `average_rating` separate from the `sample_average_rating` calculated from `ratings.csv`.

### 4. Exploratory analysis

- Compare book-level average ratings across selected genres.
- Group original publication years into periods and compare rating distributions.
- Summarize authors by their first listed name and examine selected author timelines.
- Compare popularity quartiles and calculate Spearman's rank correlation between rating counts and average ratings.
- Visualize selected relationships using Matplotlib and Seaborn.

## Setup and Execution (macOS/Linux)

Clone the repository and enter the project directory:

```bash
git clone https://github.com/sofiagolla04/page-turners.git
cd page-turners
```

Create and activate a virtual environment, install dependencies, download the data, and launch the notebook:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-notebook.txt
python -m ipykernel install --user --name page-turners --display-name "Python (Page Turners)"
bash download_data.sh
jupyter notebook page_turners_analysis.ipynb
```

Select the **Python (Page Turners)** kernel and run the notebook cells in order. An internet connection is required to download the datasets.

To launch the interactive dashboard with the same environment and downloaded files, run:

```bash
streamlit run app.py
```

Streamlit will provide a local address (usually `http://localhost:8501`) where you can open the dashboard in your browser. A public deployment is not included.

## Deploy on Streamlit Community Cloud

This project is ready to be deployed as a public Streamlit app, but the final publishing step requires the owner's own Streamlit/GitHub authorization. To publish:

1. Open [Streamlit Community Cloud](https://share.streamlit.io) and sign in (or sign up) with GitHub.
2. Authorize Streamlit to access the public `sofiagolla04/page-turners` repository if requested.
3. Choose **Create app** > **Yup, I have an app** and provide the following:
   - **Repository:** `sofiagolla04/page-turners`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **Advanced settings > Python version:** `3.13`
   - **App URL:** choose an available name, e.g. `page-turners-books` (the final address is assigned by Streamlit)
4. Click **Deploy**. Community Cloud will install `requirements.txt` automatically, and the dashboard will fetch its public CSV sources on first launch.
5. Once the app successfully opens, copy its actual `https://...streamlit.app` URL into this README near the top for visitors.

**Public dashboard link:** Not yet published (the owner must complete the Community Cloud deployment above).

The hosted dashboard needs no manual `bash download_data.sh` step. Local notebook users should still run that script to obtain all four source CSVs.
## Tools and Libraries

Python, Jupyter Notebook, pandas, NumPy, SciPy, Matplotlib, Seaborn, and Streamlit. Dependency versions are recorded in `requirements.txt`.

## Interactive Streamlit Dashboard

The completed `app.py` dashboard provides six interactive views: Overview, Genres, Publication periods, Authors, Popularity, and Discover books. Users can compare selected genre summaries, publication-period boxplots, selected author timelines, and popularity quartiles with recalculated Spearman correlation. They can also search books, filter by genre and rating measures, and export the filtered results as CSV.

The Discover books view also offers an exploratory answer to the fifth research question: it lists books above the **75th percentile of both average rating and rating count** within this dataset. This is a transparent, dataset-relative selection rule, not a claim that these books are objectively the best.

The dashboard uses a custom editorial layout with a book-themed header, styled KPI tiles, responsive sections, clearer chart presentation, and a light Streamlit theme configured in `.streamlit/config.toml`.

Streamlit Community Cloud does not include the files ignored by Git in `data/raw/`. On first start, the dashboard automatically downloads `books.csv`, `tags.csv`, and `book_tags.csv` from the public goodbooks-10k repository using `src/data_download.py`. It does not need the large `ratings.csv` sample because the interactive summaries use the aggregate metadata. The original notebook workflow still uses `bash download_data.sh` to download all four files.

The interface imports the existing `src` functions. To reduce initial processing, it joins only source tags included in `GENRE_MAP`, yielding the same selected book–genre pairs used in the notebook. The dashboard is implemented for **local execution**; it has not been published as a hosted web application.

## Key Findings

The notebook analyses 10,000 books and reports the following descriptive results:

| Analysis | Result |
| --- | --- |
| Genre coverage | 8,392 books (83.92%) have at least one of the selected genre tags |
| Genre ratings | Fantasy has the highest mean among the seven mapped genres (4.058); Historical fiction the lowest (3.966) |
| Publication periods | 9,979 books have usable publication years; period means range from 3.892 (1–1799) to 4.034 (1950–1999) |
| Selected authors | Among James Patterson, Stephen King, and Nora Roberts, Nora Roberts has the highest mean (4.075) and lowest book-level standard deviation (0.093) |
| Popularity quartiles | Mean ratings rise from 3.968 in the lowest quartile to 4.025 in the highest |
| Popularity–appreciation association | Spearman's rho = 0.0792 across 10,000 books |

**Main conclusion:** Popularity and reader appreciation capture different aspects of book reception. The association between the number of ratings and average rating is very weak and positive; it does not establish causality. All results refer to the books represented in goodbooks-10k.

For full tables, visualizations, methodological choices, and interpretations, see Sections 12–14 of the [analysis notebook](page_turners_analysis.ipynb).

## Interpretation and Limitations

- The goodbooks-10k dataset is a selected collection of books, not a representative sample of all published books or readers.
- Genre categories are derived from a selected mapping of user-generated tags; categories may overlap and do not cover every book.
- Author comparisons use the **first listed author**, which does not fully represent co-authored books.
- Book-level mean ratings are not weighted by their number of ratings in the genre, author, and period summaries.
- Publication years may be missing, and original publication year is not necessarily the year of the edition rated.
- Correlations describe associations, not causal relationships.
- Aggregate ratings from `books.csv` and summaries of the individual ratings sample must not be treated as interchangeable.

## Project Status

The notebook includes data preparation, integration, exploratory analyses, visualizations, findings, limitations, and a conclusion. An interactive Streamlit application has also been added in `app.py`, with launch instructions above. The project author confirmed that restarting the notebook kernel and running all cells completed without errors in their local environment on 31 October 2026. That check predates the Streamlit addition. The Streamlit code has not yet been independently tested end to end on a clean machine or deployed publicly.
