'''
    The purpose of this module is to plot information about automatized d-tree ensemble-based models.

    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    22 February 2017
    Version 1.0
'''

# Utility Imports
import matplotlib.pyplot as plt

# Plot the number of thresholds across features
def plot_thresholds(threshold_map):

    # The features are the keys of the threshold_map
    features = threshold_map.keys()

    # The values are a list of unique thresholdsccs
    threshold_counts = [len(thresholds) for f, thresholds in threshold_map.iteritems()]

    # Zip the two together, so we can sort them
    threshold_counts = zip(features, threshold_counts)

    # Sort tuples of (feature, threshold_count) by threshold_count
    threshold_counts.sort(key=lambda x: x[1])

    # Split the sorted list of (feature, len(thresholds)) tuples
    features = [x[0] for x in threshold_counts]
    thresholds = [x[1] for x in threshold_counts]

    # Print stats
    print "Min:", min(thresholds)
    print "Max:", max(thresholds)
    print "Total:", sum(thresholds)

    # Plot threshold counts
    plt.scatter(range(len(features)), thresholds)
    plt.xlabel('Feature (sorted by threshold count)')
    plt.ylabel('Number of Unique Thresholds Used in Ensemble')
    plt.title('Number of Unique Thresholds Required per Feature')
    plt.grid(True)

    plt.show()