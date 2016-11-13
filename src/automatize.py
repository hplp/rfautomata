'''
    The purpose of this program is to convert SKLEARN models into 
    an automata representation.
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

# SKLEARN inputs

# Micron AP import

# Main()
if __name__ == '__main__':

    # Parse Command Line Arguments
    usage = '%prog [options][text]'
    parser = OptionParser(usage)
    parser.add_option('-m', '--model', type='string', dest='model', help='Input SKLEARN model')
    parser.add_option('-a', '--anml', type='string', dest='anml', default='model.anml', help='ANML output filename')
    parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Verbose')
    options, args = parser.parse_args()

