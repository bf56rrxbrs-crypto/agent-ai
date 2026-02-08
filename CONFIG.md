# Configuration Example

This is an example configuration file for the Autonomous AI Agent.

## Usage

Copy `config.example.json` and customize it for your environment:

```bash
cp config.example.json config.json
# Edit config.json with your settings
```

## Configuration Structure

### Agent Section
- `agent_id`: Unique identifier for the agent
- `name`: Human-readable name for the agent
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `max_concurrent_tasks`: Maximum number of concurrent tasks
- `health_check_interval`: Interval in seconds for health checks
- `task_timeout`: Maximum time in seconds for a task to complete
- `enable_auto_recovery`: Enable automatic recovery from failures

### Cache Section
- `enabled`: Enable/disable caching
- `max_size`: Maximum number of items in cache
- `ttl_seconds`: Time to live for cache entries in seconds
- `strategy`: Caching strategy ("lru" or "lfu")

### Monitoring Section
- `enabled`: Enable/disable monitoring
- `metrics_interval`: Interval in seconds for collecting metrics
- `log_rotation`: Enable log file rotation
- `max_log_size_mb`: Maximum log file size in megabytes

### Integrations Section
- `enabled`: List of enabled integration IDs
- `configs`: Configuration for each integration
  - API integrations require: `base_url`, `api_key`, and optional `headers`
  - Webhook integrations require: `webhook_url` and `secret`

## Example Configuration

See `config.example.json` for a complete example with all available options.
