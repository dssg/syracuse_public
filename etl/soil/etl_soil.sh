#!/bin/bash

./import_soil.sh
psql -f soil_to_database.sql 
