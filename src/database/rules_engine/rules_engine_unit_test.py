# TODO: Look into finding more stable test cases if any

import datetime
import unittest
import uuid
from contextlib import contextmanager
from unittest.mock import patch

from src.database.rules_engine.exceptions import (
    RuleEngineError,
    RuleNotFoundError,
    RuleValidationError,
)
from src.database.rules_engine.rules_engine_client import RuleEngineClient
from src.database.rules_engine.rules_engine_entity import Rule


class DummyToken:
    def __init__(self):
        self.access_token = "fake-token"
        self.claims = {"sub": "fake-uuid", "tapis/username": "alice"}


class DummyTapis:
    def __init__(self, base_url=None, username=None, password=None):
        pass

    def get_tokens(self):
        # Stubbing authentication call
        return None

    @property
    def access_token(self):
        return DummyToken()


class DummyCollection:
    def __init__(self):
        self.storage = {}

    def insert_one(self, doc):
        self.storage[doc["Rule_UUID"]] = doc.copy()

    def find(self, query=None):
        query = query or {}
        for doc in list(self.storage.values()):
            if all(doc.get(k) == v for k, v in query.items()):
                yield {**doc, "_id": None}

    def update_one(self, query, update):
        key = query.get("Rule_UUID")
        if key in self.storage:
            self.storage[key].update(update.get("$set", {}))
            return type("R", (), {"matched_count": 1})()
        return type("R", (), {"matched_count": 0})()

    def delete_one(self, query):
        key = query.get("Rule_UUID")
        if key in self.storage:
            del self.storage[key]
            return type("R", (), {"deleted_count": 1})()
        return type("R", (), {"deleted_count": 0})()


class DummyDB:
    def __init__(self):
        self.user_rules = DummyCollection()


class DummyMongoClient:
    def __init__(self, uri=None):
        self._db = DummyDB()

    def __getitem__(self, name):
        return self._db


@contextmanager
def patch_config(overrides: dict | None = None):
    """
    Patch the Config used by RuleEngineClient to avoid real env defaults.
    By default, clears TAPIS_* and MONGO_URI so tests can control behavior.
    """
    overrides = overrides or {}
    target = "src.database.rules_engine.rules_engine_client.Config"
    with patch(target) as cfg:
        cfg.TAPIS_URL = overrides.get("TAPIS_URL", "")
        cfg.TAPIS_USER = overrides.get("TAPIS_USER", "")
        cfg.TAPIS_PASS = overrides.get("TAPIS_PASS", "")
        cfg.MONGO_URI = overrides.get("MONGO_URI", "")
        yield


class TestRuleEngineClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Patch Tapis and MongoClient used inside RuleEngineClient
        cls.patcher_tapis = patch(
            "src.database.rules_engine.rules_engine_client.Tapis", DummyTapis
        )
        cls.patcher_mongo = patch(
            "src.database.rules_engine.rules_engine_client.MongoClient", DummyMongoClient
        )
        cls.patcher_tapis.start()
        cls.patcher_mongo.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher_tapis.stop()
        cls.patcher_mongo.stop()

    def make_client(self, **kwargs):
        defaults = {
            "tapis_url": "u",
            "tapis_user": "u",
            "tapis_pass": "p",
            "mongo_uri": "dummy://",
            "db_name": "IMT_Rule_Engine",
        }
        defaults.update(kwargs)
        return RuleEngineClient(**defaults)

    def test_init_variants(self):
        """
        For error cases, ensure Config.MONGO_URI is blank so __init__ must rely
        on provided args (which we omit), causing RuleEngineError.
        For success cases, pass mongo_uri explicitly and still clear Config to avoid
        accidental success via real env.
        """
        cases = [
            ({}, True),
            ({"tapis_url": "u", "tapis_user": "u", "tapis_pass": "p"}, True),
            ({"mongo_uri": "dummy://"}, False),
            (
                {
                    "tapis_url": "u",
                    "tapis_user": "u",
                    "tapis_pass": "p",
                    "mongo_uri": "dummy://",
                },
                False,
            ),
        ]
        for params, should_raise in cases:
            with self.subTest(params=params):
                with patch_config({}):  # clear Config defaults (incl. MONGO_URI)
                    if should_raise:
                        with self.assertRaises(RuleEngineError):
                            RuleEngineClient(**params)
                    else:
                        client = RuleEngineClient(**params)
                        self.assertIsInstance(client, RuleEngineClient)

    def test_create_rule_missing_fields(self):
        with patch_config({}):
            client = self.make_client()
            with self.assertRaises(RuleValidationError):
                client.create_rule({"CI": "only_one_field"})

    def test_create_and_list_rule(self):
        with patch_config({}):
            client = self.make_client()
            data = {
                "CI": "OSC",
                "Type": "data",
                "Active_From": "2024-05-06T12:00:00",
                "Active_To": None,
                "Services": ["data-label", "model-train"],
                "Data_Rules": [
                    {
                        "Folder_Path": "/fs/ess/PAS2271/Gautam/Animal_Ecology/output/old/visualized_images",
                        "Type": "count",
                        "Count": 10000,
                        "Apps": ["<TAPIS_APP_ID_1>", "<TAPIS_APP_ID_2>"],
                        "Sample_Images": True,
                        "Wait_Manual": True,
                    }
                ],
                "Model_Rules": [],
            }
            rule_uuid = client.create_rule(data)
            self.assertIsInstance(rule_uuid, str)

            rules = client.list_rules({"Rule_UUID": rule_uuid})
            self.assertEqual(len(rules), 1)
            r = rules[0]
            self.assertIsInstance(r, Rule)
            self.assertEqual(r.Rule_UUID, rule_uuid)
            datetime.datetime.fromisoformat(r.Active_From)

    def test_update_and_delete(self):
        with patch_config({}):
            client = self.make_client()
            data = {"CI": "c", "Type": "model", "Services": [], "Data_Rules": []}
            rule_uuid = client.create_rule(data)
            client.update_rule(rule_uuid, {"Active_To": "2099-01-01T00:00:00"})
            updated = client.list_rules({"Rule_UUID": rule_uuid})[0]
            self.assertEqual(updated.Active_To, "2099-01-01T00:00:00")
            client.delete_rule(rule_uuid)
            self.assertEqual(client.list_rules({"Rule_UUID": rule_uuid}), [])

    def test_update_not_found(self):
        with patch_config({}):
            client = self.make_client()
            with self.assertRaises(RuleNotFoundError):
                client.update_rule(str(uuid.uuid4()), {})

    def test_delete_not_found(self):
        with patch_config({}):
            client = self.make_client()
            with self.assertRaises(RuleNotFoundError):
                client.delete_rule(str(uuid.uuid4()))

    def test_list_empty(self):
        with patch_config({}):
            client = self.make_client()
            self.assertEqual(client.list_rules(), [])


if __name__ == "__main__":
    unittest.main()