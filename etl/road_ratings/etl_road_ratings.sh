#!/bin/bash

python wrangle_road_ratings.py
psql -f road_ratings_import.sql
# Calls to Google API takes time -- commenting out geocoding, but can be rerun if desired.
python geocode_road_ratings.py
psql -f generate_road_rating_geom.sql
