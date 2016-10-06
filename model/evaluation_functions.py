from sklearn.metrics import precision_score, recall_score
import numpy as np


def precision_at_k(y_true, y_scores, k):
    # from Rayid's magicloops code
    if np.all(y_true.isnull()):
        return None
    y_pred = binarize_at_k(y_scores, k)
    return precision_score(y_true, y_pred)


def recall_at_k(y_true, y_scores, k):
    # from Rayid's magicloops code
    if np.all(y_true.isnull()):
        return None
    y_pred = binarize_at_k(y_scores, k)
    return recall_score(y_true, y_pred)


def binarize_at_k(y_scores, k):
    threshold = np.sort(y_scores)[::-1][int(k * len(y_scores))]
    y_pred = np.asarray([1 if i >= threshold else 0 for i in y_scores])
    return y_pred
