# Syracuse
[![Build Status](https://travis-ci.com/dssg/syracuse.svg?token=qr1WKDpoEiNDipEKFzrb&branch=master)](https://travis-ci.com/dssg/syracuse)

## About
Syracuse is a city located in Onondaga County in Central New York. It has a
population of about 150,000 and a metro area population of approximately
665,000. The Syracuse Innovation Team is a Bloomberg Philanthropies funded
office created in 2015. It was set up with a specific focus on solving
infrastructure problems. The city has a rich history of innovation, but
at this point, the government does not do a lot of work that relies on
data to help make decisions. Having heard about the work that the Center
for Data Science and Public Policy did with Cincinnati on proactive blight
reduction during the 2015 Data Science for the Social Good Fellowship,
the Syracuse Innovation Team reached out to DSaPP about participating in the
2016 Fellowship. Infrastructure, particularly the state of water mains in the
city, is especially important. Based on review of prior DSSG projects, the city
believes that a partnership could be beneficial in pushing data-led initiatives
forward, ultimately benefiting the infrastructure as a whole, as well as the residents.
More information can be found
[here](http://dssg.uchicago.edu/project/early-warning-system-for-water-infrastructure-problems/)

## Project Overview
This project entails designing and implementing a data-driven process to
proacively address water main breaks and leaks. The ulimate goal is to predict
areas where water mains are most at risk of breaking, and which features are the
best for predicting a water main break (e.g, year laid, materials, soil composition).

## Installation

### Get the code
```
git clone https://github.com/dssg/syracuse
cd syracuse
```

### Python Dependencies
```
cd syracuse
pip install -r requirements.txt
```

### Database Configuration

Database Type: *PostGreSQL 9.4*
with PostGIS extension
```
syracuse=> select PostGIS_full_version();
                                                                                postgis_full_version
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 POSTGIS="2.1.8 r13780" GEOS="3.5.0-CAPI-1.9.0 r4084" PROJ="Rel. 4.9.2, 08 September 2015" GDAL="GDAL 1.11.4, released 2016/01/25" LIBXML="2.9.1" LIBJSON="UNKNOWN" TOPOLOGY RASTER
```


See [database credential files](/model/config/example_default_profile.yaml) for details.

Example:
```
PGPORT: 5432
PGHOST: "postgres.123fake.com"
PGDATABASE: "123fake"
PGPASSWORD: "123fake"
```

## Load data into postgres
See the [etl directory](etl) for details

```
bash ./etl/do_etl.sh
```

## Create features from the data
See [model/features](model/features) directory for details
```
bash ./model/features/do_features.sh
```

## Run the modeling pipeline
See [model/README.md](model/README.md) for details

## Directory Structure
```
.
├── config
├── descriptive_stats
│   ├── mains_streets_stats
│   └── water_work_orders
├── etl
│   ├── bin
│   ├── geology
│   ├── road_ratings
│   ├── soil
│   ├── street_line_data
│   ├── tax_data
│   ├── updated_main_data
│   ├── waterorders
│   └── water_system
├── model
│   ├── config
│   ├── features
│   └── log
├── models_evaluation
└── results
    └── figures

```


## Low hanging fruit TODO
- Implement a logger instead of print statements
- Make sure package is python 3 compatible
- Make more unit tests that test whole pipeline
