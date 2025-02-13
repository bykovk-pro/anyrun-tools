# Configuration

## Basic configuration

The minimal configuration requires only an API key:

```python
from anyrun import AnyRunClient

client = AnyRunClient(api_key="your-api-key")
```

## Advanced configuration

You can customize various aspects of the client:

```python
from anyrun import AnyRunClient

client = AnyRunClient(
    # API settings
    api_key="your-api-key",
    sandbox_version="v1",
    ti_lookup_version="v1",
    ti_yara_version="v1",
    base_url="https://api.any.run",

    # HTTP settings
    timeout=30,
    verify_ssl=True,
    user_agent="your-app/1.0",
    headers={"X-Custom": "value"},
    proxies={
        "http": "http://proxy:8080",
        "https": "http://proxy:8080"
    },

    # Cache settings
    cache_enabled=True,
    cache_ttl=300,
    cache_backend="redis",
    cache_config={
        "url": "redis://localhost:6379",
        "password": "secret"
    },

    # Retry settings
    retry_enabled=True,
    retry_count=3,
    retry_delay=1.0,
    retry_on_status=[408, 429, 500, 502, 503, 504],

    # Rate limiting
    rate_limit_enabled=True,
    rate_limit_strategy="wait",  # or "error"

    # Logging
    log_level="INFO",
    log_format="[{time}] {level} - {message}"
)
```

## Environment variables

You can also configure the client using environment variables:

```bash
# API settings
export ANYRUN_API_KEY="your-api-key"
export ANYRUN_API_VERSION="v1"
export ANYRUN_BASE_URL="https://api.any.run"

# HTTP settings
export ANYRUN_TIMEOUT=30
export ANYRUN_VERIFY_SSL=true
export ANYRUN_USER_AGENT="your-app/1.0"
export ANYRUN_PROXY_HTTP="http://proxy:8080"
export ANYRUN_PROXY_HTTPS="http://proxy:8080"

# Cache settings
export ANYRUN_CACHE_ENABLED=true
export ANYRUN_CACHE_TTL=300
export ANYRUN_CACHE_BACKEND="redis"
export ANYRUN_REDIS_URL="redis://localhost:6379"
export ANYRUN_REDIS_PASSWORD="secret"

# Retry settings
export ANYRUN_RETRY_ENABLED=true
export ANYRUN_RETRY_COUNT=3
export ANYRUN_RETRY_DELAY=1.0

# Rate limiting
export ANYRUN_RATE_LIMIT_ENABLED=true
export ANYRUN_RATE_LIMIT_STRATEGY="wait"

# Logging
export ANYRUN_LOG_LEVEL="INFO"
export ANYRUN_LOG_FORMAT="[{time}] {level} - {message}"
```

## Configuration file

You can also create a configuration file `anyrun.toml`:

```toml
[api]
key = "your-api-key"
version = "v1"
base_url = "https://api.any.run"

[http]
timeout = 30
verify_ssl = true
user_agent = "your-app/1.0"

[http.proxies]
http = "http://proxy:8080"
https = "http://proxy:8080"

[cache]
enabled = true
ttl = 300
backend = "redis"

[cache.redis]
url = "redis://localhost:6379"
password = "secret"

[retry]
enabled = true
count = 3
delay = 1.0
status_codes = [408, 429, 500, 502, 503, 504]

[rate_limit]
enabled = true
strategy = "wait"

[logging]
level = "INFO"
format = "[{time}] {level} - {message}"
```

## Configuration priority

Configuration values are loaded in the following order (later values override earlier ones):

1. Default values
2. Configuration file
3. Environment variables
4. Constructor arguments

## Next steps

- [Quick start guide](quickstart.md)
- [API reference](https://any.run/api-documentation/)
- [Examples](https://github.com/bykovk-pro/anyrun-tools/tree/main/examples)
