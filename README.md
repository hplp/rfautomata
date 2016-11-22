# Random Forest Automata

This is an open-source implementation of Decision Tree-based (Random Forest, Boosted Regression Trees, Adaboost) machine learning models as Automata on Micron's Automata Processor (AP). This code trains a DT-based model with Scikit Learn (on the CPU), and transforms the resulting model into ANML, an XML-like representation of Nondeterministic Finite Automata (NFA) for the Automata Processor.

For more about the Automata Processor, visit CAP's website: http://cap.virginia.edu/

This project is written in Python in the Object-Oriented style.

# The Data

In order to use this code to train ensemble modes from your data, it is necessary to write an extractor for the raw data. This file processes your raw data and converts it into Numpy X and y matrices. These are then stored in a Numpy Zip file (.npz) for more efficient processing. Please see the following examples found in data/:

### ocrExtractor

The ocrExtractor program extracts the pixel feature matrix (X) and classification vector (y) from normalized handwritten letter data based on Rob Kassel's OCR work. The data can be obtained from the following locations:

https://github.com/adiyoss/StructED/tree/master/tutorials-code/ocr/data

http://ai.stanford.edu/~btaskar/ocr/

-i: Input OCR data file derived from Rob Kassel's MIT work

-o: The output .npz filename that will contain X and y

-v: Verbosity flag

--visualize: This flag will open a gui and show a random handwritten character for reference.

# mslrExtractor

The mslrExtractor program extracts the learn-to-rank feature matrix (X) and resulting rank score vector (y) from the MSLR LETOR data. The data can be obtained from Microsoft's website.

-i: Input MSLR data file

-o: The output .npz filename that will contain X and y

-v: Verbosity flag

# The Programs 

The src/ directory contains the following executable files (with main()):

### trainEnsemble.py

The trainEnsemble program is responsible for training an SKLEARN ensemble machine learning model given a training/testing data set, depth and tree count. The output of this program includes a training score, an output model pickle file, and a report file containing the model's metrics.

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

### automatize.py

The automatize program is responsible for converting an SKLEARN ensemble machine learning model into a representation that can be executed on the Automata Processor, ANML.

-m: Input SKLEARN model pickle file from trainEnsemble.py

-a: ANML output filename

--chain-ft-vm: Intermediate pickle filename containing the chains, the feature table, and value map

-v: Verbosity flag

# Citing This Code

If you use this code for research purposes, please cite the below paper which introduces the contained algorithms.
Citation:
Tracy II, Tommy, et al. "Towards machine learning on the Automata Processor." International Conference on High Performance Computing. Springer International Publishing, 2016.
