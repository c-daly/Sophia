"""
Tests for the centralized configuration system.
"""

import unittest
import os
import json
import tempfile
import argparse
from unittest.mock import patch, mock_open
from pathlib import Path
import sys

# Add the config directory to sys.path to import the config module
config_dir = Path(__file__).parent.parent / 'config'
sys.path.insert(0, str(config_dir))

# Import directly from the config directory to avoid circular imports
from config import Config, get_config


class TestConfig(unittest.TestCase):
    """Tests for the Config class."""
    
    def setUp(self):
        """Reset config singleton before each test."""
        Config._instance = None
        Config._initialized = False
    
    def test_singleton_behavior(self):
        """Test that Config is a singleton."""
        config1 = Config()
        config2 = Config()
        self.assertIs(config1, config2)
    
    def test_default_configuration(self):
        """Test that default configuration values are loaded."""
        # Mock argparse to return empty args and mock file system
        with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
            mock_parse.return_value = (argparse.Namespace(
                env=None, config=None, memory=None, debug=None,
                log_level=None, mongo_url=None, neo4j_uri=None
            ), [])
            
            # Mock the file path so no config file is found
            with patch('pathlib.Path.exists', return_value=False):
                config = Config()
                
                # Check default values
                self.assertEqual(config.get("debug"), False)
                self.assertEqual(config.get("log_level"), "INFO")
                self.assertEqual(config.get("memory_backend"), "standard")
                self.assertEqual(config.get("mongo_url"), "mongodb://localhost:27017/sophia")
                self.assertEqual(config.get("neo4j_uri"), "bolt://localhost:7687")
    
    def test_environment_variables(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "SOPHIA_ENV": "test",
            "SOPHIA_DEBUG": "true",
            "SOPHIA_LOG_LEVEL": "DEBUG",
            "MONGO_URL": "mongodb://test:27017/test_db",
            "NEO4J_URI": "bolt://test:7687",
            "OPENAI_API_KEY": "test-key-123"
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
                mock_parse.return_value = (argparse.Namespace(
                    env=None, config=None, memory=None, debug=None,
                    log_level=None, mongo_url=None, neo4j_uri=None
                ), [])
                
                config = Config()
                
                # Check environment variable values
                self.assertEqual(config.get_environment(), "test")
                self.assertEqual(config.get("debug"), True)
                self.assertEqual(config.get("log_level"), "DEBUG")
                self.assertEqual(config.get("mongo_url"), "mongodb://test:27017/test_db")
                self.assertEqual(config.get("neo4j_uri"), "bolt://test:7687")
                self.assertEqual(config.get("openai_api_key"), "test-key-123")
    
    def test_config_file_loading(self):
        """Test loading configuration from JSON files."""
        test_config = {
            "debug": True,
            "log_level": "WARNING",
            "custom_setting": "test_value"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test.json"
            with open(config_file, "w") as f:
                json.dump(test_config, f)
            
            with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
                mock_parse.return_value = (argparse.Namespace(
                    env="test", config=None, memory=None, debug=None,
                    log_level=None, mongo_url=None, neo4j_uri=None
                ), [])
                
                with patch('pathlib.Path.__new__') as mock_path:
                    mock_instance = mock_path.return_value
                    mock_instance.parent = Path(temp_dir)
                    
                    config = Config()
                    
                    # Check config file values
                    self.assertEqual(config.get("custom_setting"), "test_value")
    
    def test_cli_argument_overrides(self):
        """Test that CLI arguments override other configuration sources."""
        env_vars = {
            "SOPHIA_DEBUG": "false",
            "SOPHIA_LOG_LEVEL": "INFO",
            "MONGO_URL": "mongodb://env:27017/env_db"
        }
        
        cli_args = argparse.Namespace(
            env="prod",
            config=None,
            memory="enhanced",
            debug=True,
            log_level="ERROR",
            mongo_url="mongodb://cli:27017/cli_db",
            neo4j_uri="bolt://cli:7687"
        )
        
        with patch.dict(os.environ, env_vars):
            with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
                mock_parse.return_value = (cli_args, [])
                
                config = Config()
                
                # CLI args should override env vars and defaults
                self.assertEqual(config.get_environment(), "prod")
                self.assertEqual(config.get("debug"), True)  # CLI override
                self.assertEqual(config.get("log_level"), "ERROR")  # CLI override
                self.assertEqual(config.get("memory_backend"), "enhanced")  # CLI override
                self.assertEqual(config.get("mongo_url"), "mongodb://cli:27017/cli_db")  # CLI override
                self.assertEqual(config.get("neo4j_uri"), "bolt://cli:7687")  # CLI override
    
    def test_precedence_order(self):
        """Test the complete precedence order: CLI > Env > Config File > Defaults."""
        # Set up environment variable
        env_vars = {"SOPHIA_DEBUG": "true"}
        
        # Set up config file
        test_config = {"debug": False, "custom_setting": "from_file"}
        
        # Set up CLI args
        cli_args = argparse.Namespace(
            env="test", config=None, memory=None, debug=True,
            log_level="DEBUG", mongo_url=None, neo4j_uri=None
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test.json"
            with open(config_file, "w") as f:
                json.dump(test_config, f)
            
            with patch.dict(os.environ, env_vars):
                with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
                    mock_parse.return_value = (cli_args, [])
                    
                    with patch('pathlib.Path.__new__') as mock_path:
                        mock_instance = mock_path.return_value
                        mock_instance.parent = Path(temp_dir)
                        
                        config = Config()
                        
                        # CLI should win (debug=True from CLI vs false from env/file)
                        self.assertEqual(config.get("debug"), True)
                        # Config file value should be present when no override
                        self.assertEqual(config.get("custom_setting"), "from_file")
                        # CLI should win for log_level
                        self.assertEqual(config.get("log_level"), "DEBUG")
                        # Default should be used when nothing else specified
                        self.assertEqual(config.get("memory_backend"), "standard")
    
    def test_custom_config_file_override(self):
        """Test loading a custom config file via CLI argument."""
        base_config = {"debug": False}
        override_config = {"debug": True, "custom_override": "test"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            base_file = Path(temp_dir) / "dev.json"
            override_file = Path(temp_dir) / "override.json"
            
            with open(base_file, "w") as f:
                json.dump(base_config, f)
            with open(override_file, "w") as f:
                json.dump(override_config, f)
            
            cli_args = argparse.Namespace(
                env="dev", config=str(override_file), memory=None, debug=None,
                log_level=None, mongo_url=None, neo4j_uri=None
            )
            
            with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
                mock_parse.return_value = (cli_args, [])
                
                with patch('pathlib.Path.__new__') as mock_path:
                    mock_instance = mock_path.return_value
                    mock_instance.parent = Path(temp_dir)
                    
                    config = Config()
                    
                    # Override file should win
                    self.assertEqual(config.get("debug"), True)
                    self.assertEqual(config.get("custom_override"), "test")
    
    def test_get_config_function(self):
        """Test the get_config function."""
        with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
            mock_parse.return_value = (argparse.Namespace(
                env=None, config=None, memory=None, debug=None,
                log_level=None, mongo_url=None, neo4j_uri=None
            ), [])
            
            config1 = get_config()
            config2 = get_config()
            
            # Should return the same instance
            self.assertIs(config1, config2)
    
    def test_set_and_get_methods(self):
        """Test the set and get methods."""
        with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
            mock_parse.return_value = (argparse.Namespace(
                env=None, config=None, memory=None, debug=None,
                log_level=None, mongo_url=None, neo4j_uri=None
            ), [])
            
            config = Config()
            
            # Test setting and getting a custom value
            config.set("test_key", "test_value")
            self.assertEqual(config.get("test_key"), "test_value")
            
            # Test default value
            self.assertEqual(config.get("nonexistent_key", "default"), "default")
    
    def test_get_all_method(self):
        """Test the get_all method."""
        with patch('argparse.ArgumentParser.parse_known_args') as mock_parse:
            mock_parse.return_value = (argparse.Namespace(
                env=None, config=None, memory=None, debug=None,
                log_level=None, mongo_url=None, neo4j_uri=None
            ), [])
            
            config = Config()
            all_config = config.get_all()
            
            # Should contain default values
            self.assertIn("debug", all_config)
            self.assertIn("log_level", all_config)
            self.assertIn("memory_backend", all_config)
            
            # Should be a copy, not the original
            all_config["test"] = "modified"
            self.assertNotIn("test", config.config)


if __name__ == "__main__":
    unittest.main()