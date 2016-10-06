#!/usr/bin/env python
"""
functions for downsampling data
"""
import numpy as np
import math
import pandas as pd


def check_balance(Yt):
    """
    check the balance of a training set

    Input
    -----
    Yt: df
        DF of training labels.

    Output
    ------
    dic_balance: dic
        dictionary of 0s and 1s

    """
    n_train_labels = len(Yt)

    ls_label_cols = Yt.columns.tolist()
    assert len(ls_label_cols) == 1
    label = ls_label_cols[0]

    balance = {'break': round(
        np.sum(Yt[label] == 1.) / float(n_train_labels), 2 ),
               'no_break': round(
                   np.sum(Yt[label] == 0) / float(n_train_labels), 2 ),
               'n_points': len(Yt)}

    return balance


def downsample(pX,
               Yt,
               downsample_balance=[0.3, 0.7],
               Verbose=False):
    """
    downsample the training set

    Input
    -----
    pX: df
        DataFrame of features wiht block/year id to be downsampled. This is before
        the categorical features are dummified.
    Yt: df
        DataFrame of labels with block/year id to be downsampled.

    Output
    ------
    (downnsample_X, downsample_Y): df
        DataFrame of the new downsampled training set and labels.

    """

    n_train_labels = len(Yt)  # count number of labels #grab label
    ls_label_cols = Yt.columns.tolist()
    assert len(ls_label_cols) == 1
    label = ls_label_cols[0]

    if Verbose:
        print "Balance Before", check_balance(Yt)

    frac_breaks, frac_nobreaks = downsample_balance

    breaks = Yt[Yt[label] == 1]
    n_breaks = len(breaks)

    n_total = int(math.floor(n_breaks / frac_breaks))

    n_nobreaks = n_total - n_breaks

    nobreaks = Yt[Yt[label] == 0]
    nobreak_ids = np.random.choice(nobreaks.index, n_nobreaks, replace=False)
    nobreak_sample = nobreaks.ix[nobreak_ids, :]

    downsample_Y = pd.concat((breaks, nobreak_sample))

    if Verbose:
        print "Balance After", check_balance(downsample_Y)

    downsample_ind = downsample_Y.index
    downsample_X = pX.ix[downsample_ind, :]
    assert np.all(downsample_X.index == downsample_Y.index)

    return downsample_X, downsample_Y
