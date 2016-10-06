#!/bin/bash

RAW_DIR="/mnt/data/syracuse/raw/updated_distribution_system/"

echo ${RAW_DIR};


## Import water distribution system
7z x ${RAW_DIR}Active_SWD_Water_Mains.lpk -o ${RAW_DIR}

exit 1;

# Imports data from a .gdb file (proprietary ESRI geodatabase format) of the Syracuse water system into Postgres.
ogr2ogr -f "PostgreSQL" PG:"active_schema=water_system" -overwrite ${RAW_DIR}v103/distribution_system.gdb


7z x /mnt/data/syracuse/raw/updated_distribution_system/distribution_system/Distribution_System_DBO_pressure_zones.lpk
ogr2ogr -f "PostgreSQL" PG:"active_schema=water_system" ${RAW_DIR}distribution_system/water_viewer.gdb
