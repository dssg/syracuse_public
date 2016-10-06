----------------------------------------------------
--This script does the following
-- -creates a proto type table
-- - creates a table for testing main to road snapping 
-- - creates a table for static features
-- - need to map soil features 
----------------------------------------------------

--run the script features_gen1.sql one----------------------------------

-----------------------------------------------
--map the soil data------------------------
---------------------------------------------
create temp table street_info as 
select mts.street_id, sl.street, sl.geom  
from features.mains_to_streets mts
join streets.street_lines sl on sl.street_id = mts.street_id;


drop table if exists soil_street_crosses; 
create temp table soil_street_crosses as 
select si.street_id, si.street, si.geom st_geom,
	   sc.spatialver, sc.musym, sc.mukey, sc.geom, ST_Length(ST_Intersection(si.geom,sc.geom)) 
from street_info as si
join soil.soil_composition sc on ST_Intersects(si.geom, sc.geom);

drop table if exists features.blocks_soils; 
create table features.blocks_soils as
select street_id, musym 
from
(
select *, row_number() over(partition by street_id order by st_length desc) rank
from soil_street_crosses
) as tmp
where rank = 1; 
--
---------------------------------------------------------
-----------------------Geology Data----------------------
---------------------------------------------------------
--map the geology data to the street blocks 
--store in a feature table

create temp table blocks_geo as
select si.street_id, si.street, si.geom st_geom,
       g.rocktype1, g.rocktype2, 
       ST_Length( ST_Intersection(g.geom, si.geom) ) length
from street_info si
join soil.geology g on ST_Intersects(g.geom, si.geom);

create temp table blocks_geo_rank as 
select * from(
select *, row_number() over(partition by street_id order by length desc) rank 
from (select * from blocks_geo) as tmp 
) as tmp2
where rank =1


drop table if exists features.blocks_geo;
create table features.blocks_geo as 
select * from blocks_geo_rank;
--------------------------------------------------------
--------------------------------------------------------
--------------------------------------------------------
--------------------------------------------------------------
--map soil and geology to curated block to main properties----
--------------------------------------------------------------
drop table if exists features.static_features;
create table features.static_features as
select bmp.*, bg.rocktype1, bg.rocktype2, bs.musym
from features.blocks_main_properties bmp
join features.blocks_geo bg on bg.street_id=bmp.street_id
join features.blocks_soils bs on bs.street_id=bmp.street_id;
-------------------------------------------------------------
-------------------------------------------------------------
-------------------------------------------------------------

------------------------------------------------
------------ Pressure Zone Tables--------------- 
------------------------------------------------
--find the pressure zones for blocks 
--make a temp table of 100 random street blocks
--and geometry

drop table if exists street_sample;
create temp table street_sample as 
select sf.street_id, sl.street, sl.geom st_geom 
from static_features sf
join streets.street_lines sl 
on sl.street_id=sf.street_id;  

--join street_sample onto the pressure zones 
drop table if exists pressure_zone_block_map; 
create temp table pressure_zone_block_map as
select ss.*, 
       pz.zone_name, pz.globalid zone_id, pz.wkb_geometry pz_geom,
from street_sample as ss
join water_system.pressure_zones pz 
on ST_Intersects(ss.st_geom, pz.wkb_geometry);


select tmp.*, row_number() over(partition by street_id order by st_length) rank
into features.blocks_pressure_zones
from (
select *, ST_Length( ST_Intersection(st_geom, pz_geom) ) from pressure_zone_block_map
) as tmp


create temp table block_pressure_zone as
select street_id, zone_name from 
features.blocks_pressure_zones
where rank = 1;



----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------
---join main property table with with geology, soil and pressure zone
drop table if exists features.static_features;
create table features.static_features as
select bmp.*, bg.rocktype1, bg.rocktype2, 
       bs.musym, 
       pz.zone_name
from features.blocks_main_properties bmp
left join features.blocks_geo bg on bg.street_id=bmp.street_id
left join features.blocks_soils bs on bs.street_id=bmp.street_id
left join block_pressure_zone pz on pz.street_id = bmp.street_id;
-------------------------------------------------------------------------------------------------



