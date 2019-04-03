# Pruning and Splitting

Data pre-processing.

## Current Status

`python corenlp.py`
coreNLP server (despite upping the available memory to 12g) still crashes due to heap memory limits
when parsing a full plot summary.
Truncating the plot summaries helps (but we need to parse an entire summary for the paper)
Even with truncated plot summaries, the parsing still fails sometimes (empty parse responses and
loooong runtimes). Will investigate reducing the number of annotators used
(see https://stanfordnlp.github.io/CoreNLP/memory-time.html) and adding more memory.

`python dataCleaning.py` now runs without error on the hardcoded text (on line 298).
Still need to feed in the results from `python corenlp.py`.

## Dependencies
**Corpus Text**
Original paper used raw text from http://www.cs.cmu.edu/~ark/personas/

`wget http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz`

`tar xf MovieSummaries.tar.gz`

`cp MovieSummaries/plot_summaries.txt ASTER/ps-work`

**Stanford CoreNLP Server**

Attempting to run using 2018-10-05 release (original work used 2016-10-31 release).
TODO: confirm 2018 release compatibility.

`sudo apt install openjdk-11-jdk-headless`

`java -version` # version 10.0

`echo 'JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64/bin/java"' | sudo tee --append /etc/environment`

`source /etc/environment`

`cd ~/dev`

`wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip`

`unzip stanford-corenlp-full-2018-10-05.zip`

`ln -s stanford-corenlp-full-2018-10-05 ASTER`

corenlp.py expects to find englishPCFG.ser.gz so extract it (will update path strings in corenlp.py)

`mkdir coreNLP-support`

`cp stanford-corenlp-full-2018-10-05/stanford-corenlp-3.9.2-models.jar coreNLP-support`

`ln -s coreNLP-support ASTER`

`cd coreNLP-support`

`unzip stanford-corenlp-3.9.2-models.jar`

`find . | grep PCFG` # ./edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz

**VerbNet**

The discovery of verbnet dir inside the Event_Creation dir makes the following
installation unecessary (probably).

`cd ~/dev/coreNLP-support`

`wget http://verbs.colorado.edu/verbnet_downloads/vn_3_14.zip`

`unzip vn_3_14.zip`

`cd verbnet && cp pronounce-29.3.1 pronounce-29.3.1.xml` # misnamed file?

**Stanford Named Entity Recognition (NER)**

`cd ~/dev/coreNLP-support`

`wget https://nlp.stanford.edu/software/stanford-ner-2018-10-16.zip`

`unzip stanford-ner-2018-10-16.zip`

`ln -s stanford-ner-2018-10-16 ASTER`

## Usage
**Install & Setup**

`virtualenv --system-site-packages -p python2.7 .venv && source .venv/bin/activate && pip install -r requirements.txt`

**Running**

After install use the standard `source .venv/bin/activate` and `deactivate` virtualenv helpers.

To start a Stanford CoreNLP server, run: `sh runNLPserver.sh`. (visit http://localhost:9000 to test)

Run `python corenlp.py` to parse your data and then you can run `python dataCleaning.py`
to prune and split.
