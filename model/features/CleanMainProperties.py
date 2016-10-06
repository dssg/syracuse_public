#!/usr/bin/env python
"""
CleanMainProperties
===================

Description
-----------
This script takes the table, tmp.static_main_features,
made using static_features_gen_pt1.sql and cleans it
in the following way:

Given multiple main globaids on a single block,
denoted by block_id, we want to pull at the following
parameters

- Diameters, take the largest diameter on the block
- Install_Year, take the lowest non-zero install year
- Material, Take the majority material.

For data for which we have install_year but no material:

- If the block install_year > 1966 and there is no material
  then fill in as Ductile Iron

- If the block install year < 1920 and there is no material
  then fill in as Cast Iron.

The results are then written to the database
features.blocks_main_properties.
"""

import pandas as pd
import os
import sys
import numpy as np
from sqlalchemy import create_engine

sys.path.append('./../')
from setup_environment import db_dict, get_dbengine
engine = get_dbengine(**db_dict)


def pull_out_install_year(yrs):
    """
    Pulls out lowest non-zero install year.
    If all install years are 0 then just return 0

    Input
    -----
    yrs: numpy array or Series
       array of years

    Output
    ------
    min_year: int
       minimum year of the array that is greater
       than zero.

    """
    #check for all zeroes
    if np.all( yrs== 0 ):
        return 0
    else:
        return yrs[yrs >0].min()


def pull_out_material(df):
    """
    Pulls out the majority material of a set

    Input
    -----
    df: Series object of materials
       Series object of the materials on a single
       block

    Output
    ------
    material: str
       Major material on that block
    """
    val_cnts = df.value_counts()
    if len(val_cnts) == 0:
        return None
    else:
        return df.value_counts().index[0]


def map_names(material):
    """
    Given a name convert it to the proper one
    so that we have Ductile_Iron and Cast_Iron
    and Universal instead of its many variants.

    Input
    -----
    material: str
       Given material in table

    Output
    ------
    fixed_name: str
       Standardized material name
    """
    if material == 'Ductile':
        return 'Ductile_Iron'
    elif material == 'D.I':
        return 'Ductile_Iron'
    elif material == 'Ductile Iron':
        return 'Ductile_Iron'
    elif material == 'Cast':
        return 'Cast_Iron'
    elif material == 'C.I':
        return 'Cast_Iron'
    elif material =='Univ':
        return 'Universal'
    else:
        return material



def impute_pipe_material(dfx):
    """
    use a list of pipe materials to determine pipe age
    """
    is_empty = dfx['material'].map(lambda x: True if x == None else False)
    pre_20 = (dfx['install_year'] < 1921) & (dfx['install_year'] > 0)
    post_70 = (dfx['install_year'] > 1969) & (dfx['install_year'] > 0)
    empty_andpost70 = (post_70) & (is_empty)
    empty_andpre20 = ((is_empty) & (pre_20))
    dfx.loc[empty_andpre20,'material'] = 'Cast_Iron'
    dfx.loc[empty_andpost70,'material'] = 'Ductile_Iron'

    return dfx



sys.path.insert(0,r'./../')
import setup_environment
data = setup_environment.run_query('select * from tmp.static_main_features')

street_to_diam = data.groupby('street_id')['diameters'].max()
street_to_year = data.groupby('street_id')['install_year'].agg(pull_out_install_year)
sample=data.groupby('street_id').get_group(12563572.0)
streets_material = data.groupby('street_id')['material'].agg(pull_out_material)
dfx = pd.DataFrame()
dfx['diameters'] = street_to_diam
dfx['install_year'] = street_to_year
dfx['material'] = streets_material


dfx['material'] = dfx['material'].map(map_names)


dfx.to_sql(name = 'blocks_main_properties',
           schema = 'features',
           con = engine,
           if_exists = 'replace')
