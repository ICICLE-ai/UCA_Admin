import unittest
import create_topic


class TestCreateTopic(unittest.TestCase):
    def test_create(self):
        topics = create_topic.create_topic("test_topic_1")
        print(topics)
