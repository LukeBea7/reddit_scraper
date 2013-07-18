#---- SENTIMENT MODULES --------
import os
import sys
# PATTERN_MODULE_MAC = "/Users/Shared/pattern-2.5"
# PATTERN_MODULE_WIMPY = "/home/jhack/Programming/Scraper2/pattern_install_directory/lib/python2.6/site-packages"
# if PATTERN_MODULE_MAC not in sys.path:
# 	sys.path.append(PATTERN_MODULE_MAC)
# if PATTERN_MODULE_WIMPY not in sys.path:
# 	sys.path.append (PATTERN_MODULE_WIMPY)
# from pattern.en import sentiment

class Comment:

	break_string = "|||BREAK_PATTERN|||"

	# --- class variables ---
	user = ''
	content = ''
	my_id = ''
	time = ''
	upvotes = 0
	downvotes = 0
	score = 0
	subreddit = ''
	post_id = '' #post that the comment is in reference to
	parent_id = ''	#id of the comment that is this comment's parent

	# --- NLP characterizations ---
	polarity = 0.0
	subjectivity = 0.5
	mood = 0.0
	modality = 0.0
	negated = False


	# Function: Constructor
	# ---------------------
	# currently, this only stores objective information about a post.
	def __init__ (self, user, content, my_id, time, upvotes, downvotes, subreddit, post_id, div_selector, parent_id="ROOT"):

		# --- fill in objective stats ---
		if user == '0':
			self.user = '[deleted]'
		else:
			self.user = user
		
		self.content = content
		self.my_id = my_id
		self.time = time
		self.upvotes = upvotes
		self.downvotes = downvotes
		self.score = upvotes - downvotes
		self.subreddit = subreddit 
		self.post_id = post_id
		self.parent_id = parent_id

		self.div_selector = div_selector

		# --- get sentiment ---
		sa = sentiment (self.content)
		self.polarity = sa[0]
		self.subjectivity = sa[1]

		# --- get mood, modality ---
		# self.negated = negated (self.content)


		# --- TODO: have to debug and add these in later!!!
		# self.mood = mood (self.content)
		# self.modality = modality (self.content)





	# Function: dump_info
	# -------------------
	# this function will print out any relevant information about this post.
	def print_info (self):

		print "	PRINTING COMMENT INFO: "
		print "	------------------ "
		print "	user: " + self.user
		print "	content: " + self.content
		print "	subreddit: " + self.subreddit
		print "	my_id: " + self.my_id 
		print "	parent_id: " + self.parent_id
		print " post_id: " + self.post_id
		print "	upvotes: ", self.upvotes
		print "	downvotes: ", self.downvotes
		print "	score: ", self.score
		print "	time: " + self.time
		# print "	polarity: " + str(self.polarity)
		# print "	subjectivity: " + str(self.subjectivity)
		print "	\n"



	# Function: get_dict_representation
	# ---------------------------------
	# this will return a dict representation of the post object
	def get_dict_rep ():
		
		dict_rep = {
			'user': self.user,
			'content': self.conent,
			'subreddit': self.subreddit,
			'id': self.my_id,
			'parent_id': self.parent_id,
			'post_id': self.post_id,
			'upvotes': self.upvotes,
			'downvotes': self.downvotes,
			'score': self.score,
			'time': self.time,
			'link_url': self.link_url,
			'comments_url': self.comments_url
		}
		return dict_rep


	# Function: dump_info
	# -------------------
	# given a filename, this function will dump all of the user's info into a file
	def dump_info (self, write_file):

		user_string = " user=" + self.user
		content_string = ' content="' + self.content + '"'
		subreddit_string = " subreddit=" + self.subreddit
		my_id_string = ' id=' + self.my_id
		parent_id_string = ' parent_id=' + self.parent_id	
		post_id_string = '	post_id=' + self.post_id	
		upvotes_string = " upvotes=" + str(self.upvotes)
		downvotes_string = " downvotes=" + str(self.downvotes)
		time_string = ' timestamp="' + self.time + '"'
		polarity_string = ' polarity=' + str(self.polarity)
		subjectivity_string = ' subjectivity=' + str(self.subjectivity)
		type_string = ' type=comment'

		splunk_entry = self.break_string + type_string + time_string + user_string + my_id_string + parent_id_string + post_id_string + content_string + upvotes_string + downvotes_string + subreddit_string + polarity_string + subjectivity_string + "\n\n\n"
		splunk_entry = splunk_entry.encode('utf8')
		write_file.write (splunk_entry)

