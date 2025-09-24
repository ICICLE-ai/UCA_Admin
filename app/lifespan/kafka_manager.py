from kafka import KafkaAdminClient, KafkaProducer
from app.utils.settings import kafka_bootstrap_servers, kafka_client_id

def connect_kafka(app):
    print("Connecting to Kafka admin client...")
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=kafka_bootstrap_servers,
            client_id=kafka_client_id,
        )
        app.state.kafka_admin_client = admin_client
        print("Kafka admin client connected successfully.")
    except Exception as e:
        print(f"Failed to connect to Kafka Admin Client: {e}")
    print("Connecting to Kafka producer...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: str(v).encode('utf-8')
        )
        app.state.kafka_producer = producer
        print("Kafka producer started successfully.")
    except Exception as e:
        print(f"Failed to start Kafka Producer: {e}")

    # print("Connecting to Kafka consumer...")
    # try:
    #     consumer = KafkaConsumer(
    #         bootstrap_servers=kafka_bootstrap_servers,
    #         auto_offset_reset='earliest',
    #         enable_auto_commit=True,
    #     )
    #     app.state.kafka_consumer = consumer
    #     print("Kafka consumer started successfully.")
    # except Exception as e:
    #     print(f"Failed to start Kafka Consumer: {e}")


def disconnect_kafka(app):
    if hasattr(app.state, 'kafka_admin_client'):
        print("Closing Kafka admin client connection...")
        app.state.kafka_admin_client.close()
        print("Kafka admin client closed.")
    if hasattr(app.state, 'kafka_producer'):
        print("Closing Kafka producer connection...")
        app.state.kafka_producer.close()
        print("Kafka producer closed.")
    # if hasattr(app.state, 'kafka_consumer'):
    #     print("Closing Kafka consumer connection...")
    #     app.state.kafka_consumer.close()
    #     print("Kafka consumer closed.")
