'''
    The purpose of this program is to extract the X feature vector and y
    results from normalized OCR data.
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    Data can be found
    https://github.com/adiyoss/StructED/tree/master/tutorials-code/ocr/data
    http://ai.stanford.edu/~btaskar/ocr/
    ----------------------
    14 November 2016
    Version 1.0
'''
# Support imports
import sys, json
from optparse import OptionParser
import numpy as np
import logging

# Visualization imports

# Turn on logging.
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)

# read from the ocr file
def readOCR(filename):
    y = np.empty((0, 1), int)
    X = np.empty((0, 135), float)
    with open(filename) as ocrfile:
        for line in ocrfile:
            tokens = line.split('\t')
            y = np.append(y, np.array([int(tokens[1])]))
            X = np.append(X, np.array([float(x.split(':')[1]) for x in tokens[2:]]))
    return X, y


if __name__ == '__main__':

    # Parse Command Line Arguments
    usage = '%prog [options][text]'
    parser = OptionParser(usage)
    parser.add_option('-i', '--file-in', type='string', dest='infile', help='Input OCR data file')
    parser.add_option('-o', '--file-out', type='string', dest='outfile', help='Save resulting X and y to a file')
    parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Verbose')
    parser.add_option('--vizualize', action='store_true', default=False, dest='viz', help='Enable to visualize')
    options, args = parser.parse_args()

    if options.outfile is None:
        raise ValueError("No valid OCR output file name specified; provide '-o'")
        exit(-1)

    if options.infile is not None:
        if options.verbose:
            logging.info('Reading from file: %s' % options.infile)

        X, y = readmslr(options.infile)

        if options.verbose:
            logging.info('Done reading file')

    else:
        raise ValueError("No valid OCR input file name specified; provide '-i")
        exit(-1)

    if options.verbose:
        logging.info("Writing to file: %s" % options.outfile)

    np.savez(options.outfile, X=X, y=y)
