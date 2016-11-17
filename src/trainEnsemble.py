'''
    The purpose of this program is to train a decision-tree based learning
    algorithm using SKLEARN and to write the resulting model to a file.
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
	12 November 2016
	Version 1.0
'''

# Global dictionaries
model_names = {	'rf': 'Random Forest', \
				'brt': 'Boosted Regression Trees', \
				'ada': 'Adaboost Classifier' \
}

metric_names = {'acc': 'accuracy',\
				'f1': 'f1-score', \
				'mse': 'mean squared error' \
}

# Support Imports
import sys, pickle
from optparse import OptionParser
import numpy as np
import logging

# Model Imports
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier

# Metrics Import
from sklearn import metrics

# Turn on logging.
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)

# Train the model on the given training data
def train_model(model, X_train, y_train):
	model.fit(X_train, y_train.ravel())

# Test the model on the given testing data
def test_model(model, X_test, y_test, metric):
	if metric == 'acc':
		return metrics.accuracy_score(y_test, model.predict(X_test))
	elif metric == 'f1':
		return metrics.f1_score(y_test, model.predict(X_test))
	elif metric == 'mse':
		return metrics.mean_squared_error(y_test, model.predict(X_test))
	else:
		raise ValueError("Invalid metric %s provided" % metric)
		return -1

# Dump the model to a file
def dump_model(model, modelfile):
	f = open(modelfile, 'wb')
	pickle.dump(model, f)
	f.close()

# Write report out to file
def write_report(report_name, report_dict):
	f = open(report_name, 'w')
	for key, value in report_dict.items():
		f.write(str(key)+": "+str(value))
	f.close()
	return

# Main()
if __name__ == '__main__':

    # Parse Command Line Arguments
    usage = '%prog [options][text]'
    parser = OptionParser(usage)
    parser.add_option('-t', '--train', type='string', dest='trainfile', help='Training Data File (.npz file)')
    parser.add_option('-x', '--test', type='string', dest='testfile', help='Testing Data File (.npz file)')
    parser.add_option('--metric', type='string', default='acc', dest='metric', help='Provide the training metric to be displayed')
    parser.add_option('-m', '--model', type='string', dest='model', help='Choose the model')
    parser.add_option('--model-out', type='string', dest='modelout', default='model.pickle', help='Output model file')
    #parser.add_option('-o', '--file-out', type='string', dest='outfile', help='Save resulting X and y to a file')
    parser.add_option('-d', '--depth', type='int', dest='depth', help='Max depth of the decision tree learners')
    parser.add_option('-n', '--tree_n', type='int', dest='tree_n', help='Number of decision trees')
    parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Verbose')
    parser.add_option('-r', '--report', type='string', dest='report', help='Name of the report file')
    options, args = parser.parse_args()

    params = {}
    report_dict = {}

    # Validate command line arguments
    if options.trainfile is None:
    	raise ValueError("No valid training data filename specified; provide -t")
    	exit(-1)

    if options.model not in model_names.keys():
    	raise ValueError("No valid model specified; provide {'rf', 'brt', 'ada'}")
    	exit(-1)

    if options.depth is None:
    	raise ValueError("No valid tree depth specified; provide -d <max depth>")
    	exit(-1)

    params['max_depth'] = options.depth
    report_dict['max_depth'] = options.depth

    if options.tree_n is None:
    	raise ValueError("No valid tree count specified; provide -n <num trees>")
    	exit(-1)

    params['n_estimators'] = options.tree_n
    report_dict['n_estimators'] = options.tree_n

    if options.verbose:
    	logging.info("Loading training file from %s" % options.trainfile)

	# Load the training files
	npzfile = np.load(options.trainfile)
	X = npzfile['X']
	y = npzfile['y']

	if options.verbose:
		logging.info("Shape of the loaded training data. X:(%d,%d), y:(%d,%d)" %(X.shape[0], X.shape[1], y.shape[0], y.shape[1]))

	X_test = None
	y_test = None

	if options.testfile is None:
		logging.info("No included test file, so going to split training data")
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33, random_state=42)

	else:
        # Use train file for training
		X_train = X
		y_train = y

		# Load the testing files
		npzfile = np.load(options.testfile)
		X_test = npzfile['X']
		y_test = npzfile['y']

	if options.verbose:
		logging.info("Shape of the loaded testing data. X:(%d,%d), y:(%d,%d)" %(X_test.shape[0], X_test.shape[1], y_test.shape[0], y_test.shape[1]))

	if options.verbose:
		logging.info("Setting the model to be learned to: %s" % options.model)
		logging.info("With parameters: %s" % str(params))


	model = None
	if options.model == 'rf':
		params['n_jobs'] = 10
		model = RandomForestClassifier(**params)
	elif options.model == 'brt':
		model = GradientBoostingClassifier(**params)
	elif options.model == 'ada':
		model = AdaBoostClassifier(**params)
	else:
		raise ValueError("No valid model specified")
		exit(-1)

	report_dict['model'] = model

	if options.verbose:
		logging.info("Training the %s model" % model_names[options.model])

	train_model(model, X_train, y_train)

	if options.verbose:
		logging.info("Testing the %s model" % model_names[options.model])

	metric = options.metric
	if options.metric not in metric_names.keys():
		logging.info("No metric defined; defaulting to accuracy")
		metric = 'acc'

	result = test_model(model, X_test, y_test, metric)

	logging.info(metric_names[metric] + ": " + str(result))
	report_dict[metric_names[metric]] = str(result)

	if options.verbose:
		logging.info("Writing model out to %s" % options.modelout)

	# Write the model out to a file
	dump_model(model, options.modelout)

	if options.report is not None:
		write_report(options.report, report_dict)

	if options.verbose:
		logging.info("Done")
