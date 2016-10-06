import settings as sett
from datafiles import model_config, test_run_config, test_csv
from pipeline import train_valid_test_split
import numpy as np
import math
import pandas as pd
from downsample import check_balance, downsample


def test_balance():
    """

    Test the configuration in the run.yaml file
    """
    config = sett.SetContainer(test_run_config, model_config)
    assert type(config.downsample) == bool


def test_balance_set():
    """

    Given a set of labels of a training set
    balance_set will determine how balanced the
    set is and then downsample to a specfied proportion

    Input
    -----
    fraction_1s: float
       fraction of ones we want
    fraction_0s: float
       fraction of zeros we want

    Output
    ------
    labels: ls
       index of labels that have the proper portion to
       downsample
    """
    config = sett.SetContainer(test_run_config, model_config)
    #data = get_feature_table(config.tablename)
    data = pd.read_csv(test_csv).set_index('block_year')
    break_window = '2Year'
    pX_train, Y_train, pX_valid, Y_valid, pX_test, Y_test, date_dic = train_valid_test_split(
        data,
        break_window,
        config.static_features,
        config.cv_cuts['thirty_seventy'],
        config.past,
        config.future,
        past_yr=4)

    ls_balance = [[0.3, 0.7], [0.2, 0.8], [0.1, 0.9], [0.5, 0.5]]
    for balance in ls_balance:
        break_bal, nobreak_bal = balance
        X_bal, Y_bal = downsample(
            pX_train,
            Y_train,
            downsample_balance=balance,
            Verbose=True)

        print 'Y_train: ', np.sum(Y_train == 1)
        print check_balance(Y_train)
        balance_after = check_balance(Y_bal)
        assert np.isclose(
            break_bal, balance_after['break'], atol=1e-4), '{} {}'.format(break_bal, balance_after['break'])
        assert np.isclose(nobreak_bal, balance_after['no_break'], atol=1e-4)
        print balance_after
