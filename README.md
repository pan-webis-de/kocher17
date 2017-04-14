# kocher17

This repository contains the software for an unsupervised author clustering model and a supervised author profiling approach.
The systems were used in the PAN Author Identification task and Author Profiling task at CLEF 2016.

## Usage Author Clustering

Run:

    python panAC.py -i input_folder -o output_folder


## Usage Author Profiling

Train:

    python panAPtrain.py -i input_folder -o train_folder

Test:

    python panAPtest.py -i input_folder -r train_folder -o output_folder

If in the test  script the input_folder and the train_folder contain the same data, then "loo" in panAPtest.py on line 14 should be changed from 0 to 1 to use the leaving-one-out approach.

## Requirements

- Python 2.7.13 (probably also works with other versions)
- The PAN data, available [here](http://pan.webis.de/clef17/pan17-web/author-identification.html "clustering corpus") and [here](http://pan.webis.de/clef17/pan17-web/author-profiling.html "clustering corpus") to download.