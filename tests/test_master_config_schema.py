import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

jsonschema = pytest.importorskip("jsonschema")
from jsonschema import ValidationError, validate

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "master_config.json"
SCHEMA_PATH = ROOT / "config" / "master_config.schema.json"


@pytest.fixture(scope="module")
def master_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def master_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_master_config_matches_schema(master_config, master_schema):
    """The baseline master_config.json should satisfy the schema."""
    validate(instance=master_config, schema=master_schema)


def test_schema_rejects_missing_precision_section(master_config, master_schema):
    """If precision_system section is missing, validation must fail."""
    broken_config = {**master_config}
    broken_config.pop("precision_system", None)

    with pytest.raises(ValidationError):
        validate(instance=broken_config, schema=master_schema)
