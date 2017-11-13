'''
    The purpose of this module is to plot information
    about automatized d-tree ensemble-based models.

    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    12 June 2017
    Version 0.2
'''

# Utility Imports
import matplotlib.pyplot as plt


# Plot the number of thresholds across features
def plot_thresholds(threshold_map):

    # Feature, unique threshold pairs
    threshold_counts = [(f, len(thresholds)) for f,
                        thresholds in threshold_map.iteritems()]

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
    plt.bar(range(len(features)), thresholds)
    plt.xlabel('Feature (sorted by threshold count)')
    plt.ylabel('Count of Unique Thresholds Per Feature')
    plt.ylim([0, thresholds[-1]])
    plt.xlim([0, len(features)])
    plt.title('Unique Thresholds Used Per Feature (Min:%d, Max:%d)' %
              (thresholds[0], thresholds[-1]))
    plt.grid(True)

    plt.show()