#!/bin/bash

psql -f create_water_system_schema.sql
./import_water_system.sh
