# rfautomata
Random Forest Automata

This is an open-source implementation of Random Forests as automata on Micron's Automata Processor. In short, this code trains a Random Forest with Scikit Learn, and transforms the resulting model into ANML, an XML-like representation for the Automata Processor.

This project is written in Python in the Object-Oriented style.

The src/ directory contains the following executable files (with main()):

# trainEnsemble.py

### The trainEnsemble program is responsible for training an SKLEARN ensemble machine learning model given a training/testing data set, depth and tree count. The output of this program includes a training score, an output model pickle file, and a report file containing the model's metrics.

-t: Training data file in .npz format

-x: Testing data file in .npz format

--metric: Provide training metric to be displayed

	1. 'acc': Accuracy

	2. 'f1': F1 Score

	3. 'mse': Mean-squared error

-m: Choose one of the following models to train

	1. 'rf': Random Forest

	2. 'brt': Boosted Regression Tree

	3. 'ada': Adaboost Classifier

--model-out: Name of the file for the model to be output to.

-d: Max depth of the resulting ensemble model

-n: Number of decision trees allowed in the ensemble

-v: Verbosity flag

-r: Name of the report file containing metrics

# automatize.py

### The automatize program is responsible for converting an SKLEARN ensemble machine learning model into a representation that can be executed on the Automata Processor, ANML.

-m: Input SKLEARN model pickle file from trainEnsemble.py

-a: ANML output filename

--chain-ft-vm: Intermediate pickle filename containing the chains, the feature table, and value map

-v: Verbosity flag

# Citing This Code

If you use this code for research purposes, please cite the below paper which introduces the contained algorithms.
Citation:
Tracy II, Tommy, et al. "Towards machine learning on the Automata Processor." International Conference on High Performance Computing. Springer International Publishing, 2016.
