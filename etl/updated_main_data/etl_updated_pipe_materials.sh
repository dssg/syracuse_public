#!/bin/bash
#load updated pipe
#materials

./../bin/dbfToCsv.py /mnt/data/syracuse/updated_pipes_materials.dbf
psql -f load_script.sql
