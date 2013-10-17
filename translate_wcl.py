# translate_wcl.py
# parse wcl corpus, prepare input to our system
# @author: Yiping 2013

import re
import random
from random import shuffle

def main():
  """ calls parse_wcl and extract the input files for positive and negative input
  """
   
  good_path    = './wiki_good.txt' #location of the documents
  bad_path = './wiki_bad.txt'

  good_intermediate = './wiki_good.column'
  bad_intermediate = './wiki_bad.column'

  good_output = './wiki_good.output'
  bad_output = './wiki_bad.output'

  training_txt = './training.txt'
  test_txt = './test.txt'

  process_wcl(good_path, good_intermediate, True)  #parse wcl format at good_path and output to good_output
  process_wcl(bad_path, bad_intermediate, False)  #parse wcl format at bad_path and output to bad_output

  extract_extended_features(good_intermediate, good_output)
  extract_extended_features(bad_intermediate, bad_output)

  #extract_features(good_intermediate, good_output)  #from the column representation prepare input file to GRMM
  #extract_features(bad_intermediate, bad_output)  #from the column representation prepare input file to GRMM

  split_test_and_training_data(good_output, bad_output, training_txt, test_txt, 3000, 3000)
  
# End of prepare_columns()

def process_wcl(input_path, output_path, is_definition_sentence):
  """ parse the wcl corpus from input_path and write as column feature format

  the output are in wiki_good.column and wiki_bad.column
  each line contains a single word, columns are separated 
  by a tab. Columns represent (sentence label, token label,
  word, pos, chunking tab)

  Args:
    input_path: file path to the input file, original wcl corpus
    output_path: file path to the output file
    is_definition_sentence: boolean if the file contains definition or non-definition sentences
  """
  f = open(input_path,'r')
  sentences = f.readlines()
  f.close()
    
  f = open(output_path,"w+")
   
  for sentence in sentences:
    sentence = sentence.strip()
    if len(sentence)>1 and not sentence.startswith("#"):
      new_sent = ""
      startDef = False
      tokens = sentence.split("\t")

      # locate the term
      target = tokens[0]
      term = ""
      if is_definition_sentence:
	      term = target[:target.find(":")]
      else:
        term = target[1:target.find(":")]
      chunk_feature = "NULL"
      pos_feature = "NULL"
      word_feature = "NULL"
      # fixed sentence label
      if is_definition_sentence:
        sentence_label = "DS"
      else:
        sentence_label = "NDS"
      word_label = "OTHER"

      for token in tokens:
        if '_' in token:
          if ":" in token:
            token = token[target.find(":")+1:]

          columns = token.split('_')
          if(len(columns)==3):  #it's a word
            chunk_feature = columns[0]
            pos_feature = columns[1]
            word_feature = columns[2]
            if startDef:  # the word is a hypernym
              word_label = "HYPER"
              startDef = False
            elif word_feature == "TARGET":  # the word is a term
              word_feature = term
              word_label = "TERM"
            else:
              word_label = "OTHER"
          elif(len(columns)==2):  #it's a punctuation mark   
            chunk_feature = "NULL"
            pos_feature = columns[0]
            word_feature = columns[1]
            word_label = "OTHER"
        
          #add a new line to output file
          f.write("%s\n" % "\t".join([sentence_label, word_label, word_feature, pos_feature, chunk_feature])) 
        
        if token == "<HYPER>":
          startDef = True
            
      f.write("\n")  # put an empty line between each sentence 	                        
    else:
      pass#f.write(sentence)
  f.close() 

# end of process_wcl

def extract_features(input_path, output_path):
  """ extract the features from the .column input file

  the input are in wiki_good.column and wiki_bad.column
  each line contains a single word, columns are separated 
  by a tab. Columns represent (sentence label, token label,
  word, pos, chunking tab)
  The output file follows grmm requirement

  Args:
    input_path: file path to the input file, *.column
    output_path: file path to the output file
  """
  f = open(input_path,'r')
  words = f.readlines()
  f.close()

  f = open(output_path,"w+")
    
  for word in words:
    if not "\t" in word:  # empty line
      pass #f.write("\n")
    else:
      columns = word.strip().split("\t")
      chunk_feature = columns[4]
      pos_feature = columns[3]
      word_feature = columns[2]
      word_label = columns[1]
      sentence_label = columns[0]
         
      f.write("%s %s ---- Word=%s Pos=%s Chunk=%s\n" % (sentence_label, word_label, word_feature, pos_feature, chunk_feature))
  f.close()

def extract_extended_features(input_path, output_path):
  """ extract the features from the .column input file

  The difference between this function and extract_features function is that
  this function includes words from the same sentence and their features in the
  feature set of each word.

  the input are in wiki_good.column and wiki_bad.column
  each line contains a single word, columns are separated 
  by a tab. Columns represent (sentence label, token label,
  word, pos, chunking tab)
  The output file follows grmm requirement

  Args:
    input_path: file path to the input file, *.column
    output_path: file path to the output file
  """
  f = open(input_path,'r')
  words = f.readlines()
  f.close()
    
  lines = []
  words_in_a_line = []
  for word in words:
    if not "\t" in word:  # empty line
      lines.append(words_in_a_line)
      words_in_a_line = []
    else:
      words_in_a_line.append(word)

  shuffle(lines)

  f = open(output_path,"w+")

  for line in lines:
    num_words = len(line)
    avg_word_length = int(sum(len(word.strip().split("\t")[2]) for word in line)/num_words)

    for word in line:
      current_index = line.index(word)
      columns = word.strip().split("\t")
      word_label = columns[1]
      sentence_label = columns[0]
      features = ""
      for num in range(0,num_words-1):
        if abs(num - current_index) < 4:
          features += extract_features_from_row(line[num], num - current_index)
          if num != num_words-1:
            features += " "

      #f.write("%s %s ---- NumWords=%i AvgWordsLength=%i %s\n" % (sentence_label, word_label, num_words, avg_word_length, features))
      f.write("%s ---- NumWords=%i AvgWordsLength=%i %s\n" % (word_label, num_words, avg_word_length, features))
    f.write("\n")
  f.close()

def extract_features_from_row(word, position):
  """ extract the features from a row from .column file

  Args:
    word: a row in the .column file
    position: position of the current word in the sentence
  """
  columns = word.strip().split("\t")
  chunk_feature = columns[4]
  pos_feature = columns[3]
  word_feature = columns[2]
  word_length = len(columns[2])

  features = ""
  if position == 0:
    features = "Word={} Pos={} Chunk={} Length={}".format(word_feature, pos_feature, chunk_feature, word_length)
  else:
    features = "Word={1}@{0} Pos={2}@{0} Chunk={3}@{0} Length={4}@{0}".format(position, word_feature, pos_feature, chunk_feature, word_length)

  return features


def split_test_and_training_data(good_input_path, bad_input_path, training_txt_path, test_txt_path, training_size, test_size):
  """ get .output files and split them into training.txt and test.txt based on training_to_test_ratio

  the input are in wiki_good.out and wiki_bad.out
  the output file follows grmm requirement

  Args:
    good_input_path: file path to the good output file (e.g. wiki_good.output)
    bad_input_path: file path to the bad output file (e.g. wiki_bad.output)
    training_txt_path: file path to the training output file
    test_txt_pat: file path to the test output file
    training_size: the maximum size of training dataset
    test_size: the maximum size of test dataset
  """

  f = open(good_input_path)
  good_words = f.readlines();
  f.close()

  f = open(bad_input_path)
  bad_words = (f.readlines())
  f.close()

  #shuffle(lines)

  f1 = open(training_txt_path, "w+")
  f2 = open(test_txt_path, "w+")

  test_sentence = 0
  training_sentence = 0

  count = 0
  for word in good_words:
    if "\t" in word:  # empty line
      #pass #f.write("\n")
      if count < training_size:
        training_sentence = training_sentence + 1
      else:
        test_sentence = test_sentence + 1
    else:
      if count < training_size:
        f1.write("%s" % word)
      elif count >= training_size and count < training_size + test_size:
        f2.write("%s" % word)
      else:
        break
      count = count + 1

  count = 0
  for word in bad_words:
    if not "\t" in word:  # empty line
      #pass #f.write("\n")
      if count < training_size:
        training_sentence = training_sentence + 1
      else:
        test_sentence = test_sentence + 1
    else:
      if count < training_size:
        f1.write("%s" % word)
      elif count >= training_size and count < training_size + test_size:
        f2.write("%s" % word)
      else:
        break
      count = count + 1

  print test_sentence
  print training_sentence

  f1.close()
  f2.close()

    
# End of extract_features()

################################################
#                 Main Function                #
################################################

if __name__ == '__main__' :
    main()
    
