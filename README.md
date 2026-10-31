# Page Turners

## Project Overview

Page Turners is a Python data analysis project exploring the relationship between book ratings, genres, publication periods, authors, and popularity. It is developed for the Coding for Data Science course.

The project distinguishes **popularity** (the number of ratings a book receives) from **reader appreciation** (its average rating). It uses a Jupyter notebook for the analysis narrative and reusable functions in the `src/` directory for data preparation, validation, analysis, and plotting.

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
| `requirements.txt` | Pinned Python environment dependencies |

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
python -m pip install -r requirements.txt
python -m ipykernel install --user --name page-turners --display-name "Python (Page Turners)"
bash download_data.sh
jupyter notebook page_turners_analysis.ipynb
```

Select the **Python (Page Turners)** kernel and run the notebook cells in order. An internet connection is required to download the datasets.

## Tools and Libraries

Python, Jupyter Notebook, pandas, NumPy, SciPy, Matplotlib, and Seaborn. Dependency versions are recorded in `requirements.txt`.

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

The notebook includes data preparation, integration, exploratory analyses, visualizations, findings, limitations, and a conclusion. The project author confirmed that restarting the kernel and running all cells completed without errors in their local environment on 31 October 2026. This is a successful local execution check, not an independent test on a clean machine.
