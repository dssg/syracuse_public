#!/usr/bin/env python
from __future__ import print_function
import settings as sett
from datafiles import model_config, test_run_config, test_csv
from pipeline import get_feature_table, train_valid_test_split
import numpy as np
import pandas as pd



def test_3window():
    config = sett.SetContainer(test_run_config, model_config)
    data = pd.read_csv(test_csv).set_index('block_year')
    label = '3Year'

    train_yrs, valid_yrs, test_yrs = train_valid_test_split(data,
                                                            label,
                                                            config.static_features,
                                                            config.cv_cuts[
                                                                'thirty_seventy'],
                                                            config.past,
                                                            config.future,
                                                            past_yr=0,
                                                            testing=True,
                                                            Verbose=True)

    train_yrs = np.array(train_yrs, dtype=int)
    valid_yrs = np.array(valid_yrs, dtype=int)


    print(train_yrs)
    assert np.all(np.array(range(2006, 2010)) == train_yrs), train_yrs
    assert np.all(np.array(range(2010, 2012)) == valid_yrs), valid_yrs
    assert 2012 == test_yrs


def test_1window():
    config = sett.SetContainer(test_run_config, model_config)
    data = pd.read_csv(test_csv).set_index('block_year')
    label = '1Year'

    train_yrs, valid_yrs, test_yrs = train_valid_test_split(data,
                                                            label,
                                                            config.static_features,
                                                            config.cv_cuts[
                                                                'thirty_seventy'],
                                                            config.past,
                                                            config.future,
                                                            testing=True)

    train_yrs = np.array(train_yrs, dtype=int)
    valid_yrs = np.array(valid_yrs, dtype=int)
    test_yrs = np.array(test_yrs, dtype=int)

    assert np.all(np.array(range(2004, 2011)) == train_yrs)
    assert np.all(np.array(range(2011, 2014)) == valid_yrs)
    assert 2014 == test_yrs


def test_3roving_window():
    config = sett.SetContainer(test_run_config, model_config)
    data = pd.read_csv(test_csv).set_index('block_year')
    label = '3Year'
    start_yr = 2004
    for _past_yr in range(1, 7):
        train_yrs, valid_yrs, test_yrs = train_valid_test_split(data,
                                                                label,
                                                                config.static_features,
                                                                config.cv_cuts[
                                                                    'thirty_seventy'],
                                                                config.past,
                                                                config.future,
                                                                past_yr=_past_yr,
                                                                testing=True)

        train_yrs = np.array(train_yrs, dtype=int)
        valid_yrs = np.array(valid_yrs, dtype=int)
        test_yrs = np.array(test_yrs, dtype=int)

        assert train_yrs[0] == (start_yr - 1) + _past_yr
        assert valid_yrs[-1] == 2011
        assert 2012 == test_yrs


def test_1roving_window():
    config = sett.SetContainer(test_run_config, model_config)
    data = pd.read_csv(test_csv).set_index('block_year')
    label = '1Year'
    start_yr = 2004
    for _past_yr in range(1, 7):
        train_yrs, valid_yrs, test_yrs = train_valid_test_split(data,
                                                                label,
                                                                config.static_features,
                                                                config.cv_cuts[
                                                                    'thirty_seventy'],
                                                                config.past,
                                                                config.future,
                                                                past_yr=_past_yr,
                                                                testing=True)

        train_yrs = np.array(train_yrs, dtype=int)
        valid_yrs = np.array(valid_yrs, dtype=int)
        test_yrs = np.array(test_yrs, dtype=int)

        assert train_yrs[0] == (start_yr - 1) + _past_yr
        assert valid_yrs[-1] == 2013
        assert 2014 == test_yrs


if __name__ == "__main__":
    test_3window()
