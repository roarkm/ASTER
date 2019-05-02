# Event Creation

Data pre-processing.

## Usage
**Install & Setup**

`virtualenv -p python2.7 .venv && source .venv/bin/activate && pip install -r requirements.txt`

`unzip genre_0_sents.txt.zip`
(Outputs a json file. I think this is a sample of the structured data output from Pruning-Splitting)

**Running**

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


**Event Creation (From Top Level README)**
code takes separate NER and parse files, and extracts multiple events.

*Note:* The parsing code we have provided has combined the parses and NER into a single file.
You will have to change these following files to match this format.

Regarding the above note, I ran both `generalize_events.py` and `generalize_events_bigrams.py`
using seperate NER and parse files (genre_0_sents.txt.json) which seemed to work as intended (I think).



Once you have the parses, you can run `python generalize_events.py` for generalized events,
or `python generalize_events_bigrams.py` for event bigrams with continuing named entities,
or `python generalize_entire_sentence.py` to generalize the entire sentence.

Currently `python generalize_entire_sentence.py` does not work, need to identify what the
expected contents of OriginalSentences.txt should be (maybe a subset of the raw chorpus text?)

You can also do topic modeling using LDA (in the folder `Event_Creation/Topic_Modeling`).
After you adjust the input file, run `python train_lda.py` to create a model.
Once the model is made, run `python lda_classify.py` to find the top words in each topic
or `python finidGenre_args.py` to create data files that are separated by these new genres.

