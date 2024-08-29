import logging
from . import connection, defaults
try:
    from scrapy.utils.request import request_from_dict
except ImportError:
    from scrapy.utils.reqser import request_to_dict, request_from_dict

import pickle

logger = logging.getLogger(__name__)



class Base():

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

    def next_request(self):
        """Pop a request"""
        raise NotImplementedError

    def has_pending_requests(self):
        """Check if queue is not empty"""
        raise NotImplementedError


class RabbitMQQueue(Base):
    """Per-spider FIFO queue"""

    def __init__(self,sever:connection.RabbitmqManager,spider=None):

        self.sever = sever
        self.spider = spider

    def __len__(self) -> int:
        """Return the length of the queue"""
        return self.sever.len()

    def push(self, request) -> None:
        """Push an item"""
        self.sever.publish(self._encode_request(request))

    def pop(self):
        """Pop an url"""

        data = self.sever.consume()

        if data:
            return self._decode_request(data)
     
    def clear(self):
        """Clear queue/stack"""
        self.sever.clear()

    def close(self):
        """Close channel"""
        self.sever.close()