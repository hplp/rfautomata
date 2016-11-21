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
def generate_anml(chains, feature_table, value_map, anml_filename):

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

		for feature in feature_table.features_:

			node = chain.nodes_[node_index]

			ste_index, start, end = feature_table.get_range(feature)

			if node.feature_ == feature:

				for c in chain.nodes_[node_index].character_set:
					character_classes[ste_index] += r"\x%02X" % c
				
				node_index += 1

			# Don't use this feature in our chain, accept all
			else:
				assert feature < node.feature_, "feature is NOT > node.feature_"
				character_classes[ste_index] += r"\x%02X-\x%02X" % (start, end)


		# End the character class
		for cc in character_classes:
			cc += ']'

		print "character_class:"
		print character_classes

		exit()

		# stes for the current chain
		stes = []

		# Start the chain with an id that ends in :s
		ste_id = "%dt:%dl:s" % (chain.tree_id, chain.chain_id_)

		# Have a start ste that matches on 255
		start_ste = anml_net.AddSTE(report_symbol, AnmlDefs.ALL_INPUT, anmlId=ste_id, match=False)
		stes.append(start_ste)

		for ste_i in range(feature_table.ste_count_):
			ste_id = "%dt:%dl:%ds" % (chain.tree_id, chain.chain_id_, ste_i)

			ste = anml_net.AddSTE(character_classes[ste_i], AnmlDefs.NO_START, anmlId=ste_id, match=False)

			anml_net.AddAnmlEdge(stes[-1], ste, 0)

			stes.append(ste)

		anml_net.AddAnmlEdge(stes[-1], stes[1], 0)

		# Reporting STE
		ste_id = '%dt:%dl:r' % (chain.tree_id, chain.chain_id)
		report_code = value_map(chain.value_)

		ste = anml_net.AddSTE(report_symbol, AnmlDefs.NO_START, anmlID=ste_id, ReportCode=report_code)

		anml_net.AddAnmlEdge()

	anml_net.ExportAnml(anml_filename)

# Expect single filename (ANML) or two filenames (ANML, Element File)
def compile_anml(anml, *filenames)


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