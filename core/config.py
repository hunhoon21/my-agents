import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str = ""
    password: str = ""
    database: str = ""
    type: str = "postgresql"  # postgresql, mysql, sqlite


class LLMConfig(BaseModel):
    provider: str = "openai"  # openai, anthropic, local
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7


class SystemConfig(BaseModel):
    log_level: str = "INFO"
    log_file: Optional[str] = None
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    
    
def load_config(config_path: Optional[str] = None) -> SystemConfig:
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "configs/config.yaml")
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        return SystemConfig()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    return SystemConfig(**config_data)


def get_env_config() -> Dict[str, Any]:
    return {
        "database": {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "username": os.getenv("DB_USERNAME", ""),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", ""),
            "type": os.getenv("DB_TYPE", "postgresql")
        },
        "llm": {
            "provider": os.getenv("LLM_PROVIDER", "openai"),
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "model": os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "1000")),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7"))
        },
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "log_file": os.getenv("LOG_FILE")
    }