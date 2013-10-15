# translate_wcl.py
# parse wcl corpus, prepare input to our system
# @author: Yiping 2013

import re
import random

def prepare_columns():
    """ calls parse_wcl and extract the input files for positive and negative input
    """
    #Parameters
    good_path    = './wiki_good.txt' #location of the documents
    bad_path = './wiki_bad.txt'

    good_output = './wiki_good.column'
    bad_output = './wiki_bad.column'

    process_wcl(good_path, good_output, True)  #parse wcl format at good_path and output to good_output
    process_wcl(bad_path, bad_output, False)  #parse wcl format at bad_path and output to bad_output
  
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
	    term = target[:target.find(":")]

            chunk_feature = "NULL"
            pos_feature = "NULL"
            word_feature = "NULL"
            # fixed sentence label
            if is_definition_sentence:
                sentence_label = "1"
            else:
                sentence_label = "0"
            word_label = "O"

	    for token in tokens:
		if '_' in token:
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
                            word_label = "O"
                    elif(len(columns)==2):  #it's a punctuation mark   
		        chunk_feature = "NULL"
                        pos_feature = columns[0]
                        word_feature = columns[1]
                        word_label = "O"
                    #add a new line to output file
                    f.write("%s\n" % "\t".join([sentence_label, word_label, word_feature, pos_feature, chunk_feature])) 

		if token == "<HYPER>":
		    startDef = True
            
            f.write("\n")  # put an empty line between each sentence 	        
                
	else:
	    pass#f.write(sentence)
    f.close() 
# end of process_wcl

def extract_features():
    """ extract the features from the .column input file

    """
# End of extract_features()

################################################
#                 Main Function                #
################################################


if __name__ == '__main__' : 

    prepare_columns()
    extract_features()