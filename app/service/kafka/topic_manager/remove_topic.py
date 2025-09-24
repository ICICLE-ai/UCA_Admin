from kafka import KafkaAdminClient, errors
from app.service.kafka.custom_exceptions import TopicNotFoundException, UnknownException

def remove_topic(admin_client: KafkaAdminClient, topic: str):
    try:
        admin_client.delete_topics([topic])
    except errors.UnknownTopicOrPartitionError:
        raise TopicNotFoundException(topic)
    except Exception as e:
        print("ERROR: (delete_topic_service)", e)
        raise UnknownException("delete_topic_service")