
-- Converts the long/lat fields into geometric object in google map projection 4326
-- Transforms that object into the NYState Projection 

alter table water_workorders drop column if exists geom; 
alter table water_workorders add column geom geometry(Point, 2261);
update water_workorders set geom = ST_Transform( ST_SetSRID(
ST_MakePoint(longitude, latitude), 4326 ), 2261);
