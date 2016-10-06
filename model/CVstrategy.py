import pandas as pd
import numpy as np
from datafiles import test_run_config, model_config
import settings as sett

dict_yrs = { '3Year': 3,
             '2Year': 2,
             '1Year': 1}


dict_label = {'3Year': 'wo_next3',
             '2Year': 'wo_next2',
             '1Year': 'wo_next1'}

class LabelError():
    pass


def _dummy_text_feature(data, feature):
    """ Generates dummy columns for a categorical variable """
    dummies = pd.get_dummies(data[feature], prefix=feature, dummy_na=True)
    return dummies


def _dumify_categorical_features(df):
    """
    Dummfies all categorical features that are read in
    as objects

    Input
    -----
    df: DataFrame
        DataFrame with the columns to be dummified


    Output
    ------
    dummy_df: DataFrame
         Dummified Output
    """
    prepped = pd.DataFrame(index=df.index)
    for feature in df.columns:
        # print feature, df.dtypes[feature]
        if df.dtypes[feature] == 'object':
            dummied = _dummy_text_feature(df, feature)
            prepped = prepped.join(dummied)
        else:
            prepped = prepped.join(df[feature])
    return prepped


def calc_fake_today(label,
                    past_yrs,
                    min_yr=2004,
                    max_yr=2016):
    """
    calculate the necessary fake todays

    Input
    -----
    label: str
       label of time frame to predict a break
    past_yrs: int
       number of years you are looking into the past
    min_yr: int
       beginning of the time range there is data for
    max_yr: int
       one year **after** the time range there is data for

    Output
    ------
    fake_todays: ls
       ls of fake_todays the first is the fake_today
       of the test set, seceond is the fake today of the
       validation set, thrid and onward are fake todays
       for the training set.
    """
    yr_range = np.array( range(min_yr, max_yr), dtype=int)
    sub_yr_range = yr_range[(past_yrs-1):]
    return sub_yr_range[::-dict_yrs[label]][1:]



def get_fake_todays(label, past_yrs):
    """
    get the necessary fake todays

    Input
    -----
    label: str
       label of time frame to predict a break
    past_yrs: int
       number of years you are looking into the past

    Output
    ------
    (test_today, vaid_today) int
       years to the test and valid set

    ls_train_today: ls
       ls of years to to train

    """
    fake_todays = calc_fake_today(label, past_yrs)
    test_today = fake_todays[0]
    valid_today = fake_todays[1]
    train_today = fake_todays[2:]

    return test_today, valid_today, train_today


def CV_no_overlap(label, past_yr, data, config):
    """
    CV_no_cheaing or no overlap is a CV strategy
    where the train, valid and test set never have
    labels persist as they would in a window strategy.

    Input
    -----
    label: str
       Prediction: 3Year, 2Year, 1Year
    past_yr: int
       Number of years looking into the past
    data: df
       Contains the feature and the labels
    config: obj
       Config Object from settings.py

    Output
    ------
    (X_train, Y_train, X_valid, Y_valid, X_test, Y_test, dic_year): df
        Contains the train, valid, test set features and labels.


    TODO: Output a named tuple instead of just 7 things
    """
    test_today, valid_today, ls_train = get_fake_todays(label, past_yr)
    if config.use_nearby_wo:
        features = config.static_features + config.past[:past_yr] +\
                   config.nearby_wo[:past_yr]
    else:
        features = config.static_features + config.past[:past_yr]

    sel_cols = features + ['year_curr']


    df_features = data[sel_cols]
    df_dum_features = _dumify_categorical_features(df_features)

    X_test_mask =  df_dum_features.year_curr.isin( [test_today] )
    X_test = df_dum_features[X_test_mask].copy()
    X_test.drop('year_curr', axis=1, inplace=True)
    X_test = X_test.dropna()
    Y_test = pd.DataFrame( data.ix[X_test.index,dict_label[label]] )

    X_valid_mask = df_dum_features.year_curr.isin( [valid_today] )
    X_valid = df_dum_features[X_valid_mask].copy()
    X_valid.drop('year_curr', axis=1, inplace=True)
    X_valid = X_valid.dropna()
    Y_valid = pd.DataFrame( data.ix[X_valid.index,dict_label[label]] )

    X_train_mask = df_dum_features.year_curr.isin( ls_train )
    X_train = df_dum_features[X_train_mask].copy()
    X_train.drop('year_curr', axis=1, inplace=True)
    X_train = X_train.dropna()
    Y_train = pd.DataFrame( data.ix[X_train.index,dict_label[label]] )



    assert np.all(X_train.index == Y_train.index)
    assert np.all(X_valid.index == Y_valid.index)
    assert np.all(X_test.index == Y_test.index)


    X_train_colset = set(X_train.columns.tolist())
    X_valid_colset = set(X_valid.columns.tolist())
    X_test_colset = set(X_test.columns.tolist())

    #check that all the columns are the same
    assert X_train_colset == X_valid_colset
    assert X_train_colset == X_test_colset
    assert X_valid_colset == X_test_colset


    assert np.all( np.unique(
        X_train.index.map(lambda x: x.split('_')[1]) ) == np.array(ls_train, dtype=str))
    assert np.unique(
        X_valid.index.map(lambda x: x.split('_')[1]) ) == [str(valid_today)]
    assert np.unique(
        X_test.index.map(lambda x: x.split('_')[1]) ) == [str(test_today)]



    dict_year = {'test': test_today,
                'valid': np.array(range(valid_today, test_today),dtype='str'),
                'train': np.array(ls_train)}

    return X_train, Y_train, X_valid, Y_valid, X_test, Y_test, dict_year


def get_features_label(fake_today, label, past_yr, data, config, Verbose=False):
    """
    given a label and past years this will return two
    DFs of the feature set dummified and labels.

    Input
    -----
    fake_today: ls
       Fake years that we are looking at.
    label: str
       Number of years out that we are trying to predict a
       main break.
    past_yr: int
       Number of years we are looking into the past
    data: df
       DataFrame with possible features and labels
    config: obj
       object that comtains all the configuation settings
    Verbose: bool


    Ouput
    -----
    df_features: df
    df_labels: df
    """
    if config.use_nearby_wo:
        features = config.static_features + config.past[:past_yr] +\
                   config.nearby_wo[:past_yr]
    else:
        features = config.static_features + config.past[:past_yr]

    sel_cols = features + ['year_curr']

    df_features = data[sel_cols]
    df_dum_features = _dumify_categorical_features(df_features)

    X_mask =  df_dum_features.year_curr.isin( fake_today )
    X = df_dum_features[X_mask].copy()
    X.drop('year_curr', axis=1, inplace=True)
    X = X.dropna()
    Y = pd.DataFrame( data.ix[X.index,dict_label[label]] )
    return X, Y
