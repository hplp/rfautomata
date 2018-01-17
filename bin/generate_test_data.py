#!/usr/bin/env python

import numpy as np
from tools.io import *
import sys

if __name__ == '__main__':

    size = 10
    X_test, y_test = load_test("testing_data.pickle")
    print X_test
    print "-----"
    print y_test
    np.savetxt("testing.csv", X_test[:size], delimiter=',', fmt='%d')
    np.savetxt("predictions.csv", y_test[:size], delimiter=',', fmt='%d')
