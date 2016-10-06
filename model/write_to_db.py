import pickle
import json
import pandas as pd
import numpy as np
from evaluation_functions import precision_at_k, recall_at_k
from setup_environment import db_dict, get_dbengine
engine = get_dbengine(**db_dict)

rename_columns={'wo_next1': 'y_true', 'wo_next2': 'y_true', 'wo_next3': 'y_true'}


def write_labels(df, timestamp, tablename=''):
    y = df.copy()
    y.rename(columns=rename_columns, inplace=True)
    nrows = len(y)
    y['model_id'] = [timestamp] * nrows
    y = y.reset_index()
    y['block_id'] = y['block_year'].map(lambda x: x.split('_')[0])
    y['year'] = y['block_year'].map(lambda x: x.split('_')[1])
    y.to_sql(name=tablename, schema='model', con=engine,
             if_exists='append', index=False)


def get_yr_range(np_yr_range):
    min_yr = np.array(np_yr_range, dtype=int).min()
    max_yr = np.array(np_yr_range, dtype=int).max()
    return '{0}-{1}'.format(min_yr, max_yr)


def write_to_result_stats(outputs):

    y_validate = outputs['y_validate']
    y_validate.rename(columns=rename_columns, inplace=True)

    results_rows = {'model_id': outputs['timestamp'],
                    'break_window': outputs['break_window'],
                    'model_name': outputs['model_name'],
                    'cross_val': outputs['cross_val'],
                    'train_range': get_yr_range(outputs['date_dic']['train']),
                    'valid_range': get_yr_range(outputs['date_dic']['valid']),
                    'test_today':  outputs['date_dic']['test'],
                    'rebalancing': outputs['rebalancing'],
                    'use_imputed': outputs['use_imputed'],
                    'features': ','.join(outputs['features']),
                    'static_features': ','.join(outputs['static_features']),
                    'past_year': outputs['past_yr'],
                    'parameters': json.dumps(outputs['parameters']),
                    'precision_at_pt5': precision_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.005),
                    'precision_at_1': precision_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.01),
                    'precision_at_2': precision_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.02),
                    'precision_at_5': precision_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.05),
                    'precision_at_10': precision_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.1),
                    'recall_at_pt5': recall_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.005),
                    'recall_at_1': recall_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.01),
                    'recall_at_2': recall_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.02),
                    'recall_at_5': recall_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.05),
                    'recall_at_10': recall_at_k(y_validate['y_true'], y_validate['y_pred_proba'], 0.1),
                    }

    df = pd.DataFrame([results_rows])
    df.to_sql(name='results_stats', schema='model',
              con=engine, if_exists='append', index=False)


def write_to_feature_importances(outputs):
    df_feature_importance = pd.DataFrame(
        outputs['feature_import'].items(), columns=['feature', 'importance'])
    n_feature_importance = len(df_feature_importance)
    df_feature_importance['model_id'] = [
        outputs['timestamp']] * n_feature_importance
    df_feature_importance.to_sql(
        name='feature_importances', schema='model', con=engine, if_exists='append', index=False)
