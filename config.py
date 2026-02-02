"""
Configuration management for RFP Automation System
Centralized configuration with environment variable support and validation
"""
import os
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field, validator
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url: str = Field(
        default="sqlite:///./data/rfp_automation.db",
        env="DATABASE_URL"
    )
    echo: bool = Field(
        default=False,
        env="DATABASE_ECHO"
    )
    pool_size: int = Field(
        default=5,
        env="DATABASE_POOL_SIZE"
    )
    max_overflow: int = Field(
        default=10,
        env="DATABASE_MAX_OVERFLOW"
    )


class LLMConfig(BaseSettings):
    """LLM configuration"""
    provider: str = Field(
        default="cerebras",
        env="LLM_PROVIDER"
    )
    api_key: str = Field(
        env="CEREBRAS_API_KEY"
    )
    model: str = Field(
        default="llama-3.3-70b",
        env="CEREBRAS_MODEL"
    )
    temperature: float = Field(
        default=0.7,
        env="LLM_TEMPERATURE"
    )
    max_tokens: int = Field(
        default=8192,
        env="LLM_MAX_TOKENS"
    )
    timeout: int = Field(
        default=120,
        env="LLM_TIMEOUT"
    )
    max_retries: int = Field(
        default=2,
        env="LLM_MAX_RETRIES"
    )


class CacheConfig(BaseSettings):
    """Cache configuration"""
    type: str = Field(
        default="memory",
        env="CACHE_TYPE"
    )
    max_size: int = Field(
        default=1000,
        env="CACHE_MAX_SIZE"
    )
    default_ttl: int = Field(
        default=3600,
        env="CACHE_DEFAULT_TTL"
    )
    redis_url: Optional[str] = Field(
        default=None,
        env="REDIS_URL"
    )


class SecurityConfig(BaseSettings):
    """Security configuration"""
    jwt_secret_key: str = Field(
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        env="JWT_ALGORITHM"
    )
    jwt_expire_minutes: int = Field(
        default=30,
        env="JWT_EXPIRE_MINUTES"
    )
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"],
        env="ALLOWED_ORIGINS"
    )
    rate_limit_calls: int = Field(
        default=100,
        env="RATE_LIMIT_CALLS"
    )
    rate_limit_period: int = Field(
        default=60,
        env="RATE_LIMIT_PERIOD"
    )


class LoggingConfig(BaseSettings):
    """Logging configuration"""
    level: LogLevel = Field(
        default=LogLevel.INFO,
        env="LOG_LEVEL"
    )
    file: Optional[str] = Field(
        default="logs/app.log",
        env="LOG_FILE"
    )
    enable_console: bool = Field(
        default=True,
        env="LOG_CONSOLE"
    )
    max_file_size: int = Field(
        default=10485760,  # 10MB
        env="LOG_MAX_FILE_SIZE"
    )
    backup_count: int = Field(
        default=5,
        env="LOG_BACKUP_COUNT"
    )


class MonitoringConfig(BaseSettings):
    """Monitoring configuration"""
    enabled: bool = Field(
        default=True,
        env="MONITORING_ENABLED"
    )
    metrics_interval: int = Field(
        default=30,
        env="METRICS_INTERVAL"
    )
    health_check_interval: int = Field(
        default=60,
        env="HEALTH_CHECK_INTERVAL"
    )
    alert_webhook: Optional[str] = Field(
        default=None,
        env="ALERT_WEBHOOK"
    )


class AppConfig(BaseSettings):
    """Main application configuration"""
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        env="ENVIRONMENT"
    )
    debug: bool = Field(
        default=False,
        env="DEBUG"
    )
    host: str = Field(
        default="0.0.0.0",
        env="HOST"
    )
    port: int = Field(
        default=8000,
        env="PORT"
    )
    workers: int = Field(
        default=1,
        env="WORKERS"
    )
    reload: bool = Field(
        default=True,
        env="RELOAD"
    )
    
    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("security")
    def validate_security(cls, v):
        """Validate security configuration"""
        if not v.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY must be set")
        return v
    
    @validator("llm")
    def validate_llm(cls, v):
        """Validate LLM configuration"""
        if not v.api_key:
            raise ValueError("CEREBRAS_API_KEY must be set")
        return v
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.security.allowed_origins, str):
            return [origin.strip() for origin in self.security.allowed_origins.split(",")]
        return self.security.allowed_origins
    
    def get_database_url(self) -> str:
        """Get database URL"""
        return self.database.url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment.value,
            "debug": self.debug,
            "host": self.host,
            "port": self.port,
            "database": self.database.dict(),
            "llm": {
                k: v for k, v in self.llm.dict().items()
                if k != "api_key"  # Don't expose API key
            },
            "cache": self.cache.dict(),
            "security": {
                k: v for k, v in self.security.dict().items()
                if k != "jwt_secret_key"  # Don't expose secret
            },
            "logging": self.logging.dict(),
            "monitoring": self.monitoring.dict()
        }


# Global configuration instance
config = AppConfig()


def load_config_from_file(config_path: str) -> AppConfig:
    """Load configuration from file"""
    if os.path.exists(config_path):
        logger.info(f"Loading configuration from: {config_path}")
        return AppConfig(_env_file=config_path)
    else:
        logger.warning(f"Configuration file not found: {config_path}")
        return config


def validate_config() -> bool:
    """Validate configuration"""
    try:
        # This will trigger pydantic validators
        config.dict()
        logger.info("Configuration validation passed")
        return True
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary for logging"""
    return {
        "environment": config.environment.value,
        "debug": config.debug,
        "database_type": "sqlite" if "sqlite" in config.database.url else "postgresql",
        "llm_provider": config.llm.provider,
        "cache_type": config.cache.type,
        "monitoring_enabled": config.monitoring.enabled,
        "log_level": config.logging.level.value
    }
