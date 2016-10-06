#!/usr/bin/env python
"""
Setup Enviroment

Tools for connecting to the
database.

"""

import yaml
import psycopg2
import pandas as pd
from contextlib import contextmanager
from pkg_resources import resource_filename
from sqlalchemy import create_engine


db_setup_file = resource_filename(
    __name__, '/config/secret_default_profile.yaml')
example_db_setup_file = resource_filename(
    __name__, './config/example_default_profile.yaml')

try:
    db_dict = yaml.load(open(db_setup_file))
except IOError:
    print "Cannot find file"
    db_dict = yaml.load(open(example_db_setup_file))




def get_dbengine(PGDATABASE='',
                  PGHOST='',
                  PGPORT=5432,
                  PGPASSWORD='',
                  PGUSER='',
                  DBTYPE='postgresql'):
    """
    Returns a sql engine

    Input
    -----
    PGDATABASE: str
    DB Name
    PGHOST: str
    hostname
    PGPASSWORD: str
    DB password
    DBTYPE: str
    type of database, default is posgresql

    Output
    ------
    engine: SQLalchemy engine
    """
    str_conn =\
            '{dbtype}://{username}@{host}:{port}/{db}'.format(dbtype=DBTYPE,
                                                                   username=PGUSER,
                                                                   db=PGDATABASE,
                                                                   host=PGHOST,
                                                                   port=PGPORT)


    return create_engine(str_conn)


@contextmanager
def connect_to_syracuse_db(PGDATABASE='',
                           PGHOST='',
                           PGPORT=5432,
                           PGUSER='',
                           PGPASSWORD=''):
    """
    Connects to syracuse database
    Output
    ------
    conn: object
       Database connection.
    """
    try:
        conn = psycopg2.connect(
            "dbname={PGDATABASE} user={PGUSER} host={PGHOST} \
            password={PGPASSWORD}".format(
                PGDATABASE=PGDATABASE,
                PGUSER=PGUSER,
                PGHOST=PGHOST,
                PGPORT=PGPORT,
                PGPASSWORD=PGPASSWORD))

        yield conn
    except psycopg2.Error:
        raise SystemExit("Cannot Connect to DB")
    else:
        conn.close()


def run_query(query):
    """
    Runs a query on the database and returns
    the result in a dataframe.
    """
    with connect_to_syracuse_db(**db_dict) as conn:
        data = pd.read_sql(query, conn)
    return data


def test_database_connect():
    """
    test database connection
    """
    with connect_to_syracuse_db(**db_dict) as conn:
        query = 'select * from water_workorders'
        data = pd.read_sql_query(query, conn)
        assert len(data) > 1
