#!/bin/sh

# Data downloaded from this website: http://mrdata.usgs.gov/geology/state/state.php?state=NY
DATA_DIR="/mnt/data/syracuse/raw/NYgeol_dd/"
shp2pgsql -d -s 4267:2261 ${DATA_DIR}nygeol_poly_dd.shp soil.geology | psql
