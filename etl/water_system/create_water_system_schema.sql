-- creates schema to insert GIS data from ArcGIS into Postgres
-- schema referenced in import shell script (import_water_system.sh)
create schema if not exists water_system;
