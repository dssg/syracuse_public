#!/bin/bash

csvfile="/mnt/data/syracuse/Main_Breaks_And_Leaks_Geocoded.csv" 
table_name="water_workorders"
./Clean_Updated_Water_WorkOrders.py
cleaned_csvfile="/mnt/data/syracuse/Main_Breaks_And_Leaks_Geocoded_cleaned.csv"
psql -f maketable.script
psql -f creategeom_fromlonglat.sql
