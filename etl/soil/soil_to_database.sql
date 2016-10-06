drop table if exists soil.soil_types;
create schema if not exists soil;
create table soil.soil_types(

);

\copy soil.soil_types from 'mapunitsans.txt' delimiter '|';
