class User:


	break_string = "|||BREAK_PATTERN|||"

	# --- class variables ---
	name = ''
	link_karma = 0
	comment_karma = 0
	age = 0
	posts = []
	comments = []



	# Function: Constructor
	# ---------------------
	# currently, this only stores objective information about a post.
	def __init__ (self, name, link_karma, comment_karma, age, posts=[], comments=[]):

		self.name = name
		self.link_karma = link_karma
		self.comment_karma = comment_karma
		self.posts = posts
		self.comments = comments
		self.age = age


	# Function: print_info
	# -------------------
	# this function will print out any relevant information about this post.
	def print_info (self):

		print "PRINTING USER INFO: "
		print "------------------ "
		print "name: " + self.name
		print "link/comment karma: ", self.link_karma + ", " + self.comment_karma
		print "age: " + self.age
		print "\n"


	# Function: get_dict_representation
	# ---------------------------------
	# this will return a dict representation of the post object
	def get_dict_representation ():
		dict_rep = {
			'name': self.name,
			'link_karma': self.link_karma,
			'comment_karma': self.comment_karma,
			'age': self.age
		}
		return dict_rep


	# Function: dump_info
	# -------------------
	# given a filename, this function will dump all of the user's info into a file
	def dump_info (self, write_file):

		name_string = " name=" + self.name 
		karma_string = " link_karma=" + self.link_karma + " comment_karma=" + self.comment_karma
		age_string= " timestamp=" + self.age
		type_string = ' type=user'

		dump_string = self.break_string + type_string + age_string + name_string + karma_string + "\n\n\n"
		write_file.write (dump_string)



