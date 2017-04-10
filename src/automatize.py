'''
    The purpose of this program is to convert
    SKLEARN and QUICKLEARN models into an
    automata representation.

    For the time being let's only support Random Forests,
    BRTs, ADABOOST, and Quicklearn Models.
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
    threshold_map: a DICT that maps features to a list of
    all thresholds used for that feature in the model
'''

# Utility Imports
from optparse import OptionParser
import logging
import pickle
import numpy as np

# Automata Imports
from chain import *
from featureTable import *
import quickrank as qr
from anmltools import *
import gputools

# Turn on logging; let's see what all is going on
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)


# Load a sklearn model from a file
def load_model(modelfile):

    # Read the modelfile pickle
    with open(modelfile, 'rb') as f:
        model = pickle.load(f)

    return model


# Load testing data
def load_test(testfile):

    # Read the testing data in to be used to generate a symbol file
    with open(testfile, 'rb') as f:
        X_test, y_test = pickle.load(f)

    return X_test, y_test


# Dump pickle file containing chains, ft, value_map
def dump_cftvm(chains, ft, value_map, reverse_value_map, filename):

    with open(filename, 'wb') as f:
        pickle.dump((chains, ft, value_map, reverse_value_map), f)

    return 0


# Load the chains, FT and value map from a file
def load_cftvm(cftFile):

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

    # If feature already seen, check to see if this is a unique threshold
    elif threshold not in threshold_map[feature]:
        threshold_map[feature].append(threshold)

    # Let's grab references to our children nodes!
    left = tree.children_left[0]
    right = tree.children_right[0]

    # Let's create a 'left' chain from the root
    left_chain = Chain(tree_id)
    # This is the root node -> left decision
    root_node = Node(feature, threshold, False)
    left_chain.add_node(root_node)

    # Let's create a 'right' chain from the root
    right_chain = Chain(tree_id)
    # This is the root node -> right decision
    root_node = Node(feature, threshold, True)
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

    # Take the most observed class index
    value = np.argmax(tree.value[index])

    # We're a leaf; we're done here
    if feature == -2:

        # Have we seen this leaf node value before?
        if value not in values:
            # We have a new leaf up in here!
            values.append(value)

        # Set the value of the chain
        temp_chain.set_value(value)

        # This returns the chain as a single value list
        return [temp_chain]

    # If we're not a leaf, we got children!
    else:

        left = tree.children_left[index]
        right = tree.children_right[index]

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

    # Iterate through all nodes
    for node in chain.nodes_:

        # Build character set list for this node
        # one character set per STE assigned to node
        character_sets = []

        # Grab STE labels associated with feature; make a copy
        # [(ste, start, end)]
        ranges = list(ft.get_ranges(node.feature_))

        # Haven't found our 'range' yet
        found = False

        # If this STE accepts <=
        if not node.gt_:

            # Go through each STE from the smallest to largest features
            for ste, start, end in ranges:

                # Each STE assigned to this feature needs its own character set
                character_set = []

                # Grab labels assigned to range for this feature in this STE
                labels = range(start, end)

                # Also grab the thresholds assigned to the feature at this ste
                thresholds = ft.stes_[ste][start:end]

                # print " <= ", node.threshold_
                # print "Thresholds: ", thresholds
                # print "Labels: ", labels

                assert len(labels) == len(thresholds),\
                    "Zipping labels and thresholds is gonna fail :("

                # If range was discovered in a previous bin, -2
                if found:

                    # Only accept '-2' flag; not in any ranges (for this STE))
                    character_set.append(labels[-1])

                    assert thresholds[-1] == -2,\
                        "The last label for this bin is not -2, it's %d" %\
                        (labels[-1])
                    assert character_set == [labels[-1]]

                else:

                    # Go from  first (smallest) to the last (largest) label
                    for label, threshold_limit in zip(labels, thresholds):

                        # We accept this label, because its <= threshold
                        if threshold_limit < node.threshold_:
                            character_set.append(label)

                        # We accept this label, and we're done
                        elif threshold_limit == node.threshold_:
                            character_set.append(label)
                            found = True
                            break

                        # We should never have made it here!
                        else:
                            print "We should not be here!"
                            exit()

                # Append the character set for this ste
                character_sets.append(character_set)

        # If this STE accepts >
        else:

            # Invert the ranges, to start from the largest features
            # Means we'll need to reverse our character sets at the end
            ranges.reverse()

            # Go through each STE from the larges to the smallest feature
            for ste, start, end in ranges:

                character_set = []

                # Reversed labels
                labels = range(end - 1, start - 1, -1)

                # We're going throught the thresholds from back to front
                thresholds = ft.stes_[ste][start:end]
                thresholds.reverse()

                # print "> Threshold: ", node.threshold_
                # print "Thresholds: ", thresholds
                # print "Labels: ", labels

                assert len(labels) == len(thresholds),\
                    "Zipping labels and thresholds is gonna fail :("

                # If range was discovered in a previous bin, -2
                if found:

                    # We'll only accept the '-2' flag
                    character_set.append(labels[0])

                    assert thresholds[0] == -2,\
                        "The last label for this bin is not -2"

                else:

                    # Go from last (largest) to first (smallest) label
                    for label, threshold_limit in zip(labels, thresholds):

                        # Expect -2 before outside of our range; ignore it
                        if threshold_limit == -2:
                            continue

                        # -1 will always be accepts (for >)
                        elif threshold_limit == -1:
                            character_set.append(label)

                        # If our threshold > threshold_limit, we'll accept
                        elif threshold_limit > node.threshold_:
                            character_set.append(label)

                        # Don't accept and break
                        elif threshold_limit == node.threshold_:
                            found = True
                            break

                        else:
                            print "We shouldn't be here"
                            exit()

                # Append the character set for this ste
                character_sets.append(character_set)

            character_sets.reverse()

        assert len(ft.feature_pointer_[node.feature_]) == len(character_sets),\
            "character sets aren't the right length"

        for c_s in character_sets:
            c_s.sort()

        # Set the node's character sets
        node.set_character_sets(character_sets)


# Main()
if __name__ == '__main__':

    quickrank = False

    # Parse Command Line Arguments
    usage = '%prog [options][text]'
    parser = OptionParser(usage)
    parser.add_option('-m', '--model', type='string', dest='model',
                      help='Input SKLEARN model pickle file')
    parser.add_option('-a', '--anml', type='string', dest='anml',
                      default='model.anml', help='ANML output filename')
    parser.add_option('-f', '--fsm', type='string', dest='fsm',
                      help='FSM filename for compiling')
    parser.add_option('--chain-ft-vm', type='string', dest='cftvm',
                      help="Filename of chains and feature table pickle")
    parser.add_option('--spf', action='store_true', default=False, dest='spf',
                      help='Use one STE per Feature')
    parser.add_option('--gpu', action='store_true', default=False, dest='gpu',
                      help='Generate GPU compatible chains and output files')
    parser.add_option('-v', '--verbose', action='store_true', default=False,
                      dest='verbose', help='Verbose')
    options, args = parser.parse_args()

    # Allows us to test ANML code faster by loading converted data structures
    if options.cftvm is not None:
        chains, ft, value_map, reverse_value_map = load_cftvm(options.cftvm)

    # Otherwise, let's do this from scratch
    else:

        # Load the model file
        if options.model is not None:
            logging.info("Loading model file from %s" % options.model)

            # Grab the model
            model = None

            # Simple check if quickrank model
            if '.xml' in options.model:

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
            raise ValueError("No valid model; provide -m <model filename>")
            exit(-1)

        logging.info("Grabbed %d constituent trees to be 'chained'" %
                     len(trees))

        # Convert all trees to chains
        chains = []

        # Keep track of features -> thresholds
        threshold_map = {}

        # Keep track of unique values
        values = []

        # We're going to use these to index leaf values (classes)
        value_map = {}
        reverse_value_map = {}

        # To deal with quickrank, we need to parse the trees differently
        if quickrank:

            logging.info("Converting QuickRank trees to chains")

            # Here is where we generate the chains from the trees
            for tree_id, tree_weight, tree_split in trees:

                qr.tree_to_chains(tree_id, tree_weight, tree_split,
                                  chains, threshold_map, values)

            values.sort()

            # Create a mapping from value to index (starting from 1)
            for _i, _value in enumerate(values):
                value_map[_value] = _i + 1
                reverse_value_map[_i + 1] = _value

        else:

            logging.info("Converting SKLEARN trees to chains")

            classes = model.classes_

            logging.info("%d unique classifications available: %s" %
                         (len(classes), str(model.classes_)))

            for tree_id, tree in enumerate(trees):

                tree_to_chains(tree, tree_id, chains, threshold_map, values)

            logging.info("There are %d chains" % len(chains))

            for _i in values:
                # value_map[classes[_i]] = _i + 1

                # We don't need a value map
                value_map = None
                reverse_value_map[_i + 1] = classes[_i]

        logging.info("Done converting trees to chains; now sorting")

        # Because we built the chains from the left-most to the right-most leaf
        # We can simply assign chain ids sequentially over our list
        for chain_id, chain in enumerate(chains):
            chain.set_chain_id(chain_id)

        # Sort the thresholds for all features
        for f, t in threshold_map.items():
            t.sort()

        if options.verbose:
            logging.info("There are %d features in the threshold map [%d-%d]" %
                         (len(threshold_map.keys()), min(threshold_map.keys()),
                          max(threshold_map.keys())))

        # Let's look at the threshold distribution if verbose
        # if options.verbose:
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

        logging.info("Dumping Chains, Feature Table,\
            Value Map and Reverse Value Map to pickle")

        # dump_cftvm(chains, ft, value_map,reverse_value_map,
        # 'chains_ft_vm_rvm.pickle')

        logging.info("Done writing out files")

    if options.gpu:

        logging.info("Generating %d GPU chains" % (len(chains)))
        gputools.gpu_chains(chains, ft, value_map, options.anml,
                            naive=options.spf)

    else:

        logging.info("Generating ANML file with%d chains" % (len(chains)))

        generate_anml(chains, ft, value_map, options.anml, naive=options.spf)

    logging.info("Dumping test file")

    X_test, y_test = load_test("testing_data.pickle")

    # If using quickrank, are features are based at index = 1, instead of 0
    ft.input_file(X_test, "input_file.bin", onebased=quickrank,
                  short=False, delimited=not options.gpu)

    logging.info("Done!")
