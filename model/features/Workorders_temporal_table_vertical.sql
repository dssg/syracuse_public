--Code for generating vertical feature table: workorders_temporal_vert
--for keeping track of the workorders that occur on that block each year

--The columns of the final table have:
--street_id, leak_num_y, WO_count, WO_ids

--street_id is the block identifier, this repeats multiple times in the rows, because all the blocks ids are repeated each year
--leak_num_y is the year for which the data in the following columns is for
--WO_count number of work orders that are main breaks that happpend on that block in that year
--WO_ids aggregated array column which has the workorder ids in it for all the workorders counted on that block

--code first created 25 July 2016 SAAR


drop table if exists features.temporal_features_vert;

--Starting the table with 2004 workorders
select SL.street_id, 2004 as leak_num_y, count(WTB2.workid) as WO_count, array_agg(WTB2.workid) as WO_ids
into features.temporal_features_vert
from streets.street_lines SL  left outer join 
	(select * 
	from public.workorders_to_block WTB 
	where WTB.leak_num_y = 2004) WTB2
on (SL.street_id = WTB2.street_id)
group by SL.street_id;

--Looping over the workorders from 2005 to 2016
do 
$$
begin 
	for YEAR_num in 2005..2016 loop
insert into features.temporal_features_vert
select SL.street_id, YEAR_num as leak_num_y, count(WTB2.workid) as WO_count, array_agg(WTB2.workid) as WO_ids
from streets.street_lines SL  left outer join 
	(select * 
	from public.workorders_to_block WTB 
	where WTB.leak_num_y = YEAR_num) WTB2
on (SL.street_id = WTB2.street_id)
group by SL.street_id;
end loop;
end; 
$$