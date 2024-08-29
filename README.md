# README





**Inspired by scrapy-redis, this scrapy scheduler is realized by using rabbitmq, and it can also be connected with rabbitmq queue to realize the read request.**



#### **Here's how to use it**

```
git clone https://github.com/anxiangyipiao/rabbitmq-scrapy/tree/main
python setup.py install

or 

pip install rabbitmq-scrapy

```

#### Must be set

```
[#Parameters to be configured
MAX_IDLE_TIME_BEFORE_CLOSE = 0
RABBITMQ_CONNECTION_URL = 'amqp://guest:guest@localhost:5672/%2F?heartbeat=600&blocked_connection_timeout=300&connection_attempts=3&retry_delay=5'
RABBITMQ_AUTO_ACK = True
RABBITMQ_DURABLE = True
RABBITMQ_CONFIRM_DELIVERY = True
SCHEDULER_QUEUE_KEY = "scheduler_queue"
SCHEDULER_AUTO_ACK = True
SCHEDULER_DURABLE = True
DELIVERY_MODE = 2
RABBITMQ_PREFETCH_COUNT = 10
```

#### then,how to use

```python

you need override this func,data is data from your rabbitmq 

def make_request_from_data(self,data):
        
	return scrapy.Request(url = data, callback=self.parse)
```





