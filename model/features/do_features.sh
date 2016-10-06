#!/bin/bash
# generate static features

psql -f mains_to_streets.sql
psql -f static_features_gen_pt1.sql #makes a table of pipes to streets
python CleanMainProperties.py       #cleans and filters
psql -f static_features_gen_pt2.sql #adds soil, geology, pressure zone
psql -f parcels_to_streets.sql #creates mappings between streets and nearby parcels
psql -f impute_material_and_age.sql #imputes missing pipe age using tax parcel data
psql -f Workorders_temporal_table_vertical.sql #counts workorders by year-block
psql -f generated_feature_workorders_nearby_blocks.sql #count nearby workorders for each block
psql -f features_combined.sql #combines temporal features and static features
