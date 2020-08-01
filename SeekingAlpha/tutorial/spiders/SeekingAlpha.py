import scrapy
from urllib.parse import urlparse
from slugify import slugify

# RANDOMIZE USER AGENTS ON EACH REQUEST:
import random
# SRC: https://developers.whatismybrowser.com/useragents/explore/
user_agent_list = [
   #Chrome
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
   "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
]
debug_mode = False

class QuotesSpider(scrapy.Spider):

    name = "quotes"
    custom_settings = {
            #'LOG_LEVEL': 'CRITICAL', # 'DEBUG'
            #'LOG_ENABLED': True,
            #'COOKIES_ENABLED' : False,
            'CONCURRENT_REQUESTS_PER_DOMAIN':1,
            'CONCURRENT_REQUESTS': 2,
            'DOWNLOAD_DELAY': 2 # 0.25 == 250 ms of delay, 1 == 1000ms of delay, etc.
    }

    def start_requests(self):
        # GET LAST INDEX PAGE NUMBER
        urls = [ 'https://seekingalpha.com/earnings/earnings-call-transcripts/9999' ]
        last_page=32
        for x in range(0, last_page+1):
            print("Number: %d",x)
            # DEBUGGING: CHECK ONLY FIRST ELEMENT
            if debug_mode == True and x > 0:
                break
            url = "https://seekingalpha.com/earnings/earnings-call-transcripts/%d" % (x)
            yield scrapy.Request(url=url, callback=self.parse_link)

    # SAVE CONTENTS TO AN HTML FILE 
    def save_contents(self, response):
        data = response.css("div#content-rail article #a-body")
        data = data.extract()
        url = urlparse(response.url)
        url = url.path
        filename = slugify(url) + ".html"
        with open(filename, 'w') as f:
            f.write(data[0])
            f.close()

    def parse_link(self, response):
        print("Parsing results for: " + response.url)
        links = response.css("a[sasource='earnings-center-transcripts_article']")
        links.extract()
        for index, link in enumerate(links):
            url = link.xpath('@href').extract()
            # DEBUGGING MODE: Parse only first link
            if debug_mode == True and index > 0:
                break
            url = link.xpath('@href').extract()
            data = urlparse(response.url)
            data = data.scheme + "://" + data.netloc + url[0]  # .scheme, .path, .params, .query
            user_agent = random.choice(user_agent_list)
            print("======------======")
            print("Getting Page:")
            print("URL: " + data)
            print("USER AGENT: " + user_agent)
            print("======------======")
            request = scrapy.Request(data,callback=self.save_contents,headers={'User-Agent': user_agent})
            yield request