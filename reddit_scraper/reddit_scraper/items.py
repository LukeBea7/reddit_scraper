# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class RedditScraperItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass


# Item: PostItem
# --------------
# this item will hold all information relevant to an encountered post
class PostItem(Item):

	user = Field ()
	title = Field ()
	score = Field ()
	url = Field ()
	time = Field ()

