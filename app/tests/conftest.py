import os
import tempfile

import pytest

# Antes de importar la app: base SQLite temporal, sin Redis, con caos habilitado.
_tmpdir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"
os.environ.pop("REDIS_URL", None)
os.environ["CHAOS_ENABLED"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
