#!/usr/bin/env python
"""
Pipeline
========

Description
-----------
Syracuse Pipeline

Usage
-----
./pipeline.py run.yaml

"""
import warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import setup_environment

import yaml
import pandas as pd
import numpy as np
import sklearn.metrics as metrics
from sklearn.metrics import precision_recall_curve
import models
import math
import write_to_db as dbwrite
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.grid_search import ParameterGrid
from evaluation import full_evaluation
from datafiles import model_config
import sys
import settings as sett
import time
import pickle
from downsample import check_balance, downsample
import json
from CVstrategy import CV_no_overlap

def get_data(query):
    """
    Pulls data from the db based on the query

    Input
    -----
    query: str
       SQL query from the database

    Output
    ------
    data: DataFrame
       Dump of Query into a DataFrame
    """
    from setup_environment import db_dict
    with setup_environment.connect_to_syracuse_db(**db_dict) as conn:
        data = pd.read_sql_query(query, conn)
    return data


def plot_precision_recall_n(y_true, y_prob, model_name, pdf=None):
    y_score = y_prob
    precision_curve, recall_curve, pr_thresholds = precision_recall_curve(
        y_true, y_score)
    precision_curve = precision_curve[:-1]
    recall_curve = recall_curve[:-1]
    pct_above_per_thresh = []
    number_scored = len(y_score)
    for value in pr_thresholds:
        num_above_thresh = len(y_score[y_score >= value])
        pct_above_thresh = num_above_thresh / float(number_scored)
        pct_above_per_thresh.append(pct_above_thresh)
    pct_above_per_thresh = np.array(pct_above_per_thresh)
    plt.clf()
    fig, ax1 = plt.subplots()
    ax1.plot(pct_above_per_thresh, precision_curve, 'b')
    ax1.set_xlabel('percent of population')
    ax1.set_ylabel('precision', color='b')
    ax2 = ax1.twinx()
    ax2.plot(pct_above_per_thresh, recall_curve, 'r')
    ax2.set_ylabel('recall', color='r')

    name = model_name
    plt.title(name)
    if pdf:
        pdf.savefig()
        plt.close()
    else:
        plt.show()


def plot_predict_proba(y_pred_probs, clf, pdf=None):
    """Plots the predict proba distribution"""
    fig, ax = plt.subplots(1, figsize=(18, 8))
    sns.set_style("white")
    sns.set_context("poster",
                    font_scale=2.25,
                    rc={"lines.linewidth": 1.25, "lines.markersize": 8})
    sns.distplot(y_pred_probs)
    plt.xlabel('predict_proba')
    plt.ylabel('frequency')
    plt.title(clf + ' proba')
    if pdf:
        pdf.savefig()
        plt.close()
    else:
        plt.show()


def plot_to_pdf(Y_valid, y_predict_probs, filename):
    """
    Plots the predict proba and precision recall
    curve on a single graph
    """
    with PdfPages(filename + '.pdf') as pdf:
        y_predict = y_predict_probs
        inclf = filename
        plot_predict_proba(y_predict, inclf, pdf=pdf)
        plot_precision_recall_n(Y_valid.values.ravel(),
                                y_predict_probs, inclf, pdf=pdf)




def prep_data(data, features, label, year_var='year_curr'):
    """
    Makes categorical variables into dummies and preps for model
    """

    prepped = pd.DataFrame(index=data.index)
    for col_name in features:
        if data.dtypes[col_name] == 'object':
            dummied = dummy_text_feature(data, col_name)
            prepped = prepped.join(dummied)
        else:
            prepped = prepped.join(data[col_name])
    prepped = prepped.join(data[[label, year_var]])
    return prepped


def dummy_text_feature(data, feature):
    """ Generates dummy columns for a categorical variable """
    dummies = pd.get_dummies(data[feature], prefix=feature, dummy_na=True)
    return dummies


def dumify_categorical_features(df):
    """
    Takes the df and returns a dummified
    dataframe

    Input
    -----
    df: DF
       Dataframe with features

    Output
    ------
    prepped: DF
       Dummified DF
    """
    prepped = pd.DataFrame(index=df.index)
    for feature in df.columns:
        # print feature, df.dtypes[feature]
        if df.dtypes[feature] == 'object':
            dummied = dummy_text_feature(df, feature)
            prepped = prepped.join(dummied)
        else:
            prepped = prepped.join(df[feature])
    return prepped


def get_feature_table(tablename):
    """
    Fetches the data from the repository
    and adds the year block_id as an index.

    Input
    -----
    tablename: str
       schema.tablename to fetch from the db

    Output
    ------
    data: df
       DataFrame object of data indexed with block_year id

    """
    query = 'select * from {table}'.format(table=tablename)
    data = get_data(query)
    data['block_year'] =\
        ['_'.join(
            np.array(
                np.array(row, dtype='int'), dtype='str'))
         for row in data[['street_id', 'year_curr']].values]
    data = data.set_index('block_year')
    return data


def predict_n_years(break_window):
    """
    Predict n_years

    Input
    -----
    break_window: int


    Output
    ------
    predict_n_years: int

    n_test: int
    n_holdout: int
    """

    if break_window == '1Year':
        return 1, 2
    if break_window == '2Year':
        return 2, 3
    if break_window == '3Year':
        return 3, 4


def train_valid_test_split(data,
                           break_window,
                           static_features,
                           cv_cut,
                           past,
                           future,
                           past_yr=None,
                           Verbose=False,
                           testing=False,
                           config=None):
    """
    Does the train, validate_test_split using the split from cv_cut

    Input
    -----
    data: df
        Feature table
    break_window: str
        How many years we want to predict a break will occur e.g. 1Year
    static_features: ls
        ls of static_features to be used
    cv_cut:
        ls of how to split the train and validation set e.g. [0.3,0.7]
        means 30% of the validation set and 70% of the training set
    past: ls
        columns names of the past work orders
    future: ls
        columns names of the future work orders
    past_yr int
        how many year in the past you want to look in the training
        and validation set.
    Verbose: bool
        Flag for debugging
    testing: bool
        flag for testing that outputs for the year ranges

    Output
    ------
    (X_train, Y_train, X_valid, Y_valid, X_test, Y_test): df
         Traning and testing DataFrames
    dict_year: dict
       Dictionary of year ranges.

    """
    predict_n_yr, n_holdout = predict_n_years(break_window)
    yr_range = np.sort(data.year_curr.unique())
    holdout_yrs = yr_range[-n_holdout]
    test_train_yrs = yr_range[:-n_holdout]

    test = data[data.year_curr.isin([holdout_yrs])].copy()

    if past_yr:
        features = static_features + past[:past_yr]
    else:
        features = static_features + past[:predict_n_yr]

    label = future[(predict_n_yr - 1):predict_n_yr]

    X_test = test[features]
    Y_test = test[label]

    ind_yrs = data.year_curr.isin(test_train_yrs)
    train_valid = data[ind_yrs]
    train_valid = train_valid[features + label]
    train_valid.dropna(inplace=True)

    train_valid['yr'] = map(lambda x: x.split('_')[1],
                            train_valid.index.values)

    yrs = np.unique(map(lambda x: x.split('_')[1], train_valid.index.values))

    n_yrs = len(yrs)
    valid_split, train_split = cv_cut
    n_train_yrs = int(math.floor(n_yrs * train_split))
    n_valid_yrs = int(math.ceil(n_yrs * valid_split))

    train_yr_range = yrs[:n_train_yrs]
    valid_yr_range = yrs[-n_valid_yrs:]

    if Verbose:
        print 'features: ', features
        print 'label: ', label
        print 'predict_n_yr ', predict_n_yr
        print 'n_yrs', n_yrs
        print 'n_train_yrs', n_train_yrs
        print 'n_valid_yrs', n_valid_yrs
        print 'test_train_yrs', test_train_yrs
        print 'train_yr_range', train_yr_range
        print 'valid_yr_range', valid_yr_range
        print 'holdout_yrs', holdout_yrs

    if testing:
        return train_yr_range, valid_yr_range, holdout_yrs

    dic_year = {'train': train_yr_range,
                'valid': valid_yr_range,
                'test':  str(holdout_yrs)}

    X_train_yr_mask = train_valid['yr'].isin(train_yr_range)
    X_valid_yr_mask = train_valid['yr'].isin(valid_yr_range)

    Y_train_yr_mask = train_valid['yr'].isin(train_yr_range)
    Y_valid_yr_mask = train_valid['yr'].isin(valid_yr_range)

    X_train = train_valid[X_train_yr_mask][features]
    X_valid = train_valid[X_valid_yr_mask][features]

    Y_train = train_valid[Y_train_yr_mask][label]
    Y_valid = train_valid[Y_valid_yr_mask][label]

    return X_train, Y_train, X_valid, Y_valid, X_test, Y_test, dic_year


def run_models(clfs, visualize, break_window,
               X_train, Y_train, X_valid, Y_valid,
               cross_valname,
               results_dir='./../results/',
               dic_year=None,
               config=None,
               past_year=None):
    """
    Run models is the functions for looping over models and parameters
    and passing the results to full evaluation in evaluation.py


    Input
    -----
    clfs: ls
       list of the classifiers to use
    visualize: bool
       visualization flag
    break_window: str
       break window string (e.g., 1Year, 2Year, 3Year)
    (X_train, Y_train, X_valid, Y_valid): df
       df of the train and validation set
    results_dir: str
       dirname to store the results
    dic_year: dict
       pass in a dictionary of the year ranges
    config: obj
       containter obj for all the settings
    past_year: int
       Amount of years looking into the past
    """
    run_log_date = time.strftime("%d_%b_%Y_%H_%M_%S", time.gmtime())
    run_log_df = pd.DataFrame(columns=('run_log_date', 'model_id'))
    pkl_file_name = "./log/run_log_" + run_log_date + ".pkl"

    for clf in clfs:
        param_dict = config.parameters[clf]
        if config.all_parameters:
            param_grid = ParameterGrid(param_dict)

        else:
            param_grid = [ParameterGrid(param_dict)[0]]
        for parameter in param_grid:
            starttime = time.time()
            mdl = models.gen_model(
                X_train.values, Y_train.values.ravel(), clf, parameter)

            if hasattr(mdl, 'coef_'):
                feature_import = dict(
                    zip(X_train.columns.tolist(), mdl.coef_.ravel()))
            else:
                feature_import = dict(
                    zip(X_train.columns.tolist(), mdl.feature_importances_))
            label = Y_valid.columns.tolist()[0]
            assert len(Y_valid.columns.tolist()) == 1
            train_balance = check_balance(Y_train)

            y_predict_probs_valid = mdl.predict_proba(X_valid.values)[:, 1]
            Y_valid_for_eval = Y_valid.copy()
            Y_valid_for_eval['y_pred_proba'] = y_predict_probs_valid
            y_predict_probs_train = mdl.predict_proba(X_train.values)[:, 1]
            Y_train_for_eval = Y_train.copy()
            Y_train_for_eval['y_pred_proba'] = y_predict_probs_train

            # figure out how balanced the training set is
            outputs = {
                'timestamp': "{:.6f}".format(time.time()),
                'results_dir': results_dir + '/figures/',
                'full_results': config.writeToDB,
                'visualize': visualize,
                'use_imputed': True,
                'model_name': clf,
                'y_validate': Y_valid_for_eval,
                'y_train': Y_train_for_eval,
                'break_window': break_window,
                'features': X_train.columns.tolist(),
                'cross_val': cross_valname,
                'rebalancing': json.dumps(train_balance),
                'parameters': parameter,
                'date_dic': dic_year,
                'feature_import': feature_import,
                'static_features': config.static_features,
                'past_yr': past_year
            }

            if config.debug:
                pkl_name = "{0}_{1}_{2}.pkl".format(
                    outputs['timestamp'],
                    outputs['model_name'],
                    outputs['break_window'])

                pickle.dump(outputs,
                            open(pkl_name, "wb"))

                plot_to_pdf(Y_valid, y_predict_probs_valid,
                            results_dir + clf + label)

            if not(config.debug):
                full_evaluation(outputs)

            print clf, parameter, train_balance, "{:.2f}".format(time.time() - starttime)

            model_id_for_pkl = outputs['timestamp']
            run_log_df.loc[len(run_log_df)] = [run_log_date, model_id_for_pkl]
            run_log_df.to_pickle(pkl_file_name)


class CVError():
    pass


def run_pipeline(run_config):
    """
    Main function for running throug the pipeline

    #read the model config and run yaml file here.


    The run_pipeline does the following;

    - Load the configuration file
    - Load the data from the features table
    - Loops through break windows and past_yrs
    - In the loop implement a cross_validation strategy that
      is either "seventy_thirty' or 'no_overlap'
    - In the loop run through models and parameters.

    **If the debug flag is True then there will be no output
    to the DB.**

    **The writeToDB must be True to write to the DB**

    Input
    -----
    run_config: yaml object
        run configutaion for doing a run.

    """
    config = sett.SetContainer(run_config, model_config)
    data = get_feature_table(config.tablename)
    for break_window in config.break_windows:
        print break_window
        for _past_yr in config.past_years:
            print 'past_yr', _past_yr

            if config.cross_valname == 'seventy_thirty':
                pX_train, _Y_train, pX_valid, Y_valid, pX_test, Y_test, dic_year = \
                    train_valid_test_split(
                        data,
                        break_window,
                        config.static_features,
                        config.cv_cuts[
                            'thirty_seventy'],
                        config.past,
                        config.future,
                        past_yr=_past_yr,
                        config=config)


                X_train = dumify_categorical_features(pX_train)
                X_valid = dumify_categorical_features(pX_valid)
                X_test = dumify_categorical_features(pX_test)
                print dic_year
            elif config.cross_valname == 'no_overlap':
                _X_train, _Y_train, X_valid, Y_valid, X_test, Y_test, dic_year =\
                                            CV_no_overlap(break_window,
                                                          _past_yr,
                                                          data,
                                                          config)
            else:
                raise CVerror, 'no cross validation set'


            if config.downsample:
                for ls_dwn_smple in config.rebalancing:
                    X_train, Y_train = downsample(_X_train,
                                                  _Y_train,
                                                  downsample_balance=ls_dwn_smple)

                    X_train_cols = X_train.columns.tolist()
                    X_valid_cols = X_valid.columns.tolist()
                    X_test_cols = X_test.columns.tolist()

                    assert set(X_train_cols) == set(X_valid_cols)
                    assert set(X_train_cols) == set(X_test_cols)
                    assert set(X_test_cols) == set(X_valid_cols)

                    run_models(config.clfs,
                               config.visualize,
                               break_window,
                               X_train, Y_train, X_valid, Y_valid,
                               config.cross_valname,
                               results_dir=config.results_dir,
                               dic_year=dic_year,
                               config=config,
                               past_year=_past_yr)

            else:  # case of no down sampling then just rename

                X_train = _X_train
                Y_train = _Y_train

                run_models(config.clfs,
                           config.visualize,
                           break_window,
                           X_train, Y_train, X_valid, Y_valid,
                           config.cross_valname,
                           results_dir=config.results_dir,
                           dic_year=dic_year,
                           config=config,
                           past_year=_past_yr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        exit()
    else:
        run_yamlfile = sys.argv[1]
        run_config = yaml.load(open(run_yamlfile))
    run_pipeline(run_config)
