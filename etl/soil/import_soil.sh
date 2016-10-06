#!/bin/bash

#adding soil shape file to soil schema, as soil composition
shp2pgsql -d /mnt/data/syracuse/raw/NY067/spatial/soilmu_a_ny067.shp soil.soil_composition | psql

#For removing quotes from the file and replacing with no charachter
cat /mnt/data/syracuse/raw/NY067/tabular/mapunit.txt | sed s/\"//g > mapunitsans.txt
