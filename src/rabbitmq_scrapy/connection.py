import pika
import logging
from . import defaults

logger = logging.getLogger(__name__)


class RabbitmqManager():

    def __init__(self,
        RABBITMQ_CONNECTION_URL=None,
        RABBITMQ_AUTO_ACK=None,
        RABBITMQ_DURABLE=None,
        RABBITMQ_PREFETCH_COUNT=None,
        RABBITMQ_CONFIRM_DELIVERY=None,
        RABBITMQ_QUEUE_NAME=None,
        DELIVERY_MODE = 1,
    ):
        
        self.rabbitmq_connection_url = RABBITMQ_CONNECTION_URL
        self.rabbitmq_auto_ack = RABBITMQ_AUTO_ACK
        self.rabbitmq_durable = RABBITMQ_DURABLE
        self.rabbitmq_prefetch_count = RABBITMQ_PREFETCH_COUNT
        self.rabbitmq_confirm_delivery = RABBITMQ_CONFIRM_DELIVERY
        self.queue_name = RABBITMQ_QUEUE_NAME
        self.delivery_mode = DELIVERY_MODE

        self.channel = self.get_rabbitmq_channel()
 

    def get_rabbitmq_channel(self) -> pika.channel.Channel:
        
        # get the RabbitMQ server connection parameters
        connection_parameters = pika.URLParameters(self.rabbitmq_connection_url)
        # create a connection to the RabbitMQ server
        try:
            connection = pika.BlockingConnection(connection_parameters)
       
            # create a channel to the RabbitMQ server
            channel = connection.channel()

            # declare a queue on the RabbitMQ server
            channel.queue_declare(
                queue=self.queue_name,
                durable=self.rabbitmq_durable,   
            )

            # enable delivery confirmation
            if self.rabbitmq_confirm_delivery:
                channel.confirm_delivery()

            # set the prefetch count
            channel.basic_qos(prefetch_count=self.rabbitmq_prefetch_count)

            return channel
    
        except Exception as e:
             logger.error("RabbitMQ connection error %s" % str(e))

    def len(self) -> int:
        try:
            result = self.channel.queue_declare(queue=self.queue_name, passive=True)
            return result.method.message_count
        except Exception as e:
            logger.error("RabbitMQ get_len error %s" % str(e))
            
    def publish(self, message) -> None:
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message,
                properties=pika.BasicProperties(delivery_mode=self.delivery_mode)
            ) 
        except Exception as e:
            logger.error("RabbitMQ publish error %s" % str(e))

    def consume(self) -> str:

        try:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=self.rabbitmq_auto_ack)
            
            if method_frame:
                return body

            return None
        
        except Exception as e:
            logger.error("RabbitMQ consume error %s" % str(e))
            
    def clear(self) -> None:
        self.channel.queue_purge(queue=self.queue_name)    

    def close(self) -> None:
        self.channel.close()