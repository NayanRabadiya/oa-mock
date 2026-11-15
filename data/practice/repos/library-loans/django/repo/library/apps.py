import json
import os
import sys

from django.apps import AppConfig


class LibraryConfig(AppConfig):
    name = "library"

    def ready(self):
        # `runserver` starts with the sample data; the tests load their own
        if "runserver" in sys.argv:
            from . import store
            with open(os.path.join(os.path.dirname(__file__), "data", "seed.json"), encoding="utf-8") as f:
                store.reset(json.load(f))
