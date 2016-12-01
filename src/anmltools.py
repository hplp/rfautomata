'''
	This module is meant for interfacing with the ANML API

    This module contains two functions:
    1. generate_anmL(): Generate ANML from the chains

    2. compile_anml(): Compile the resulting ANML into an FSM for the AP
    ----------------------
    Author: Tom Tracy II
    email: tjt7a@virginia.edu
    University of Virginia
    ----------------------
    21 November 2016
    Version 1.0
'''

from micronap.sdk import *

# Generate ANML code for the provided chains
def generate_anml(chains, feature_table, anml_filename):

	# Create an automata network
	anml = Anml()
	anml_net = anml.CreateAutomataNetwork()

	# This code is used to start and report
	report_symbol = r"\x%02X" % 255

	# Iterate through all chains

	for chain in chains:

		# character class assignements for each STE start with '[' and end with ']'
		character_classes = ['[' for _ste in range(feature_table.ste_count_)]

		node_index = 0
		feature_index = 0

		while True:

			# We're done
			if feature_index == len(feature_table.features_):
				break # We're done here, ya'll

			# If we've gone through all of the nodes in the chain...
			if node_index == len(chain.nodes_):
				node = None
			else:
				node = chain.nodes_[node_index]

			feature = feature_table.features_[feature_index]

			ste_index, start, end = feature_table.get_range(feature)

			if (node is None) or (node.feature_ != feature):
				character_classes[ste_index] += r"\x%02X-\x%02X" % (start, end)

			else:
				for c in node.character_set:
					character_classes[ste_index] += r"\x%02X" % c

				node_index += 1

			feature_index += 1


		# End the character class
		for i in range(len(character_classes)):
			character_classes[i] += "]"

		print "character_class:"
		print character_classes

		# stes for the current chain
		stes = []

		# Start the chain with an id that ends in :s
		ste_id = "%dt_%dl_s" % (chain.tree_id_, chain.chain_id_)

		# Have a start ste that matches on 255
		start_ste = anml_net.AddSTE(report_symbol, AnmlDefs.ALL_INPUT, anmlId=ste_id, match=False)
		stes.append(start_ste)

		for ste_i in range(feature_table.ste_count_):
			ste_id = "%dt_%dl_%ds" % (chain.tree_id_, chain.chain_id_, ste_i)

			print "Ste_i: ", ste_i
			print "Character_classes: ", character_classes[ste_i]
			print "ste_id: ", ste_id

			ste = anml_net.AddSTE(character_classes[ste_i], AnmlDefs.NO_START, anmlId=ste_id, match=False)

			anml_net.AddAnmlEdge(stes[-1], ste, 0)

			stes.append(ste)

		# This is our cycle; we're mapping from the last ste back to the 2nd (the first non-start one)
		anml_net.AddAnmlEdge(stes[-1], stes[1], 0)


		last_feature = feature_table.features_[-1]

		# We want the index of the last feature's STE, because that's who's going to break us out
		ste_index_last, start, end = feature_table.get_range(last_feature)

		# Reporting STE
		ste_id = "%dt_%dl_r" % (chain.tree_id_, chain.chain_id_)

		# Add the 1 offset to the value for now (workaround)
		report_code = chain.value_ + 1#value_map[chain.value_]

		ste = anml_net.AddSTE(report_symbol, AnmlDefs.NO_START, anmlId=ste_id, reportCode=report_code)

		# Need to add 1 to the index, because the first STE is the starting STE
		anml_net.AddAnmlEdge(stes[ste_index_last + 1], ste, 0)

	anml_net.ExportAnml(anml_filename)

# Expect single filename (ANML) or two filenames (ANML, Element File)
def compile_anml(anml, *filenames):


	if len(filenames) == 0:
		raise ValueError("Error: No filename[s] specified to compiler!")

	automata_filename = filenames[0]

	if len(filenames) == 1:
		emap_filename = None
	elif len(filenames) == 2:
		emap_filename = filenames[1]

	automata, element_map = anml.CompileAnml(CompileDefs.AP_OPT_SHOW_STATS | CompileDefs.AP_OPT_SHOW_PROGRESS | \
		CompileDefs.AP_OPT_MERGE_ONE_EXPRESSION)

	automata.save(automata_filename)

	if emap_filename is not None:
		element_map.SaveElementMap(emap_filename)
