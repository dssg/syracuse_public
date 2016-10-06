--add primary key to the result_stats table
--add foreign key to the valid and model table
alter table model.results_stats add primary key (model_id);

alter table model.train
add constraint model_results_statsfk
foreign key (model_id)
references model.results_stats (model_id) match full;

alter table model.valid
add constraint model_results_statsfk
foreign key (model_id)
references model.results_stats (model_id) match full;
