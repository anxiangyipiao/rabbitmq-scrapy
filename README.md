Inspired by scrapy-redis, this scrapy scheduler is realized by using rabbitmq, and it can also be connected with rabbitmq queue to realize the read request.
Here's how to use it

git clone 
python setup.py install



#Parameters to be configured
MAX_IDLE_TIME_BEFORE_CLOSE = 0
//RabbitMQ connection parameters
RABBITMQ_CONNECTION_URL = 'amqp://guest:guest@localhost:5672/%2F?heartbeat=600&blocked_connection_timeout=300&connection_attempts=3&retry_delay=5'
RABBITMQ_AUTO_ACK = True
RABBITMQ_DURABLE = True
RABBITMQ_CONFIRM_DELIVERY = True
//rabbitmq scheduler_name
SCHEDULER_QUEUE_KEY = "scheduler_queue"
//rabbitmq scheduler 
SCHEDULER_AUTO_ACK = True
//rabbitmq scheduler 
SCHEDULER_DURABLE = True
DELIVERY_MODE = 2
RABBITMQ_PREFETCH_COUNT = 10



#then,how to use

def make_request_from_data(self,data):
        
    return scrapy.Request(url = data, callback=self.parse)






