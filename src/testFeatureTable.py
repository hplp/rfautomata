import unittest
from featureTable import *
from random import *

'''
    This unit test file tests various aspects of the featureTable class

    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    21 November 2016
    Version 1.0
'''

# Test the FeatureTable class with a few unit tests
class TestFeatureTable(unittest.TestCase):

	# Build an arbitrary node; we'll use this for testing
	def setUp(self):
		self.features = []
		self.threshold_map = {}

		for _i in range(100):
			f = randint(1, 100)

			if f in self.features:
				continue

			self.features.append(f)

			thresholds = []

			for _j in range(randint(50, 100)):
				t = randint(1, 100)

				if t in thresholds:
					continue

				thresholds.append(t)

			self.threshold_map[f] = thresholds

		self.features.sort()

		for k, val in self.threshold_map.items():
			val.sort()

		self.ft = FeatureTable(self.features, self.threshold_map)

	# Make sure the constructor was built correctly
	def test_constructor(self):
		self.assertEqual(self.ft.features_, self.features)
		self.assertEqual(self.ft.threshold_map_, self.threshold_map)

		# Grab the number of thresholds used in total
		total_address_space = sum([len(val) for key, val in self.threshold_map.items()])

		# Then add the number of -1s added (one per feature)
		total_address_space += len(self.features)

		# Check to make sure the address spaces have the same size
		self.assertEqual(len(self.ft.stes_[0]), total_address_space)

		# Now let us test each feature!
		for feature in self.features:

			ste, start, end = self.ft.feature_pointer_[feature]
			thresholds = self.threshold_map[feature]

			self.assertEqual(ste, 0)

			for i,j in enumerate(range(start, end)):
				self.assertEqual(thresholds[i], self.ft.stes_[ste][j])

	def test_get_range(self):
		ste, start, end = self.ft.get_range(self.ft.features_[-1])
		self.assertEqual(ste, 0)
		self.assertTrue(start < end)

	def test_get_symbol(self):
		# Choose a random feature
		feature_index = randint(0, len(self.ft.features_))
		feature = self.features[feature_index]
		ste, start, end = self.ft.get_range(feature)

		# Check smallest range
		thresholds = self.threshold_map[feature]
		small_value = thresholds[0] - 1
		small_label = self.ft.get_symbol(feature, small_value)[1]
		self.assertEqual(small_label, start)

		# Check largest range
		large_value = thresholds[-1] + 1
		large_label = self.ft.get_symbol(feature, large_value)[1]
		self.assertEqual(large_label, end)

if __name__ == '__main__':
	unittest.main()