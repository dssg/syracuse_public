
#!/usr/bin/env python
# coding: utf-8
"""
Clean road ratings data
-----------------------

Description
-----------
Data cleaning for yearly audit of road quality.
- Appends all years of data together.
- Standardizes column names.
- Removes invalid values.
- Exports to CSV.
"""

import pandas as pd
import numpy as np
import glob
import re
import sys
import yaml

# ## Static variables

DATA_PATHS = yaml.load( open('./../../datafiles.yaml') )
ROAD_RATINGS_DIR = DATA_PATHS['datadir']['raw_data_dir'] + '/Road_Ratings/'

# Regex chunk to identify four digit numbers in file names (year)
YEAR_REGEX = re.compile(r'\d{4}')

# Column names found in CSVs
COLUMN_NAMES = ['Street Name', 'From', 'To', 'Block', 'Ward',
                'Overall', 'Crack', 'Patch', 'Date R8d', 'Length', 'Width',
                'year_inspected'
               ]

# Column names to export to SQL
SQL_COLUMN_NAMES = ['street_name', 'street_from', 'street_to', 'block_number', 'ward_number',
                    'overall_rating', 'crack_rating', 'patch_rating', 'date_rated', 'street_length',
                    'street_width', 'year_inspected']

# Columns that should be integers (used to put in blanks where text is observed)
SQL_INT_COLUMNS = ['block_number', 'ward_number', 'overall_rating', 'crack_rating', 'patch_rating', 
                   'street_length', 'street_width', 'year_inspected']

# Used to ignore funky data where overall rating is not between 0-10.
ACCEPTABLE_RATINGS = range(0,11)


# ## Extract and append CSVs containing road ratings.

# Extract list of CSV file names.
csv_list = []
for file_name in glob.glob(ROAD_RATINGS_DIR + '*.csv'):
    csv_list.append(file_name)

# Take each CSV and create a dataframe.
df_list = []
for file_name in csv_list:
    df = pd.read_csv(file_name)
    
    search = YEAR_REGEX.search(file_name)
    year = search.group(0)
    df['year_inspected'] = year
    
    if 'Rating' in df.columns:
        # 2002 data has column name of "Rating" instead of "Overall"
        df = df.rename(columns = {'Rating': 'Overall'})
    trimmed = df[COLUMN_NAMES]
    
    df_list.append(trimmed)

# appended has all dataframes appended
appended = pd.concat(df_list) 


# ## Filter invalid data and coerce incorrect data to null (e.g., text in numeric column)

# Filter data to only include rows where the overall rating is 0-10 (about 99% of data)
appended['Numeric_Overall'] = pd.to_numeric( appended.Overall, errors='coerce')
filtered = appended[appended['Numeric_Overall'].isin(ACCEPTABLE_RATINGS)]

# Rename columns.
trimmed = filtered[COLUMN_NAMES]
trimmed.columns = SQL_COLUMN_NAMES

# Puts blanks into rows in each column that should be numeric.
for col in trimmed.columns:
    if col in SQL_INT_COLUMNS:
        trimmed[col] = pd.to_numeric(trimmed[col], errors='coerce')


# ## Export to CSV to copy into DB
trimmed.to_csv(DATA_PATHS['datadir']['clean_data_dir'] + '/road_ratings.csv', index = False)

