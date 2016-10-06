"""
Models
======

Contains the code for grabbing the models for the experiments
"""
from sklearn import __version__
from sklearn import linear_model
from sklearn import neighbors
from sklearn import tree
from sklearn import ensemble
from sklearn import naive_bayes
from sklearn import svm
from sklearn import discriminant_analysis
import numpy as np


class ConfigError():
    pass


def gen_model(train_X, train_Y, modelname, parameters=None):
    """
    Generates a model and predicts on the test set. Returns
    the model and results.
    Input
    -----
    train_X: numpy array
       array of features from the training set (n_samples, n_features)
    train_Y: numpy array
       array of labels from the training set (n_samples,)
    model: str
       name of the model e.g. Logistic Regression
    parameters: dict
       dictionary of parameters for a specific model
    Output
    ------
    model: obj
      Trained model
    """

    clf = define_model(modelname)
    clf.set_params(**parameters)
    clf.fit(train_X, train_Y)
    return clf


def define_model(modelname):
    """
    Outputs model type and parameters

    Input
    ----
    model: str
       model type e.g., Logistic Regression
    parameters: ls
       hyperparameters of corresponding model

    Output
    ------
    clf: model object
       Model Object Classifier

    """
    if modelname == 'LR':
        return linear_model.LogisticRegression()
    elif modelname == 'NN':
        return neighbors.KNeighborsClassifier()
    elif modelname == 'DT':
        return tree.DecisionTreeClassifier()
    elif modelname == 'RF':
        return ensemble.RandomForestClassifier()
    elif modelname == 'NB':
        return naive_bayes.GaussianNB()
    elif modelname == 'SVM':
        return svm.SVC()
    elif modelname == 'ET':
        return ensemble.ExtraTreesClassifier()
    elif modelname == 'SGD':
        return linear_model.SGDClassifier()
    elif modelname == 'AB':
        return ensemble.AdaBoostClassifier(
            tree.DecisionTreeClassifier(max_depth=1)
        )
    elif modelname == 'GB':
        return ensemble.GradientBoostingClassifier()
    elif modelname == 'VC':
        return ensemble.VotingClassifier(estimators=[
            ('RFC', ensemble.RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)), ('ETC', ensemble.ExtraTreesClassifier(max_depth=None, max_features=5, n_estimators=10, random_state=0, min_samples_split=1)), ('ABC', ensemble.AdaBoostClassifier())],
            voting='soft')
    elif modelname == 'VC2':
        return ensemble.VotingClassifier(estimators=[
            ('LR', linear_model.LogisticRegression(C=0.1, random_state=1)), ('RFC', ensemble.RandomForestClassifier(max_depth=None, n_estimators=10, random_state=0, min_samples_split=1)), ('ETC', ensemble.ExtraTreesClassifier(max_depth=None, max_features=5, n_estimators=10, random_state=0, min_samples_split=1))],
            voting='soft')

    else:
        raise ConfigError("Can't find the model: {}".format(model))
