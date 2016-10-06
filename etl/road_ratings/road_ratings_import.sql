create schema if not exists roads;

drop table if exists roads.road_ratings;
create table roads.road_ratings (
        street_name     varchar(100),
        street_from     varchar(100),
        street_to       varchar(100),
        block_number    float,
        ward_number     float,
        overall_rating  float,
        crack_rating    float,
        patch_rating    float,
        date_rated      varchar(100),
        street_length   float,
        street_width    float,
        year_inspected  float
);

\copy roads.road_ratings from '/mnt/data/syracuse/clean_data/road_ratings.csv' delimiter ',' csv header;
