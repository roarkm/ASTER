# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Binary for training translation models and decoding from them.

Running this program without --decode will download the WMT corpus into
the directory specified as --data_dir and tokenize it in a very basic way,
and then start training a model saving checkpoints to --train_dir.

Running with --decode starts an interactive loop so you can see how
the current checkpoint translates English sentences into French.

See the following papers for more information on neural translation models.
 * http://arxiv.org/abs/1409.3215
 * http://arxiv.org/abs/1409.0473
 * http://arxiv.org/abs/1412.2007
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import random
import sys
import time

import numpy as np
from six.moves import xrange    # pylint: disable=redefined-builtin
import tensorflow as tf

import cmu_data_utils
#from tensorflow.models.rnn.translate
import seq2seq_model_fb
from tensorflow.core.protobuf import saver_pb2

#from nltk.model import NgramModel
from nltk import translate as tr

tf.app.flags.DEFINE_float("learning_rate", 0.500, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,"Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,"Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 64, "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 1024, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", 4, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("in_vocab_size", 80000, "Input vocabulary size.")
tf.app.flags.DEFINE_integer("out_vocab_size",80000, "Output vocabulary size.")
tf.app.flags.DEFINE_string("data_dir", "/mnt/sdb1/EventEval/original/translate", "Data directory") ##
tf.app.flags.DEFINE_string("train_dir", "/mnt/sdb1/EventEval/original/translate/sent_checkpoints", "Training directory.") ##
tf.app.flags.DEFINE_integer("max_train_data_size", 0,"Limit on the size of training data (0: no limit).")
tf.app.flags.DEFINE_integer("steps_per_checkpoint", 200,"How many training steps to do per checkpoint.")
tf.app.flags.DEFINE_boolean("decode", True,"Set to True for interactive decoding.")
tf.app.flags.DEFINE_boolean("self_test", False,"Run a self-test if this is set to True.")
tf.app.flags.DEFINE_boolean("use_fp16", False,"Train using fp16 instead of fp32.")
tf.app.flags.DEFINE_string("max_epochs", 2000, "Maximum number of epochs.")

tf.app.flags.DEFINE_string("vocabulary","cmu_general_event.vocab", "Vocabulary File") ##
tf.app.flags.DEFINE_string("in_file","generalEvent_input.txt", "Input File") ##

FLAGS = tf.app.flags.FLAGS

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
_buckets = [(25,25),(5, 10), (10, 15), (20, 25), (40, 50)]


def read_data(source_path, target_path, max_size=None):
    """Read data from source and target files and put into buckets.

    Args:
        source_path: path to the files with token-ids for the source language.
        target_path: path to the file with token-ids for the target language;
            it must be aligned with the source file: n-th line contains the desired
            output for n-th line from the source_path.
        max_size: maximum number of lines to read, all other will be ignored;
            if 0 or None, data files will be read completely (no limit).

    Returns:
        data_set: a list of length len(_buckets); data_set[n] contains a list of
            (source, target) pairs read from the provided data files that fit
            into the n-th bucket, i.e., such that len(source) < _buckets[n][0] and
            len(target) < _buckets[n][1]; source and target are lists of token-ids.
    """
    data_set = [[] for _ in _buckets]
    with tf.gfile.GFile(source_path, mode="r") as source_file:
        with tf.gfile.GFile(target_path, mode="r") as target_file:
            source, target = source_file.readline(), target_file.readline()
            counter = 0
            while source and target and (not max_size or counter < max_size):
                counter += 1
                if counter % 100000 == 0:
                    print(" reading data line %d" % counter)
                    sys.stdout.flush()
                source_ids = [int(x) for x in source.split()]
                target_ids = [int(x) for x in target.split()]
                target_ids.append(cmu_data_utils.EOS_ID)
                
                #for bucket_id, (source_size, target_size) in enumerate(_buckets):
                #   if len(source_ids) < source_size and len(target_ids) < target_size:
                #       data_set[bucket_id].append([source_ids, target_ids])
                #       break
                data_set[0].append([source_ids, target_ids])
                source, target = source_file.readline(), target_file.readline()
    return data_set


def create_model(session, forward_only):
    """Create translation model and initialize or load parameters in session."""
    dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
    model = seq2seq_model_fb.Seq2SeqModel(
            FLAGS.in_vocab_size,
            FLAGS.out_vocab_size,
            _buckets,
            FLAGS.size,
            FLAGS.num_layers,
            FLAGS.max_gradient_norm,
            FLAGS.batch_size,
            FLAGS.learning_rate,
            FLAGS.learning_rate_decay_factor,
            forward_only=forward_only)
            #dtype=dtype)
    ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
    #if ckpt:# and tf.gfile.Exists(ckpt.model_checkpoint_path):
    print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    model.saver.restore(session, ckpt.model_checkpoint_path)
    #else:
    #   print("Created model with fresh parameters.")
    #   session.run(tf.global_variables_initializer())
    return model


def train():
    """Train a en->fr translation model using WMT data."""
    # Prepare WMT data.
    print("Preparing WMT data in %s" % FLAGS.data_dir)
    in_train, out_train, in_dev, out_dev, _, _ = cmu_data_utils.prepare_wmt_data(FLAGS.data_dir, FLAGS.in_vocab_size, FLAGS.out_vocab_size)

    with tf.Session() as sess:
        # Create model.
        print("Creating %d layers of %d units." % (FLAGS.num_layers, FLAGS.size))
        model = create_model(sess, False)

        #vocab_file = open('cmu_event_specific_translate.vocab', 'rb')
        #vocab = pickle.load(vocab_file)
        #vocab_file.cloe()

        # test_set = read_data.read_with_buckets(FLAGS.test_file, vocab,_buckets)
        #train_set = read_data.read_with_buckets(FLAGS.train_file, vocab,_buckets)
        dev_set = read_data(in_dev, out_dev)
        train_set = read_data(in_train, out_train)#, FLAGS.max_train_data_size)


        #print ("######################################")
        #print ("Read data as follows:")
        #print (train_set[0][:5])
        #print (train_set[1:])
        #print ("######################################")


        # This is the training loop.
        step_time, loss = 0.0, 0.0
        current_step = 0
        previous_losses = []
        counter_iter=0
        pos = 0
        epochs = 0
        
        while epochs < FLAGS.max_epochs:
            bucket_id = 0

            # Get a batch and make a step.
            start_time = time.time()

            encoder_inputs, decoder_inputs, target_weights = model.get_batch(train_set, bucket_id, pos)
            if (pos + FLAGS.batch_size) >= len(train_set[bucket_id]):
                epochs += 1
                print("The number of epochs is:{}".format(epochs))
                print ("The step_loss is: ",float(step_loss))
                print ("The loss is: ",float(loss))
                print
                step_time, loss = 0.0, 0.0
                # Decrease learning rate if no improvement was seen over last 3 times.
                if len(previous_losses) > 2 and loss > max(previous_losses[-3:]):
                    sess.run(model.learning_rate_decay_op)
                previous_losses.append(loss)

            pos = (pos + FLAGS.batch_size) % len(train_set[bucket_id])


            _, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs, target_weights, bucket_id, False)
            step_time += (time.time() - start_time) / FLAGS.steps_per_checkpoint
            loss += step_loss / FLAGS.steps_per_checkpoint
            current_step += 1

            # Once in a while, we save checkpoint, print statistics, and run evals.
            if epochs%10 == 0 and pos<FLAGS.batch_size:
                #learning rate
                print ("global step %d learning rate %.4f step-time %.2f "
                             "and epochs %d" % (model.global_step.eval(), model.learning_rate.eval(),
                                                 step_time, epochs))

            if epochs%10 == 0 and pos<FLAGS.batch_size:
                # Save checkpoint and zero timer and loss.
                checkpoint_path = os.path.join("/mnt/sdb1/EventEval/original/translate/sent_checkpoints","original_sent_epoch{}.ckpt".format(epochs))
                model.saver.save(sess, checkpoint_path, global_step=model.global_step)
                print ("CHECKPOINT SAVED")
                
                #run perplexity
                encoder_inputs, decoder_inputs, target_weights = model.get_batch(dev_set, bucket_id, pos)
                _, eval_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,target_weights, bucket_id, True)
                eval_ppx = math.exp(float(eval_loss)) if eval_loss < 300 else float("inf")
                print(" eval: bucket %d perplexity %.2f" % (bucket_id, eval_ppx))


def decode():
    with tf.Session() as sess:
        # Create model and load parameters.
        model = create_model(sess, True)
        model.batch_size = 1    # We decode one sentence at a time.

        # Load vocabularies.
        #en_vocab_path = os.path.join(FLAGS.data_dir,"vocab%d.en" % FLAGS.en_vocab_size)
        #fr_vocab_path = os.path.join(FLAGS.data_dir,"vocab%d.fr" % FLAGS.fr_vocab_size)
        vocab_path = os.path.join(FLAGS.data_dir, FLAGS.vocabulary)
        input_vocab, rev_output_vocab = cmu_data_utils.initialize_vocabulary(vocab_path)
        #_, rev_fr_vocab = cmu_data_utils.initialize_vocabulary(vocab_path)

        test_dir = os.path.join(FLAGS.data_dir, FLAGS.in_file)
        pos = 0
        for sentence in open(test_dir):
            token_ids = cmu_data_utils.sentence_to_token_ids(tf.compat.as_bytes(sentence), input_vocab)
            bucket_id = 0#min([b for b in xrange(len(_buckets)) if _buckets[b][0] > len(token_ids)])
            encoder_inputs, decoder_inputs, target_weights = model.get_batch({bucket_id: [(token_ids, [])]}, bucket_id, pos)
            pos += 1
            #Loop this step 1000 times and get best of those based on perplexity as opposed to outputs argmax
            _, _, output_logits = model.step(sess, encoder_inputs, decoder_inputs,target_weights, bucket_id, True)
            """
            #Creating probability distribution
            for i, logit in enumerate(output_logits):
                '''max_l = np.amax(logit, axis=1)
                min_l = np.amin(logit, axis=1)
                #scaling and smoothing
                logit = (logit - min_l) / (max_l - min_l) + 1e-10
                tot_sum = np.sum(logit)
                #normalizing
                logit = logit / tot_sum'''
                #print(np.sum(logit))
                logit = 1 / (np.exp2(-logit) + 1)
                tot_sum = np.sum(logit)
                logit = logit / tot_sum
                #print("max" + str(np.amax(logit, axis=1)))
                #print(logit)
                #print(np.sum(logit))
                output_logits[i] = logit
            
            final_opt_bleu = -1.0
            final_opt = ""
            
            for i in range(1000):
                cur_seq = []
                for logit in output_logits:
                    word_index = np.random.choice(output_logits[0].size, p=np.ravel(logit))
                    if word_index >= len(rev_output_vocab):
                        word_index = 3
                    cur_seq.append(word_index) 
                #print(cur_seq)
                #a = np.ravel(logit)
                #for b in cur_seq:
                #   print(a[b])
                #print(len(rev_output_vocab))
                curr_word_seq = " ".join([tf.compat.as_str(rev_output_vocab[output]) for output in cur_seq])
                curr_bleu = tr.bleu_score.sentence_bleu(sentence.split(), curr_word_seq.split())
                #if curr_bleu > 0:
                #   print(curr_bleu)
                #Use alternate methods of evaluating the sentence, nltk.model has bugs (use BLEU perhaps?)
                if final_opt_bleu < curr_bleu:
                    final_opt = curr_word_seq
                    final_opt_perp = curr_bleu
            #print(final_opt_bleu)
            print(final_opt)
            """
            #"""
            outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
            if cmu_data_utils.EOS_ID in outputs:
                                outputs = outputs[:outputs.index(cmu_data_utils.EOS_ID)]
                        #print("given: "+str(sentence)+">>predicted: "+" ".join([tf.compat.as_str(rev_output_vocab[output]) for output in outputs]))
                        print(" ".join([tf.compat.as_str(rev_output_vocab[output]) for output in outputs]))
            #"""
        #decoded_sparse, decoded_logprobs = beam_decoder(cell=tf.nn.rnn_cell.RNNCell, beam)size=5,stop_token=cmu_data_utils.EOS_ID,initial_state=token_ids[3],initial_input=        
#path, symbol, output_logits = model.step(sess, encoder_inputs, decoder_inputs,target_weights, bucket_id, True)
            #k = output_logits[0]
            #paths = []
            #for kk in range(5):
            #   paths.append([])
            #curr = range(5)
            #num_steps = len(path)
            #for i in range(num_steps - 1, -1, -1):
            #   for kk in range(5):
            #       paths[kk].append(symbol[i][curr[kk]])
            #       curr[kk] = path[i][curr[kk]]
            #recos = set()
            #print("------------------------------------------------------------")
            #for kk in range(5):
            #   foutputs = [int(logit) for logit in paths[kk][::-1]]
            #if cmu_data_utils.EOS_ID in foutputs:
            #   foutputs = foutputs[:foutputs.index(cmu_data_utils.EOS_ID)]
            #rec = " ".join([tf.compat.as_str(rev_vocab[output]) for outputs in foutputs])
            #if rec not in recos:
            #   recos.add(rec)
            #   print(rec)
            #outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
            #if cmu_data_utils.EOS_ID in outputs:
            #   outputs = outputs[:outputs.index(cmu_data_utils.EOS_ID)]
            #print("given: "+str(sentence)+">>predicted: "+" ".join([tf.compat.as_str(rev_output_vocab[output]) for output in outputs]))
            #print(" ".join([tf.compat.as_str(rev_output_vocab[output]) for output in outputs]))
            # Decode from standard input.
            #sys.stdout.write("> ")
            #sys.stdout.flush()
            #sentence = sys.stdin.readline()
            #while sentence:
                # Get token-ids for the input sentence.
            #   token_ids = cmu_data_utils.sentence_to_token_ids(tf.compat.as_bytes(sentence), en_vocab)
                # Which bucket does it belong to?
            #   bucket_id = min([b for b in xrange(len(_buckets))if _buckets[b][0] > len(token_ids)])
                # Get a 1-element batch to feed the sentence to the model.
            #   encoder_inputs, decoder_inputs, target_weights = model.get_batch({bucket_id: [(token_ids, [])]}, bucket_id)
                # Get output logits for the sentence.
            #   _, _, output_logits = model.step(sess, encoder_inputs, decoder_inputs,target_weights, bucket_id, True)
                # This is a greedy decoder - outputs are just argmaxes of output_logits.
            #   outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
                # If there is an EOS symbol in outputs, cut them at that point.
            #   if cmu_data_utils.EOS_ID in outputs:
            #       outputs = outputs[:outputs.index(cmu_data_utils.EOS_ID)]
                # Print out French sentence corresponding to outputs.
            #   print(" ".join([tf.compat.as_str(rev_fr_vocab[output]) for output in outputs]))
            #   print("> ", end="")
            #   sys.stdout.flush()
            #   sentence = sys.stdin.readline()


def self_test():
    """Test the translation model."""
    with tf.Session() as sess:
        print("Self-test for neural translation model.")
        # Create model with vocabularies of 10, 2 small buckets, 2 layers of 32.
        model = seq2seq_model_fb.Seq2SeqModel(10, 10, [(3, 3), (6, 6)], 32, 2, 5.0, 32, 0.3, 0.99, num_samples=8)
        sess.run(tf.initialize_all_variables())

        # Fake data set for both the (3, 3) and (6, 6) bucket.
        data_set = ([([1, 1], [2, 2]), ([3, 3], [4]), ([5], [6])],
                                [([1, 1, 1, 1, 1], [2, 2, 2, 2, 2]), ([3, 3, 3], [5, 6])])
        for _ in xrange(5): # Train the fake model for 5 steps.
            bucket_id = random.choice([0, 1])
            encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                    data_set, bucket_id)
            model.step(sess, encoder_inputs, decoder_inputs, target_weights,
                                 bucket_id, False)


def main(_):
    if FLAGS.self_test:
        self_test()
    elif FLAGS.decode:
        decode()
    else:
        train()

if __name__ == "__main__":
    tf.app.run()

