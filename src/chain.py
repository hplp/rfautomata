'''
    This module defines a chain class
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    16 November 2016
    Version 1.0
'''

# Define Node class
class Node(object):

	def __init__(self, feature, threshold, gt):
		self.index_ = None 					# Index of the node
		self.feature_ = feature 			# Index of the feature
		self.threshold_ = threshold 		# Threshold
		self.gt_ = gt 						# greater-than?; else less-than

	def __str__(self):
		string = ""
		string += "[i:" + str(self.index_) + ","
		string += "f:" + str(self.feature_)
		if self.gt_:
			string += ">"
		else:
			string += "<="
		string += str(self.threshold_) + ']'
		return string

	def set_index(self, index):
		self.index_ = index

# Define Chain class
class Chain(object):

	def __init__(self):

		self.node_lookup_ = []				# List of nodes
		self.nodes_ = {}					# Node -> {list of adjacent nodes}
		self.start_ = None					# Start of the chain
		self.end_ = None					# End of the chain
		self.uid_ = 0

	def __str__(self):
		string = ""
		for key, values in self.nodes_.items():
			if key == self.start_:
				string += "(START): "
			string += (str(key) + " -> " + str(values))
			if key == self.end_:
				string += ": (END)"
			string +=  '\n'
		return string

	# Set the start node of the chain
	def set_start(self, node):
		self.start_ = node.index_

	# Set the end node of the chain
	def set_end(self, node):
		self.end_ = node.index_

	# Add a node to the chain
	def add_node(self, node):
		node.set_index(self.uid_)
		self.uid_ += 1
		self.node_lookup_.append(node)
		self.nodes_[node.index_] = []


	# Add an edge from node -> neighbor
	def add_edge(self, node, neighbor):
		if node.index_ is None:
			self.add_node(node)
		if neighbor.index_ is None:
			self.add_node(neighbor)
			
		if neighbor.index_ in self.nodes_[node.index_]:
			return -1	# Edge already exists
		else:
			self.nodes_[node.index_].append(neighbor.index_)

	# Remove node from chain
	def remove_node(self, node):
		if node.index_ not in self.nodes_:
			return -1
		else:
			del self.nodes_[node.index_]
			self.node_lookup_[node.index_] = None

		try:
			del self.nodes_[index]
		except:
			return -1						# No such node

	# Remove an edge from the chain
	def remove_edge(self, node, neighbor):
		if node.index_ in self.nodes_:
			try:
				self.nodes_[node.index_].remove(neighbor.index_)
			except:
				return -1					# No such edge
		else:
			return -1						# No such edge

# Main() for testing
if __name__ == "__main__":
	
	C = Chain()

	for f in range(10):	
		node = Node(f, 0.1*f, f%2)
		C.add_node(node)
		if f > 0:
			C.add_edge(C.node_lookup_[-2], C.node_lookup_[-1])

	C.set_start(C.node_lookup_[0])
	C.set_end(C.node_lookup_[-1])
	C.remove_edge(C.node_lookup_[2], C.node_lookup_[3])

	print(C)
	for n in C.node_lookup_:
		print n