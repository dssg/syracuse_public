
-- Converts the long/lat fields into geometric object in google map projection 4326
-- Transforms that object into the NYState Projection 
alter table roads.road_intersections drop column if exists geom; 
alter table roads.road_intersections add column geom geometry(Point, 2261);
update roads.road_intersections set geom = ST_Transform( ST_SetSRID(
ST_MakePoint(lng, lat), 4326 ), 2261);

-- where clause prevents geocoding to rows where we got a generic response from Google ('Syracuse, NY, USA')
-- or the address that Google returned was outside of syracuse
drop table if exists roads.rated_segments;
create table roads.rated_segments(
	rating_id serial primary key,
	rated_segment geometry,
	year_inspected int,
	street_name varchar(100),
	street_from varchar(100),
	street_to varchar(100),
	overall_rating int
);

insert into roads.rated_segments (rated_segment, year_inspected, street_name, street_from, street_to, overall_rating)
select ST_MakeLine(ri1.geom, ri2.geom) rated_segment, rr.year_inspected, rr.street_name, rr.street_from, rr.street_to, overall_rating
from roads.road_ratings rr
join roads.road_intersections ri1 on lower(rr.street_name) = ri1.street_name and lower(rr.street_from) = ri1.street_intersecting
join roads.road_intersections ri2 on lower(rr.street_name) = ri2.street_name and lower(rr.street_to) = ri2.street_intersecting
where ri1.address_google like '%Syracuse, NY%'
and ri1.address_google not in ('Syracuse, NY, USA', 'North Syracuse, NY, USA')
and ri2.address_google like '%Syracuse, NY%'
and ri2.address_google not in ('Syracuse, NY, USA', 'North Syracuse, NY, USA');

drop table if exists rs;
create temp table rs as
select rating_id, year_inspected, overall_rating, st_buffer(rated_segment, 50) buffered_geom
from roads.rated_segments rs
where st_length(rated_segment) < 2000; -- Arbitrary limit to remove outliers; removes about 2% of ratings;

drop table if exists features.streets_to_ratings;
create table features.streets_to_ratings as
select street_id, rating_id, year_inspected, overall_rating, length_in_buffer, street_length
from
( -- rank each road rating by how much intersects
	select street_id, rating_id, street_length, length_in_buffer, year_inspected, overall_rating,
	row_number() over(partition by street_id, year_inspected order by length_in_buffer desc) rank
	from
	( -- get the length of road that falls within each buffered road rating geometry that it intersects
		select st_Length(ST_Intersection(geom, buffered_geom)) length_in_buffer, 
		street_id, shape_stle street_length, rating_id, year_inspected, overall_rating
		from streets.street_lines, rs
		where st_intersects(geom, buffered_geom)
		order by street_id, length_in_buffer desc 
	) temp
) r
where r.rank = 1
and length_in_buffer / street_length > 0.8;
-- only including ratings where at least 80% of the street intersects with the buffered road ratings.
-- prevents mapping roads to road ratings for perpendicular roads (where a road rating for the original road does not exist)

-- road_paved
-- lists roads that increased from a 6 or below to a 9 or 10
-- in consecutive years.
-- From 2007-2015, the number of roads paved is ~40 per year
-- in 2006, only 6 roads paved?
-- and pre-2006, 100 or more roads paved per year?
drop table if exists features.road_paved;
create table features.road_paved as
select str.street_id, str.year_inspected, str.overall_rating overall_rating_curr, 
str_prev.overall_rating overall_rating_prev, 
str.overall_rating - str_prev.overall_rating rating_change
from features.streets_to_ratings str
join features.streets_to_ratings str_prev on str_prev.year_inspected + 1 = str.year_inspected and str.street_id = str_prev.street_id
where str.overall_rating >= 9
and str_prev.overall_rating <= 6;


	
