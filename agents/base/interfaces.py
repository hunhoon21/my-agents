from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class AgentConfig(BaseModel):
    name: str
    description: str
    enabled: bool = True
    max_retries: int = 3
    timeout: float = 30.0
    config: Dict[str, Any] = {}


class AgentResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class BaseAgent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        
    @abstractmethod
    async def execute(self, **kwargs) -> AgentResult:
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        pass
    
    def get_description(self) -> str:
        return self.config.description