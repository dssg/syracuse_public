#!/usr/bin/env python
"""
Convert DBF table to CSV
========================

Description
-----------
Converts a DBF table to CSV
and outputs to stdout.

Usage
-----
```
./dbfToCsV.py <dbfile> <schema> <table>
```
"""
import csv
import sys
from dbfread import DBF
import sys
import pandas as pd
from sqlalchemy import create_engine

def convert_to_df(dbf_file):
    """
    Converts contents of dbf file
    to a DataFrame

    Input
    -----
    dbffile: str
       name of dbf file

    Output
    ------
    df: DataFrame
       Dataframe Object
    """
    table = DBF(dbf_file)
    df = pd.DataFrame( iter(table) )
    return df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        exit()

    dbf_file = sys.argv[1]
    df = convert_to_df(dbf_file)
    df.to_csv('temp.csv',index=False)
