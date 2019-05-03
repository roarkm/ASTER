# Event To Sentence
Translates event representations back into human readable sentences.


## Usage
`conda activate aster`

**Event-to-Sentence** code is run using an
[Anaconda](https://www.anaconda.com/download/#linux "Anaconda 2") environment for Python 2.7.
The environment is defined in **Event-to-Sentence/environment.yml**.
Run `conda env create -f environment.yml` and then `source activate aster`
to enter the correct environment.

All configurations can be done in **config.json**.
Data is formatted as bi-text (one text file with the input sequences and another with the
corresponding output sequences aligned by line number). Run the code using
`python nmt.py --config config.json` to train and `python decode.py --config config.json` to decode.
