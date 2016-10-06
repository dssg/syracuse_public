#!/bin/bash
#ETL script for importing shape files.

usage="./etl_road_data.sh -y yaml_dir -s schema -t table -f shapefilename"

if [ ${#} -eq 0 ]
then
    echo ${usage}
    exit 1;
fi

function die () {
# die errormessage [error_number]
local errmsg="$1" errcode="${2:-1}"
echo "ERROR: ${errmsg}"
exit ${errcode}
}


#------------------------------------------------
# process inputs
#-------------------------------------------------
projection=2261
file="" #standard projection is NYState
while getopts hp:y:s:t:f: OPT; do
case "${OPT}" in
h)  echo "${usage}";
exit 0
;;
p)  projection="${OPTARG}"
;;
y)  yaml_dir="${OPTARG}"
;;
s)  schema="${OPTARG}"
;;
t)  table="${OPTARG}"
;;
f)  file="${OPTARG}"
;;
?)  die "unknown option or missing arument; see -h for usage" 2
;;
esac
done
echo "projection: ${projection}"
echo "yaml_dir ${yaml_dir}"
echo "schema ${schema}"
echo "table ${table}"
echo "file ${file}"


dirname=$(grep ${yaml_dir} ./../datafiles.yaml|\
 awk -F: '{print $2}'| sed  s/\'//g | sed 's/ //g');


if [ -z ${file} ]
then
    shapefile=$(ls "${dirname}" | grep ".shp$")
else
    shapefile=$(basename ${file})
fi


projection=2261

echo "shapefile: ${shapefile}"
echo "dirname: ${dirname}"
echo "projection: ${projection}"
#check that there is only one shapefile


num=$(echo ${shapefile} | wc -l )
if [ ${num} -ne 1 ]
then
    echo "Should only be one shapefile, not ${num}";
    exit 1;
fi


#create table and schema
psql -c "drop table if exists ${schema}.${table}"
psql -c "create schema if not exists ${schema}"

#import the data
shp2pgsql -s ${projection} -d ${dirname}/${shapefile} ${schema}.${table} | psql
