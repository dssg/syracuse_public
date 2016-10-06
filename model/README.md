Modeling approach:

### Syntax
```
python pipeline.py config/run.yaml
```

### Configuration files
- config/run.yaml
  - [Example run.yaml](https://github.com/dssg/syracuse/blob/master/model/config/run.yaml)
  - run.yaml is used to customize each run. (e.g. Runnning Random Forest *(RF)*,
    Extra Trees *(ET)* Models with a *3Year* label looking *6,5,4* years in the past,
- config/model.yaml
  - [Example model.yaml](https://github.com/dssg/syracuse/blob/master/model/config/model.yaml)
  - The *model.yaml* contains parameters that change much more slowly, (i.e. parameter grids,
    output_directory, tablename).


### Configuration options
- See documentation in the [Example run.yaml](https://github.com/dssg/syracuse/blob/master/model/config/run.yaml)


## Core files
- pipeline.py: main function for running pipeline
- evaluation.py: contains all the evaluation functions
- write_to_db.py: contains functions for writing to db

## Support files
- datafiles.py: contains paths to the config files
- downsample.py: routines for downsampling the data
- models.py: routines for calling classifers and models
- settings.py: container for settings set in the model.yaml and run.yaml-
- evaluation_functions.py: precision and recall functions

## Test files
| File        | Purpose           |
| ------------- |-------------|
| test_downsample.py | Tests whether the balance of breaks/non-breaks is as expected when rebalancing your data. |
| test_indices.py | Tests that the indices for the feature set and labels are all the same and there is no leakage of data in the training and testing set |
| test_timewindows.py | Tests to make sure that a) the same year-block combinations appear in X and Y sets, and that no year-block appears in more than one of the test, cross-validate, and training sets. |
| test_evaluation.py | Takes sample data and makes sure that evaluation runs without errors. |

## Important Tables for Modelling

### features.combined
- Description: Main feature table
```
                  Table "features.combined"
        Column        |           Type            | Modifiers
----------------------+---------------------------+-----------
 street_id            | double precision          |
 street               | character varying(38)     |
 geom                 | geometry(LineString,2261) |
 diameters            | double precision          |
 rocktype1            | character varying(40)     |
 rocktype2            | character varying(40)     |
 musym                | character varying(6)      |
 zone_name            | character varying         |
 material_imputed     | text                      |
 install_year_imputed | double precision          |
 year_curr            | integer                   |
 pipe_age             | double precision          |
 wo_curr              | bigint                    |
 wo_last1             | bigint                    |
 wo_last2             | bigint                    |
 wo_last3             | bigint                    |
 wo_last4             | bigint                    |
 wo_last5             | bigint                    |
 wo_next1             | integer                   |
 wo_next2             | integer                   |
 wo_next3             | integer                   |
 wo_nearby_last_1     | bigint                    |
 wo_nearby_last_2     | bigint                    |
 wo_nearby_last_3     | bigint                    |
 wo_nearby_last_4     | bigint                    |
 wo_nearby_last_5     | bigint                    |
 wo_nearby_last_6     | bigint                    |
 overall_rating       | integer                   |
 paved_year_curr      | integer                   |

```


### model.result_stats
- Description: Contains summary output of an experiment
```
           Table "model.results_stats"
      Column      |       Type       | Modifiers
------------------+------------------+-----------
 break_window     | text             |
 cross_val        | text             |
 features         | text             |
 model_id         | text             | not null
 model_name       | text             |
 parameters       | text             |
 past_year        | bigint           |
 precision_at_1   | double precision |
 precision_at_10  | double precision |
 precision_at_2   | double precision |
 precision_at_5   | double precision |
 precision_at_pt5 | double precision |
 rebalancing      | text             |
 recall_at_1      | double precision |
 recall_at_10     | double precision |
 recall_at_2      | double precision |
 recall_at_5      | double precision |
 recall_at_pt5    | double precision |
 static_features  | text             |
 test_today       | text             |
 train_range      | text             |
 use_imputed      | boolean          |
 valid_range      | text             |
Indexes:
    "results_stats_pkey" PRIMARY KEY, btree (model_id)
    "results_stats_model_id_idx" UNIQUE, btree (model_id)
Referenced by:
    TABLE "model.train" CONSTRAINT "model_results_statsfk" FOREIGN KEY (model_id) REFERENCES mo
del.results_stats(model_id) MATCH FULL
    TABLE "model.valid" CONSTRAINT "model_results_statsfk" FOREIGN KEY (model_id) REFERENCES mo
del.results_stats(model_id) MATCH FULL

```

### model.train
- Description: Results for prediction on training set
```
             Table "model.train"
    Column    |       Type       | Modifiers
--------------+------------------+-----------
 block_year   | text             |
 y_true       | double precision |
 y_pred_proba | double precision |
 model_id     | text             |
 block_id     | text             |
 year         | text             |
Foreign-key constraints:
    "model_results_statsfk" FOREIGN KEY (model_id) REFERENCES model.results_stats(model_id) MAT
CH FULL

```

### model.valid
- Description: Results for validation set
```
             Table "model.valid"
    Column    |       Type       | Modifiers
--------------+------------------+-----------
 block_year   | text             |
 y_true       | double precision |
 y_pred_proba | double precision |
 model_id     | text             |
 block_id     | text             |
 year         | text             |
Foreign-key constraints:
    "model_results_statsfk" FOREIGN KEY (model_id) REFERENCES model.results_stats(model_id) MAT
CH FULL

```

### model.feature_importances
- Description: Table to record feature_importances for
  an experiment.
```
     Table "model.feature_importances"
   Column   |       Type       | Modifiers
------------+------------------+-----------
 feature    | text             |
 importance | double precision |
 model_id   | text             |

```
