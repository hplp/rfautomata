'''
    The purpose of this program is to train a decision-tree based learning
    algorithm use SKLEARN and write the resulting model to a file
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
	12 November 2016
	Version 1.0
'''

# Global dictionaries
model_names = {'rf': 'Random Forest', \
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier

# Metrics Import
from sklearn import metrics

# Turn on logging.
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)

# Train the model on the given training data
def train_model(model, X_train, y_train):
    model.fit(X_train, y_train)

# Test the model on the given testing data
def test_model(model, X_test, y_test, metric):
    if metric == 'mse':
        return metrics.mean_squared_error(y_test, model.predict(X_test))
    elif metric == 'f1':
        return metrics.f1_score(y_test, model.predict(X_test))
    elif metric == 'mse':
        return metrics.mean_squared_error(y_test, model.predict(X_test))
    else:
        return -1

# Dump the model to a file
def dump_model(model, modelfile)
    pickle.dump(model, modelfile)

# Main()
if __name__ == '__main__':

    # Parse Command Line Arguments
    usage = '%prog [options][text]'
    parser = OptionParser(usage)
    parser.add_option('-t', '--train', type='string', dest='trainfile', help='Training Data File (.npz file)')
    parser.add_option('-x', '--test', type='string', dest='testfile', help='Testing Data File (.npz file)')
    parser.add_option('--metric', type='string', default='acc' dest='metric', help='Provide the training metric to be displayed')
    parser.add_option('-m', '--model', type='string', dest='model', help='Choose the model')
    parser.add_option('--model-out', type='string', dest='modelout', default='model.pickle', help='Output model file')
    parser.add_option('-o', '--file-out', type='string', dest='outfile', help='Save resulting X and y to a file')
    parser.add_option('-d', '--depth', type='int', dest='depth', help='Max depth of the decision tree learners')
    parser.add_option('-n', '--tree_n', type='int', dest='tree_n', help='Number of decision trees')
    parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Verbose')
    options, args = parser.parse_args()

    params = {}

    # Validate command line arguments
    if options.trainfile is None:
        raise ValueError("No valid training data filename specified; provide -t")
        exit(-1)
	    
    if options.verbose:
        logging.info("Loading training file from %s" % options.trainfile)

	# Load the training files
	npzfile = np.load(options.trainfile)
	train_X = npzfile['X']
	train_y = npzfile['y']

	if options.verbose:
        logging.info("Done loading training file")

	if options.testfile is None:
		raise ValueError("No valid testing data filename specified; provide -x")
		exit(-1)

	# Load the testing files
	npzfile = np.load(options.testfile)
	test_X = npzfile['X']
	test_y = npzfile['y']

    if options.model is None:
        raise ValueError("No valid model specified; provide {'rf', 'brt', 'ada'}")
        exit(-1)

    if options.modelout is None:
        raise ValueError("No valid --model-out; provide --model-out <filename>")
        exit(-1)

    if options.depth is None:
        raise ValueError("No valid tree depth specified; provide -d <max depth>")
        exit(-1)

	params['max_depth'] = options.depth

    if options.tree_n is None:
        raise ValueError("No valid tree count specified; provide -n <num trees>")
        exit(-1)

    params['n_estimators'] = options.tree_n

    if options.verbose:
    	logging.info("Setting the model to be learned to: %s" % options.model)

    if options.model == 'rf':
        model = RandomForestClassifier(n_jobs=2, **params)
    elif options.model == 'brt':
        model = GradientBoostingClassifier(n_jobs=2, **params)
    elif options.model == 'ada':
        model = AdaBoostClassifier(n_jobs=2, **params)
    else:
        raise ValueError("No valid model specified")
        exit(-1)

    if options.metric not in metric_names.keys():
        raise ValueError("No valid testing metric specified")
        exit(-1)

    if options.verbose:
    	logging.info("Training the %s model" % model_names[options.model])

    train_model(model, X_train, y_train)

    if options.verbose:
        logging.info("Testing the %s model" % model_names[options.model])

    result = test_model(model, X_test, y_test, options.metric)

    logging.info(metric_names[options.metric] + ": " + result)

    if options.verbose:
        logging.info("Writing model out to %s" %s options.modelout)

    # Write the model out to a file
    dump_model(model, options.modelout)

    if options.verbose:
        logging.info("Done")
