from heapq import heappop, heappush

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.contrib.loader import XPathItemLoader

from User import User
from Post import Post
from Comment import Comment


############################################################################################################
##############################[ --- GENERAL UTILITIES--- ]##################################################
############################################################################################################


# Function: get_subreddit_name_from_url
# ----------------------------
# given a response, this function returns a string containing the name of the subreddit
# that the response is from.
def get_subreddit_name_from_url (url):
	splits = url.split ('/')
	return splits[4]

# Function: get_post_id_from_url
# ---------------------
# given the url of a post page, this function will return the 'id' of the post
def get_post_id_from_url(url):
	splits = url.split('/')
	return splits[6]


# Function: get_username_from_url
# ----------------------
# given the url to a /u/ page, this will return the user's name
def get_username_from_url (url):
	splits = url.split ('/')
	return splits [4]

# Function: get_next_page_url
# ---------------------------
# given an xpath selector object for the current page, this function will return
# the url of the 'next' page, for both comments and posts on a subreddit.
def get_next_page_url (hxs):
	xpath_next = ".//p[@class='nextprev']/a[last()]/@href"
	next_url = hxs.select (xpath_next).extract ()
	if len(next_url) > 0:
		return next_url[0]
	else:
		return None

# Function: process_xpath
# -----------------------
# will take the result of an xpath query and return it as a single object.
def process_xpath (xpath_result):
	if len(xpath_result) < 1:
		return '0'
	else:
		return xpath_result[0]










############################################################################################################
##############################[ --- POSTS --- ]#############################################################
############################################################################################################

# Function: build_post_from_post_div
# ----------------------------------
# given the selector for a post, this function will build and return a 'post' object for it.
def build_post_from_post_div (post_div, url):

	# --- SCORE ---
	xpath_score = ".//div[@class='score unvoted']/text()"
	score = post_div.select(xpath_score).extract()
	score = process_xpath (score)


	# --- TITLE ---
	xpath_title = ".//a[@class='title ']/text()"
	title = post_div.select(xpath_title).extract ()
	title = process_xpath (title)


	# --- TIME ---
	xpath_time = ".//time/@datetime"
	time = post_div.select(xpath_time).extract ()
	time = process_xpath (time)


	#--- for user and subreddit, get the tagline... ---
	xpath_tagline = ".//p[@class='tagline']"
	tagline = post_div.select(xpath_tagline)


	# --- USER ---
	xpath_user = ".//a[1]/text()"
	user = tagline.select(xpath_user).extract ()
	user = process_xpath (user)


	# --- SUBREDDIT ---
	xpath_subreddit = ".//a[2]/text()"
	subreddit = tagline.select(xpath_subreddit).extract()
	if len(subreddit) < 1:
		subreddit = get_subreddit_name_from_url (url)
	else:
		subreddit = subreddit[0]


	# --- URL (to actual link) ---
	xpath_link_url = ".//a[@class='title ']/@href"
	link_url = post_div.select(xpath_link_url).extract ()
	link_url = process_xpath (link_url)

	# --- URL (to comments) ---
	xpath_comments_url = ".//li[@class='first']//a/@href"
	comments_url = post_div.select(xpath_comments_url).extract()
	comments_url = process_xpath (comments_url)

	new_post = Post (user, title, time, score, subreddit, link_url, comments_url)
	return new_post

# Function: get_subreddit_posts
# --------------------------------
# given a response object from the front page of a subreddit (or just the front page), this function
# will return a list of all the post objects. (only for one page, mind you!)
def get_subreddit_posts (thread_response):

	selector = HtmlXPathSelector (thread_response)

	# --- Step 1: get the content column ---
	xpath_content = "//div[@class='content']//div[@id='siteTable']"
	content = selector.select (xpath_content)[0]

	# --- Step 2: get each of the posts --- 
	xpath_post = ".//div[@onclick='click_thing(this)']"
	post_divs = content.select (xpath_post)

	# --- Step 4: for each post, create a post object ---
	posts = []
	for post_div in post_divs:

		new_post = build_post_from_post_div (post_div, thread_response.url)
		posts.append (new_post)

	return posts














############################################################################################################
##############################[ --- COMMENTS --- ]##########################################################
############################################################################################################

# Function: get_child_comments
# ----------------------------
# given a comment object (which includes its "div_selector"), this function will return a list of comment objects
# that represent its immediate children
def get_child_comments (parent_comment, url):
	div_selector = parent_comment.div_selector

	child_comments = []

	xpath_children = "./div[@class='child']/div[@class='sitetable listing']/div[@onclick='click_thing(this)']"
	children_selector = div_selector.select(xpath_children)

	for child_div in children_selector:
		comment = build_comment_from_comment_div(child_div, url, parent_id=parent_comment.my_id)
		child_comments.append(comment)

	return child_comments

# Function: build_comment_from_comment_div
# ----------------------------------------
# given a selector for a comment_div and the page url, this function will build a comment object out of it.
#
# Notes:
# - discards all quoted text and links
# - doesn't currently get the comment/post that its in response to (just the subreddit)
def build_comment_from_comment_div (comment_div, url, parent_id="ROOT"):

	# --- UPVOTES ---
	xpath_upvotes = "./@data-ups"
	upvotes = comment_div.select(xpath_upvotes).extract()
	upvotes = process_xpath (upvotes)


	# --- DOWNVOTES ---
	xpath_downvotes = "./@data-downs"
	downvotes = comment_div.select(xpath_downvotes).extract()
	downvotes = process_xpath (upvotes)


	# --- TITLE ---
	xpath_my_id = "./@data-fullname"
	my_id = comment_div.select(xpath_my_id).extract ()
	my_id = process_xpath (my_id)


	# --- TIME ---
	xpath_time = "./div[@class='entry unvoted']//time/@title"
	time = comment_div.select(xpath_time).extract ()
	time = process_xpath (time)


	#--- for user and subreddit... ---
	xpath_tagline = ".//p[@class='tagline']"
	tagline = comment_div.select(xpath_tagline)
	tagline = process_xpath (tagline)


	# --- USER ---
	xpath_user = ".//a[2]/text()"
	user = tagline.select(xpath_user).extract ()
	user = process_xpath (user)

	# --- SUBREDDIT ---
	subreddit = get_subreddit_name_from_url (url)


	# --- POST_ID ---
	post_id = get_post_id_from_url(url)


	# --- CONTENT (get each paragraph) ---
	xpath_content = "./div[@class='entry unvoted']//div[@class='usertext-body']/div[@class='md']/p/text()"
	content_list = comment_div.select(xpath_content).extract()
	if len(content_list) < 1:
		content = ''
	else:
		content = '.'.join (content_list)



	# print my_id[0]
	# print upvotes[0]
	# print downvotes[0]
	# print time[0]
	# print content
	# print user[0]


	return Comment (user, content, my_id, time, int(upvotes), int(downvotes), subreddit, post_id, comment_div, parent_id=parent_id)

# Function: build_comment_from_comment_div_user
# ----------------------------------------
# same as above, though it doesn't get the subreddit through the URL
def build_comment_from_comment_div_user (comment_div, parent_id="ROOT"):

	# --- UPVOTES ---
	xpath_upvotes = "./@data-ups"
	upvotes = comment_div.select(xpath_upvotes).extract()
	upvotes = process_xpath (upvotes)


	# --- DOWNVOTES ---
	xpath_downvotes = "./@data-downs"
	downvotes = comment_div.select(xpath_downvotes).extract()
	downvotes = process_xpath (upvotes)


	# --- TITLE ---
	xpath_my_id = "./@data-fullname"
	my_id = comment_div.select(xpath_my_id).extract ()
	my_id = process_xpath (my_id)


	# --- TIME ---
	xpath_time = "./div[@class='entry unvoted']//time/@title"
	time = comment_div.select(xpath_time).extract ()
	time = process_xpath (time)


	#--- for user and subreddit... ---
	xpath_tagline = ".//p[@class='tagline']"
	tagline = comment_div.select(xpath_tagline)
	tagline = process_xpath (tagline)


	# --- USER ---
	xpath_user = ".//a[2]/text()"
	user = tagline.select(xpath_user).extract ()
	user = process_xpath (user)

	# --- SUBREDDIT ---
	xpath_subreddit = ".//a[@class='subreddit hover']/text()"
	subreddit = comment_div.select(xpath_subreddit).extract ()
	subreddit = process_xpath (subreddit)


	# --- POST_ID ---
	xpath_post_url = ".//a[@class='title']/@href"
	post_url = comment_div.select(xpath_post_url).extract ()[0]
	splits = post_url.split('/')
	post_id = splits[2]


	# --- CONTENT (get each paragraph) ---
	xpath_content = "./div[@class='entry unvoted']//div[@class='usertext-body']/div[@class='md']/p/text()"
	content_list = comment_div.select(xpath_content).extract()
	if len(content_list) < 1:
		content = ''
	else:
		content = '.'.join (content_list)
		content.replace ('"', "'") 			#sanitize: strings can only contain single quotes




	# print my_id[0]
	# print upvotes[0]
	# print downvotes[0]
	# print time[0]
	# print content
	# print user[0]


	return Comment (user, content, my_id, time, int(upvotes), int(downvotes), subreddit, post_id, comment_div, parent_id=parent_id)












############################################################################################################
##############################[ --- USERS --- ]#############################################################
############################################################################################################
# Function: build_user_from_user_response
# --------------------------------------
# given a request object to a user's page, this function will build and return a user object
# that contains all the available information
def build_user_from_user_page_selector (hxs, url):
		
		# USERNAME
		username = get_username_from_url (url)


		# LINK KARMA
		xpath_link = "//span[@class='karma']/text()"
		link_karma = hxs.select(xpath_link).extract ()
		link_karma = link_karma[0]


		# COMMENT KARMA
		xpath_comment = "//span[@class='karma comment-karma']/text()"
		comment_karma = hxs.select(xpath_comment).extract ()
		comment_karma = comment_karma[0]


		# AGE
		xpath_age = "//span[@class='age']/time/@datetime"
		age = hxs.select (xpath_age).extract ()
		age = age[0]


		### Step 2: create the user object ###
		new_user = User (username, link_karma, comment_karma, age)
		# new_user.print_info ()


		return new_user











