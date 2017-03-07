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

#from micronap.sdk import *

# Generate ANML code for the provided chains
def generate_anml(chains, feature_table, anml_filename, reverse_value_map=None, naive=False):

	# Create an automata network
	#anml = Anml()
	#anml_net = anml.CreateAutomataNetwork()

	# This code is used to start and report
	report_symbol = r"\x%02X" % 255

	# Iterate through all chains
	for chain in chains:

		# character class assignements for each STE start with '[' and end with ']'
		character_classes = ['[' for _ste in range(feature_table.ste_count_)]

		next_node_index = 0

		for _f in feature_table.features_:

			# If we're still pointing to a valid node ...
			if next_node_index != len(chain.nodes_):

				# Grab that next node
				next_node = chain.nodes_[next_node_index]

				# If that node has the feature we're looking at...
				if next_node.feature_ == _f:

					# If we have multiple STEs assigned to this feature...
					ste_index = 0

					for _ste, _start, _end in feature_table.get_ranges(_f):

						for c in next_node.character_sets[ste_index]:

							character_classes[_ste] += r"\x%02X" % c

						ste_index += 1

					next_node_index += 1

				# If the node does not have the feature we're looking for
				else:

					for _ste, _start, _end  in feature_table.get_ranges(_f):

						character_classes[_ste] += r"\x%02X-\x%02X" % (_start, _end - 1)


			#
			else:

				for _ste, _start, _end  in feature_table.get_ranges(_f):

					character_classes[_ste] += r"\x%02X-\x%02X" % (_start, _end - 1)

		# End the character classes with ']'
		for i in range(len(character_classes)):
			character_classes[i] += "]"


		exit()
		# stes for the current chain
		stes = []

		# Start the chain with an id that ends in :s
		ste_id = "%dt_%dl_s" % (chain.tree_id_, chain.chain_id_)

		# Have a start ste that matches on 255
		start_ste = anml_net.AddSTE(report_symbol, AnmlDefs.ALL_INPUT, anmlId=ste_id, match=False)
		stes.append(start_ste)

		for ste_i in range(feature_table.ste_count_):

			ste_id = "%dt_%dl_%ds" % (chain.tree_id_, chain.chain_id_, ste_i)

			ste = anml_net.AddSTE(character_classes[ste_i], AnmlDefs.NO_START, anmlId=ste_id, match=False)

			anml_net.AddAnmlEdge(stes[-1], ste, 0)

			stes.append(ste)

		# This is our cycle; we're mapping from the last ste back to the 2nd (the first non-start one)
		# If we're naive, don't loop back; we're in the final state
		if not naive:
			anml_net.AddAnmlEdge(stes[-1], stes[1], 0)

		last_feature = feature_table.features_[-1]

		# We want the index of the last feature's STE, because that's who's going to break us out
		ste_index_last, start, end = feature_table.get_range(last_feature)

		# Reporting STE
		ste_id = "%dt_%dl_r" % (chain.tree_id_, chain.chain_id_)

		# Add the 1 offset to the value for now (workaround)

		if reverse_value_map is not None:
			report_code = reverse_value_map[chain.value_] + 1
		else:
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
