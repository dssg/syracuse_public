#!/usr/bin/env python
# coding: utf-8
"""
Clean Updated Water Work Orders
--------------------------------

Description
-----------

Data Cleaning for water work orders.
- Converts to utf-8
- Fixes columns names
- Makes all column names lowercase
"""
import yaml
import numpy as np
import pandas as pd

data_paths = yaml.load(open('./../../datafiles.yaml'))
datafile = data_paths['datafiles']['updated_water_work_orders']
clean_data_dir = data_paths['datadir']['clean_data_dir']
data = pd.read_csv(datafile, encoding='utf-8')

# drop Unnamed columns, fix partial column names and make all columns lowercase
data.drop([col for col in data.columns if 'Unnamed' in col],
          inplace=True, axis=1)
cols = data.columns.tolist()
newcols = map(lambda x: x.replace('Job_Catego', 'Job_Category').replace(
    'Leak_Numbe', 'Leak_Number').lower(
).strip('_'), cols)
data = data.rename(columns=dict(zip(cols, newcols)))

base_filename = datafile.split('/')[-1]
cleaned_file = base_filename.replace('.csv', '_cleaned.csv')
data.to_csv(clean_data_dir + '/' + cleaned_file,
            index=False,
            encoding='utf-8')
