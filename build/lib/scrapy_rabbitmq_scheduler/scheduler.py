
import logging
import logging
from .queue import RabbitMQQueue  # Assuming this is the module where RabbitMQQueue is defined
from . import defaults

logger = logging.getLogger(__name__)


class Scheduler(object):
    """ Base Scrapy scheduler class. """

    def __init__(self):
        raise NotImplementedError

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError


    def open(self, spider):
        """Start scheduling"""
        raise NotImplementedError

    def close(self, reason):
        """Stop scheduling"""
        raise NotImplementedError

    def enqueue_request(self, request):
        """Add request to queue"""
        raise NotImplementedError

    def next_request(self):
        """Pop a request"""
        raise NotImplementedError

    def has_pending_requests(self):
        """Check if queue is not empty"""
        raise NotImplementedError
    

class RabbitMQScheduler(Scheduler):

    """ A RabbitMQ Scheduler for Scrapy. """
  
    def __init__(self, settings):
        self.settings = settings
        self.spider = None
        self.queue = None
     
    @classmethod
    def from_settings(cls, settings):
        
        return cls(settings)
      
    @classmethod
    def from_crawler(cls, crawler):
        instance = cls.from_settings(crawler.settings)
        instance.stats = crawler.stats
        return instance

    def __len__(self):
        return len(self.queue)

    def open(self, spider):

        self.spider = spider
        queue_name = self.settings.get('SCHEDULER_QUEUE_KEY', defaults.SCHEDULER_QUEUE_KEY)
        self.queue = self._make_queue(queue_name)

        msg_count = len(self.queue)
        if msg_count:
            logger.info(
                'Resuming crawling ({} urls scheduled)'.format(msg_count))
        else:
            logger.info('No items to crawl in {}'.format(spider.queue_name))

    def _make_queue(self, queue_name):

        return RabbitMQQueue(self.settings,queue_name,spider=self.spider)

    def close(self, reason):
        try:
            self.queue.close()
            self.queue = None
        except:
            logger.error('scheduler schchannel close error!')

    def enqueue_request(self, request):

        """ Enqueues request to main queues back
        """
        if self.queue is not None:
            if self.stats:
                self.stats.inc_value('scheduler/enqueued/rabbitmq',
                                     spider=self.spider)
            self.queue.push(request)

        return True

    def next_request(self):
        """ Creates and returns a request to fire
        """
        if self.queue is not None:
            request = self.queue.pop()
            if request:
                if self.stats:
                    self.stats.inc_value('scheduler/dequeued/rabbitmq',
                                         spider=self.spider)

                return request

    def has_pending_requests(self):
        return len(self) > 0



