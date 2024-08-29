
import time
from collections.abc import Iterable
from scrapy import signals
from scrapy import version_info as scrapy_version
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import CrawlSpider, Spider
from . import connection, defaults


class RabbitMQMixin:
    """Mixin class to implement reading urls from a RabbitMQ queue."""

    # name of the queue
    queue_name = None
    server = None
    spider_idle_start_time = int(time.time())
    max_idle_time = None

    def start_requests(self):
        """Returns a batch of start requests from RabbitMQ.""" 
        return self.next_requests()

    def setup_rabbitmq(self, crawler):
        ''' set up RabbitMQ connection '''
        if self.server is not None:
            return

        if crawler is None:
            crawler = getattr(self, "crawler", None)

        if crawler is None:
            raise ValueError("crawler is required")

        settings = crawler.settings

        if self.max_idle_time is None:
            self.max_idle_time = settings.get(
                "MAX_IDLE_TIME_BEFORE_CLOSE", defaults.MAX_IDLE_TIME
            )

        try:
            self.max_idle_time = int(self.max_idle_time)
        except (TypeError, ValueError):
            raise ValueError("max_idle_time must be an integer")

        # get the RabbitMQ server connection parameters from settings
        self.server = connection.RabbitmqManager(settings, self.queue_name)

        
        self.crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)
        
    def next_requests(self):
        
        found = 0
        # get a data from the RabbitMQ server
        data = self.server.consume()
        if data:
            # make a request from the data
            reqs = self.make_request_from_data(data)
            # yield the request
            if isinstance(reqs, Iterable):
                for req in reqs:
                    yield req
                    # XXX: should be here?
                    found += 1
                    self.logger.info(f"start req url:{req.url}")
            elif reqs:
                yield reqs
                found += 1
            else:
                self.logger.debug(f"Request not made from data: {data}")

        if found:
            self.logger.debug(f"Read {found} requests from '{self.queue_name}'")

    def make_request_from_data(self, data):
        # make a request from the data
        # return a Request object
        # args: data:str  - the data from the RabbitMQ server
        
        pass

    def schedule_next_requests(self):
        
        for req in self.next_requests():
            
            if scrapy_version >= (2, 6):
                self.crawler.engine.crawl(req)
            else:
                self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self):
           
        if self.server is not None and self.server.len() > 0:
            self.spider_idle_start_time = int(time.time())

        self.schedule_next_requests()

        idle_time = int(time.time()) - self.spider_idle_start_time
        if self.max_idle_time != 0 and idle_time >= self.max_idle_time:
            return
        raise DontCloseSpider


class RabbitSpider(RabbitMQMixin, Spider):
    """Spider that reads urls from RabbitMQ queue when idle."""
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        obj = super().from_crawler(crawler, *args, **kwargs)
        obj.setup_rabbitmq(crawler)
        return obj
    

class RabbitCrawlSpider(RabbitMQMixin, CrawlSpider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        obj = super().from_crawler(crawler, *args, **kwargs)
        obj.setup_rabbitmq(crawler)
        return obj
