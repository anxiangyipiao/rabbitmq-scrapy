
import logging
import logging
from .queue import RabbitMQQueue  # Assuming this is the module where RabbitMQQueue is defined
from . import defaults,connection


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
  
    def __init__(self, sever: connection.RabbitmqManager):
        self.sever = sever
        self.spider = None
        self.queue = None
     
    @classmethod
    def from_settings(cls, settings):
    
        server = connection.RabbitmqManager(
            settings.get("RABBITMQ_CONNECTION_URL", defaults.RABBITMQ_CONNECTION_URL),
            settings.get("SCHEDULER_AUTO_ACK ", defaults.SCHEDULER_AUTO_ACK),
            settings.get("SCHEDULER_DURABLE", defaults.SCHEDULER_DURABLE),
            settings.get("RABBITMQ_PREFETCH_COUNT", defaults.RABBITMQ_PREFETCH_COUNT),
            settings.get("RABBITMQ_CONFIRM_DELIVERY", defaults.RABBITMQ_CONFIRM_DELIVERY),
            settings.get("SCHEDULER_QUEUE_KEY", defaults.SCHEDULER_QUEUE_KEY),
            settings.get("DELIVERY_MODE", defaults.DELIVERY_MODE),
        )

        return cls(server)
      
    @classmethod
    def from_crawler(cls, crawler):
        instance = cls.from_settings(crawler.settings)
        instance.stats = crawler.stats
        return instance

    def __len__(self):
        return len(self.queue)

    def open(self, spider):

        self.spider = spider
        
        self.queue = RabbitMQQueue(self.sever,spider)

        msg_count = len(self.queue)
        if msg_count:
            logger.info(
                'Resuming crawling ({} urls scheduled)'.format(msg_count))
        else:
            logger.info('No items to crawl in {}'.format(spider.queue_name))

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



