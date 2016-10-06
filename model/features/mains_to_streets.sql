-- buffered street lines
drop temp table if exists sl;
create temp table sl as
select objectid, st_buffer(geom, 50) buffered_geom, geom, street_id
from streets.street_lines;

create schema if not exists features;

drop table if exists features.mains_to_streets;
create table features.mains_to_streets as
select globalid, street_id, length_in_buffer, shape_length
from
( -- rank each intersection by how much intersects
	select globalid, street_id, length_in_buffer, shape_length, row_number() over(partition by globalid order by length_in_buffer desc) rank
	from
	( -- get the length of pipe that falls within each buffered street geometry that it intersects
		select st_Length(ST_Intersection(wkb_geometry, buffered_geom)) length_in_buffer, 
		globalid, street_id, shape_length
		from water_system.mains m, sl
		where st_intersects(wkb_geometry, buffered_geom)
		and m.lat_system = 'Main'
		and m.owner = 'SWD'
		order by globalid, length_in_buffer desc 
	) temp
) r
where r.rank = 1;
