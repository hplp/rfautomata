'''
    The purpose of this program is to convert SKLEARN models into 
    an automata representation.

    For the time being let's only support Random Forests
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    12 November 2016
    Version 1.0
'''


# Support Imports
from optparse import OptionParser
import logging
import chain
import pickle
import numpy as np

# SKLEARN inputs

# Micron AP import

# Turn on logging.
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)
 
# Load the model from a file
def load_model(modelfile):
    f = open(modelfile, 'rb')
    model = pickle.load(f)
    f.close()
    return model


'''
    Attributes of an SKLEARN Tree -- returned by dir(tree)

    ['__class__', '__delattr__', '__doc__', '__format__',
     '__getattribute__', '__getstate__', '__hash__', '__init__', 
     '__new__', '__pyx_vtable__', '__reduce__', '__reduce_ex__', 
     '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__',
      '__subclasshook__', 'apply', 'capacity', 'children_left', 
      'children_right', 'compute_feature_importances', 'decision_path', 
      'feature', 'impurity', 'max_depth', 'max_n_classes', 'n_classes', '
      n_features', 'n_node_samples', 'n_outputs', 'node_count', 'predict', 
      'threshold', 'value', 'weighted_n_node_samples']

'''

# Convert tree to chains
def tree_to_chains(tree, chains, features, threshold_map):

    # Return a list of chains
    #chains = []

    # Return a list of features used
    #features = []

    # Return dictionary mapping features to all thresholds
    #threshold_map = {}

    # Root node attributes
    feature = tree.feature[0]
    threshold = tree.threshold[0]

    # Keeping track of features and associated thresholds
    if feature not in features:
        features.append(feature)
        threshold_map[feature] = [threshold]

    elif threshold not in threshold_map[feature]:
        threshold_map[feature].append(threshold)


    value = np.argmax(tree.value[0])
    left = tree.children_left[0]
    right = tree.children_right[0]

    left_chain = chain.Chain()
    node = chain.Node(feature, threshold, value, False, False)
    left_chain.add_node(node)
    left_chain.set_start(node)
    chains += recurse(tree, left, left_chain, features, threshold_map)

    right_chain = chain.Chain()
    node = chain.Node(feature, threshold, value, False, True)
    right_chain.add_node(node)
    right_chain.set_start(node)
    chains += recurse(tree, right, right_chain, features, threshold_map)

# Recursive function to convert trees into chains
def recurse(tree, index, temp_chain, features, threshold_map):

    feature = tree.feature[index]
    threshold = tree.threshold[index]
    value = np.argmax(tree.value[index])

    left = tree.children_left[index]
    right = tree.children_right[index]

    leaf = (feature == -2)          # We're a leaf (also an end)

    if leaf:                        # It's a leaf

        node = chain.Node(feature, threshold, value, True, False)
        temp_chain.add_edge(temp_chain.nodes_[-1], node)
        temp_chain.set_end(node)

        return [temp_chain]

    else:                           # We can do this because all trees with children have both

        # Keeping track of features and associated thresholds
        if feature not in features:
            features.append(feature)
            threshold_map[feature] = [threshold]

        elif threshold not in threshold_map[feature]:
            threshold_map[feature].append(threshold)

        node = chain.Node(feature, threshold, value, leaf, False)
        temp_chain.add_edge(temp_chain.nodes_[-1], node)
        right_copy = temp_chain.copy()

        left_chains =  recurse(tree, left, temp_chain, features, threshold_map)

        right_copy.nodes_[-1].set_direction(True)

        right_chains = recurse(tree, right, right_copy, features, threshold_map)

        return left_chains + right_chains

# Set the character sets of each node in the chains
def set_character_sets(chain, features, threshold_map):

    for node in chain.nodes_:
        feature = node.compute_
        threshold = node.threshold_
        gt = node.gt_

        feature_range = threshold_map[feature]

        # We're at a <= node
        if not gt:
            min_symbol = 0      # The left-most symbol is always accepted by a <= node

        else:
            max_symbol = 



# Main()
if __name__ == '__main__':

    # Parse Command Line Arguments
    usage = '%prog [options][text]'
    parser = OptionParser(usage)
    parser.add_option('-m', '--model', type='string', dest='model', help='Input SKLEARN model pickle file')
    parser.add_option('-a', '--anml', type='string', dest='anml', default='model.anml', help='ANML output filename')
    parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Verbose')
    options, args = parser.parse_args()

    # Load the model file
    if options.model is not None:
        model = load_model(options.model)
    else:
        raise ValueError("No valid model file; provide -m <model filename>")
        exit(-1)

    # Grab the constituent trees
    trees = [dtc.tree_ for dtc in  model.estimators_]

    # Convert all trees to chains
    chains = []

    # Keep track of all features used in the forest
    features = []

    # Keep track of features to all thresholds
    threshold_map = {}

    # Iterate through all trees in the forest and keep track of chains, features, and thresholds
    for tree in trees:
        tree_to_chains(tree, chains, features, threshold_map)

    # Sort the features
    features.sort()

    # For each set of thresholds, sort them
    for k, v in threshold_map.items():
        v.sort()

    # Set the character sets for each node in the chains
    for chain in chains:
        set_character_sets(chain, features, threshold_map)

