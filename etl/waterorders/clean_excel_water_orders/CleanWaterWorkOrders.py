#!/usr/bin/env python
"""
Clean Water Workorders from excel file.

"""
# coding: utf-8

import pandas as pd
import numpy as np
import yaml

# get water work orders
# get directory for outputing files
data_paths = yaml.load(open('./../../datafiles.yaml'))
water_orders = data_paths['datafiles']['excel_water_work_orders']
clean_data_dir = data_paths['datadir']['clean_data_dir']
df_water_work_orders = pd.read_excel(water_orders, encoding='utf-8')

datadir = '/mnt/data/syracuse/'


# # Clean Columns
cols = df_water_work_orders.columns.tolist()
newcols = map(lambda x: x.strip('_'), cols)
df_water_work_orders.rename(columns=dict(zip(cols, newcols)), inplace=True)


def clean_leaknumbers(leakentry):
    """
    Check if a leak number is a str or float. If str
    change the separtor (&,-) for multiple leaks numbers into a comma.

    Inputs
    ------
    leakentry: float or str
        entry into the Leak_Number columns

    Output
    ------
    cleanleakentry: float or str
        Clened leak entry
    """
    if leakentry == '<Null>':
        return np.nan
    if type(leakentry) == float:
        return leakentry
    else:
        return leakentry.replace('&', ',').replace('-', ',')


df_water_work_orders['Leak_Number'] = \
    df_water_work_orders['Leak_Number'].map(clean_leaknumbers)


# # Separate Leak Numbers
# seperate leak numbers to treat as separte leaks--not sure if this is
# correct things to do
stack_leak_numbers = df_water_work_orders['Leak_Number'].str.split(',').apply(
    pd.Series, 1).stack()
stack_leak_numbers.name = 'Leak_Num_Sep'
stack_leak_numbers.index = stack_leak_numbers.index.droplevel(-1)
df_water_work_orders = df_water_work_orders.join(stack_leak_numbers)

# clean the leam numbers
leak_numbers = []
for i, row in enumerate(df_water_work_orders['Leak_Num_Sep']):
    try:
        if type(row) == float:  # floats are NaN
            leak_numbers.append(np.nan)
        else:
            leak_numbers.append(int(row.lstrip('0')))
    except:
        print i, row

df_water_work_orders['Leak_Num_Sep'] = leak_numbers


df_water_work_orders.to_csv(
    clean_data_dir + '/water_work_orders_2004-2015.csv',
    index=False,
    encoding='utf-8')
