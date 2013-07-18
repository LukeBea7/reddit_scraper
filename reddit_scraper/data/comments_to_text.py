#!/usr/bin/python
import os
import sys
import pickle

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "ERROR: specify the file to convert to all text and the nameof the outfile"

    comments = pickle.load(open (sys.argv[1], 'rb'))
    output = open (sys.argv[2], 'w')
    for comment in comments:
        print comment

        ascii_version = comment['content'].encode ('ascii', 'ignore')
        output.write (ascii_version + "\n")


