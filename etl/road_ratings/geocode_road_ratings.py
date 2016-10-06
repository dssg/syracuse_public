
import yaml
DATA_PATHS = yaml.load(open('../../datafiles.yaml'))
SENSITIVE_DATA_DIR = DATA_PATHS['datadir']['sensitive_data_dir']

import sys
sys.path.append(SENSITIVE_DATA_DIR)
import sensitive

import googlemaps
import pandas as pd
import os

sys.path.append(os.getcwd() + '/../../model/')
from setup_environment import db_dict, get_dbengine




API_KEYS = sensitive.google_geocode_API_keys

# Query gets all unique intersections found in the road_ratings table.
# Reduces the number of API calls we need to make to Google API.
QUERY = """
select *
from
(
select distinct lower(street_name) street_name, lower(street_to) street_intersecting
from roads.road_ratings
union
select distinct lower(street_name) street_name, lower(street_from) street_intersecting
from roads.road_ratings
) t
where street_intersecting is not null
"""
    
COL_NAMES = ['street_name', 'street_intersecting', 'lat', 'lng', 'address_google']


def postprocess_geocode(geo):
    """Postprocess the output of a google geocoding query

    :param geo [list of dict] The list of dictionaries resulting from a call
     to gmaps.geocode() in the googlemaps library.

    :return [dict] A dictionary of simplified output from geo. Only
     information from the first search hit is returned. The output fields are
       pos [dict] A dictionary giving the geocoded latitude and longitude.
       address [dict] A text description of the address that was matched.
       If the geolocation worked, usually will return something like 
       "W Glen Ave & Ferndale Dr, Syracuse, NY 13205, USA". If not, 
       will return something more general (e.g., "Syracuse, NY 13205, USA")
       Can be used as a measure of quality.
    :rtype: dict
    """
    # only use the top geocoding hit
    if len(geo) == 0:
        return {"pos": {"lat": float("nan"), "lng": float("nan")},
                "address": "No match"}

    address = geo[0]['formatted_address']
    pos = geo[0]["geometry"]["location"]

    return {"pos": pos, "address": address}

def get_search_str(street, intersecting_street):
    """Combines two roads into a form Google's geocoding API understands as an intersection

    :param street [str] Street name
    :param intersecting_street [str] Street name

    : return [str] String of the form "Walnut St & Chicago Ave , Syracuse, NY"
    """
    components = [street, '&', intersecting_street, ', Syracuse, NY']
    return ' '.join(components)


if __name__ == '__main__': 
    engine = get_dbengine(**db_dict)
    df = pd.io.sql.read_sql(sql=QUERY, con=engine.connect())

    output = []

    api_key = API_KEYS.pop()
    gmap = googlemaps.Client(key=api_key)

    for index, row in df.iterrows():	
        search_str = get_search_str(row['street_name'], row['street_intersecting'])

        try:
            geo = gmap.geocode(search_str)
        except googlemaps.exceptions.Timeout:
            api_key = API_KEYS.pop()
            gmap = googlemaps.Client(key=api_key)
            geo = gmap.geocode(search_str)

        processed = postprocess_geocode(geo)

        result = [row['street_name'], row['street_intersecting'], processed['pos']['lat'], processed['pos']['lng'], processed['address']]
        output.append(result)

    df_sql = pd.DataFrame(output, columns = COL_NAMES)
    df_sql.to_sql(name = 'road_intersections', schema = 'roads', con = engine, if_exists = 'replace', index = False)    
