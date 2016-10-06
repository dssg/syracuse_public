-- removes 2016 data that we don't use in our analysis (because it is only Jan-May 2016)
drop table if exists tfv;
create temp table tfv as
select *
from features.temporal_features_vert
where leak_num_y != 2016;

-- combined_base
-- serves as base table for what will eventually be features.combined (main modeling table)
drop table if exists combined_base;
create temp table combined_base as
select sfi.street_id,
       SL.street,
       sl.geom,
	   sfi.diameters,
	   sfi.rocktype1,
	   sfi.rocktype2,
	   sfi.musym,
	   sfi.zone_name,
	   sfi.material_imputed,
	   case when sfi.install_year_raw is not null and sfi.install_year_raw > tfv_curr.leak_num_y then sfi.install_year_parcel_data
	   		when sfi.install_year_raw is not null and sfi.install_year_raw <= tfv_curr.leak_num_y then sfi.install_year_raw
	   		when sfi.install_year_raw is null then sfi.install_year_parcel_data end install_year_imputed,
	   tfv_curr.leak_num_y year_curr,
	   tfv_curr.leak_num_y - 
		   	case when sfi.install_year_raw is not null and sfi.install_year_raw > tfv_curr.leak_num_y then sfi.install_year_parcel_data
		   		when sfi.install_year_raw is not null and sfi.install_year_raw <= tfv_curr.leak_num_y then sfi.install_year_raw
		   		when sfi.install_year_raw is null then sfi.install_year_parcel_data end as pipe_age,
   	   case when (tfv_curr.wo_count is NULL) then null else tfv_curr.wo_count end wo_curr,
	   case when (tfv_curr.wo_count IS NULL OR tfv_minus1.wo_count is NULL) then null else (tfv_curr.wo_count + tfv_minus1.wo_count) end wo_last1,
	   case when (tfv_curr.wo_count IS NULL OR tfv_minus1.wo_count is null or tfv_minus2.wo_count is null) then null else (tfv_curr.wo_count + tfv_minus1.wo_count + tfv_minus2.wo_count) end wo_last2,
	   case when (tfv_curr.wo_count IS NULL OR tfv_minus1.wo_count is null or tfv_minus2.wo_count is null or tfv_minus3.wo_count is null) then null else (tfv_curr.wo_count + tfv_minus1.wo_count + tfv_minus2.wo_count + tfv_minus3.wo_count) end wo_last3,
	   case when (tfv_curr.wo_count IS NULL OR tfv_minus1.wo_count is null or tfv_minus2.wo_count is null or tfv_minus3.wo_count is null or tfv_minus4.wo_count is null) then null else (tfv_curr.wo_count + tfv_minus1.wo_count + tfv_minus2.wo_count + tfv_minus3.wo_count + tfv_minus4.wo_count) end wo_last4,
	   case when (tfv_curr.wo_count IS NULL OR tfv_minus1.wo_count is null or tfv_minus2.wo_count is null or tfv_minus3.wo_count is null or tfv_minus4.wo_count is null or tfv_minus5.wo_count is null) then null else (tfv_curr.wo_count + tfv_minus1.wo_count + tfv_minus2.wo_count + tfv_minus3.wo_count + tfv_minus4.wo_count + tfv_minus5.wo_count) end wo_last5,
	   case when (tfv_plus1.wo_count is NULL) then null when tfv_plus1.wo_count > 0 then 1 else 0 end wo_next1,
	   case when (tfv_plus1.wo_count is null or tfv_plus2.wo_count is null) then null when tfv_plus1.wo_count > 0 or tfv_plus2.wo_count > 0 then 1 else 0 end wo_next2,
	   case when (tfv_plus1.wo_count is null or tfv_plus2.wo_count is null or tfv_plus3.wo_count is null) then null when tfv_plus1.wo_count > 0 or tfv_plus2.wo_count > 0 or tfv_plus3.wo_count > 0 then 1 else 0 end wo_next3
from tfv tfv_curr
join features.static_features_imputed sfi on sfi.street_id = tfv_curr.street_id
left join tfv tfv_minus1 on tfv_curr.leak_num_y = tfv_minus1.leak_num_y + 1 and tfv_curr.street_id = tfv_minus1.street_id
left join tfv tfv_minus2 on tfv_curr.leak_num_y = tfv_minus2.leak_num_y + 2 and tfv_curr.street_id = tfv_minus2.street_id
left join tfv tfv_minus3 on tfv_curr.leak_num_y = tfv_minus3.leak_num_y + 3 and tfv_curr.street_id = tfv_minus3.street_id
left join tfv tfv_minus4 on tfv_curr.leak_num_y = tfv_minus4.leak_num_y + 4 and tfv_curr.street_id = tfv_minus4.street_id
left join tfv tfv_minus5 on tfv_curr.leak_num_y = tfv_minus5.leak_num_y + 5 and tfv_curr.street_id = tfv_minus5.street_id
left join tfv tfv_plus1 on tfv_curr.leak_num_y = tfv_plus1.leak_num_y - 1 and tfv_curr.street_id = tfv_plus1.street_id
left join tfv tfv_plus2 on tfv_curr.leak_num_y = tfv_plus2.leak_num_y - 2 and tfv_curr.street_id = tfv_plus2.street_id
left join tfv tfv_plus3 on tfv_curr.leak_num_y = tfv_plus3.leak_num_y - 3 and tfv_curr.street_id = tfv_plus3.street_id
LEFT JOIN streets.street_lines SL ON sfi.street_id = SL.street_id;

-- add in features showing the # of breaks that have occurred within 300 feet in past 1, 2, 3, etc. years
drop table if exists combined_nearby;
create temp table combined_nearby as
select 	CB.*
		, A.wo_nearby_last_1
		, A.wo_nearby_last_2
		, A.wo_nearby_last_3
		, A.wo_nearby_last_4
		, A.wo_nearby_last_5
		, A.wo_nearby_last_6
from features.workorders_near_blocks A, combined_base CB
where CB.street_id = A.street_id
and CB.year_curr = A.year_curr;

-- final features table
-- adds in road ratings data
-- paved_this_year is 1 if it was paved in year_curr, 0 if it wasn't, and null if we dont know
drop table if exists features.combined;
create table features.combined as
select 	CN.*
		, A.overall_rating
		, case when RP.street_id is not null then 1 when A.street_id is not null and RP.street_id is null then 0 else null end paved_year_curr
from combined_nearby CN
left join features.streets_to_ratings A on A.street_id = CN.street_id and CN.year_curr = A.year_inspected
left join features.road_paved RP on CN.street_id = RP.street_id and CN.year_curr = RP.year_inspected;
