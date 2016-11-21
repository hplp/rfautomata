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
		self.character_set = []			# Start with an empty set

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
		string += "CharSet: %s\n" % str(self.character_set)
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

	# Set the character set of the current node
	# Either pass in a list, or the min, max of the range
	def set_character_set(self, *character_set):
		# If we passed a list
		if len(character_set) == 1:
			for c in character_set[0]:
				if c not in self.character_set:
					self.character_set.append(c)

		elif len(character_set) == 2:
			for c in range(character_set[0], character_set[1] + 1):
				if c not in self.character_set:
					self.character_set.append(c)

		self.character_set.sort()

# Define Chain class
class Chain(object):

	# Chain constructor
	def __init__(self, tree_id):
		self.nodes_ = []				# List of nodes
		self.uid_ = 0					# Unique id for the current node
		self.tree_id_ = tree_id
		self.chain_id_ = None
		self.value_ = None

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
	def sort_and_combine(self):

		# Sort the nodes_ in the chain by feature value (increasing)
		self.nodes_ = sorted(self.nodes_)

		# Can't combine with only one node!
		if len(self.nodes_) == 1 or len(self.nodes_) == 0:
			return

		# Let's combine!
		previous_index = 0
		current_index = 1

		assert len(self.nodes_[0].character_set) > 0, "Character sets not set!"

		while True:
			previous_node = self.nodes_[previous_index]
			current_node = self.nodes_[current_index]

			# If they have the same feature, combine
			if previous_node.feature_ == current_node.feature_:
				previous_node.set_character_set(current_node.character_set)
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
