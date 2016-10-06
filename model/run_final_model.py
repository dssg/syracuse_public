"""
This script runs the final model. Parametes are
shown below.

-Run an ExtraTrees (ET) model with the following parameter set:

max_depth: [100, 500]
max_features: [log2, sqrt]
n_estimators: [100, 500]
random_state: [1]
min_samples_split: [1]

"""
from datafiles import test_run_config, model_config
import settings as sett
from pipeline import get_feature_table, run_models
from CVstrategy import get_features_label

config = sett.SetContainer(test_run_config, model_config)
data = get_feature_table(config.tablename)

fake_train_today = [2009, 2010, 2011, 2012]
fake_valid_today = [2015]
break_window = '3Year'
past_yr = 6

X_train, Y_train = get_features_label(fake_train_today,
                                      break_window,
                                      past_yr,
                                      data, config)
X_valid, Y_valid = get_features_label(fake_valid_today,
                                      break_window,
                                      past_yr,
                                      data, config)

config.cross_valname = 'test_GB'

dic_year = {'train': fake_train_today, 'valid': fake_valid_today, 'test': 2015}

run_models(config.clfs,
           config.visualize,
           break_window,
           X_train, Y_train, X_valid, Y_valid,
           config.cross_valname,
           results_dir=config.results_dir,
           dic_year=dic_year,
           config=config,
           past_year=past_yr)
