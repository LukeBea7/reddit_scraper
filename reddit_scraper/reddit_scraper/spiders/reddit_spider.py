#---- SCRAPY MODULES ----
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.loader import XPathItemLoader


#---- SENTIMENT MODULES ----
# PATTERN_MODULE_MAC = "/Users/Shared/pattern-2.5"
# PATTERN_MODULE_WIMPY = "/home/jhack/Programming/Scraper2/pattern_install_directory/lib/python2.6/site-packages"
# if PATTERN_MODULE_MAC not in sys.path:
	# sys.path.append(PATTERN_MODULE_MAC)
# if PATTERN_MODULE_WIMPY not in sys.path:
	# sys.path.append (PATTERN_MODULE_WIMPY)

#---- OUR MODULES ---
from User import User
from Post import Post
from Comment import Comment
from reddit_scraping_utilities import *

#---- MISC MODULES ----
from heapq import heappop, heappush
import os
import sys
import pickle 





# Spider: RedditSpider
# ------------------
# This is the spider for crawling a subreddit
class RedditSpider(BaseSpider):
	
	#----[ SCRAPY DATA ]---
	name = "reddit"
	allowed_domains = ["reddit.com"] #later we are going to want to add youtube, quickmeme, etc
	start_urls = ["http://www.reddit.com/"]
	comments_depth = 50


	#---[ SCRAPING DEPTHS ]---
	subreddit_page_posts_depth = 1000 # max number of posts to scrape from a subreddit page
	thread_page_comments_depth = 500 # max number of comments to scrape from a thread page
	user_page_comments_depth = 500 # max number of comments to scrape from a user's page
	user_page_posts_depth = 250 # max number of posts to scrape from a user's page


	#---[ INPUT/OUTPUT DATA ]---
	datafile_directory = os.getcwd () + "/reddit_data/"
	posts_filename = datafile_directory + "posts_"
	comments_filename = datafile_directory + "comments_"
	users_filename = datafile_directory + "users_" 
	scrape_user=None
	scrape_subreddit=None
	scrape_thread=None


	#---[ DATA TO SAVE: lists of dicts representing the objects we encounter ]---
	posts = []
	comments = []
	users = []


	# makes the start request for a user page
	def start_requests (self):

		return_request = ''

		if self.scrape_user:
			return_request = Request (url="http://www.reddit.com/user/" + self.scrape_user + "/", callback=self.parse_user)
		elif self.scrape_subreddit:
			return Request (url="http://www.reddit.com/r/" + self.scrape_subreddit + "/", callback=self.parse_subreddit)
		elif self.scrape_thread:
			return_request = Request (url="http://www.reddit.com/r/malefashionadvice/comments/" + self.scrape_thread + "/", callback=self.parse_thread,  meta={'all_comments':False})
	
		return [return_request]


	#----[ DEALING WITH POSTS ]---
	this_page_posts = [] #posts only on this page
	all_posts = []  #all posts encountered



	# Function: constructor
	# ---------------------
	# opens the files that we will be writing to
	# NOTE: currently it over-writes the file every time we open it; 
	#		should this be fixed in the future?
	def __init__ (self, user=None, subreddit=None, thread=None):

		if user:
			self.scrape_user = user
			self.users_filename += user + "_user.txt"
			self.posts_filename += user + "_user.txt"
			self.comments_filename += user + "_user.txt"
		elif subreddit:
			self.scrape_subreddit = subreddit
			self.users_filename += subreddit + "_subreddit.txt"
			self.posts_filename += subreddit + "_subreddit.txt"
			self.comments_filename += subreddit + "_subreddit.txt"
		elif thread:
			self.scrape_thread = thread
			self.users_filename += thread + "_thread.txt"
			self.posts_filename += thread + "_thread.txt"
			self.comments_filename += thread  + "_thread.txt"
		else:
			self.users_filename += "generic.txt"
			self.posts_filename += "generic.txt"
			self.comments_filename += "generic.txt"


		# self.users_file = open(self.users_filename, "w")
		# self.posts_file = open (self.posts_filename, "w")
		# self.comments_file = open (self.comments_filename, "w")


	

	# Function: deconstructor
	# -----------------------
	# will dump all of the users/comments/posts appropriately
	def __del__ (self):

		posts_file 		= open ('posts.obj', 'wb')
		comments_file 	= open ('comments.obj', 'wb') 
		users_file 		= open ('users.obj', 'wb')

		pickle.dump (self.posts, posts_file)
		pickle.dump (self.comments, comments_file)
		pickle.dump (self.users, users_file)

		print "---> dumped successfully"









	############################################################################################################
	##############################[ --- SUBREDDIT SPIDER --- ]##################################################
	############################################################################################################

	# Function: build_thread_page_request
	# -----------------------------------
	# given a list of post objects, this function will return a list of Request objects that correspond to
	# requests to mine the 'comments' page of each post
	def build_thread_page_request (self, post):
		
		new_url = post.comments_url + "?limit=500"
		return Request (url=new_url, callback=self.parse_thread)

	# Function: build_next_page_request_subreddit
	# -------------------------------------------
	# given a response for the current page of posts, this function will return a request for the next page
	# of posts.
	def build_next_page_request_subreddit (self, subreddit_response, num_pages_remaining):

		hxs = HtmlXPathSelector (subreddit_response)

		xpath_next = '//p[@class="nextprev"]/a[@rel="nofollow next"]/@href'
		next_url = hxs.select (xpath_next).extract()

		new_request = Request(url=next_url[0], callback=self.parse_subreddit, meta={'num_pages_remaining':num_pages_remaining})
		return new_request

	# Function: parse_subreddit
	# -------------------------
	# will parse a subreddit by getting each of the posts on the front page, dumping their info, then 
	# getting the top n comments from them
	def parse_subreddit (self, subreddit_response):

		# print "############################ PARSING SUBREDDIT PAGE #################################"
		print "-----> Status: Parsing subreddit " + subreddit_response.url

		# next_requests: will contain a list of all the requests to perform after this one.
		next_requests = []

		### Step 1: Deal with termination conditions/boundaries ###
		num_pages_remaining = 0
		if 'num_pages_remaining' in subreddit_response.meta.keys():
			num_pages_remaining = subreddit_response.meta['num_pages_remaining'] - 1
		else:
			num_pages_remaining = self.subreddit_page_posts_depth
		if num_pages_remaining < 0:
			return


		### Step 2: get all of the posts on this page ###
		this_page_posts = get_subreddit_posts (subreddit_response)


		### Step 3: dump each post, then add requests for their thread pages ###
		thread_requests = []
		for post in this_page_posts:

			#--- dump data on the post ---
			# post.print_info ()
			self.posts.append (post.get_dict_rep());		#get the dict representation	
			# post.dump_info (self.posts_file)				#get the textfile representation

			#--- gather requests for each of their thread pages ---
			thread_requests.append(self.build_thread_page_request (post))


		next_page_request_subreddit = self.build_next_page_request_subreddit(subreddit_response, num_pages_remaining)
		next_requests = thread_requests + [next_page_request_subreddit]
		return next_requests



















	############################################################################################################
	###################################[ --- THREAD SPIDER --- ]################################################
	############################################################################################################

	# Function: parse_thread
	# ----------------------
	# the main parsing function for a thread; this will get and dump all comments to a specified depth.
	# (depth will probably be hard-coded)
	def parse_thread(self, thread_response):

		print "-----> Status: Parsing thread " + thread_response.url 

		selector = HtmlXPathSelector (thread_response)

		# --- Step 1: get the content column ---
		xpath_content = "//div[@class='content']//div[@class='commentarea']//div[@class='sitetable nestedlisting']"
		content = selector.select (xpath_content)[0]

		# --- Step 2: get each of the parent comments. Syntax is different for parents and children --- 
		parent_comments = []
		xpath_comment = "./div[@onclick='click_thing(this)']"
		parent_comment_divs = content.select (xpath_comment)
		for parent_comment_div in parent_comment_divs:
			parent_comment = build_comment_from_comment_div(parent_comment_div, thread_response.url)
			parent_comments.append (parent_comment)
		

		# --- Step 4: get all of the other comments, dfs-style ---
		my_heap = []
		for comment in parent_comments:
			heappush(my_heap, (comment.score, comment))

		#--- Step 5: do BFS with choice heuristic of score on the comments ---
		depth = 0
		for depth in range(self.thread_page_comments_depth):

			if len(my_heap) > 0:

				#--- get the next most important comment ---
				process_comment = heappop (my_heap)[1]

				# --- dump info on it ---
				# process_comment.print_info ()
				# process_comment.dump_info (self.comments_file)		#get the text representation
				self.comments.append (process_comment.get_dict_rep())	#get the dict representation

				#--- remove if from the heap, 
				child_comments = get_child_comments (process_comment, thread_response.url)
				for child_comment in child_comments:
					heappush (my_heap, (child_comment.score, child_comment))
			else:
				break

		print "	---> Comments retrieved: " + str(depth) + "\n"




















	############################################################################################################
	###################################[ --- USER SPIDER --- ]##################################################
	############################################################################################################


	# Function: build_next_comments_request
	# -----------------------------------
	# given a selector for the current page and the depth we have already gone to,
	# this function will construct a request for the next page of comments
	# returns a nonetype if there is no next page
	def build_next_comments_request (self, hxs, comments_left, comments_retrieved):

		next_page_url = get_next_page_url (hxs)

		if next_page_url:
			meta = {'comments_left':comments_left, 'comments_retrieved':comments_retrieved}
			next_page_request = Request (url=next_page_url, callback=self.parse_user_comments, meta=meta)
			return next_page_request
		else:
			return None

	# Function: parse_user_comments
	# -----------------------------
	# function to parse the user comments section
	# it will chain itself and go as deep as self.user_page_comments_depth
	def parse_user_comments (self, user_comments_response):

		hxs = HtmlXPathSelector(user_comments_response)
		comments_left = user_comments_response.meta['comments_left']
		comments_retrieved = user_comments_response.meta['comments_retrieved']

		# --- Step 1: get the content div ---
		xpath_content = "//div[@class='content']//div[@id='siteTable']"
		all_content = hxs.select (xpath_content)[0]


		# --- Step 2: get each of the user activity divs --- 
		xpath_comment_divs = "./div[@onclick='click_thing(this)']"
		comment_divs = all_content.select (xpath_comment_divs)
		

		# --- Step 3: get each of the comments from the comment divs ---
		comments = []
		for comment_div in comment_divs:
			new_comment = build_comment_from_comment_div_user(comment_div)
			
			# --- Print/Dump Info ---
			# print "	--- comments retrieved/left: " + str(comments_retrieved) + "/" + str(comments_left) + " ---"
			# new_comment.print_info ()
			# new_comment.dump_info (self.comments_file)				#get the text rep of the comment
			self.comments.append (new_comment.get_dict_rep) 		#get the dict rep of the comment
		
			comments.append (new_comment)
			comments_retrieved += 1
			comments_left -= 1
			if comments_left == 0:
				return


		#--- Step 4: submit request for next page, if necessary ---
		if comments_left > 0:
			next_request = self.build_next_comments_request (hxs, comments_left, comments_retrieved)
			return next_request
		else:
			return 





	# Function: build_next_posts_request
	# -----------------------------------
	# given a selector for the current page and the depth we have already gone to,
	# this function will construct a request for the next page of comments
	# returns a nonetype if there is no next page
	def build_next_posts_request (self, hxs, posts_left, posts_retrieved):

		next_page_url = get_next_page_url (hxs)

		if next_page_url:
			meta = {'posts_left':posts_left, 'posts_retrieved':posts_retrieved}
			next_page_request = Request (url=next_page_url, callback=self.parse_user_posts, meta=meta)
			return next_page_request
		else:
			return None

	# Function: parse_user_posts
	# -----------------------------
	# function to parse the user comments section
	# it will chain itself and go as deep as self.user_page_comments_depth
	def parse_user_posts (self, user_posts_response):

		hxs = HtmlXPathSelector(user_posts_response)
		posts_left = user_posts_response.meta['posts_left']
		posts_retrieved = user_posts_response.meta['posts_retrieved']

		# --- Step 1: get the content div ---
		xpath_content = "//div[@class='content']//div[@id='siteTable']"
		all_content = hxs.select (xpath_content)[0]


		# --- Step 2: get each of the user activity divs --- 
		xpath_post_divs = "./div[@onclick='click_thing(this)']"
		post_divs = all_content.select (xpath_post_divs)
		

		# --- Step 3: get each of the posts from the post divs ---
		posts = []
		for post_div in post_divs:
			new_post = build_post_from_post_div(post_div, user_posts_response.url)
			
			#--- Print/Dump Info ---
			# print "	--- posts retrieved/left: " + str(posts_retrieved) + "/" + str(posts_left) + " ---"
			# new_post.print_info ()
			# new_post.dump_info (self.posts_file)
			self.posts.append (new_post.get_dict_rep())
			

			posts.append (new_post)
			posts_retrieved += 1
			posts_left -= 1
			if posts_left == 0:
				return


		# --- Step 4: get all the comments on a post from this user ---
		thread_page_requests = []
		for post in posts:
			thread_page_request = self.build_thread_page_request (post)
			thread_page_requests.append (thread_page_request)


		next_requests = thread_page_requests
		#--- Step 4: submit request for next page, if necessary ---
		if posts_left > 0:
			next_post_page_request = self.build_next_posts_request (hxs, posts_left, posts_retrieved)
			next_requests.append (next_post_page_request)

		return next_requests






	# Function: parse_user
	# --------------------
	# given a response object from a user's page, this function will gather all the info about him and 
	# dump it to splunk for more analysis
	def parse_user (self, user_response):

		print "-----> Status: Parsing user " + user_response.url + "\n"

		hxs = HtmlXPathSelector (user_response)


		#### Step 1: get objective info on user (name, karma, age) ###
		user = build_user_from_user_page_selector (hxs, user_response.url)
		# user.print_info ()
		# user.dump_info(self.users_file)

		### Step 2: get the tabmenu ###
		xpath_tabmenu = "//ul[@class='tabmenu ']"
		tabmenu = hxs.select (xpath_tabmenu)


		### Step 3: build request for user's comments ###
		user_comments_url = user_response.url + "/comments/"
		meta = {'comments_left':self.user_page_comments_depth, 'comments_retrieved':0}
		user_comments_request = Request (url=user_comments_url, callback=self.parse_user_comments, meta=meta)


		### Step 4: build request for user's posts ###
		user_posts_url = user_response.url + "/submitted/"
		meta = {'posts_left':self.user_page_posts_depth, 'posts_retrieved':0}
		user_posts_request = Request (url=user_posts_url, callback=self.parse_user_posts, meta=meta)


		# return user_comments_request
		# return user_posts_request

		# FOR WHEN YOU WANT TO SCRAPE COMMENTS AS WELL 
		return [user_comments_request, user_posts_request]











