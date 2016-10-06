#!/bin/bash
#ETL script for importing street line data

dirname=$(grep "street_lines_dir" ./../datafiles.yaml|\
 awk -F: '{print $2}'| sed  s/\'//g | sed 's/ //g');

shapefile=$(ls "${dirname}" | grep ".shp$")
projection=2261

echo "shapefile: ${shapefile}"
echo "dirname: ${dirname}"
echo "projection: ${projection}"
#check that there is only one shapefile
num=$(echo ${shapefile} | wc -l )
if [ ${num} -ne 1 ]
then
    echo "Should only be one shapefile, not ${num}";
    exit 1;
fi

#create table and schema
psql -c "drop table if exists streets.street_lines"
psql -c "drop schema if exists streets"
psql -c "create schema streets"

#import the data
shp2pgsql -s ${projection} -d ${dirname}/${shapefile} streets.street_lines | psql
