import pika
import logging
from . import defaults

logger = logging.getLogger(__name__)


class RabbitmqManager(object):

    def __init__(self,settings:object, queue_name:str):
        self.settings = settings
        self.dict = None
        self.queue_name = queue_name
        self.channel = self.get_rabbitmq_channel()
        
    def update_default_settings(self):
        
        '''如果不存在设置，则使用默认设置'''

        dict = {}
        dict['RABBITMQ_CONNECTION_PARAMETERS'] = self.settings.get('RABBITMQ_CONNECTION_PARAMETERS', defaults.RABBITMQ_CONNECTION_PARAMETERS)
        dict['RABBITMQ_AUTO_ACK'] = self.settings.get('RABBITMQ_AUTO_ACK', defaults.RABBITMQ_AUTO_ACK)
        dict['RABBITMQ_DURABLE'] = self.settings.get('RABBITMQ_DURABLE', defaults.RABBITMQ_DURABLE)
        dict['RABBITMQ_PREFETCH_COUNT'] = self.settings.get('RABBITMQ_PREFETCH_COUNT', defaults.RABBITMQ_PREFETCH_COUNT)
        dict['RABBITMQ_CONFIRM_DELIVERY'] = self.settings.get('RABBITMQ_CONFIRM_DELIVERY', defaults.RABBITMQ_CONFIRM_DELIVERY)

        self.dict = dict

    def get_rabbitmq_channel(self) -> pika.channel.Channel:
        """
        获取RabbitMQ的连接通道。
        
        Args:
            settings (dict): 包含RabbitMQ连接相关信息的字典。
        
        Returns:
            pika.channel.Channel: RabbitMQ的连接通道。
        
        Raises:
            无。
        """

        self.update_default_settings()
        
        # get the RabbitMQ server connection parameters
        connection_parameters = pika.URLParameters(self.dict.get('RABBITMQ_CONNECTION_PARAMETERS'))
        # create a connection to the RabbitMQ server
        try:
            connection = pika.BlockingConnection(connection_parameters)
        except Exception as e:
             logger.error("RabbitMQ connection error %s" % str(e))
        
        # create a channel to the RabbitMQ server
        channel = connection.channel()

        # declare a queue on the RabbitMQ server
        channel.queue_declare(
            queue=self.queue_name,
            durable=self.dict.get('RABBITMQ_DURABLE'),   
        )

        # enable delivery confirmation
        if self.dict.get('RABBITMQ_CONFIRM_DELIVERY'):
            channel.confirm_delivery()

        # set the prefetch count
        channel.basic_qos(prefetch_count=self.dict.get('RABBITMQ_PREFETCH_COUNT'))

        return channel

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
                properties=pika.BasicProperties(delivery_mode=2)
            ) 
        except Exception as e:
            logger.error("RabbitMQ publish error %s" % str(e))

    def consume(self) -> str:

        try:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=self.dict.get('RABBITMQ_AUTO_ACK'))
            
            if method_frame:
                return body

            return None
        
        except Exception as e:
            logger.error("RabbitMQ consume error %s" % str(e))
            
    def clear(self) -> None:
        self.channel.queue_purge(queue=self.queue_name)    

    def close(self) -> None:
        self.channel.close()