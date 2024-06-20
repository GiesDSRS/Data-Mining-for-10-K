# -*- coding: utf-8 -*-
"""10-K_Data_mining.ipynb
"""

!pip install sec_edgar_downloader

import os
import re
import unicodedata
from bs4 import BeautifulSoup
import glob
import pandas as pd
from sec_edgar_downloader import Downloader


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

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
    # soup = BeautifulSoup(html_content, "html.parser")
    # Remove tables with high numeric content
    def get_digit_percentage(tablestring):
        if len(tablestring) > 0:
            numbers = sum(char.isdigit() for char in tablestring)
            length = len(tablestring)
            return numbers / length
        else:
            return 1


    for table in soup.find_all('table'):
        if get_digit_percentage(table.get_text()) > 0.15:
            table.decompose()  # Completely remove the table and its contents

    # Removes all tags
    for tag in soup.find_all(True):
        tag.unwrap()

    # Extract text and normalize Unicode characters
    text = soup.get_text(separator=' ')
    text = unicodedata.normalize('NFKD', text)

    # Remove any remaining HTML entities
    text = re.sub(r'<.*?>', '', text)  # Remove any remaining HTML tags
    text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)

    # Define a function to remove gibberish based on specific patterns
    def remove_gibberish(text):
        # Removes long sequences of characters without spaces
        text = re.sub(r'\b\w{15,}\b', '', text)

        # Removes sequences with high special character density
        text = re.sub(r'[!@#$%^&*()_+={}\[\]:;"\'<>,.?/\\|`~\-]{5,}', '', text)

        # Removes lines that are mostly numbers or symbols
        text = re.sub(r'^[^a-zA-Z\s]*$', '', text, flags=re.MULTILINE)

        # Additional patterns for gibberish removal
        # Removes base64 encoded text patterns
        text = re.sub(r'(begin [0-9]{3} [^\n]+\n(.*\n)+end)', '', text, flags=re.MULTILINE)

        # Removes lines that contain too many non-alphanumeric characters
        text = re.sub(r'^[^\w\s]{10,}$', '', text, flags=re.MULTILINE)

        return text

    text = remove_gibberish(text)
    text = ' '.join(text.split())

    return text

def process_files(base_directory):
    file_paths = glob.glob(os.path.join(base_directory, '**', 'full-submission.txt'), recursive=True)

    # Process each file
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            print(file)
        cleaned_text = clean_html_content(file_content)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_text)

        print(f"Processed and cleaned: {file_path}")

base_directory = 'sec-edgar-filings'

process_files(base_directory)

import os
import re
import glob
import pandas as pd

us_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
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
