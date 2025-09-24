import unittest
import remove_topic


class TestCreateTopic(unittest.TestCase):
    def test_create(self):
        topics = remove_topic.remove_topic("test_topic_1")
        print(topics)
