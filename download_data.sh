#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

mkdir -p data/raw

base_url="https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master"

for filename in books.csv ratings.csv tags.csv book_tags.csv; do
    destination="data/raw/$filename"

    if [ -s "$destination" ]; then
        echo "Keeping existing file: $destination"
        continue
    fi

    echo "Downloading $filename..."

    curl --fail --location --retry 3 \
        "$base_url/$filename" \
        --output "$destination.download"

    mv "$destination.download" "$destination"

    echo "Saved: $destination"
done
