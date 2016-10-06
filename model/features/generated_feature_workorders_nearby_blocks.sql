drop table if exists features.workorders_near_blocks;

select 
		  SL.street_id
		, 2004 as year_curr
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= 2004
						and ww.leak_num_y >= (2004)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_1
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= 2004
						and ww.leak_num_y >= (2004 - 1)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_2
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= 2004
						and ww.leak_num_y >= (2004 - 2)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_3
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= 2004
						and ww.leak_num_y >= (2004 - 3)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_4
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= 2004
						and ww.leak_num_y >= (2004 - 4)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_5
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= 2004
						and ww.leak_num_y >= (2004 - 5)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_6 
into features.workorders_near_blocks
from features.mains_to_streets as SL
group by SL.street_id, year_curr;



--Looping over the workorders from 2005 to 2016
do 
$$
begin 
	for YEAR_num in 2005..2016 loop
insert into features.workorders_near_blocks
select 
		  SL.street_id
		, YEAR_num as year_curr
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= YEAR_num
						and ww.leak_num_y >= (YEAR_num)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_1
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= YEAR_num
						and ww.leak_num_y >= (YEAR_num - 1)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_2
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= YEAR_num
						and ww.leak_num_y >= (YEAR_num - 2)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_3
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= YEAR_num
						and ww.leak_num_y >= (YEAR_num - 3)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_4
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= YEAR_num
						and ww.leak_num_y >= (YEAR_num - 4)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_5
		, (select count (FOO.workid) from
			        	(select 
						ww.workid
						from streets.street_lines SL1, public.water_workorders as ww
						where ST_DWithin(SL1.geom,ww.geom,300)
						and ww.leak_num_y <= YEAR_num
						and ww.leak_num_y >= (YEAR_num - 5)
						and SL1.street_id = SL.street_id--so it's not comparing to itself
						) as FOO
		  ) as WO_nearby_last_6 
from features.mains_to_streets as SL
group by SL.street_id, year_curr;
end loop;
end; 
$$