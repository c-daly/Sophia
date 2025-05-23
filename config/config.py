import argparse
import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.args = self._parse_args()
        self.env = self.args.env or os.getenv("SOPHIA_ENV", "dev")
        self.config = self._load_config_file()
        self._apply_overrides()

    def _parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--env", type=str, help="Environment (dev/prod/test)")
        parser.add_argument("--config", type=str, help="Path to config override JSON")
        parser.add_argument("--memory", type=str, help="Override memory backend")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        return parser.parse_args()

    def _load_config_file(self):
        base_config_path = Path(__file__).parent / f"{self.env}.json"
        config = {}
        if base_config_path.exists():
            with open(base_config_path, "r") as f:
                config = json.load(f)
        return config

    def _apply_overrides(self):
        # CLI args override config file values
        for key, value in vars(self.args).items():
            if value is not None:
                self.config[key] = value

    def get(self, key, default=None):
        return self.config.get(key, default)

