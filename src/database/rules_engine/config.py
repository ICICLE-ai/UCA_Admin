import yaml

with open("config.yaml", "r") as f:  # MUST run the app from the repo root (or WORKDIR=/app in Docker)
    _cfg = yaml.safe_load(f) or {}

def _req(key: str) -> str:
    v = _cfg.get(key)
    if not v:
        raise RuntimeError(f"Missing required config key: {key}")
    return v

class Config:
    MONGO_URI  = _req("mongo_uri")
    RULES_DB   = _req("rules_db")
    TAPIS_URL  = _req("tapis_url")
    TAPIS_USER = _cfg.get("tapis_user", "")
    TAPIS_PASS = _cfg.get("tapis_pass", "")