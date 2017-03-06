'''
    The purpose of this program is to convert SKLEARN models into
    an automata representation.

    For the time being let's only support Random Forests
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    8 February 2017
    Version 1.1

    *Definitions*
    ----------------------
    features: a LIST containing all of the features
    threshold_map: a DICT that maps features to a list of all thresholds used for that feature
'''

# Utility Imports
import sys
from optparse import OptionParser
import logging
import pickle
import numpy as np

# Automata Imports
from chain import *
from featureTable import *
#import plot
import quickrank as qr
#from anmltools import *

# Turn on logging; let's see what all is going on
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)

# Load a sklearn model from a file
def load_model(modelfile):

    # Read the modelfile pickle
    with open(modelfile, 'rb') as f:
        model = pickle.load(f)

    return model

# Dump pickle file containing chains, ft, value_map
def dump_cftvm(chains, ft, value_map, reverse_value_map, filename):

    with open(filename, 'wb') as f:
        pickle.dump((chains, ft, value_map, reverse_value_map), f)

    return 0

# Load the chains, FT and value map from a file
def load_cft_vm(cftFile):

    with open(cftFile, 'rb') as f:
        chains, ft, value_map, reverse_value_map = pickle.load(f)

    return chains, ft, value_map, reverse_value_map

# Convert tree to chains (for scikit-learn models)
def tree_to_chains(tree, tree_id, chains, threshold_map, values):

    # Root node attributes
    feature = tree.feature[0]
    threshold = tree.threshold[0]

    # Keeping track of features and associated thresholds for all trees
    if feature not in threshold_map:
        threshold_map[feature] = [threshold]

    # If the feature has already been seen, check to see if this is a unique threshold
    elif threshold not in threshold_map[feature]:
        threshold_map[feature].append(threshold)

    # Let's grab references to our children nodes!
    left = tree.children_left[0]
    right = tree.children_right[0]

    # Let's create a 'left' chain from the root
    left_chain = Chain(tree_id)
    root_node = Node(feature, threshold, False) # This is the root node -> left decision
    left_chain.add_node(root_node)

    # Let's create a 'right' chain from the root
    right_chain = Chain(tree_id)
    root_node = Node(feature, threshold, True) # This is the root node -> right decision
    right_chain.add_node(root_node)

    # We have our left chain; let's recurse!
    chains += recurse(tree, left, left_chain, threshold_map, values)

    # We have our right chain; let's recurse!
    chains += recurse(tree, right, right_chain, threshold_map, values)

    # Ok we're done here
    return

# Recursive function to convert trees into chains
def recurse(tree, index, temp_chain, threshold_map, values):

    feature = tree.feature[index]
    threshold = tree.threshold[index]
    value = np.argmax(tree.value[index])

    left = tree.children_left[index]
    right = tree.children_right[index]

    # We're a leaf; we're done here
    if feature == -2:

        # Have we seen this leaf node value before?
        if value not in values:
            values.append(value)    # We have a new leaf up in here!

        temp_chain.set_value(value) # Set the value of the chain

        return [temp_chain]         # This returns the chain as a single value list

    # If we're not a leaf, we got children!
    else:                           # We can do this because all trees with children have both

        # Keeping track of features and associated thresholds
        if feature not in threshold_map:
            threshold_map[feature] = [threshold]

        elif threshold not in threshold_map[feature]:
            threshold_map[feature].append(threshold)

        # Let's go left, then right
        left_chain = temp_chain
        right_chain = left_chain.copy()

                    # feature, threshold, gt
        node_l = Node(feature, threshold, False)
        left_chain.add_node(node_l)

        # Let's do the same for the right and recurse
        node_r = Node(feature, threshold, True)
        right_chain.add_node(node_r)

        return recurse(tree, left, left_chain, threshold_map, values) + \
            recurse(tree, right, right_chain, threshold_map, values)

# Set the character sets of each node in the chains
def set_character_sets(chain, ft):

     # Iterate through all nodes,
    for node in chain.nodes_:

        # Let us build a character set list
        character_sets = []

        # Grab node attributes
        feature = node.feature_
        threshold = node.threshold_
        gt = node.gt_

        # Grab STE labels associated with feature
        ranges = ft.get_ranges(feature) # [(ste, start, end)]

        found = False

        # Go through each STE
        for ste, start, end in ranges:

            # Each STE assigned to this feature needs its own character set
            character_set = []

            # If this STE accepts <=
            if not gt:

                # Grab the labels assigned to the range for this feature in this STE
                labels = range(start, end)

                # Also grab the thresholds assigned to the feauture
                thresholds = ft.stes_[ste][start:end]

                # If the range was discovered in a previous bin, we're going with -2
                if found:

                    # We'll only accept the '-2' flag
                    character_set = [labels[-1]]

                else:

                    for label, threshold_limit in zip(labels, thresholds):

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

                        # If we've reached the end of the STE, that means we're still looking
                        # DO NOT accept this
                        elif threshold_limit == -2:
                            break

                        # Our threshold is > current range limit, break
                        else:
                            break

            else:

                labels = range(end, start-1, -1)

                # We're going throught he thresholds from back to front
                thresholds = (ft.stes_[ste][start:end])[::-1]

                # If the range was discovered in a previous bin, we're going with -2
                if found:

                    # We'll only accept the '-2' flag
                    character_set = [labels[-1]]

                else:

                    for label, threshold_limit in zip(labels, thresholds):

                        if threshold_limit == -1:
                            character_set.append(label)

                        elif threshold > threshold_limit:
                            character_set.append(label)

                        else:
                            break

            character_sets.append(character_set)

        node.set_character_sets(character_sets)


# Main()
if __name__ == '__main__':

    quickrank = False

    # Parse Command Line Arguments
    usage = '%prog [options][text]'
    parser = OptionParser(usage)
    parser.add_option('-m', '--model', type='string', dest='model', help='Input SKLEARN model pickle file')
    parser.add_option('-a', '--anml', type='string', dest='anml', default='model.anml', help='ANML output filename')
    parser.add_option('-c', '--compile', action='store_true', default=False, dest='compile', help='To compile or not to compile')
    parser.add_option('-f', '--fsm', type='string', dest='fsm', help='FSM filename for compiling')
    parser.add_option('--chain-ft-vm', type='string', dest='cftvm', help="Filename of chains and feature table pickle")
    parser.add_option('--spf', action='store_true', default=False, dest='spf', help='Use one STE per Feature')
    parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Verbose')
    options, args = parser.parse_args()

    # This allows us to test the ANML code faster by loading our converted data structures
    if options.cftvm is not None:
        chains, ft, value_map, reverse_value_map = load_cft_vm(options.cftvm)

    # Otherwise, let's do this from scratch
    else:

        # Load the model file
        if options.model is not None:
            logging.info("Loading model file from %s" % options.model)

            # Grab the model
            model = None

            # Simple check if quickrank model
            if 'xml' in options.model:

                quickrank = True

                model = qr.load_qr(options.model)

                # Grab the constituent trees
                trees = qr.grab_data(model)

            # Else, its a scikit learn-type model
            else:
                model = load_model(options.model)

                # Grab the constituent trees
                trees = [dtc.tree_ for dtc in model.estimators_]

        else:
            raise ValueError("No valid model file; provide -m <model filename>")
            exit(-1)

        logging.info("Grabbed %d constituent trees to be 'chained'" %len(trees))

        # Convert all trees to chains
        chains = []

        # Keep track of features -> thresholds
        threshold_map = {}

        # Keep track of unique values
        values = []

        # Iterate through all trees in the forest and keep track of chains, features, and thresholds
        logging.info("Converting trees to chains")

        # We're going to use these to index leaf values (classes)
        value_map = {}
        reverse_value_map = {}

        # To deal with quickrank, we need to parse the trees differently
        if quickrank:

            # Here is where we generate the chains from the trees
            for tree_id, tree_weight, tree_split in trees:

                qr.tree_to_chains(tree_id, tree_weight, tree_split, chains, threshold_map, values)

            values.sort()

            # Create a mapping from value to index (starting from 1)
            for _i, _value in enumerate(values):
                value_map[_value] = _i + 1
                reverse_value_map[_i + 1] = _value

        else:

            classes = model.classes_

            for tree_id, tree in enumerate(trees):

                tree_to_chains(tree, tree_id, chains, threshold_map, values)

            for _i in values:
                value_map[classes[_i]] = _i + 1
                reverse_value_map[_i+1] = classes[_i]

        logging.info("Done converting trees to chains; now sorting")

        # Because we built the chains from the left-most to the right-most leaf
        # We can simply assign chain ids sequentially over our list
        for chain_id, chain in enumerate(chains):
            chain.set_chain_id(chain_id)

        # Sort the thresholds for all features
        for f,t in threshold_map.items():
            t.sort()

        # Let's look at the threshold distribution if verbose
        #if options.verbose:
        #   plot.plot_thresholds(threshold_map)

        logging.info("Building the Feature Table")

        # Create ideal address spacing for all features and thresholds
        ft = FeatureTable(threshold_map)

        logging.info("Sorting and combining the chains")

        # Set the character sets for each node in the chains
        # Then sort and combine the states in the chains
        for chain in chains:
            set_character_sets(chain, ft)
            chain.sort_and_combine()

        for ste in ft.stes_:
            print ste

        logging.info("Dumping Chains, Feature Table and Value Map to pickle")

        dump_cftvm(chains, ft, value_map,reverse_value_map, 'chainsFeatureTableValueMap.pickle')

        logging.info("Done writing out files")

    logging.info("Generating ANML")

    generate_anml(chains, ft, options.anml, naive=options.spf)

    # If flag enabled, compile and dump into fsm file
    #if options.compile:
    # .    compile_anml(compile_filename)

