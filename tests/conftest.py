import importlib
import sys
import types
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _install_fake_analyzer():
    fake_analyzer = types.ModuleType("geo_audit.analyzer")

    def ask_ai(*args, **kwargs):
        raise AssertionError("OpenAI API should not be called in unit tests")

    fake_analyzer.ask_ai = ask_ai
    sys.modules["geo_audit.analyzer"] = fake_analyzer


def import_without_real_analyzer(module_name):
    _install_fake_analyzer()
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


@pytest.fixture(scope="session")
def prompt_generator_module():
    return import_without_real_analyzer("geo_audit.prompt_generator")


@pytest.fixture(scope="session")
def content_generator_module():
    return import_without_real_analyzer("geo_audit.content_generator")
