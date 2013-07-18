import os
import sys



#---- SENTIMENT MODULES --------
# PATTERN_MODULE_MAC = "/Users/Shared/pattern-2.5"
# PATTERN_MODULE_WIMPY = "/home/jhack/Programming/Scraper2/pattern_install_directory/lib/python2.6/site-packages"
# if PATTERN_MODULE_MAC not in sys.path:
	# sys.path.append(PATTERN_MODULE_MAC)
# if PATTERN_MODULE_WIMPY not in sys.path:
	# sys.path.append (PATTERN_MODULE_WIMPY)
# from pattern.en import sentiment

class Post:

	break_string = "|||BREAK_PATTERN|||"

	# --- class variables ---
	user = ''
	title = ''
	my_id = '' #will be filled in upon viewing the post's page
	time = ''
	score = 0
	subreddit = ''
	link_url = ''
	comments_url = ''
	comments = []

	# --- NLP characterizations ---
	polarity = 0.0
	subjectivity = 0.5
	mood = 0.0
	modality = 0.0
	negated = False


	# Function: Constructor
	# ---------------------
	# currently, this only stores objective information about a post.
	def __init__ (self, user, title, time, score, subreddit, link_url, comments_url):

		self.user = user
		self.title = title
		self.time = time
		self.score = score
		self.subreddit = subreddit 
		self.link_url = link_url
		self.comments_url = comments_url

		# fill in id from url to comments:
		splits = self.comments_url.split('/')
		self.my_id = splits[6]


	# Function: dump_info
	# -------------------
	# this function will print out any relevant information about this post.
	def print_info (self):

		print "PRINTING POST INFO: "
		print "------------------ "
		print "title: " + self.title
		print "user: " + self.user
		print "subreddit: " + self.subreddit 
		print "score: " + self.score
		print "time: " + self.time
		print "link_url: " + self.link_url
		print "comments_url" + self.comments_url
		print "id: " + self.my_id
		print "\n"

	

	# Function: get_dict_representation
	# ---------------------------------
	# this will return a dict representation of the post object
	def get_dict_rep ():
		
		dict_rep = {
			'user': self.user,
			'title': self.title,
			'subreddit': self.subreddit,
			'score': self.score,
			'time': self.time,
			'link_url': self.link_url,
			'comments_url': self.comments_url,
			'id': self.my_id
		}
		return dict_rep
		

	# Function: dump_info
	# -------------------
	# given a filename, this function will dump all of the user's info into a file
	def dump_info (self, write_file):

		user_string = "user=" + self.user
		title_string = " title='" + self.title +"'"
		id_string = " id=" + self.my_id
		time_string = " timestamp='" + self.time + "'"
		score_string = " score=" + self.score
		subreddit_string = " subreddit=" + self.subreddit
		url_string = " link_url=" + self.link_url + " comments_url=" + self.comments_url
		type_string = ' type=post'


		splunk_entry = self.break_string + type_string + time_string + user_string + title_string + id_string + score_string + subreddit_string + url_string + "\n\n\n"
		splunk_entry = splunk_entry.encode('utf8')
		write_file.write (splunk_entry)



