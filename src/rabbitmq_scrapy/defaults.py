
# 爬虫最大空闲时间
MAX_IDLE_TIME_BEFORE_CLOSE = 0
# RabbitMQ connection parameters
RABBITMQ_CONNECTION_URL = 'amqp://guest:guest@localhost:5672/%2F?heartbeat=600&blocked_connection_timeout=300&connection_attempts=3&retry_delay=5'

# rabbitmq 消费者自动确认
RABBITMQ_AUTO_ACK = True
# rabbitmq消息 持久化
RABBITMQ_DURABLE = True
# rabbitmq 生产者消息确认机制
RABBITMQ_CONFIRM_DELIVERY = True


#rabbitmq scheduler 队列名称 
SCHEDULER_QUEUE_KEY = "scheduler_queue"
# rabbitmq scheduler 消费者自动确认
SCHEDULER_AUTO_ACK = True
# rabbitmq scheduler 持久化
SCHEDULER_DURABLE = True
# 消息持久化
DELIVERY_MODE = 2
# rabbitmq 预取数量设置
RABBITMQ_PREFETCH_COUNT = 10