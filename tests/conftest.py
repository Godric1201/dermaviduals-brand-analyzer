import importlib
import sys
import types
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _install_fake_analyzer():
    fake_analyzer = types.ModuleType("analyzer")

    def ask_ai(*args, **kwargs):
        raise AssertionError("OpenAI API should not be called in unit tests")

    fake_analyzer.ask_ai = ask_ai
    sys.modules["analyzer"] = fake_analyzer


def import_without_real_analyzer(module_name):
    _install_fake_analyzer()
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


@pytest.fixture(scope="session")
def prompt_generator_module():
    return import_without_real_analyzer("prompt_generator")


@pytest.fixture(scope="session")
def content_generator_module():
    return import_without_real_analyzer("content_generator")
