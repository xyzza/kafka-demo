"""Minimal Kafka consumer for demo_topic."""
import json
import os
from typing import Union
from kafka import KafkaConsumer

# Docker internal broker addresses
BOOTSTRAP_SERVERS = os.getenv(
    'KAFKA_BOOTSTRAP_SERVERS',
    'broker-1:19092,broker-2:19092,broker-3:19092'
).split(',')

TOPIC = os.getenv('KAFKA_TOPIC', 'demo_topic')
GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'demo-consumer-group')


def deserialize_value(data: bytes) -> Union[dict, str, None]:
    """Deserializes value: JSON -> dict, otherwise -> str."""
    if not data:
        return None
    text = data.decode('utf-8')
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def create_consumer() -> KafkaConsumer:
    """Creates and returns a Kafka consumer."""
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=deserialize_value
    )


def consume_messages():
    """Main message consumption loop."""
    consumer = create_consumer()
    print(f"Consumer started. Listening to '{TOPIC}'...")
    print(f"Bootstrap servers: {BOOTSTRAP_SERVERS}")

    try:
        for message in consumer:
            print(f"Partition: {message.partition}, Offset: {message.offset}")
            print(f"Key: {message.key}, Value: {message.value}")
            print("-" * 50)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        consumer.close()


if __name__ == '__main__':
    consume_messages()
