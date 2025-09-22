import datetime
import uuid
from typing import Optional

from pymongo import MongoClient
from tapipy.tapis import Tapis

from src.database.rules_engine.config import Config
from src.database.rules_engine.exceptions import (
    RuleEngineError,
    RuleNotFoundError,
    RuleValidationError,
)
from src.database.rules_engine.rules_engine_entity import Rule
from src.validator import Validator


class RuleEngineClient:
    def __init__(
        self,
        tapis_url: str = None,
        tapis_user: str = None,
        tapis_pass: str = None,
        mongo_uri: str = None,
        db_name: str = "IMT_Rules_engine_database",
    ):
        """
        Tapis session is OPTIONAL. We validate caller tokens per-request in the API layer.
        If TAPIS_USER/PASS are provided (via args or Config), we'll create a session;
        otherwise we skip it and rely on `claims` passed into methods.
        """
        # Optional Tapis session (only if creds provided)
        u = tapis_user or getattr(Config, "TAPIS_USER", None)
        p = tapis_pass or getattr(Config, "TAPIS_PASS", None)
        self.tapis = None
        if u and p:
            self.tapis = Tapis(
                base_url=tapis_url or Config.TAPIS_URL,
                username=u,
                password=p,
            )
            try:
                self.tapis.get_tokens()
            except Exception as e:
                raise RuleEngineError(
                    f"Failed to authenticate to TAPIS with provided creds: {e}"
                ) from e

        # MongoDB connection
        uri = mongo_uri or Config.MONGO_URI
        if not uri:
            raise RuleEngineError("`mongo_uri` must be provided")
        self.db = MongoClient(uri)[db_name]

    # ---------------- CRUD ----------------

    def create_rule(self, rule_data: dict, claims: Optional[dict] = None) -> str:
        """
        Insert a rule. Does NOT store raw tokens.
        Uses `claims` (validated by API) to stamp TAPIS_UUID and Tapis_UserName.
        """
        try:
            # add error_type here
            Validator.validate(rule_data, "dict", error_type=RuleValidationError)

            # and here
            Validator.validate_dict(
                rule_data,
                keys_mandatory=["CI", "Type", "Services", "Data_Rules"],
                keys_mandatory_types=["str", "str", "list", "list"],
                error_type=RuleValidationError,
            )
        except ValueError as ve:
            # keep this in case your validator raises ValueError elsewhere
            raise RuleValidationError(str(ve)) from ve

        if rule_data.get("Type") not in ("data", "model"):
            raise RuleValidationError("`Type` must be 'data' or 'model'")

        data = rule_data.copy()

        token_claims = claims or {}
        if not token_claims and self.tapis and getattr(self.tapis, "access_token", None):
            token_claims = getattr(self.tapis.access_token, "claims", {}) or {}

        data["TAPIS_UUID"] = token_claims.get("sub")
        data["Tapis_UserName"] = token_claims.get("tapis/username")

        data["Rule_UUID"] = str(uuid.uuid4())
        data["Active_From"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        data.setdefault("Active_To", None)

        self.db.user_rules.insert_one(data)
        return data["Rule_UUID"]

    def list_rules(self, filter_query: dict = None, claims: Optional[dict] = None) -> list[Rule]:
        """
        Return rules; optionally scoped to the caller (by TAPIS_UUID) when claims provided.
        Cleans legacy fields and provides safe defaults for required model fields.
        """
        q = filter_query.copy() if filter_query else {}
        if claims and claims.get("sub"):
            q.setdefault("TAPIS_UUID", claims["sub"])

        cursor = self.db.user_rules.find(q)
        results: list[Rule] = []
        for doc in cursor:
            doc.pop("_id", None)
            doc.pop("Model_Rules", None)
            doc.setdefault("Active_To", None)
            results.append(Rule(**doc))
        return results

    def get_rule(self, rule_uuid: str, claims: Optional[dict] = None) -> Rule:
        """
        Fetch one rule by UUID; optionally scoped by TAPIS_UUID if claims provided.
        """
        q = {"Rule_UUID": rule_uuid}
        if claims and claims.get("sub"):
            q["TAPIS_UUID"] = claims["sub"]

        doc = self.db.user_rules.find_one(q)
        if not doc:
            raise RuleNotFoundError(f"Rule {rule_uuid} not found")

        doc.pop("_id", None)
        doc.pop("Model_Rules", None)
        doc.setdefault("Active_To", None)

        return Rule(**doc)

    def update_rule(self, rule_uuid: str, updates: dict, claims: Optional[dict] = None) -> None:
        """
        Update fields on a rule; optionally enforce ownership via TAPIS_UUID from claims.
        """
        q = {"Rule_UUID": rule_uuid}
        if claims and claims.get("sub"):
            q["TAPIS_UUID"] = claims["sub"]

        res = self.db.user_rules.update_one(q, {"$set": updates})
        if res.matched_count == 0:
            raise RuleNotFoundError(f"Rule {rule_uuid} not found")

    def delete_rule(self, rule_uuid: str, claims: Optional[dict] = None) -> None:
        """
        Delete a rule; optionally enforce ownership via TAPIS_UUID from claims.
        """
        q = {"Rule_UUID": rule_uuid}
        if claims and claims.get("sub"):
            q["TAPIS_UUID"] = claims["sub"]

        res = self.db.user_rules.delete_one(q)
        if res.deleted_count == 0:
            raise RuleNotFoundError(f"Rule {rule_uuid} not found")