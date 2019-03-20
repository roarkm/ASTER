# Pruning and Splitting
Data pre-processing.
Download raw data here http://www.cs.cmu.edu/~ark/personas/

## Current Status

corenlp.py runs without error with a dummy miniSents.txt file in ps-work dir, however
the generated file miniSents-parsed.txt appears to contain no useful information
(although it's too soon for me to interpret).

`python dataCleaning.py` errors on
File "/home/m/dev/ASTER/Pruning+Splitting/eventmakerTryServer.py", line 282, in getEvent
(bottom of stack trace: ValueError: No JSON object could be decoded).
This might be related to miniSents-parsed.txt being empty as mentioned above?
(try running on a movie plot summary)

TODO: investigate the above error.

## Dependencies
**Stanford CoreNLP Server**
Attempting to run using 2018-10-05 release (original work used 2016-10-31 release).
TODO: confirm 2018 release compatibility.

`sudo apt install openjdk-11-jdk-headless`

`java -version` # version 10.0

`cd ~/dev`

`wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip`

`unzip stanford-corenlp-full-2018-10-05.zip`

`echo 'JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64/bin/java"' | sudo tee --append /etc/environment`

`source /etc/environments`

corenlp.py expects to find englishPCFG.ser.gz so extract it (will update path strings in corenlp.py)

`mkdir coreNLP-support`

`cp stanford-corenlp-full-2018-10-05/stanford-corenlp-3.9.2-models.jar coreNLP-support`

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
