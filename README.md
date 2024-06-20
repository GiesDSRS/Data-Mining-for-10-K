# Data Mining for 10-K

## Overview

This repo involves extracting mentions of each U.S. state from a company's 10-K filings for a specific year. For instance, if a 10-K filing for Target in 2020 mentions "California", the goal is to capture the word count for "California" and similarly for the other 49 states. This analysis is performed for a sample of firms.

## Project Structure

- **10_k_data_mining.py**: The main script that handles downloading 10-K filings, cleaning the HTML content, and counting state mentions.
- **state_mentions_counts.csv**: The output file that contains the count of state mentions for each CIK.

## Requirements

- Python 3.x
- sec_edgar_downloader
- pandas
- BeautifulSoup
- lxml
- html5lib

Install the required packages using:
```sh
pip install sec_edgar_downloader pandas beautifulsoup4 lxml html5lib



### Usage

## 1. Setup Directory and Download 10-Ks:

The script first sets up a directory to store downloaded 10-K files and then uses the SEC EDGAR Downloader to fetch the 10-K filings based on provided CIK codes and years.

download_dir = '../Temp'
create_directory(download_dir)

email_address = "dummy@email.com"
dl = Downloader(download_dir, email_address=email_address)

# Read the Excel file
file_path = 'file path'  # Replace with the path to your Excel file
df = pd.read_excel(file_path)
cik_years = df[['cik_x', 'year']]

for index, row in cik_years.iloc[:].iterrows():
    try:
        cik_number = str(row['cik_x'])
        year = int(row['year'])

        dl.get("10-K", cik_number, after=f"{year}-01-01", before=f"{year}-12-31")
        print(f"Downloaded 10-K for CIK: {cik_number}, Year: {year}")
    except Exception as e:
        print(f"Failed to download 10-K for CIK: {cik_number}, Year: {year}. Error: {e}")

print("Download completed.")


## 2. Clean HTML Content:

## After downloading the files, the script cleans the HTML content to remove unwanted tags and tables.

def clean_html_content(html_content):
    # Parse the HTML content
    try:
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception as e:
        print(f"html.parser failed: {e}")
        try:
            soup = BeautifulSoup(html_content, "lxml")
        except Exception as e:
            print(f"lxml failed: {e}")
            try:
                soup = BeautifulSoup(html_content, "html5lib")
            except Exception as e:
                print(f"html5lib failed: {e}")
                raise
    ...
    return cleaned_text

def process_files(base_directory):
    file_paths = glob.glob(os.path.join(base_directory, '**', '*.txt'), recursive=True)

    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        cleaned_text = clean_html_content(content)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_text)

        print(f"Processed and cleaned: {file_path}")

base_directory = 'sec-edgar-filings'
process_files(base_directory)


## 3. Count State Mentions:

## The script counts mentions of each U.S. state in the cleaned 10-K files and compiles the results into a CSV file.

import os
import re
import glob
import pandas as pd

us_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    ...
]

def count_state_mentions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    state_counts = {state: len(re.findall(rf'\b{state}\b', text, re.IGNORECASE)) for state in us_states}
    return state_counts

def process_files_for_state_mentions(base_directory):
    file_paths = glob.glob(os.path.join(base_directory, '**', 'full-submission.txt'), recursive=True)

    all_counts = []

    for file_path in file_paths:
        cik_code = os.path.basename(os.path.dirname(file_path))  # Extracts CIK code from directory name
        state_counts = count_state_mentions(file_path)
        state_counts['CIK'] = cik_code
        all_counts.append(state_counts)

    df = pd.DataFrame(all_counts)
    columns_order = ['CIK'] + us_states
    df = df[columns_order]

    return df

base_directory = '/content/sec-edgar-filings'
state_mentions_df = process_files_for_state_mentions(base_directory)

output_file = 'state_mentions_counts.csv'
state_mentions_df.to_csv(output_file, index=False)

print(f"State mentions counts have been saved to {output_file}")


## Notes

### Ensure that the paths specified in the script are correctly set to where your files are located.
### The script reads an Excel file containing CIK codes and years to fetch the corresponding 10-K filings.
### The output CSV file state_mentions_counts.csv contains the count of mentions for each state across different 10-K filings.

