import asyncio
import json
from kafka import KafkaConsumer
from app.utils.settings import kafka_bootstrap_servers


def consume_message(topic: str, queue: asyncio.Queue, shutdown_flag: dict):
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=kafka_bootstrap_servers,
            auto_offset_reset="latest",#'latest',
            enable_auto_commit=False,
            group_id="websocket-consumers",
        )
        consumer.subscribe(topics=[topic])
        print(f"Starting consumer for topic '{topic}'...")

        for message in consumer:
            value = message.value.decode('utf-8')
            msg_data = {
                "topic": message.topic,
                "value": json.loads(value.replace("'", '"')),
                "offset": message.offset,
            }
            asyncio.run(queue.put(msg_data))
            consumer.commit()

    except Exception as e:
        print(f"Kafka consumer error: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
