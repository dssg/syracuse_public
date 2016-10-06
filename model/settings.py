"""

Container for settings that come from the YAML file
"""

def set_value(key,
              var_name,
              dict_config,
              default=False):
    """
    set_values in the settings
    """

    if dict_config.has_key(key):
        self.var_name = dict_config[key]
    else:
        self.var_name = default



class SetContainer(object):
    """

    Container class for settings of a run. Consumes
    the variables in run.yaml and model.yaml

    """

    def __init__(self, run_config, model_config):
        self.run_config = run_config
        self.model_config = model_config
        self.break_windows = run_config['break_windows']
        self.tablename = model_config['features_table']
        self.past = model_config['past_cols']
        self.future = model_config['future_cols']
        self.clfs = run_config['models']
        self.debug = run_config['debug']
        self.writeToDB = run_config['writeToDB']
        self.results_dir = model_config['results_dir']

        if run_config.has_key('visualize'):
            self.visualize = run_config['visualize']
        else:
            self.visualize = True

        if run_config.has_key('cross_val'):
            self.cv_cuts = run_config['cross_val']
        else:
            self.cv_cuts = {'thirty_seventy': [0.3, 0.7]}

        if run_config.has_key('past_years'):
            self.past_years = run_config['past_years']
        else:
            self.past_year = None

        if run_config.has_key('static_features'):
            self.static_features = run_config['static_features']
        else:
            raise KeyError('No static features')

        if model_config.has_key('parameters'):
            self.parameters = model_config['parameters']

        if run_config.has_key('all_parameters'):
            self.all_parameters = run_config['all_parameters']

        if model_config.has_key('rebalancing'):
            self.rebalancing = model_config['rebalancing']

        if run_config.has_key('downsample'):
            self.downsample = run_config['downsample']
            self.rebalancing = run_config['rebalancing']
        else:
            self.downsample = False



        self.cross_valname = run_config['cross_valname']
        self.use_nearby_wo = run_config['use_nearby_wo']
        self.nearby_wo = model_config['past_nearby_cols']
