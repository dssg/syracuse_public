ETL Directory for loading data into PostgreSQL

### Key files/folders

- datafiles.yaml -- contains hard coded paths for datafiles
- do_etl.sh -- walks through each subdirectory and run the bash script
beginning with etl.
- bin directory -- contains functions to convert DBF files to CSV, as well as importing shapefiles to PostgreSQL.

### Data

| Dirname        | Type           | Description  |
| ------------- |:-------------:|:-----|
| geology      | GIS | Geological composition data imported into the soil.geology table |
| road_ratings | CSV | Syracuse road ratings by year import into the roads schema |
| soil         | GIS |  Soil composition data imported into the soil schema |
| street_line_data | GIS | Street lines file imported into the streets schema |
| water_system | GIS | Several GIS layers describing the Syracuse water system imported into the water_system schema |
| waterorders | Excel and CSV | Record of work orders from the water department from 2004-2016 |
| create_tables | SQL | Script for creating tables in PostgreSQL database |
| updated_main_data | DBF | Updated water main data provided by City of Syracuse based on extraction from logbooks |
| tax_data | GIS | Tax parcel data from Onondaga County, including the age of the structure on each parcel |

###Projections

All projections are converted into the NYState Projection [SRID:2261](http://spatialreference.org/ref/epsg/2261/)
