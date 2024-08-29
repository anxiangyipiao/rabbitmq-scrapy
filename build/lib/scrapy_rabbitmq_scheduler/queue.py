import logging
from .connection import RabbitmqManager
try:
    from scrapy.utils.request import request_from_dict
except ImportError:
    from scrapy.utils.reqser import request_to_dict, request_from_dict

import pickle

logger = logging.getLogger(__name__)



class RabbitMQQueue(object):
    """Per-spider FIFO queue"""

    def __init__(self,settings,queue_name,spider=None):

        self.settings = settings
        self.queue_name = queue_name
        self.spider = spider

        self.__check_init()

        try:
            self.rabbitmanager = self._make_connection()
        except:
            logger.error("RabbitMQQueue init error")

    def __check_init(self):
    
        if not self.settings:
            raise ValueError("settings must be set")
        
        if not self.spider:
            logger.error("RabbitMQQueue init error spider is None")

    def _make_connection(self) -> RabbitmqManager:
        """Make connection"""
        try:
           return RabbitmqManager(self.settings, self.queue_name)
        
        except Exception as e:
            logger.error("RabbitMQQueue init error %s" % str(e))

    def __len__(self) -> int:
        """Return the length of the queue"""
        return self.rabbitmanager.len()

    def push(self, request) -> None:
        
        """Push an item"""
        self.rabbitmanager.publish(self._encode_request(request))

    def _decode_request(self, encoded_request):
        """Decode an request previously encoded"""
        obj = pickle.loads(encoded_request)
        return request_from_dict(obj, spider=self.spider)

    def _encode_request(self, request):
        """Encode a request object"""
        try:
            obj = request.to_dict(spider=self.spider)
        except AttributeError:
            obj = request_to_dict(request, self.spider)
        return pickle.dumps(obj)   

    def pop(self):
        """Pop an url"""

        data = self.rabbitmanager.consume()

        if data:
            return self._decode_request(data)
     
    def clear(self):
        """Clear queue/stack"""
        self.rabbitmanager.clear()

    def close(self):
        """Close channel"""
        self.rabbitmanager.close()