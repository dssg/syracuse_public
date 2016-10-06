#!/bin/bash
#import shapfiles for the tax parcel data nd water_serivces
./../bin/load_shapefiles.sh -h #for the usage
./../bin/load_shapefiles.sh -y city_tax_dir -s tax -t tax_parcel
./../bin/load_shapefiles.sh -y water_services_dir -s water_dept -t services
