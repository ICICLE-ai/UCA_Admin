# UCA_Admin


## Rules Engine

This repo implements the **Admin-side backend** for the UCA Rules Engine.  
It exposes a FastAPI service that handles rule CRUD operations, connects to MongoDB, and validates requests via Tapis tokens.

> This is the **admin/backend repo**. End-users should interact with the lightweight [UCA Client package](https://github.com/ICICLE-ai/UCA) instead of calling these APIs directly.

---

## Configuration

All runtime config comes from `config.yaml` (mounted into the container or used locally).

**Example `config.yaml`:**
```yaml
# MongoDB creds
mongo_uri: "mongodb+srv://<USER>:<PASS>@<CLUSTER>/"
rules_db:  "IMT_Rules_engine_database"

# Tapis
tapis_url: "https://tacc.tapis.io"
```

Note: At the moment, MongoDB Atlas is hosted under Gautam’s (molakalmuru.1@osu.edu)personal account (Contact him for adding the tester to the ongoing project). This setup can be reused for development and testing, but for long-term stability we should transition to an ICICLE-managed MongoDB service (e.g., Atlas under the org account, or Mongo pods in Kubernetes).

---
### Running with Docker

**Build the image:**

```bash
docker build -t uca-rules-api .
```

**Run the container (mount your config):**
```bash
docker run --rm -p 8081:8081 -v "$PWD/config.yaml:/app/config.yaml:ro" uca-rules-api
```
---

### TODO / Next Steps
- **MongoDB**: Currently the deployment uses Mongo Atlas under Gautam’s account. This works for testing, but eventually we need to migrate to ICICLE-managed MongoDB servers for production stability or other viable approach.

This repo should be seen as the first working version.
