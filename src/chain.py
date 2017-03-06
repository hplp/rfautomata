'''
-----												-----
=  	This objected-oriented module defines a chain class =
=   ----------------------								=
=   Author: Tom Tracy II 								=
=   email: tjt7a@virginia.edu							=
=   University of virginia 								=
=   ----------------------								=
=   16 November 2016									=
=   Version 1.0											=
=														=
= 	In the first version, we removed edges				=
-----												------
'''

# Utility Imports
import copy
from random import *

# Define Node class
class Node(object):

	# Constructor for Node
	def __init__(self, feature, threshold, gt):
		self.feature_ = feature 		# Index of the feature
		self.threshold_ = threshold 	# Threshold
		self.gt_ = gt 					# greater-than?; else less-than

		# Automata-related stuff
		# We're going to need a character set per STE
		self.character_sets = None		# Start with an empty set

	# Deep copy of the Node
	def copy(self):
		return copy.deepcopy(self)

	# String representation of the node
	def __str__(self):
		string = ""
		string += "[f:%d" % self.feature_
		if self.gt_:
			string += ">"
		else:
			string += "<="
		string += "%s]" % str(self.threshold_)
		string += "CharSet: %s\n" % str(self.character_sets)
		return string

	# Define Node equivalence
	def __eq__(self, other):
		return 	self.feature_ == other.feature_ and \
				self.threshold_ == other.threshold_ and \
				self.gt_ == other.gt_

	# Define comparison operator for sorting
	def __cmp__(self, other):
		return self.get_key().__cmp__(other.get_key())

	# Define the key used for comparison
	def get_key(self):
		return self.feature_

	# Set the direction (is the direction greater-than?)
	def set_direction(self, gt):
		self.gt_ = gt

	# Set the character sets of the current node
	def set_character_sets(self, character_sets):

		if self.character_sets == None:
			self.character_sets = [[]] * len(character_sets)
		else:
			assert len(character_sets) == len(self.character_sets), \
				"|character sets| do not match!"

		# Add all chars from character_sets to self.character_sets
		for c_s, chain_c_s in zip(character_sets, self.character_sets):
			for c in c_s:
				if c not in chain_c_s:
					chain_c_s.append(c)

		self.character_sets.sort()

# Define Chain class
class Chain(object):

	# Chain constructor
	def __init__(self, tree_id, tree_weight=None):
		self.nodes_ = []				# List of nodes
		self.uid_ = 0					# Unique id for the current node
		self.tree_id_ = tree_id
		self.chain_id_ = None
		self.value_ = None
		self.chain_ = None

		# This was added for boosted regression trees; not used for other models
		self.tree_weight_ = None

	# Deep copy of the Chain
	def copy(self):
		return copy.deepcopy(self)

	# String representation of the Chain
	def __str__(self):
		string = "uid: " + str(self.uid_) + '\n'
		for index, node in enumerate(self.nodes_):
			string += str(node) + "(" + str(index) + ")"
			string +=  '\n'
		return string

	# Set the chain id
	def set_chain_id(self, chain_id):
		self.chain_id_ = chain_id

	# Set the value of the chain
	def set_value(self, value):
		self.value_ = value

	# Sort the chain by feature value, then update ids and children
	def sort_and_combine(self, verbose=False):

		# Sort the nodes_ in the chain by feature value (increasing)
		self.nodes_ = sorted(self.nodes_)

		# Can't combine with only one node!
		if len(self.nodes_) == 1 or len(self.nodes_) == 0:
			return

		# Let's combine!
		previous_index = 0
		current_index = 1

		while True:

			previous_node = self.nodes_[previous_index]
			current_node = self.nodes_[current_index]

			# If they have the same feature, combine
			if previous_node.feature_ == current_node.feature_:

				if verbose:
					print "Found two nodes with the same feature: ", \
						previous_node, " == ", current_node

				previous_node.set_character_sets(current_node.character_set)
				self.nodes_.remove(current_node)

			else:

				previous_index += 1
				current_index += 1

			# We're done
			if current_index == len(self.nodes_):
				break

	# Can't use a real generator here because then I cant pickle :(
	def index_generator(self):
		uid = self.uid_
		self.uid_ += 1
		return uid

	# Add a node to the chain
	def add_node(self, node):
		if node in self.nodes_:
			return -1
		else:
			index = self.index_generator()
			self.nodes_.append(node)

			return 1
