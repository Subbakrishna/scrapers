import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.item import Item, Field
from androidPitScrap.items import QuestionItem , AnswerItem

class AndroidPitScraper(CrawlSpider):
    name = "AndroidPitScraper"
    allowed_domains = ["androidpit.com"]

    def start_requests(self):
        return [scrapy.Request('https://www.androidpit.com/forum/recent/' )]



    def parse(self, response):
        return self.parse_listing(response)
        pass

    def parse_listing(self , response):

        sel = Selector(response)
        nextUrl = sel.xpath('//*[@id="tabs_recent_panel"]//div[@class="forumThreadListNavigation"]/a[@rel="next"]/@href').extract()
        nextUrl=self.__normalise(nextUrl)
        nextUrl=self.__to_absolute_url("https://www.androidpit.com",nextUrl)
        self.log(nextUrl)
        yield scrapy.Request(nextUrl)

        questions = sel.xpath('//*[@id="tabs_recent_panel"]/ul/li[position()>1]')
        for question in questions :
            questionURL = question.xpath('./a[@class="forumThreadListRowLink"]/@href').extract()
            questionURL = self.__normalise(questionURL)
            questionURL = self.__to_absolute_url("https://www.androidpit.com" ,questionURL )

            yield scrapy.Request(questionURL, callback=self.parse_details)

        pass

    def parse_details(self , response):

        sel= Selector(response)

        mainContainer = sel.xpath('//main')

        questionItem = QuestionItem()

        questionItem["questionCategory"]=mainContainer.xpath('./header/nav/ol/li[last()]/a/span[1]/text()').extract()
        questionItem["questionTitle"]=sel.xpath('//*[@id="forumHeadingThread"]/text()').extract()
        questionItem["numberOfAnswers"]=mainContainer.xpath('./header/div[@class="forumHeadingWithFavorite"]/ul/li[1]/span[2]/text()').extract()
        questionItem["questionAuthor"]=sel.xpath('//*[@id="forumThreadContainer"]/div[1]/article[1]/div/div/div[1]/div[1]/div[2]/div[1]/a/text()').extract()
        questionItem["questionDate"]=sel.xpath('//*[@id="forumThreadContainer"]/div[1]/article[1]/div/div/div[1]/div[1]/p/text()').extract()
        questionItem["questionContent"]=sel.xpath('//*[@id="forumThreadContainer"]/div[1]/article[1]/div/div/div[1]/div[2]/p/text()').extract()

        answersThread = sel.xpath('//*[@id="forumThreadContainer"]/div[1]/article[position() > 1 ]')
        ansList=[]
        for answer in answersThread :
            ansItem = AnswerItem()
            ansItem['answerThreadAuthor']=answer.xpath('./div/div/div[1]/div[1]/div[2]/div[1]/a/text()').extract()
            ansItem['answerThreadDate'] = answer.xpath('./div/div/div[1]/div[1]/p/text()').extract()
            ansItem['answerThreadContent']=answer.xpath('./div/div/div[1]/div[2]/p/text()').extract()
            ansList.append(ansItem)

        questionItem['answersThread']=ansList

        return questionItem
        pass

    def __normalise(self, value):
		# Convert list to string
		value = value if type(value) is not list else ' '.join(value)
		# Trim leading and trailing special characters (Whitespaces, newlines, spaces, tabs, carriage returns)
		value = value.strip()

		return value

    def __to_absolute_url(self, base_url, link):
		'''
		Convert relative URL to absolute URL
		'''

		import urlparse

		link = urlparse.urljoin(base_url, link)

		return link
