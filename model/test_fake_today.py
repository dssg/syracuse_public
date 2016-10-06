# IPython log file
import numpy as np
from CVstrategy import calc_fake_today


def test_3year():
    label = '3Year'
    past_yr = 3
    test_today, valid_today, ls_train = calc_fake_today(label, past_yr)
    assert 2012 == test_today
    assert 2009 == valid_today
    assert 2006 == ls_train

def test_2year():
    label = '2Year'
    past_yr = 2
    fake_todays = calc_fake_today(label, past_yr)
    assert 2013 == fake_todays[0]
    assert 2011 == fake_todays[1]
    assert np.all(
        np.array([2009,2007, 2005]) == fake_todays[2:])
