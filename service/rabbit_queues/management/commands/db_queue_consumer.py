"""copyright (c) 2020 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""

import json

from django.core.management.base import BaseCommand

from rabbit_queues.management.commands.db_queue_managers.wave_parser import WaveParser
from utils.rabbit_mq.queue import RabbitQueue
from vl_server import settings


class Command(BaseCommand):
    help = 'Consume wave DB QUEUE'

    __managers = {
        'wave_parser': WaveParser
    }

    def handle(self, *args, **options):
        queue = RabbitQueue(settings.RABBITMQ_DATABASE_QUEUE)
        queue.basic_consume(self.callback)
        queue.start_consuming()

    # pylint:disable=unused-argument
    def callback(self, ch, method, properties, body):
        body = json.loads(body)

        try:
            self.__managers[body['queue_engine']]().execute(body['data'])
        except KeyError:
            self.send_to_unknown_engine(body)
            return

    @staticmethod
    def send_to_unknown_engine(body):
        queue = RabbitQueue(settings.RABBITMQ_UNKNOWN_ELEMENTS_QUEUE)
        queue.basic_publish(
            routing_key=settings.RABBITMQ_UNKNOWN_ELEMENTS_QUEUE,
            body=json.dumps(body)
        )
        queue.close()
