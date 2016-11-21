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


# Utility Imports
from optparse import OptionParser
import logging
import pickle
import numpy as np

# RF Automata Imports
from chain import *
from featureTable import *
from anmltools import *

# Turn on logging.
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)
 
# Load the model from a file
def load_model(modelfile):

    logging.info("Loading model file from %s" % modelfile)

    f = open(modelfile, 'rb')
    model = pickle.load(f)
    f.close()

    return model

# Load the chains, FT and value map from a file
def load_cft_vm(cftFile):

    logging.info("Loading Chains, FT, ValueMap file from %s" % cftFile)

    f = open(cftFile, 'rb')
    chains, ft, value_map = pickel.load(f)
    f.close()

    return chains, ft, value_map

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
def tree_to_chains(tree, tree_id, chains, features, threshold_map, values):

    # Root node attributes
    feature = tree.feature[0]
    threshold = tree.threshold[0]

    # Keeping track of features and associated thresholds for all trees
    if feature not in features:
        features.append(feature)
        threshold_map[feature] = [threshold]
    elif threshold not in threshold_map[feature]:
        threshold_map[feature].append(threshold)

    # Because we're a root node, we dont care
    left = tree.children_left[0]
    right = tree.children_right[0]

    left_chain = Chain(tree_id)
                    # feature, threshold, value, leaf, gt)
    node = Node(feature, threshold, False)
    left_chain.add_node(node)
        
    chains += recurse(tree, left, left_chain, features, threshold_map, values)

    right_chain = Chain(tree_id)
                    # feature, threshold, value, leaf, gt)
    node = Node(feature, threshold, True)
    right_chain.add_node(node)
        
    chains += recurse(tree, right, right_chain, features, threshold_map, values)

    # Because we built the chains from the left-most to the right-most leaf
    # We can simply assign chain ids sequentially over our list
    for chain_id, chain in enumerate(chains):
        chain.set_chain_id(chain_id)

    # Sort the features
    features.sort()

    # Sort the thresholds for all features
    for k,val in threshold_map.items():
        val.sort()

# Recursive function to convert trees into chains
def recurse(tree, index, temp_chain, features, threshold_map, values):

    feature = tree.feature[index]
    threshold = tree.threshold[index]
    value = np.argmax(tree.value[index])

    left = tree.children_left[index]
    right = tree.children_right[index]

    # We're a leaf (also an end)
    if feature == -2:

        if value not in values:
            values.append(value)

        temp_chain.set_value(value)
        return [temp_chain]

    else:                           # We can do this because all trees with children have both

        # Keeping track of features and associated thresholds
        if feature not in features:
            features.append(feature)
            threshold_map[feature] = [threshold]

        elif threshold not in threshold_map[feature]:
            threshold_map[feature].append(threshold)

                    # feature, threshold, gt)
        node = Node(feature, threshold, False)
        temp_chain.add_node(node)

        right_copy = temp_chain.copy()

        left_chains =  recurse(tree, left, temp_chain, features, threshold_map, values)

        # Flip the last node, we're going right (>)!
        right_copy.nodes_[-1].set_direction(True)

        right_chains = recurse(tree, right, right_copy, features, threshold_map, values)

        return left_chains + right_chains

# Set the character sets of each node in the chains
def set_character_sets(chain, ft):

    # Iterate through all nodes, 
    for node in chain.nodes_:

        # Let us build a character set list
        character_set = []

        # Grab node attributes
        feature = node.feature_
        threshold = node.threshold_
        gt = node.gt_

        # Grab STE labels associated with feature
        ste, start, end = ft.get_range(feature)

        # We're at a <= node
        if not gt:

            # Let's go
            labels = range(start, end + 1)
            threshold_limits = ft.threshold_map_[feature] + [-1]

            assert len(labels) == len(threshold_limits), "len labels != len threshold_limits!"

            for label, threshold_limit in zip(labels, threshold_limits):

                # We've reached the end
                if threshold_limit == -1:
                    character_set.append(label)

                # Our thresholds == the current range limit, so we're done
                elif threshold == threshold_limit:
                    character_set.append(label)
                    break
                # Our threshold < current range limit, move on
                elif threshold < threshold_limit:
                    character_set.append(label)

                # Our threshold is > current range limit, break
                else:
                    break

        else:

            # Let's do this
            labels = range(end, start - 1, -1)
            threshold_limits = (ft.threshold_map_[feature] + [-1])[::-1]

            assert len(labels) == len(threshold_limits), "len labels != len threshold_limits!"

            for label, threshold_limit in zip(labels, threshold_limits):
                
                if threshold_limit == -1:
                    character_set.append(label)

                elif threshold > threshold_limit:
                    character_set.append(label)
                else:
                    break

        node.set_character_set(character_set)


# Main()
if __name__ == '__main__':

    # Parse Command Line Arguments
    usage = '%prog [options][text]'
    parser = OptionParser(usage)
    parser.add_option('-m', '--model', type='string', dest='model', help='Input SKLEARN model pickle file')
    parser.add_option('-a', '--anml', type='string', dest='anml', default='model.anml', help='ANML output filename')
    parser.add_option('-c', '--compile', action='store_true', default=False, dest='compile', help='To compile or not to compile')
    parser.add_option('-f', '--fsm', type='string', dest='fsm', help='FSM filename for compiling')
    parser.add_option('--chain-ft-vm', type='string', dest='cftvm', help="Filename of chains and feature table pickle")
    parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Verbose')
    options, args = parser.parse_args()

    # This allows us to test the ANML code faster
    if options.cftvm is not None:
        chains, ft, value_map = load_cft_vm(options.cft)

    # Otherwise, let's do this from scratch
    else:
        # Load the model file
        if options.model is not None:
            model = load_model(options.model)
        else:
            raise ValueError("No valid model file; provide -m <model filename>")
            exit(-1)

        # Grab the constituent trees
        trees = [dtc.tree_ for dtc in model.estimators_]

        # Convert all trees to chains
        chains = []

        # Keep track of all features used in the forest
        features = []

        # Keep track of features -> thresholds
        threshold_map = {}

        # Keep track of unique values
        values = []

        # Iterate through all trees in the forest and keep track of chains, features, and thresholds
        
        logging.info("Converting trees to chains")

        for tree_id, tree in enumerate(trees):
            tree_to_chains(tree, tree_id, chains, features, threshold_map, values)

        # The value_map is used to give unique value ids to each value
        values.sort()
        value_map = {}

        for _i, _value in enumerate(values):
            value_map[_value] = _i + 1

        logging.info("Building the Feature Table")

        # Create ideal address spacing for all features and thresholds
        ft = FeatureTable(features, threshold_map)

        logging.info("Compacting the Feature Table")

        ft.compact()    # Run the compactor (NOT IDEAL, but good enough)


        logging.info("Sorting and combining the chains")

        # Set the character sets for each node in the chains
        # Then sort and combine the states in the chains
        for chain in chains:
            set_character_sets(chain, ft)
            chain.sort_and_combine()
        

        logging.info("Dumping Chains, Feature Table and Value Map to pickle")

        # Dump the chains and featureTable to a pickle file
        f = open('chainsFeatureTableValueMap.pickle', 'wb')
        pickle.dump((chains, ft, value_map), f)
        f.close()

    # Generate ANML from the chains using the feature table
    generate_anml(chains, ft, value_map, options.anml)

    # If flag enabled, compile and dump into fsm file
    #if options.compile:
    #    compile_anml(compile_filename)

