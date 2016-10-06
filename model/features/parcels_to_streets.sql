-- buffered street lines
drop table if exists sl;
create temp table sl as
select street_id, st_buffer(geom, 100) buffered_geom, geom
from streets.street_lines;

-- subset of fields from tax parcel data
drop table if exists tp;
create temp table tp as 
select geom, landuse, gid, yearbuilt
from tax.tax_parcel;

-- map parcels to streets based on parcels that overlap with the buffered street lines
drop table if exists tax.parcel_to_street;
create table tax.parcel_to_street as
select street_id, gid, yearbuilt, landuse
from sl, tp
where st_intersects(buffered_geom, tp.geom);

-- get minimum year built (from parcels) for each street
drop table if exists features.street_min_year;
create table features.street_min_year as
select street_id, min(cast(yearbuilt as int)) min_year
from tax.parcel_to_street
where yearbuilt is not null
and cast(yearbuilt as int) != 0
group by street_id;