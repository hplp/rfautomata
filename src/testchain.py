import unittest
import chain

def build_node():
	feature = 12
	threshold = 0.12
	gt = False
	n = chain.Node(feature, threshold, gt)
	return n

def build_chain():
	c = chain.Chain()
	return c

class TestNode(unittest.TestCase):

	def test_constructor(self):
		n = build_node()

		self.assertEqual(n.index_, None)
		self.assertEqual(n.feature_, 12)
		self.assertEqual(n.threshold_, 0.12)
		self.assertEqual(n.gt_, False)

	def test_set_index(self):
		n = build_node()
		self.assertEqual(n.index_, None)
		n.set_index(9)
		self.assertEqual(n.index_, 9)

class TestChain(unittest.TestCase):

	def test_constructor(self):
		c = build_chain()
		self.assertEqual(len(c.node_lookup_), 0)
		self.assertEqual(len(c.nodes_), 0)
		self.assertEqual(c.start_, None)
		self.assertEqual(c.end_, None)
		self.assertEqual(c.uid_, 0)

	def test_add_node(self):
		c = build_chain()
		n = chain.Node(0, 0.1, False)
		c.add_node(n)

		self.assertEqual(len(c.node_lookup_), 1)
		self.assertEqual(c.node_lookup_[0], n)
		self.assertTrue(n.index_ in c.nodes_)
		self.assertTrue(n.index_ == 0)

	def test_remove_node(self):
		c = build_chain()
		n = chain.Node(0, 0.1, False)
		c.add_node(n)
		c.remove_node(n)

		self.assertEqual(c.node_lookup_[n.index_], None)
		self.assertFalse(n in c.node_lookup_)
		self.assertFalse(n.index_ in c.nodes_)

	def test_add_edge(self):
		c = build_chain()
		n1 = chain.Node(0, 0.1, False)
		n2 = chain.Node(1, 0.2, True)
		c.add_edge(n1, n2)

		self.assertEqual(n1.index_, 0)
		self.assertEqual(n2.index_, 1)
		self.assertTrue(n1.index_ in c.nodes_)
		self.assertTrue(n2.index_ in c.nodes_)
		self.assertTrue(n2.index_ in c.nodes_[n1.index_])
		self.assertTrue(n1 in c.node_lookup_)
		self.assertTrue(n2 in c.node_lookup_)

	def test_remove_edge(self):
		c = build_chain()
		n1 = chain.Node(0, 0.1, False)
		n2 = chain.Node(1, 0.2, True)
		c.add_edge(n1, n2)
		c.remove_edge(n1, n2)
		self.assertFalse(n2.index_ in c.nodes_[n1.index_])


if __name__ == '__main__':
	unittest.main()