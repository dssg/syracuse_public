--Features Generation

--make a table with mains, street_id and main features

--like install_year, material, diameters.
drop table if exists tmp.static_main_features;
select mts.globalid, mts.street_id,
       case when m.install_year is not null and m.install_year != 0 then m.install_year else nm.install_year end as install_year,
       case when m.material is not null then m.material else nm.material end as material,
       case when m.diameters is not null then m.diameters else nm.diameters end as diameters
into tmp.static_main_features
from features.mains_to_streets mts
left join water_system.new_mains nm on nm.globalid=mts.globalid
left join water_system.mains m on m.globalid=mts.globalid
order by street_id;
		     
