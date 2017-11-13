import logging
import pickle

# Turn on logging; let's see what all is going on
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)


# Load a sklearn model from a file
def load_model(modelfile):

    try:
        # Read the modelfile pickle
        with open(modelfile, 'rb') as f:
            model = pickle.load(f)
        return model

    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        return None


# Load testing data
def load_test(testfile):

    try:
        # Read the testing data in to be used to generate a symbol file
        with open(testfile, 'rb') as f:
            X_test, y_test = pickle.load(f)
        return X_test, y_test

    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        return None, None
