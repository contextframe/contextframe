"""Configuration for HTTP transport."""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HTTPTransportConfig:
    """Configuration for HTTP transport.

    This configuration can be loaded from environment variables,
    JSON files, or passed directly.
    """

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1

    # CORS settings
    cors_enabled: bool = True
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    cors_credentials: bool = True
    cors_methods: list[str] = field(default_factory=lambda: ["*"])
    cors_headers: list[str] = field(default_factory=lambda: ["*"])

    # Authentication settings
    auth_enabled: bool = False
    auth_secret_key: str | None = None
    auth_algorithm: str = "HS256"
    auth_issuer: str = "contextframe-mcp"
    auth_audience: str = "contextframe-mcp"
    auth_token_expire_minutes: int = 30

    # Rate limiting settings
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10

    # SSL/TLS settings
    ssl_enabled: bool = False
    ssl_cert: str | None = None
    ssl_key: str | None = None

    # SSE settings
    sse_max_connections: int = 1000
    sse_keepalive_interval: int = 25  # seconds
    sse_max_age_seconds: int = 3600  # 1 hour

    # Session settings
    session_enabled: bool = True
    session_secret_key: str | None = None
    session_max_age: int = 86400  # 24 hours

    # Performance settings
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    request_timeout: int = 300  # 5 minutes

    @classmethod
    def from_env(cls) -> "HTTPTransportConfig":
        """Load configuration from environment variables.

        Environment variable format: MCP_HTTP_<SETTING_NAME>
        For nested settings use double underscore: MCP_HTTP_CORS__ORIGINS
        """
        config = cls()

        # Helper to get env var with prefix
        def get_env(key: str, default: Any = None) -> Any:
            return os.environ.get(f"MCP_HTTP_{key}", default)

        # Server settings
        config.host = get_env("HOST", config.host)
        config.port = int(get_env("PORT", config.port))
        config.workers = int(get_env("WORKERS", config.workers))

        # CORS settings
        config.cors_enabled = get_env("CORS_ENABLED", "true").lower() == "true"
        cors_origins = get_env("CORS_ORIGINS")
        if cors_origins:
            config.cors_origins = cors_origins.split(",")

        # Authentication settings
        config.auth_enabled = get_env("AUTH_ENABLED", "false").lower() == "true"
        config.auth_secret_key = get_env("AUTH_SECRET_KEY")
        config.auth_issuer = get_env("AUTH_ISSUER", config.auth_issuer)
        config.auth_audience = get_env("AUTH_AUDIENCE", config.auth_audience)

        # Rate limiting
        config.rate_limit_enabled = (
            get_env("RATE_LIMIT_ENABLED", "true").lower() == "true"
        )
        config.rate_limit_requests_per_minute = int(
            get_env(
                "RATE_LIMIT_REQUESTS_PER_MINUTE", config.rate_limit_requests_per_minute
            )
        )

        # SSL settings
        config.ssl_enabled = get_env("SSL_ENABLED", "false").lower() == "true"
        config.ssl_cert = get_env("SSL_CERT")
        config.ssl_key = get_env("SSL_KEY")

        # Session settings
        config.session_enabled = get_env("SESSION_ENABLED", "true").lower() == "true"
        config.session_secret_key = get_env("SESSION_SECRET_KEY")

        return config

    @classmethod
    def from_file(cls, path: str) -> "HTTPTransportConfig":
        """Load configuration from JSON file."""
        with open(path) as f:
            data = json.load(f)

        # Convert nested dicts to flat attributes
        config = cls()

        # Server settings
        if "server" in data:
            config.host = data["server"].get("host", config.host)
            config.port = data["server"].get("port", config.port)
            config.workers = data["server"].get("workers", config.workers)

        # CORS settings
        if "cors" in data:
            config.cors_enabled = data["cors"].get("enabled", config.cors_enabled)
            config.cors_origins = data["cors"].get("origins", config.cors_origins)
            config.cors_credentials = data["cors"].get(
                "credentials", config.cors_credentials
            )

        # Authentication settings
        if "auth" in data:
            config.auth_enabled = data["auth"].get("enabled", config.auth_enabled)
            config.auth_secret_key = data["auth"].get("secret_key")
            config.auth_issuer = data["auth"].get("issuer", config.auth_issuer)
            config.auth_audience = data["auth"].get("audience", config.auth_audience)

        # Rate limiting settings
        if "rate_limit" in data:
            config.rate_limit_enabled = data["rate_limit"].get(
                "enabled", config.rate_limit_enabled
            )
            config.rate_limit_requests_per_minute = data["rate_limit"].get(
                "requests_per_minute", config.rate_limit_requests_per_minute
            )
            config.rate_limit_burst = data["rate_limit"].get(
                "burst", config.rate_limit_burst
            )

        # SSL settings
        if "ssl" in data:
            config.ssl_enabled = data["ssl"].get("enabled", config.ssl_enabled)
            config.ssl_cert = data["ssl"].get("cert")
            config.ssl_key = data["ssl"].get("key")

        # SSE settings
        if "sse" in data:
            config.sse_max_connections = data["sse"].get(
                "max_connections", config.sse_max_connections
            )
            config.sse_keepalive_interval = data["sse"].get(
                "keepalive_interval", config.sse_keepalive_interval
            )

        # Session settings
        if "session" in data:
            config.session_enabled = data["session"].get(
                "enabled", config.session_enabled
            )
            config.session_secret_key = data["session"].get("secret_key")
            config.session_max_age = data["session"].get(
                "max_age", config.session_max_age
            )

        return config

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Validate port
        if not 1 <= self.port <= 65535:
            errors.append(f"Invalid port number: {self.port}")

        # Validate auth settings
        if self.auth_enabled and not self.auth_secret_key:
            errors.append("Authentication enabled but no secret key provided")

        # Validate SSL settings
        if self.ssl_enabled:
            if not self.ssl_cert:
                errors.append("SSL enabled but no certificate provided")
            if not self.ssl_key:
                errors.append("SSL enabled but no key provided")

        # Validate session settings
        if self.session_enabled and not self.session_secret_key:
            errors.append("Sessions enabled but no secret key provided")

        # Validate rate limiting
        if self.rate_limit_requests_per_minute < 1:
            errors.append("Rate limit requests per minute must be at least 1")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "server": {
                "host": self.host,
                "port": self.port,
                "workers": self.workers,
            },
            "cors": {
                "enabled": self.cors_enabled,
                "origins": self.cors_origins,
                "credentials": self.cors_credentials,
                "methods": self.cors_methods,
                "headers": self.cors_headers,
            },
            "auth": {
                "enabled": self.auth_enabled,
                "algorithm": self.auth_algorithm,
                "issuer": self.auth_issuer,
                "audience": self.auth_audience,
                "token_expire_minutes": self.auth_token_expire_minutes,
            },
            "rate_limit": {
                "enabled": self.rate_limit_enabled,
                "requests_per_minute": self.rate_limit_requests_per_minute,
                "burst": self.rate_limit_burst,
            },
            "ssl": {
                "enabled": self.ssl_enabled,
                "cert": self.ssl_cert,
                "key": self.ssl_key,
            },
            "sse": {
                "max_connections": self.sse_max_connections,
                "keepalive_interval": self.sse_keepalive_interval,
                "max_age_seconds": self.sse_max_age_seconds,
            },
            "session": {
                "enabled": self.session_enabled,
                "max_age": self.session_max_age,
            },
            "performance": {
                "max_request_size": self.max_request_size,
                "request_timeout": self.request_timeout,
            },
        }


# Example configuration file format:
EXAMPLE_CONFIG = """
{
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "workers": 1
    },
    "cors": {
        "enabled": true,
        "origins": ["https://example.com", "http://localhost:3000"],
        "credentials": true
    },
    "auth": {
        "enabled": true,
        "secret_key": "your-secret-key-here",
        "issuer": "contextframe-mcp",
        "audience": "contextframe-mcp"
    },
    "rate_limit": {
        "enabled": true,
        "requests_per_minute": 60,
        "burst": 10
    },
    "ssl": {
        "enabled": false,
        "cert": "/path/to/cert.pem",
        "key": "/path/to/key.pem"
    },
    "sse": {
        "max_connections": 1000,
        "keepalive_interval": 25
    },
    "session": {
        "enabled": true,
        "secret_key": "your-session-secret",
        "max_age": 86400
    }
}
"""
