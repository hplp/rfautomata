'''
    This objected-oriented module defines a Feature Lookup Table class

    This lookup table has three main purposes:
    1. We use the address spaces to efficiently fit all features into
    	as few STEs as possible.
    2. We use the resulting lookup table to map feature values to feature
    	labels.
    3. We use the lookup table to generate input files for the AP.
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    7 February 2017
    Version 1.1
'''

# Utility imports
import copy
from termcolor import colored
from random import *
import math
from array import *
import util

# Define FeatureTable class
class FeatureTable(object):

	# Constructor creates one contiguous feature address space
	def __init__(self, threshold_map):

		# feature -> [(STE, start, end)]
		self.feature_pointer_ = {}

		# A list of all features used
		self.features_ = threshold_map.keys()

		# A dictionary from features -> list of thresholds
		self.threshold_map_ = threshold_map

		# Find the minimum number of stes required to handle the features
		feature_pointer, stes = util.compact(threshold_map)

		# Assign feature_pointer and stes
		self.feature_pointer_ = feature_pointer

		# List of address spaces by STE
		self.stes_ = stes

		# Set the number of stes
		self.ste_count_ = len(stes)


	# String representation of the STEs
	def __str__(self):
		string = ""

		# Enumerate all features and which STE its mapped to / what range
		for i, feature in enumerate(self.features_):
			string += colored("F:%d", 'magenta') % feature

			for ste, start, end in self.feature_pointer_[feature]:

				string += "STE:%d,S:%d,E:%d" % (ste, start, end)
				string += (";") if i != (len(self.features_) - 1) else ("\n\n")

		# Enumerate all stes
		for i, ste in enumerate(self.stes_):
			string += colored("STE:%d[", 'blue') % i

			# Enumerate all ranges
			for j, r in enumerate(ste):
				string += (colored(str(r), 'green') if r != -1 else colored(str(r), 'red'))
				string += "]"
				string += ("[") if j != len(ste) - 1 else colored("]", 'blue')

		return string

	# Return the ranges in the address space that corresponds to the start/end of a feature
	def get_ranges(self, feature):

		return self.feature_pointer_[feature]

	# Return the STEs that this feature is mapped to
	def get_stes(self, feature):

		return [ste for ste, start, end in self.get_ranges(feature)]

	# Return list of tuples [(ste, index)] that represent ranges in which the value is found
	# This is currently implemented with a linear-time algorithm, but can be
	# improved in the future
	def get_symbols(self, feature, value):

		ranges = self.get_ranges(feature)
		found_symbol = False
		return_list = []

		for ste, start, end in ranges:

			for i in range(start, end + 1):

				# If we already have a label, just tack on -2s
				if found_symbol:
					assert -2 == self.stes_[ste][end], "-2 != %d" % self.stes_[ste][end]
					return_list.append((ste, end))

				threshold_value = self.stes_[ste][i]

				# If at end of ranges, or our value <= threshold value,
				# append this label
				if threshold_value == -1 or value <= threshold_value:

					return_list.append((ste, i))
					break

				# We found a don't care
				elif threshold_value == -2:

					return_list.append((ste, i))

				# If our value is still greater than the threshold_value, keep going
				else:

					continue

		return return_list

	# This function generates an input file from an input X
	def input_file(self, X, filename):

		byte_counter = 0
		feature_set = set()

		with open(filename, 'wb') as f:

			inputstring = array('B')
			inputstring.append(255) #We always start with a /xff

			for row in X:

				# For each feature in the row
				for f_i, f_v in enumerate(row):

					assert len(row) == len(self.features_), "The row (%d) doesn't have enough features! (%d)" % (len(row), len(self.features_))

					if f_i in self.features_:

						feature_set.add(f_i)

						for ste, symbol in self.get_symbols(f_i, f_v):

							assert symbol < 255, "A symbol is >= 255!"

							inputstring.append(symbol)

							byte_counter += 1

				# Check for duplicates
				assert len(self.features_) == len(set(self.features_)), "We have duplicate features"

				assert len(feature_set) == len(self.features_), "Missing feature: %s" % str(set(self.features_).difference(feature_set))

				byte_counter = 0
				feature_set.clear()

				inputstring.append(255)

			f.write(inputstring.tostring())

		# Return the number of bytes written to the input file
		return len(inputstring.tostring())


		# Iterate through all features
		for feature_, thresholds_ in self.threshold_map_.iteritems():

			# Concatenate to end of current address space
			start = len(flat_table_)
			end = start + len(thresholds_)

			# Update pointers with (STE, Start index, end index)
			# This implies we are using only one STE (fine until we compact())
			self.feature_pointer_[feature_] = [(0, start, end)]

			# Concatenate thresholds to flat table
			flat_table_ += thresholds_

			# This is the end of the current feature
			flat_table_.append(-1)

		# For constructor cram all feature ranges into one STE
		self.stes_ = [flat_table_]
