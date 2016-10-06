#!/bin/bash
#do the whole etl process for the
#syracuse project

#this script find all the bash scripts
#that start with etl and end in .sh
#then cds into that directory executes
#the script and then moves on to the next directory

eval $(cat model/config/secret_default_profile.yaml | sed 's/^/export /' | sed 's/: /=/')

for script in $(find ./ -name 'etl*.sh')
do
    echo ${script};
    DIR=$(dirname "${script}")
    cd ${DIR}
    bash etl*.sh
    cd -
done
