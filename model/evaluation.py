
import setup_environment
import pandas as pd

import numpy as np
from sklearn.metrics import precision_score, recall_score, precision_recall_curve, \
    confusion_matrix, roc_auc_score
from evaluation_functions import precision_at_k, recall_at_k, binarize_at_k

import matplotlib.pyplot as plt
plt.switch_backend('agg')

import seaborn as sns
sns.set_style('darkgrid')

from write_to_db import write_labels, write_to_result_stats, write_to_feature_importances


def test_evaluation():
    """
    Testing evaluation pipeline. Uses some test data
    """
    def demo_data():
        DEMO_QUERY = """
        select cast(street_id as varchar)||'_'||cast(year_curr as varchar) block_year, wo_next1 y_true, random() y_pred_proba
        from features.combined
        where year_curr != 2015
        limit 1000
        """
        from setup_environment import db_dict
        with setup_environment.connect_to_syracuse_db(**db_dict) as conn:
            data = pd.read_sql_query(
                DEMO_QUERY, conn, index_col=['block_year'])
        data.columns = ['y_true', 'y_pred_proba']
        return data

    TEST_OUTPUT = {
        'timestamp': '000000',
        'debug': True,
        'results_dir': './results/figures/',
        'full_results': True,
        'visualize': True,
        'use_imputed': True,
        'model_name': 'Test',
        'y_validate': demo_data(),
        'y_train': demo_data(),
        'break_window': 'wo_next1',
        'features': ['diameters', 'pipe_age', 'musym_Ub'],
        'cross_val': 'seventy_thirty',
        'rebalancing': 'none',
        'parameters': {'C': 0.01, 'penalty': 'l1'},
        'date_dic': {'train': [2004, 2005, 2006],
                     'valid': [2007, 2008],
                     'test':  2014},
        'feature_import': {'wo_curr': 0.07,
                           'diameters': 0.25},
        'static_features': ['diameters', 'pipe_age'],
        'past_yr': 2
    }

    full_evaluation(TEST_OUTPUT)


def plot_score_distribution(y_pred, so):
    """ Plots scores of predicted values """
    min_x = min(min(y_pred), 0)
    max_x = max(max(y_pred), 1)
    sns.distplot(y_pred, kde=False)
    plt.title("distribution of scores for {} model".format(so['model_name']))
    plt.xlabel("raw prediction score")
    plt.xlim([min_x, max_x])
    plt.ylabel("number of street segments")
    base = so['results_dir'] + so['model_name'] + "_" + \
        str(so['timestamp']) + "_" + so['break_window']
    plt.savefig(base + '_score_distribution.png', bbox_inches='tight')
    plt.close()


def plot_precision_recall_n(y_true, y_prob, so):
    # from Rayid's magicloops code
    y_score = y_prob
    precision_curve, recall_curve, pr_thresholds = precision_recall_curve(
        y_true, y_prob)
    precision_curve = precision_curve[:-1]
    recall_curve = recall_curve[:-1]
    pct_above_per_thresh = []
    number_scored = len(y_prob)
    for value in pr_thresholds:
        num_above_thresh = len(y_score[y_prob >= value])
        pct_above_thresh = num_above_thresh / float(number_scored)
        pct_above_per_thresh.append(pct_above_thresh)
    pct_above_per_thresh = np.array(pct_above_per_thresh)
    plt.clf()
    fig, ax1 = plt.subplots()
    ax1.plot(pct_above_per_thresh, precision_curve, 'b')
    ax1.set_xlabel('percent of population')
    ax1.set(ylim=(0, 1))

    ax1.set_ylabel('precision', color='b')
    ax2 = ax1.twinx()
    ax1.plot(pct_above_per_thresh, recall_curve, 'r')
    ax2.set_ylabel('recall', color='r')

    base = so['results_dir'] + so['model_name'] + "_" + \
        str(so['timestamp']) + "_" + so['break_window']
    plt.savefig(base + '_precision_recall_n.png', bbox_inches='tight')
    plt.close()


def calc_confusion_matrix(y_true, y_prob, k):
    """ Calculates confusion matrix given some set of y_true, predicted values y_prob, and a threshold """
    cm = confusion_matrix(y_true, binarize_at_k(y_prob, k))
    return cm


def show_confusion_matrix(C, so, class_labels=['0', '1']):
    """
    C: ndarray, shape (2,2) as given by scikit-learn confusion_matrix function
    class_labels: list of strings, default simply labels 0 and 1.

    Draws confusion matrix with associated metrics.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    assert C.shape == (
        2, 2), "Confusion matrix should be from binary classification only."

    # true negative, false positive, etc...
    tn = C[0, 0]
    fp = C[0, 1]
    fn = C[1, 0]
    tp = C[1, 1]

    NP = fn + tp  # Num positive examples
    NN = tn + fp  # Num negative examples
    N = NP + NN

    fig = plt.figure(figsize=(8, 8))

    ax = fig.add_subplot(111)
    ax.imshow(C, interpolation='nearest', cmap=plt.cm.Blues)

    # Draw the grid boxes
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(2.5, -0.5)
    ax.plot([-0.5, 2.5], [0.5, 0.5], '-k', lw=2)
    ax.plot([-0.5, 2.5], [1.5, 1.5], '-k', lw=2)
    ax.plot([0.5, 0.5], [-0.5, 2.5], '-k', lw=2)
    ax.plot([1.5, 1.5], [-0.5, 2.5], '-k', lw=2)

    # Set xlabels
    ax.set_xlabel('Predicted Label', fontsize=16)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(class_labels + [''])
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    # These coordinate might require some tinkering. Ditto for y, below.
    ax.xaxis.set_label_coords(0.34, 1.06)

    # Set ylabels
    ax.set_ylabel('True Label', fontsize=16, rotation=90)
    ax.set_yticklabels(class_labels + [''], rotation=90)
    ax.set_yticks([0, 1, 2])
    ax.yaxis.set_label_coords(-0.09, 0.65)

    # Fill in initial metrics: tp, tn, etc...
    ax.text(0, 0,
            'True Neg: %d\n(Num Neg: %d)' % (tn, NN),
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    ax.text(0, 1,
            'False Neg: %d' % fn,
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    ax.text(1, 0,
            'False Pos: %d' % fp,
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    ax.text(1, 1,
            'True Pos: %d\n(Num Pos: %d)' % (tp, NP),
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    # Fill in secondary metrics: accuracy, true pos rate, etc...
    ax.text(2, 0,
            'False Pos Rate: %.2f' % (fp / (fp + tn + 0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    ax.text(2, 1,
            'True Pos Rate: %.2f' % (tp / (tp + fn + 0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    ax.text(2, 2,
            'Accuracy: %.2f' % ((tp + tn + 0.) / N),
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    ax.text(0, 2,
            'Neg Pre Val: %.2f' % (1 - fn / (fn + tn + 0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    ax.text(1, 2,
            'Pos Pred Val: %.2f' % (tp / (tp + fp + 0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w', boxstyle='round,pad=1'))

    base = so['results_dir'] + so['model_name'] + "_" + \
        str(so['timestamp']) + "_" + so['break_window']
    plt.savefig(base + '_confusion_matrix.png', bbox_inches='tight')
    plt.close()


def full_evaluation(so):
    """
    Given some set of data from a model run so (saved_output),
    generates figures and stores model predictions and summary stats
    in .png and SQL
    """
    rename_columns = {'wo_next1': 'y_true',
                      'wo_next2': 'y_true', 'wo_next3': 'y_true'}
    y_validate = so['y_validate']
    y_validate.rename(columns=rename_columns, inplace=True)
    y_train = so['y_train']
    y_train.rename(columns=rename_columns, inplace=True)

    if so['full_results'] == True:
        write_to_result_stats(so)
        write_to_feature_importances(so)
        write_labels(so['y_validate'], so['timestamp'], tablename='valid')
        write_labels(so['y_train'], so['timestamp'], tablename='train')
    if so['visualize'] == True:
        plot_score_distribution(y_validate['y_pred_proba'], so)
        plot_precision_recall_n(
            y_validate['y_true'], y_validate['y_pred_proba'], so)
        cm = calc_confusion_matrix(y_validate['y_true'], y_validate[
                                   'y_pred_proba'], 0.05)
        show_confusion_matrix(cm, so)


if __name__ == '__main__':
    test_evaluation()
