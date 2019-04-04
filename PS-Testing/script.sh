cd parses/01
java -cp "/home/aster/dev/890-proj/corenlp/stanford-corenlp-full-2016-10-31/*" \
-mx20g \
edu.stanford.nlp.pipeline.StanfordCoreNLPClient \
-annotators "tokenize,ssplit,parse,ner,pos,lemma,depparse" \
-filelist "/home/aster/dev/890-proj/test-data/ps/t2/filelist-split01" \
-outputFormat "json" \
-parse.flags "" \
-encoding "utf8" \
-model "/home/aster/dev/890-proj/corenlp/coreNLP-support/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz" \
-backends "localhost:9000"

