#!/usr/bin/python
import os
import sys
import pickle


if __name__ == '__main__':

	subreddits = pickle.load (open('subreddits_list.obj', 'rb'))
	for subreddit in subreddits:
		print "About to scrape subreddit = " + subreddit
		os.system("scrapy crawl reddit -a subreddit=" + subreddit)

