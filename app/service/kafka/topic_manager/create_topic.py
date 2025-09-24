from kafka import KafkaAdminClient, errors
from kafka.admin import NewTopic
from app.service.kafka.custom_exceptions import TopicAlreadyExistsException, UnknownException


def create_topic(admin_client: KafkaAdminClient, topic: str):
    try:
        new_topics = [
            NewTopic(name=topic, num_partitions=1, replication_factor=1)
        ]
        admin_client.create_topics(new_topics)
    except errors.TopicAlreadyExistsError:
        raise TopicAlreadyExistsException(topic)
    except Exception as e:
        print("ERROR: (create_topic_service)", e)
        raise UnknownException("create_topic_service")
