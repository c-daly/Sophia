# Configuration System

Sophia uses a centralized configuration system that supports multiple environments, command-line overrides, and environment variables.

## Configuration Precedence

The configuration system follows a clear precedence order (highest to lowest priority):

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Environment-specific config files** (`.json`)
4. **Default values** (lowest priority)

## Environment Support

Sophia supports multiple environments through the `SOPHIA_ENV` environment variable or the `--env` CLI argument:

- `dev` (default) - Development environment
- `test` - Testing environment  
- `prod` - Production environment

Each environment loads its configuration from `config/{env}.json`.

## Usage

### Basic Usage

```python
from config.config import get_config

# Get the global config instance
config = get_config()

# Access configuration values
debug_mode = config.get("debug")
mongo_url = config.get("mongo_url")
log_level = config.get("log_level")

# Set runtime values
config.set("custom_setting", "value")

# Get all configuration
all_config = config.get_all()
```

### Environment Variables

Set these environment variables to override configuration:

- `SOPHIA_ENV` - Environment (dev/test/prod)
- `SOPHIA_DEBUG` - Debug mode (true/false)
- `SOPHIA_LOG_LEVEL` - Log level (DEBUG/INFO/WARNING/ERROR)
- `SOPHIA_MEMORY_BACKEND` - Memory backend type
- `MONGO_URL` - MongoDB connection URL
- `NEO4J_URI` - Neo4j connection URI
- `OPENAI_API_KEY` - OpenAI API key
- `MILVUS_HOST` - Milvus host
- `MILVUS_PORT` - Milvus port

### Command-Line Arguments

Use CLI arguments to override any configuration:

```bash
# Basic usage with environment
python cli_driver.py --env prod --agent conversational "Hello"

# Override specific settings
python cli_driver.py --debug --log-level DEBUG --memory enhanced "Hello"

# Override database connections
python cli_driver.py --mongo-url "mongodb://localhost:27017/custom" "Hello"

# Use custom config file
python cli_driver.py --config /path/to/custom.json "Hello"
```

### Available CLI Arguments

- `--env ENV` - Environment (dev/test/prod)
- `--config PATH` - Path to custom config JSON file
- `--debug` - Enable debug mode
- `--log-level LEVEL` - Set log level
- `--memory BACKEND` - Set memory backend
- `--mongo-url URL` - Override MongoDB URL
- `--neo4j-uri URI` - Override Neo4j URI

## Configuration Files

### Default Values

Default configuration is defined in the `Config` class:

```json
{
  "debug": false,
  "log_level": "INFO",
  "memory_backend": "standard",
  "tool_registry": [],
  "mongo_url": "mongodb://localhost:27017/sophia",
  "neo4j_uri": "bolt://localhost:7687",
  "milvus_host": "standalone",
  "milvus_port": "19530",
  "milvus_collection": "sophia"
}
```

### Environment Files

#### `config/dev.json` (Development)
```json
{
  "debug": true,
  "log_level": "DEBUG",
  "memory_backend": "standard",
  "tool_registry": [],
  "mongo_url": "mongodb://localhost:27017/sophia_dev",
  "neo4j_uri": "bolt://localhost:7687",
  "milvus_host": "localhost",
  "milvus_port": "19530",
  "milvus_collection": "sophia_dev"
}
```

#### `config/test.json` (Testing)
```json
{
  "debug": false,
  "log_level": "WARNING",
  "memory_backend": "mock",
  "tool_registry": [],
  "mongo_url": "mongodb://localhost:27017/sophia_test",
  "neo4j_uri": "bolt://localhost:7687",
  "milvus_host": "localhost",
  "milvus_port": "19530",
  "milvus_collection": "sophia_test"
}
```

#### `config/prod.json` (Production)
```json
{
  "debug": false,
  "log_level": "INFO",
  "memory_backend": "standard",
  "tool_registry": [],
  "mongo_url": "mongodb://mongodb:27017/sophia",
  "neo4j_uri": "bolt://neo4j:7687",
  "milvus_host": "milvus",
  "milvus_port": "19530",
  "milvus_collection": "sophia"
}
```

## Examples

### Switching Environments

```bash
# Development (default)
python cli_driver.py "Hello"

# Testing
SOPHIA_ENV=test python cli_driver.py "Hello"
# or
python cli_driver.py --env test "Hello"

# Production
SOPHIA_ENV=prod python cli_driver.py "Hello"
# or
python cli_driver.py --env prod "Hello"
```

### Using Environment Variables

```bash
# Override debug and log level
SOPHIA_DEBUG=true SOPHIA_LOG_LEVEL=DEBUG python cli_driver.py "Hello"

# Override database URL
MONGO_URL="mongodb://remote:27017/sophia" python cli_driver.py "Hello"
```

### Command-Line Overrides

```bash
# Override multiple settings
python cli_driver.py --debug --log-level ERROR --memory enhanced "Hello"

# Use custom config file
python cli_driver.py --config /path/to/custom.json "Hello"
```

### Custom Config File

Create a custom JSON file with your overrides:

```json
{
  "debug": true,
  "log_level": "DEBUG",
  "custom_feature": true,
  "mongo_url": "mongodb://custom:27017/db"
}
```

Then use it:

```bash
python cli_driver.py --config custom.json "Hello"
```

## Backward Compatibility

The old `config.py` interface is maintained for backward compatibility:

```python
import config

# These still work
logger = config.logger
mongo = config.mongo  
milvus = config.milvus
```

However, it's recommended to migrate to the new centralized system:

```python
import sys
from pathlib import Path

# Add the config directory to sys.path to import the config module
config_dir = Path(__file__).parent / 'config'  # Adjust path as needed
sys.path.insert(0, str(config_dir))

from config import get_config

config = get_config()
logger = config.logger
mongo_url = config.get("mongo_url")
```

## Migration Guide

To migrate existing code:

1. Replace `import config` with the new config system import pattern (see above)
2. Replace `config.logger` with `get_config().logger`
3. Replace hardcoded values with `get_config().get("key")`
4. Use environment-specific config files instead of scattered constants
5. Use environment variables or CLI arguments for runtime configuration

### Example Migration

**Before:**
```python
import config

def some_function():
    config.logger.info("Starting process")
    db_url = os.environ["MONGO_URL"]
```

**After:**
```python
import sys
from pathlib import Path

config_dir = Path(__file__).parent / 'config'  # Adjust path as needed
sys.path.insert(0, str(config_dir))
from config import get_config

def some_function():
    config = get_config()
    config.logger.info("Starting process")
    db_url = config.get("mongo_url")
```

## Testing

The configuration system includes comprehensive tests in `tests/test_config.py`. Run them with:

```bash
python -m unittest tests.test_config -v
```

## Architecture

The configuration system uses a singleton pattern to ensure consistent configuration across the application. The `Config` class:

- Loads defaults first
- Overlays environment-specific config files
- Applies environment variables
- Applies command-line overrides
- Sets up logging based on the final configuration

This ensures predictable behavior and makes it easy to understand how configuration values are determined.