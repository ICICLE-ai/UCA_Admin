from kafka import KafkaProducer, errors
from app.service.kafka.custom_exceptions import TopicNotFoundException, UnknownException


def produce_message(producer: KafkaProducer, topic: str, message: dict):
    try:
        future = producer.send(topic, message) #this is lib
        record_metadata = future.get(timeout=1) #todo: timeout not working
        print(f"Message sent to topic '{topic}' successfully.")
        print(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
    except errors.UnknownTopicOrPartitionError:
        raise TopicNotFoundException(topic)
    except Exception as e:
        print("ERROR: (create_topic_service)", e)
        raise UnknownException("create_topic_service")
