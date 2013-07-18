# Scrapy settings for reddit_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'reddit_scraper'

SPIDER_MODULES = ['reddit_scraper.spiders']
NEWSPIDER_MODULE = 'reddit_scraper.spiders'

#disables the annoying debug messages
LOG_LEVEL = 'INFO'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'reddit_scraper (+http://www.yourdomain.com)'
