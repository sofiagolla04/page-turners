# Page Turners

## Project Overview

Page Turners investigates how book ratings relate to genres, authors,
publication years, and the number of ratings.

The project distinguishes between:

- Popularity: the number of ratings a book has received.
- Reader appreciation: the book's average rating.

The analysis is presented in a Jupyter notebook and uses reusable Python
functions from the `src` directory.

## Project Status

The project structure, dataset download script, and initial data-loading
function are implemented. Cleaning, analysis, visualisations, and final
findings are still being developed.

## Research Questions

1. How do average ratings differ across genres?
2. How are publication years associated with ratings?
3. Are more frequently rated books also rated more highly?
4. How do ratings vary across an author's published works?
5. Which books combine high average ratings with many ratings?

## Data Source

Dataset: goodbooks-10k by zygmuntz.

Source repository:
https://github.com/zygmuntz/goodbooks-10k

Files used:

- `books.csv`: book metadata.
- `ratings.csv`: individual user ratings.
- `tags.csv`: tag identifiers and names.
- `book_tags.csv`: relationships between books and tags.

The raw CSV files are not committed to this repository.
Use the download script to obtain them from the source repository.

## Project Structure

- `page_turners_analysis.ipynb`: analysis and presentation.
- `src/data_loading.py`: dataset loading.
- `src/data_cleaning.py`: cleaning functions, to be implemented.
- `src/analysis.py`: analytical functions, to be implemented.
- `src/visualization.py`: plotting functions, to be implemented.
- `data/raw/`: original datasets.
- `data/processed/`: intermediate datasets.
- `outputs/figures/`: final plots.
- `outputs/tables/`: exported summary tables.
- `download_data.sh`: dataset download script.
- `requirements.txt`: installed Python package versions.

## Libraries

The project environment includes pandas, NumPy, SciPy, Matplotlib,
Seaborn, Jupyter Notebook, IPython kernel support, and nbformat.

## Setup and Run — macOS/Linux

Clone this repository, open Terminal in the project folder, and run:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python -m ipykernel install --user --name page-turners --display-name "Python (Page Turners)"
    bash download_data.sh
    jupyter notebook page_turners_analysis.ipynb

In Jupyter, select the `Python (Page Turners)` kernel.
Run the notebook cells in order.

## Outputs

Final figures will be saved in `outputs/figures/`.
Summary tables will be saved in `outputs/tables/`.

## Findings and Limitations

These sections will be completed after the analysis.
