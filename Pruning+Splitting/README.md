# Pruning and Splitting
Data pre-processing.
Download raw data here http://www.cs.cmu.edu/~ark/personas/

## Dependencies
**Stanford CoreNLP Server**
`sudo apt install openjdk-11-jdk-headless`

`java -version` (version 10.0)

`cd ~/dev`

`wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip`

`unzip stanford-corenlp-full-2018-10-05.zip`

`echo 'JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64/bin/java"' | sudo tee --append /etc/environment`

`source /etc/environments`

`cd stanford-corenlp-full-2018-10-05`

Attempting to run using 2018-10-05 release (original work used 2016-10-31 release).
TODO: confirm 2018 release compatibility.

## Usage
**Install & Setup**
`virtualenv --system-site-packages -p python2.7 .venv && source .venv/bin/activate && pip install -r requirements.txt`

**Running**
To start a Stanford CoreNLP server, run: `sh runNLPserver.sh`. (visit http://localhost:9000 to test)

Start virtualenv session with `source .venv/bin/activate`.

TODO: edit coreNLP dir paths in eventmakerTryServer.py (maybe refactor into environment variables or
config script/file).

Run `python corenlp.py` to parse your data and then you can run `python dataCleaning.py`
to prune and split.

`deactivate`
