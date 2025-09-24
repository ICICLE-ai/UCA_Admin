from kafka import KafkaAdminClient
from app.service.kafka.custom_exceptions import UnknownException


def list_topics(admin_client: KafkaAdminClient):
    try:
        return admin_client.list_topics()
    except Exception as e:
        print("ERROR: (list_topics_service)", e)
        raise UnknownException("list_topics_service")

