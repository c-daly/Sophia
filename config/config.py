import argparse
import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """
    Centralized configuration management system for Sophia.
    
    Supports configuration loading with the following precedence order:
    1. Command-line arguments (highest priority)
    2. Environment variables
    3. Environment-specific config files (.json)
    4. Default values (lowest priority)
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, args=None):
        if self._initialized:
            return
            
        self.args = args or self._parse_args()
        self.env = self.args.env or os.getenv("SOPHIA_ENV", "dev")
        self.config = self._load_defaults()
        self._load_config_file()
        self._load_env_variables()
        self._apply_overrides()
        self._setup_logging()
        
        self._initialized = True

    def _parse_args(self):
        """Parse command line arguments. Can be overridden externally."""
        parser = argparse.ArgumentParser(add_help=False)  # Don't conflict with main parser
        parser.add_argument("--env", type=str, help="Environment (dev/test/prod)")
        parser.add_argument("--config", type=str, help="Path to config override JSON")
        parser.add_argument("--memory", type=str, help="Override memory backend")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        parser.add_argument("--log-level", type=str, help="Override log level")
        parser.add_argument("--mongo-url", type=str, help="Override MongoDB URL")
        parser.add_argument("--neo4j-uri", type=str, help="Override Neo4j URI")
        
        # Parse only known args to avoid conflicts with main application
        args, _ = parser.parse_known_args()
        return args

    def _load_defaults(self):
        """Load default configuration values."""
        return {
            "debug": False,
            "log_level": "INFO",
            "memory_backend": "standard",
            "tool_registry": [],
            "mongo_url": "mongodb://localhost:27017/sophia",
            "neo4j_uri": "bolt://localhost:7687",
            "milvus_host": "standalone",
            "milvus_port": "19530",
            "milvus_collection": "sophia"
        }

    def _load_config_file(self):
        """Load configuration from environment-specific JSON file."""
        base_config_path = Path(__file__).parent / f"{self.env}.json"
        
        if base_config_path.exists():
            try:
                with open(base_config_path, "r") as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config file {base_config_path}: {e}")

    def _load_env_variables(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "SOPHIA_DEBUG": ("debug", lambda x: x.lower() in ["true", "1", "yes"]),
            "SOPHIA_LOG_LEVEL": ("log_level", str),
            "SOPHIA_MEMORY_BACKEND": ("memory_backend", str),
            "MONGO_URL": ("mongo_url", str),
            "NEO4J_URI": ("neo4j_uri", str),
            "OPENAI_API_KEY": ("openai_api_key", str),
            "MILVUS_HOST": ("milvus_host", str),
            "MILVUS_PORT": ("milvus_port", str),
        }
        
        for env_key, (config_key, converter) in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                try:
                    self.config[config_key] = converter(env_value)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid value for {env_key}: {env_value} ({e})")

    def _apply_overrides(self):
        """Apply command-line argument overrides."""
        override_mappings = {
            "memory": "memory_backend", 
            "log_level": "log_level",
            "mongo_url": "mongo_url",
            "neo4j_uri": "neo4j_uri"
        }
        
        # Handle debug separately since it's a boolean flag
        if hasattr(self.args, 'debug') and self.args.debug:
            self.config["debug"] = True
        
        for arg_key, config_key in override_mappings.items():
            value = getattr(self.args, arg_key.replace("-", "_"), None)
            if value is not None:
                self.config[config_key] = value
        
        # Handle custom config file override
        if self.args.config:
            try:
                with open(self.args.config, "r") as f:
                    override_config = json.load(f)
                    self.config.update(override_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load override config {self.args.config}: {e}")

    def _setup_logging(self):
        """Setup logging based on configuration."""
        log_level = getattr(logging, self.config.get("log_level", "INFO").upper(), logging.INFO)
        
        # Create logger instance
        self.logger = logging.getLogger('sophia')
        
        # Clear any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # Create and configure handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(log_level)
        
        # Set debug mode if enabled
        if self.config.get("debug"):
            self.logger.setLevel(logging.DEBUG)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value at runtime.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config.copy()
    
    def get_environment(self) -> str:
        """Get the current environment."""
        return self.env


# Create global config instance
def get_config(args=None) -> Config:
    """Get the global configuration instance."""
    return Config(args)


# Maintain backward compatibility
config = get_config()

