"""Defines core consumer functionality"""
import logging

import confluent_kafka
from confluent_kafka import Consumer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from tornado import gen


logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Defines the base kafka consumer class"""

    def __init__(
        self,
        topic_name_pattern,
        message_handler,
        is_avro=True,
        offset_earliest=False,
        sleep_secs=1.0,
        consume_timeout=0.1,
    ):
        """Creates a consumer object for asynchronous use"""
        self.topic_name_pattern = topic_name_pattern
        self.message_handler = message_handler
        self.sleep_secs = sleep_secs
        self.consume_timeout = consume_timeout
        self.offset_earliest = offset_earliest

        #
        #
        # TODO: Configure the broker properties below. Make sure to reference the project README
        # and use the Host URL for Kafka and Schema Registry!
        #
        #
        self.broker_properties = {
            "bootstrap.servers": "PLAINTEXT://localhost:9092",
            "group.id": f"{topic_name_pattern}",
            "default.topic.config": {"auto.offset.reset": "earliest"},
        }

        # TODO: Create the Consumer, using the appropriate type.
        if is_avro is True:
            self.broker_properties["schema.registry.url"] = "http://localhost:8081"
            #self.consumer = AvroConsumer(...)
        else:
            #self.consumer = Consumer(...)
            pass

        #
        #
        # TODO: Configure the AvroConsumer and subscribe to the topics. Make sure to think about
        # how the `on_assign` callback should be invoked.
        #
        #
        # self.consumer.subscribe( TODO )

       def on_assign(self, consumer, partitions):
        logger.info("partition assign")
        for partition in partitions:
            if self.offset_earliest is True:
                partition.offset = confluent_kafka.OFFSET_BEGINNING
        consumer.assign(partitions)

    async def consume(self):
        """Asynchronously consumes data from kafka topic"""
        while True:
            num_results = 1s
            while num_results > 0:
                num_results = self._consume()
            await gen.sleep(self.sleep_secs)

    def _consume(self):
        message = self.consumer.poll(timeout=self.consume_timeout)

        if message is None:
            logger.info("Consumer No message")
            return 0
        elif message.error() is not None:
            print(f"Error in encountere: {message.error()}")
            logger.error(f"Error in encountere: {message.error()}")
            return 0

        print("key:",message.key())
        print("value:",message.value())
        self.message_handler(message)
        return 1

    def close(self):
        logger.debug("closing consumer...")
        self.consumer.close()