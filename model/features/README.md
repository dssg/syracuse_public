Code that combines raw features into the table eventually used for our analysis.

gen_static_features.sh runs full set of queries.

### Files

| File name        | Purpose           |
| ------------- | -------------|
| mains_to_streets.sql      | Generates mapping between each pipe and its associated street (features.mains_to_streets).|
| static_features_gen_pt1.sql, CleanMainProperties.py, static_features_gen_pt2.sql | Generates static features table features.static_features, which has one row per street with associated features that do not change over time (e.g., pipe diameter).
| parcel_to_streets.sql         | Maps tax parcels to nearby streets and identifies the build year of the oldest home within 100 feet in features.street_min_year |
| impute_material_and_age.sql | Uses street_min_year to impute missing pipe age data. |
| Workorders_temporal_table_vertical.sql | Each row identifies a street-year and counts the number of main breaks that occurred on that street. |
| generated_feature_workorders_nearby_blocks.sql | Counts number of main breaks observed within a given radius of each street. |
| features_combined.sql | Combines all of the above into a single table. |
| make_keys.sql | Make primary and foreign keys in the *model.results_stats*, *model.valid*, *model.train* tables |
