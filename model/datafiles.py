"""
Container for datafiles needed in the Syracuse pipeline
"""
import yaml
from pkg_resources import resource_filename


model_file = resource_filename(__name__, '/config/model.yaml')
model_config = yaml.load(open(model_file))
run_test_file = resource_filename(__name__, '/config/run.yaml')
test_run_config = yaml.load(open(run_test_file))
test_csv = resource_filename(__name__, '/sample_data/test.csv')
