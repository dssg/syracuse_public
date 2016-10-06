-- get most common material by decade
-- most common material from 1920-1960 is cast iron
-- most common material from 1960-1970 is steel
-- these assumptions used below to build features.static_features_imputed
-- data very sparse -- we should revisit these assumptions
select decade, material
from
(
	select decade, material, row_number() over(partition by decade order by streets desc) rank
	from
	(
		select cast(install_year_original as int) / 10 * 10 decade, material, count(*) streets
		from
		(
			select sf.*,
			case when install_year = 0 or install_year is null then min_year else install_year end install_year_original
			from features.static_features sf
			left join features.street_min_year smy on smy.street_id = sf.street_id
			where sf.material is not null
		) temp
		group by cast(install_year_original as int) / 10 * 10, material
	) temp2
) temp3
where rank = 1;

drop table if exists features.static_features_imputed;
create table features.static_features_imputed as
select temp.street_id,
	   temp.diameters,
	   temp.rocktype1,
	   temp.rocktype2,
	   temp.musym,
	   temp.zone_name,
	   temp.install_year_original,
	   temp.install_year_parcel_data,
	   temp.install_year_raw,
		case when material is null and install_year_original < 1920 then 'Cast_Iron'
			 when material is null and install_year_original >= 1970 then 'Ductile_Iron'
			 when material is null and install_year_original between 1920 and 1959 then 'Cast_Iron'
			 when material is null and install_year_original between 1960 and 1969 then 'Steel'
			 else material
			 end as material_imputed
from
(
	select sf.*,
	case when install_year != 0 and install_year is not null then install_year else null end install_year_raw,
	case when install_year = 0 or install_year is null then min_year else install_year end install_year_original,
	min_year install_year_parcel_data
	from features.static_features sf
	left join features.street_min_year smy on smy.street_id = sf.street_id
) temp;
