#!/usr/bin/env python
import settings as sett
from datafiles import model_config, test_run_config, test_csv
from pipeline import get_feature_table, train_valid_test_split
import numpy as np
import pandas as pd


def test_indices():
    config = sett.SetContainer(test_run_config, model_config)
    data = pd.read_csv(test_csv).set_index('block_year')

    for break_window in ['1Year', '2Year', '3Year']:
        print break_window
        for past_yr in range(1, 7):
            print past_yr
            pX_train, Y_train, pX_valid, Y_valid, pX_test, Y_test, dic_year = \
                train_valid_test_split(
                    data,
                    break_window,
                    config.static_features,
                    config.cv_cuts[
                        'thirty_seventy'],
                    config.past,
                    config.future,
                    past_yr=past_yr,
                    config=config)

            assert np.all(pX_train.index == Y_train.index)
            assert np.all(pX_valid.index == Y_valid.index)
            assert np.all(pX_test.index == Y_test.index)

            assert len(pX_valid.ix[pX_train.index, :].dropna()) == 0
            assert len(pX_valid.ix[pX_train.index, :].dropna()) == 0
            assert len(pX_test.ix[pX_train.index, :].dropna()) == 0
            assert len(pX_valid.ix[pX_train.index, :].dropna()) == 0


if __name__ == "__main__":
    test_indices()
