#!/usr/bin/env python
"""
Results-analysis
================

Description
-----------
Syracuse results analysis

Usage
-----
./ranalysis.py run_log.pkl 

"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import scale
from pipeline import get_data


#-----------------------------------#

def run_feature_heatmap():
    tablename= "model.results_stats"
    break_window = "'3Year'"
    past_year = "6"
    static_features = "'diameters,pipe_age,install_year_imputed,musym,rocktype1,rocktype2,zone_name,material_imputed'"
    query_models = ('select model_id,model_name'
             ' from '+tablename+
             ' where break_window = '+break_window+
             ' and past_year = '+past_year+
             ' and static_features = '+static_features
            )
    print query_models

    model_df = get_data(query_models)
    model_name_list = list(model_df.model_name)
    model_id_list = list(model_df.model_id.values.ravel())

    model_id_list_str = "'"+"','".join(map(str, model_id_list))+"'"

    tablename= "model.feature_importances"
    query_features =('select *'
                     ' from '+tablename+
                     ' where model_id in ('+model_list_str+')'
                    )
    print query_features

    feature_imp = get_data(query_features)

    #Check if all models have the same features
    for model_id in model_id_list:
        for i in (feature_imp.feature[feature_imp.model_id == model_id].sort_values(inplace=False) == feature_imp.feature[feature_imp.model_id == '1471225699.39507699'].sort_values(inplace=False)):
            if i == False:
                print model_id

    feature_names_list = list(feature_imp.feature[feature_imp.model_id == '1471225699.39507699'].sort_values(inplace=False))

    feature_imp_matrix = pd.DataFrame
              
    for model_id in model_list[:1]:
        feature_imp_matrix = feature_imp[feature_imp.model_id == model_id].sort_values("feature", inplace=False).importance.values
        
    for model_id in model_list[1:]:
        b = feature_imp[feature_imp.model_id == model_id].sort_values("feature", inplace=False).importance.values
        feature_imp_matrix = np.vstack((feature_imp_matrix, b))

    feature_imp_matrix_normd = scale(np.transpose(feature_imp_matrix),axis=0,with_mean=True, with_std=True, copy=True)
    feature_imp_matrix_normd.shape

    plt.figure(figsize=(50,50))
    sns.heatmap(feature_imp_matrix_normd
                #, annot=True            
                , square = True
                , linewidths=0.5
                , yticklabels=feature_names_list
                , xticklabels=model_names_list
               )
    plt.savefig('feature_model_heatmap.png', bbox_inches='tight')
    plt.close()

#-----------------------------------#

def gen_decile_table(model_top_precision, valid_df): 
    """ Creates the decile table """

    valid_top_precision_df = valid_df[valid_df.model_id == model_top_precision]

    valid_dec_sort_df = valid_top_precision_df.sort_values('y_pred_proba', ascending = False)
    total_breaks = valid_dec_sort_df.y_true.sum()
    total_blocks = len(valid_dec_sort_df)
    dec_breaks = total_breaks / 10
    dec_blocks =  total_blocks / 10

    decile_df = pd.DataFrame(columns=('model_id','Decile', 'No_of_blocks','risk_mul', 'Actual_breaks', 'Precision_in_decile', 'Recall_overall', 'Lift_above_random'))
    for i in range(10):
        break_sum = valid_dec_sort_df.y_true[i*dec_blocks:(i+1)*dec_blocks].sum()
        risk_mul = valid_dec_sort_df.y_pred_proba[i*dec_blocks:(i+1)*dec_blocks].sum()
        lift = break_sum / dec_breaks
        conversion = break_sum *100 / dec_blocks
        recall = break_sum *100 / total_breaks
        decile_df.loc[len(decile_df)] = [model_top_precision,i+1,dec_blocks,risk_mul ,break_sum, conversion, recall, lift]
    decile_df.loc[len(decile_df)] = ['-', 'Total',total_blocks, '_' ,total_breaks, total_breaks/total_blocks, '-', '-']
    
    writer = pd.ExcelWriter('decile_table.xlsx', engine='xlsxwriter')
    decile_df.to_excel(writer, sheet_name='Sheet1')


def gen_valid_matrix(model_id_list, valid_df):

    valid_matrix = pd.DataFrame
    for model_id in model_id_list[:1]:
        valid_matrix = valid_df[valid_df.model_id == model_id].y_pred_proba.values
    for model_id in model_id_list[1:]:
        b = valid_df[valid_df.model_id == model_id].y_pred_proba.values
        valid_matrix = np.vstack((valid_matrix, b))
    
    return valid_matrix


def gen_feature_imp_matrix(model_id_list, features_df):

    feature_imp_matrix = pd.DataFrame
    for model_id in model_id_list[:1]:
        feature_imp_matrix = features_df[features_df.model_id == model_id].sort_values("feature", inplace=False).importance.values
    for model_id in model_id_list[1:]:
        b = features_df[features_df.model_id == model_id].sort_values("feature", inplace=False).importance.values
        feature_imp_matrix = np.vstack((feature_imp_matrix, b))
    feature_imp_matrix_normd = scale(np.transpose(feature_imp_matrix),axis=0,with_mean=True, with_std=True, copy=True)

    return feature_imp_matrix_normd

    
def save_plot(matrix_to_plot, x_label,y_label, plot_name):
    plt.figure(figsize=(50,50))
    sns.heatmap(matrix_to_plot
                #, annot=True            
                , square = True
                , linewidths=0.5
                , yticklabels=y_label
                , xticklabels=x_label
                )
    plt.savefig(plot_name, bbox_inches='tight')
    plt.close()


def run_results_analysis(run_log_df):
    
    model_id_list = list(run_log_df.model_id)
    model_id_list_str = "'"+"','".join(map(str, model_id_list))+"'"
    
    results_stats_tablename= "model.results_stats"
    query_results_stats =('select *'
                    ' from '+results_stats_tablename+
                    ' where model_id in ('+model_id_list_str+')'
                )
    results_stats_df= get_data(query_results_stats)

    valid_tablename= "model.valid"
    query_valid =('select *'
                    ' from '+valid_tablename+
                    ' where model_id in ('+model_id_list_str+')'
                )
    #valid_df= get_data(query_valid)

    features_tablename= "model.feature_importances"
    query_features =('select *'
                     ' from '+features_tablename+
                     ' where model_id in ('+model_id_list_str+')'
                    )
    #features_df= get_data(query_features)

    model_top_precision = list(results_stats_df.sort_values('precision_at_1', ascending=False)['model_id'])[0]

    valid_top_precision_tablename= "model.valid"
    query_valid_top_precision =('select *'
                    ' from '+valid_top_precision_tablename+
                    " where model_id in ('"+model_top_precision+"')"
                )
    print query_valid_top_precision
    
    valid_top_precision_df = get_data(query_valid_top_precision)
    gen_decile_table(model_top_precision, valid_top_precision_df)

    #model_names_list = list(results_stats_df.model_name)
    #feature_names_list = list(features_df.feature[features_df.model_id == model_top_precision].sort_values(inplace=False))

    #feature_imp_matrix_normd = gen_feature_imp_matrix(model_id_list, features_df)
    #save_plot(feature_imp_matrix_normd,model_names_list,feature_names_list,"feature_importance_heatmap.png")

    #valid_matrix = gen_valid_matrix(model_id_list, valid_df)
    #valid_block_year_list = list(valid_df.block_year[valid_df.model_id == model_top_precision])
    #valid_y_true_list = list(valid_df.y_true[valid_df.model_id == model_top_precision])
    #valid_block_year_y_true_list=map(lambda a,b: str(a)+": "+str(b) ,valid_h_block_year_list,valid_h_y_true_list)

    #save_plot(valid_matrix,model_names_list,valid_block_year_y_true_list,"valid_block_y_true_heatmap.png")

    

#-----------------------------------#

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        exit()
    else:
        
        pkl_file_name = sys.argv[1]
        run_log_df = pd.read_pickle(pkl_file_name)

        run_results_analysis(run_log_df)

