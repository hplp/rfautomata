# Random Forest Automata

This is an open-source implementation of Decision Tree-based (Random Forest, Boosted Regression Trees, Adaboost) machine learning models as Automata on Micron's Automata Processor (AP). This code trains a Decision Tree-based model with Scikit Learn (on the CPU), and transforms the resulting model into ANML, an XML-like representation of Nondeterministic Finite Automata (NFA) for the Automata Processor.

For more about the Automata Processor, visit CAP's website: http://cap.virginia.edu/

This project is written in Python in the Object-Oriented style.

## Quickstart Guide

To get started with the code using the example MNIST dataset, use the following instructions:

### Download

Clone the code to your local machine: 
`git clone git@github.com:tjt7a/rfautomata.git`

Make sure that you have the following dependencies installed, if missing, use pip to install:
- optparse
- logging
- pickle
- numpy

### Train the MNIST Model

Use the trainensemble script to train a Random Forest model on the canned MNIST dataset.
`bin/trainEnsemble.py -c mnist -m rf -d 8 -n 10`
`bin/trainEnsemble.py -c mnist -m rf -l 250 -n 10`

- c: canned dataset (MNIST)
- m: model type (Random Forest)
- d: depth of the decision trees (8) OR -l: number of leaves per decision tree
- n: number of trees in the ensemble (10)

This script will generate several output files:
- model.pickle: a serialized Scikit Learn Random Forest model
- report.txt: a file that contains the parameters used for training the model
- testing_data.pickle: a serialized file containing the training data for testing the model
- predictions.txt: a text file that contains the model predictions (for testing)

### Test the CPU throughput of the model

Use the test_cpu script to calculate the average throughput of your model on your CPU.
`bin/test_cpu.py` (in the same directory as your generated model files)

You can also optionally provide:
- n: the number of test iterations (defaults to 1000)
- j: the number of threads to be used for running the model
- m: the serialized model file (defaults to model.pickle)
- t: the testing data (defaults to testing_data.pickle)

The resulting throughput is measures in kilo samples classified per wall-clock second.

### Convert the Scikit Learn model into ANML Automata

Use the automatize script to convert the Scikit Learn model into an AP compatible ANML file.
`bin/automatize.py model.pickle --short -v`

Some other optional parameters include: 
- a: The name of the output ANML file (default: model.anml)
- --gpu: Generate GPU compatible chains and output files **EXPERIMENTAL**
- --circuit: Generate circuit compatible chains and output files **EXPERIMENTAL**
- --unrolled: Don't compress the chains into loops; this generates one STE per feature per chains (default: false)
- --mnrl: Generate MNRL chains with floating point inequalities (default: false)
- --short: Make a short version of the input file to the AP for testing(100 samples) (default: false)
- --longer: Make a 1000x larger input file to the AP (default: false)
- -p: Generate a plot of the threshold count distribution of the features.
- -v: Verbose

This will generate several output files:
- model.anml: This is the ANML-formatted automata file that contains the RF automata.
- input_file.bin: A transformed input file for testing. It was generated from the testing_data.pickle file.


### Run on VASim

Now that you have a model.anml file and an input_file.bin, you can run your model on the AP or using a simulator like VASim.
To run with VAsim, use the following parameters:

`vasim -r model.anml input_file.bin`

## The Data

In order to use this code to train ensemble modes from your own data, it is necessary to write an extractor for your raw data. This script processes your raw data and converts it into Numpy X and y matrices. These are then stored in a Numpy Zip file (.npz). Please see the following examples found in data/:

### ocrExtractor

The ocrExtractor program extracts the pixel feature matrix (X) and classification vector (y) from normalized handwritten letter data based on Rob Kassel's OCR work. The data can be obtained from the following locations:

https://github.com/adiyoss/StructED/tree/master/tutorials-code/ocr/data

http://ai.stanford.edu/~btaskar/ocr/

-i: Input OCR data file derived from Rob Kassel's MIT work

-o: The output .npz filename that will contain X and y

-v: Verbosity flag

--visualize: This flag will open a gui and show a random handwritten character for reference.

### mslrExtractor

The mslrExtractor program extracts the learn-to-rank feature matrix (X) and resulting rank score vector (y) from the MSLR LETOR data. The data can be obtained from Microsoft's website.

-i: Input MSLR data file

-o: The output .npz filename that will contain X and y

-v: Verbosity flag


### trainEnsemble.py

The trainEnsemble program is responsible for training an SKLEARN ensemble machine learning model given a training/testing data set, depth (or number of leaf nodes per tree) and tree count. The output of this program includes a training score, an output model pickle file, test data, predictions, and a report file containing the model's metrics.

- -c: A canned dataset in SKLEARN (mnist)

- -t: Training data file in .npz format

- -x: Testing data file in .npz format

- --metric: Provide training metric to be displayed

	1. 'acc': Accuracy

	2. 'f1': F1 Score

	3. 'mse': Mean-squared error

- -m: Choose one of the following models to train

	1. 'rf': Random Forest

	2. 'brt': Boosted Regression Tree

	3. 'ada': Adaboost Classifier

- --model-out: Name of the file for the model to be output to

- -d: Max depth of the decision trees in the ensemble

- -l: Max number of leaves per tree in the ensemble

- -n: Number of decision trees allowed in the ensemble

- -f: The number of features to use when training the ensemble

- -j: The number of jobs to run in parallel for fit/predict

- --feature_importance: Dump the feature importance values of the trained ensemble

- -v: Verbosity flag

- -r: Name of the report file containing metrics

- -p: The name of the file that contains the predictions made by the model (default: predictions.txt)

# Citing This Code

If you use this code for research purposes, please cite the below paper which introduces the contained algorithms.
Citation:

Tracy II, Tommy & Fu, Al, et al. "Towards machine learning on the Automata Processor." International Conference on High Performance Computing. Springer International Publishing, 2016.
