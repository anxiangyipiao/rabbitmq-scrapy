
# 默认配置
START_URLS_NAME = "%(name)s:start_urls"

MAX_IDLE_TIME = 0
# RabbitMQ 连接参数
RABBITMQ_CONNECTION_PARAMETERS = 'amqp://guest:guest@localhost:5672/%2F?heartbeat=0'
# rabbitmq 确认消息
RABBITMQ_CONFIRM_DELIVERY = True
# rabbitmq 持久化
RABBITMQ_DURABLE = True
# rabbitmq 预取数量设置
RABBITMQ_PREFETCH_COUNT = 1
# auto_ack
RABBITMQ_AUTO_ACK = False

SCHEDULER_QUEUE_KEY = "share:requests"