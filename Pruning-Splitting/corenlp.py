from nltk import compat
from nltk.internals import find_jar, find_jar_iter, config_java, java, _java_options, find_jars_within_path
import os
import re
import subprocess
import sys
import tempfile

# be sure to symlink to your correct paths
core_nlp_dir = "../stanford-corenlp-full-2016-10-31"
models_dir   = "../coreNLP-support"
work_dir     = "../../test-data/ps/t1/"

in_file_name  = 'raw-in.txt'

input_file    = work_dir + in_file_name
output_file   = work_dir + in_file_name.split(".",1)[0] + '-parsed.txt' # output from corenlp server
sentence_file = work_dir + in_file_name.split(".",1)[0] + '-sents.txt' # lines after removePunct()

def removePunct(sentence):
    final_sentences = []
    sentence = sentence.strip()
    #remove all punctuation except periods & separate numbers
    #original_sent = sentence.lower()
    original_sent = sentence.replace("!", ".")
    original_sent = original_sent.replace("?", ".")
#   original_sent = original_sent.replace("-", " ")
#   original_sent = original_sent.replace("'", " ")
#   original_sent = original_sent.replace("/", " ")
#   original_sent = original_sent.replace("0", " 0 ")
#   original_sent = original_sent.replace("1", " 1 ")
#   original_sent = original_sent.replace("2", " 2 ")
#   original_sent = original_sent.replace("3", " 3 ")
#   original_sent = original_sent.replace("4", " 4 ")
#   original_sent = original_sent.replace("5", " 5 ")
#   original_sent = original_sent.replace("6", " 6 ")
#   original_sent = original_sent.replace("7", " 7 ")
#   original_sent = original_sent.replace("8", " 8 ")
#   original_sent = original_sent.replace("9", " 9 ")
    original_sent = original_sent.replace("Mr.", "Mr")
    original_sent = original_sent.replace("Ms.", "Ms")
    original_sent = original_sent.replace("Mrs.", "Mrs")
    original_sent = original_sent.replace("Dr.", "Dr")
    original_sent = original_sent.replace("Drs.", "Drs")
    original_sent = original_sent.replace("St.", "St")
    original_sent = original_sent.replace("Col.", "Col")
    original_sent = original_sent.replace("Sgt.", "Sgt")
    original_sent = original_sent.replace("MSgt.", "MSgt")
    original_sent = original_sent.replace("Prof.", "Prof")
    original_sent = original_sent.replace("Dept.", "Dept")
    original_sent = original_sent.replace("Cmdr.", "Cmdr")
    original_sent = original_sent.replace("Comm.", "Comm")
    original_sent = original_sent.replace("Jr.", "Jr")
    original_sent = original_sent.replace("Sr.", "Sr")
    original_sent = original_sent.replace("Lt.", "Lt")
    original_sent = original_sent.replace("Fr.", "Fr")
    original_sent = original_sent.replace("D.C.", "DC")
    original_sent = original_sent.replace(".com", " com")
    original_sent = original_sent.replace(".net", " net")
    original_sent = original_sent.replace("...", " ")
    #original_sent = re.sub(r"(?<![a-zA-Z]{3,})\.","",original_sent,flags=re.IGNORECASE) #removes periods in initials
    while "  " in original_sent:
        original_sent = original_sent.replace("  ", " ")
    sentences = original_sent.split(".")
    for sentence in sentences:
        if len(sentence) < 4:
            sentence = sentence.replace(".", "")
            final_sentences.append(sentence)
        elif sentence:
            final_sentences.append(sentence)
    return "".join(final_sentences)

def callStanford(sentence):
    # This function can call Stanford CoreNLP tool and support getEvent function.
    encoding = "utf8"
    cmd = ["java", "-cp", core_nlp_dir + "/*", "-Xmx4g",
        "edu.stanford.nlp.pipeline.StanfordCoreNLPClient",
        # "-annotators", "tokenize", # 1.34s
        # "-annotators", "ssplit",   # 1.16s
        # "-annotators", "parse",    # (3.65s empty parse), (2.1s empty parse), crash, hang, hang...
        # "-annotators", "ner",      # 14.70, 19.11, 3.31, 6.239s
        # "-annotators", "pos",      # 3.05, 1.4, 1.3s
        # "-annotators", "lemma",    # 1.29s
        # "-annotators", "depparse", # 28.01, 2.55, 18.57s
        # "-annotators", "ssplit,tokenize,ner,pos,lemma,depparse", # 6.386, 4.77s
        # "-annotators", "lemma,ssplit,tokenize,ner,pos,depparse", # 6.386s
        "-annotators", "tokenize,ssplit,parse,ner,pos,lemma,depparse", # crash, 36, hang,..., 37s
        '-outputFormat','json',
        "-parse.flags", "",
        '-encoding', encoding,
        '-model', models_dir + '/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz',
        "-backends","localhost:9000"]
    default_options = ' '.join(_java_options)
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
        temp_file.write(sentence)
        temp_file.flush()
        temp_file.seek(0)
        err_out = sys.stderr
        # err_out = os.devnull # suppress client error noise
        try:
            out = subprocess.check_output(cmd, stdin=temp_file, stderr=err_out)
        except subprocess.CalledProcessError as err:
            print("openNLP CLIENT ERROR: ", err.errorcode)
            return
        out = out.replace(b'\xc2\xa0',b' ')
        out = out.replace(b'\xa0',b' ')
        out = out.replace(b'NLP>',b'')
        out = out.decode(encoding)
        os.unlink(temp_file.name)
    config_java(options=default_options, verbose=False) # Return java config to default values
    return out

write_file = open(output_file, "w")
sent_file = open(sentence_file, "w")
write_file.write('{\n"parses":[\n')
for line in open(input_file, 'r').readlines():
    if "<EOS>" in line:
        sent_file.write("<EOS>\n")
    else:
        sentences = removePunct(line)
        for sentence in sentences.split(". "):
            result = callStanford(sentence+".")
            sent_file.write(sentence+".\n")
            write_file.write((result+",\n").encode('utf8'))

write_file.write("]\n}") ###MAKE SURE TO GET RID OF THAT LAST ,
write_file.close()
sent_file.close()
