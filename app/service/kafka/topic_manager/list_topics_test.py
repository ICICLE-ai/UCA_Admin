import unittest
from app.utils.settings import kafka_bootstrap_servers, kafka_client_id
from kafka import KafkaAdminClient
import list_topics


class TestListTopic(unittest.TestCase):
    def test_list_kafka_topics(self):
        kafka_admin_client = KafkaAdminClient(
            bootstrap_servers=kafka_bootstrap_servers,
            client_id=kafka_client_id,
        )
        topics = list_topics.list_topics(kafka_admin_client)
        print(topics)
