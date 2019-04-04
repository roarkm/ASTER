# Pruning and Splitting

Data pre-processing.

## Current Status

`python corenlp.py`
coreNLP server (despite upping the available memory to 12g) still crashes due to heap memory limits
when parsing a full plot summary.
Truncating the plot summaries helps (but we need to parse an entire summary for the paper)
Even with truncated plot summaries, the parsing still fails sometimes (empty parse responses and
loooong parsetimes). Will investigate reducing the number of annotators used
(see https://stanfordnlp.github.io/CoreNLP/memory-time.html).

`python dataCleaning.py` now runs without error on the hardcoded text (on line 298).
Still need to feed in the results from `python corenlp.py`.

## Dependencies
**Corpus Text**
Original paper used raw text from http://www.cs.cmu.edu/~ark/personas/

Raw text `wget http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz`

Preparsed (not with needed annotators)`wget http://www.cs.cmu.edu/~ark/personas/data/corenlp_plot_summaries.tar`


**Stanford CoreNLP Server**

coreNLP is NOT compatible with Java 10. Use Java 8.
Also, using the intended 2016 version of coreNLP for now.

`wget http://nlp.stanford.edu/software/stanford-corenlp-full-2016-10-31.zip`

`unzip stanford-corenlp-full-2016-10-31.zip`

`ln -s stanford-corenlp-full-2016-10-31 ASTER`

corenlp.py expects to find englishPCFG.ser.gz so extract it (will update path strings in corenlp.py)

`mkdir coreNLP-support`

`cp stanford-corenlp-full-2016-10-31/stanford-corenlp-3.9.2-models.jar coreNLP-support`

`ln -s coreNLP-support ASTER`

`cd coreNLP-support`

`unzip stanford-corenlp-3.7.0-models.jar`

`find . | grep PCFG` # ./edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz

**VerbNet**

verbnet dir is inside the Event-Creation.

**Stanford Named Entity Recognition (NER)**

`cd ~/dev/coreNLP-support`

`wget https://nlp.stanford.edu/software/stanford-ner-2016-10-31.zip`

`unzip stanford-ner-2016-10-31.zip`

`ln -s stanford-ner-2016-10-31 ASTER`

## Usage
**Install & Setup**

`virtualenv -p python2.7 .venv && source .venv/bin/activate && pip install -r requirements.txt`

**Running**

After install use the standard `source .venv/bin/activate` and `deactivate` virtualenv helpers.

To start a Stanford CoreNLP server, run: `sh runNLPserver.sh`. (visit http://localhost:9000 to test)

Run `python corenlp.py` to parse your data and then you can run `python dataCleaning.py`
to prune and split.
