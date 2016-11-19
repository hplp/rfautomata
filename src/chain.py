'''
    This objected-oriented module defines a chain class
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    16 November 2016
    Version 1.0
'''

import copy

# Define Node class
class Node(object):

	def __init__(self, feature, threshold, value, leaf, gt):
		self.index_ = -1 					# Index of the node
		self.feature_ = feature 			# Index of the feature
		self.threshold_ = threshold 		# Threshold
		self.value_ = value 				# Value
		self.leaf_ = leaf					# Leaf node?
		self.gt_ = gt 						# greater-than?; else less-than

		# Automata-related stuff
		self.character_set = []				# Start with an empty set

	def copy(self):
		return copy.deepcopy(self)

	def __str__(self):
		string = ""
		if self.leaf_:
			string += "<LEAF: %s>" % str(self.value_)
		else:
			string += "[i:%s,f:%d" % (str(self.index_), self.feature_)
			if self.gt_:
				string += ">"
			else:
				string += "<="
			string += "%s]" % str(self.threshold_)
		return string

	def __eq__(self, other):
		return self.index_ == other.index_ and \
				self.feature_ == other.feature_ and \
				self.threshold_ == other.threshold_ and \
				self.value_ == other.value_ and \
				self.leaf_ == other.leaf_ and \
				self.gt_ == other.gt_

	# Set the index
	def set_index(self, index):
		self.index_ = index

	# Set the direction (is the direction greater-than?)
	def set_direction(self, gt):
		self.gt_ = gt

	# Set the character set of the current node
	def set_character_set(self, min, max):
		for i in range(min_symbol, max_symbol+1):
			self.character_set.append(i)

# Define Chain class
class Chain(object):

	def __init__(self):

		self.nodes_ = []							# List of nodes
		self.children_ = []							# Node -> [list of adjacent nodes]
		self.start_ = None							# Start of the chain
		self.end_ = None							# End of the chain
		self.uid_ = 0								# Unique id for the current node

	def copy(self):
		return copy.deepcopy(self)

	def __str__(self):
		string = "uid: " + str(self.uid_) + '\n'
		for index, childs in enumerate(self.children_):
			if index == self.start_:
				string += "(START): "
			string += str(self.nodes_[index]) + "(" + str(index) + ")"
			string += " -> "
			if len(childs) > 0:
				string += str(self.nodes_[childs[0]]) + "(" + str(childs[0]) + ")"
			else:
				string += "(NONE)"
			if index == self.end_:
				string += ": (END)"
			string +=  '\n'
		return string

	# Can't use a real generator here because then I cant pickle :(
	def index_generator(self):
		uid = self.uid_
		self.uid_ += 1
		return uid

	# Set the start node of the chain
	def set_start(self, node):
		self.start_ = node.index_

	# Set the end node of the chain
	def set_end(self, node):
		self.end_ = node.index_

	# Add a node to the chain
	def add_node(self, node):
		if node in self.nodes_:
			return -1
		else:
			index = self.index_generator()
			node.set_index(index)
			self.nodes_.append(node)
			self.children_.append([])

			assert node.index_ == (len(self.nodes_) - 1), "Node.index != len(nodes) - 1"
			assert node.index_ == (len(self.children_) - 1), "Node.index != len(children) - 1"

			return 1


	# Add an edge from node -> neighbor
	def add_edge(self, node, neighbor):
		if node not in self.nodes_:				# It hasn't been added to the chain yet
			self.add_node(node)
		if neighbor not in self.nodes_:
			self.add_node(neighbor)
			
		if neighbor.index_ in self.children_[node.index_]:
			return -1	# Edge already exists
		else:
			self.children_[node.index_].append(neighbor.index_)
			return 1

	# Remove node from chain
	def remove_node(self, node):
		if node not in self.nodes_:
			return -1
		else:
			del self.children_[node.index_]
			self.nodes_[node.index_] = None
			return 1

	# Remove an edge from the chain
	def remove_edge(self, node, neighbor):
		if node not in self.nodes_:
			return -1
		if neighbor not in self.nodes_:
			return -1

		if neighbor.index_ in self.children_[node.index_]:
			self.children_[node.index_].remove(neighbor.index_)
			return 1
		else:
			return -1						# No such edge

# Main() for testing
if __name__ == "__main__":
	
	C = Chain()

	for f in range(10):	
		node = Node(f, 0.1*f, f%2, 0, False)
		C.add_node(node)
		if f > 0:
			C.add_edge(C.nodes_[-2], C.nodes_[-1])

	C.set_start(C.nodes_[0])
	C.set_end(C.nodes_[-1])

	D = C.copy()

	print(C)

	node = Node(10, 0.1*10, 0, 0, True)
	D.add_edge(D.nodes_[-1], node)

	print(D)