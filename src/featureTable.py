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

# Define FeatureTable class
class FeatureTable(object):

	# Constructor creates one contiguous feature address space
	def __init__(self, features, threshold_map):

		# feature -> [(STE, start, end)]
		self.feature_pointer_ = {}

		# List of address spaces by STE
		self.stes_ = []

		# Number of STES requires
		# Start with 1, then calculate correct number (with compact())
		self.ste_count_ = 1

		# A list of all features used
		self.features_ = features

		# A dictionary from features -> list of thresholds
		self.threshold_map_ = threshold_map

		# Check to see if we've compacted this FT already
		self.compact_ = False

		flat_table_ = []

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
		self.stes_.append(flat_table_)

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


	# Complex compaction that deals with features with many splits
	# Not looking to run a knapsack algorithm here
	#* This needs to be further developed *#
	def compact2(self, MAX_RANGE_SIZE=150):

		if self.compact_:
			print "Already compact!"
			return 0

		self.ste_count_ = 1

		while True:

			# Keep incrementing the STE count
			self.ste_count_ += 1
			ste_index = 0

			# Zero the counters for the STEs
			temp_counts = [0 for x in range(self.ste_count_)]

			for feature in self.features_:

				if ste_index == self.ste_count_:
					ste_index = 0

				two_stes = False

				for ste, start_index, end_index in self.get_ranges(feature):

					range_size = (end_index - start_index) + 1

				# If the range for a particular feature is too big,
				# this compaction algorithm won't work
					if range_size > MAX_RANGE_SIZE:

					# Break up this feature into multiple STEs
						# The max range size is a knob that needs to be turned
						num_stes = range_size / MAX_RANGE_SIZE

						#OK, we need two STEs
						temp_counts[ste_index] += range_size_msb

						ste_index += 1

						ste_index = 0 if ste_index == self.ste_count_ else ste_index

						temp_counts[ste_index] += range_size_lsb

				else:
					temp_counts[ste_index(feature)] += range_size

				ste_index += 1

			if max(temp_counts) > 254:
				continue

			else:
				break

		print "Found minumum number of stes required to be: ", \
			self.ste_count_

		# Empty the stes to fill with feature threshold ranges
		self.stes_ = [[] for x in range(self.ste_count_)]

		# Iterate over all features and fill STE namespaces
		for feature_index,feature in enumerate(self.features_):

			ste_i = ste_index(feature_index)
			thresholds = self.threshold_map_[feature]

			start = len(self.stes_[ste_i])
			end = start + len(thresholds)

			self.feature_pointer_[feature] = (ste_i, start, end)
			self.stes_[ste_i] +=  thresholds
			self.stes_[ste_i].append(-1)

	# Fit all ranges of all features in the minimum number of STEs
	def compact(self, naive=False):

		if self.compact_:
			print "Already compacted"
			return 0

		# This will set self.ste_count_
		if naive:

			self.ste_count_ = 0
			self.stes_ = []

			for feature in self.features_:

				# Because we're not already compact, there will be one of these
				ste, start_index, end_index = self.get_ranges(feature)[0]

				assert ste == 0, "STE is not 0!"

				range_size = (end_index - start_index) + 1

				# If we can cram this feature into a single STE
				if range_size < 255:

					# Index of the next STE
					ste_i = self.ste_count_

					# Grab this feature's thresholds
					thresholds = self.threshold_map_[feature]

					# We're making a new STE
					self.stes_.append([])
					self.ste_count_ += 1

					# The features start at 0
					start = 0

					# and end at |thresholds|
					end = len(thresholds)

					# Update FT members with (STE, START, END) tuple
					self.feature_pointer_[feature] = [(ste_i, start, end)]

					# Append the thresholds to the new STE
					self.stes_[-1] += thresholds

					# Finish off the thresholds with the > last token (-1)
					self.stes_[-1].append(-1)

				# If not
				else:

					ste_i = self.ste_count_
					thresholds = self.threshold_map_[feature]

					tuples = []

					num_stes = int(math.ceil(len(thresholds) / 254))

					for s in range(num_stes):

						self.stes_.append([])

						start = 0
						end = 254 if s < (num_stes - 1) else (len(thresholds) % num_stes)

						self.stes_[-1] += thresholds

						if s == (num_stes - 1):
							self.stes_[-1].append(-1)

						# This is the don't care label
						self.stes_[-1].append(-2)

						tuples.append((ste_i + s, start, end))

						self.ste_count_ += 1


					self.feature_pointer_[feature] = tuples

		else:

			return_code = self.calculate_min_stes()

			# Naive compaction failed
			if return_code == -1:
				if self.compact2() == -1:
					print "Sorry, we're railed"
					exit()
				else:
					print "Compact2() worked!"
					return 0

			else:

				# Naive compaction worked; use the proposed STE count
				self.ste_count_ = return_code

				# Lambda expression for assigning ste_id based on feature
				ste_index = lambda fid : fid % self.ste_count_

				# Empty the stes to fill with feature threshold ranges
				self.stes_ = [[] for x in range(self.ste_count_)]

				# Iterate over all features and fill STE namespaces
				for feature_index,feature in enumerate(self.features_):

					ste_i = ste_index(feature_index)
					thresholds = self.threshold_map_[feature]

					start = len(self.stes_[ste_i])
					end = start + len(thresholds)

					self.feature_pointer_[feature] = [(ste_i, start, end)]
					self.stes_[ste_i] +=  thresholds
					self.stes_[ste_i].append(-1)

	'''
		For simplicity, we're making the assumption that all features
		have fewer than 254 thresholds; if this is not the case, this function
		and the compact() function need to be combined and extended.

		We use an assert to catch features that are too large
	'''

	# Calculate min STE count to fit all features; return number of stes needed
	def calculate_min_stes(self):

		# If max address space of all stes is <= 254 we good
		# This assumes that we've pushed all of the address spaces into
		# one STE to be split up into multiple
		if max(len(ste) for ste in self.stes_) <= 254:
			return 1

		else:
			ste_count_ = 1

			# Lambda expression for assigning ste_id by feature
			ste_index = lambda fid, ste_count : fid % ste_count

			while True:

				# Keep incrementing the STE count
				ste_count_ += 1

				# Zero the counters for the STEs
				temp_counts = [0 for x in range(ste_count_)]

				for feature in self.features_:

					ste, start_index, end_index = self.get_ranges(feature)[0]

					range_size = (end_index - start_index) + 1

					# If the range for a particular feature is too big,
					# this compaction algorithm won't work
					if range_size > 254:
						return -1

					temp_counts[ste_index(feature, ste_count_)] += range_size

				if max(temp_counts) > 254:
					continue

				else:
					return ste_count_
