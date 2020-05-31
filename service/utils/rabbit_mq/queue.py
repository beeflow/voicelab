"""RabbitMQ Queue helper."""

import pika
from pika.exceptions import StreamLostError

from vl_server.settings import get_env_value


class RabbitQueue:
    """RabbitMQ Euque consumer and producer."""

    def __init__(self, queue: str):
        """Initialize channel and queue."""
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=get_env_value('RABBITMQ_HOSTNAME'),
            port=get_env_value('RABBITMQ_DEFAULT_PORT'),
            virtual_host=get_env_value('RABBITMQ_DEFAULT_VHOST'),
            credentials=pika.credentials.PlainCredentials(
                username=get_env_value('RABBITMQ_DEFAULT_USER'),
                password=get_env_value('RABBITMQ_DEFAULT_PASS')
            ),
        ))
        self.channel = self.connection.channel()
        self.queue = queue
        self.channel.queue_declare(queue=queue)

    def basic_publish(self, routing_key, body):
        """Publish data."""
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=body
        )

    def basic_consume(self, on_message_callback, auto_ack: bool = True):
        """Consume data."""
        self.channel.basic_consume(
            queue=self.queue,
            auto_ack=auto_ack,
            on_message_callback=on_message_callback
        )

    def start_consuming(self):
        """Start consuming."""
        try:
            self.channel.start_consuming()
        except StreamLostError:
            self.start_consuming()

    def close(self):
        """Close connection."""
        self.connection.close()


class UseRabbitQueue:
    """RabbitQueue context manager."""

    def __init__(self, queue: str):
        self._queue_name = queue

    def __enter__(self) -> RabbitQueue:
        self._queue = RabbitQueue(self._queue_name)
        return self._queue

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._queue.close()
