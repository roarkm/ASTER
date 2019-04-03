# be sure to symlink to your correct paths
cd ../stanford-corenlp-full-2016-10-31
java -mx12g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 999999
