import asyncio
import time
from typing import Any, Dict, Optional

from .interfaces import BaseAgent, AgentResult, AgentConfig
from core.logging import get_logger


class Agent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger = get_logger(f"agent.{self.name}")
        
    async def run(self, **kwargs) -> AgentResult:
        if not self.config.enabled:
            return AgentResult(
                success=False, 
                error="Agent is disabled"
            )
            
        if not self.validate_config():
            return AgentResult(
                success=False, 
                error="Invalid configuration"
            )
            
        start_time = time.time()
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.info(f"Executing {self.name} (attempt {attempt + 1})")
                
                result = await asyncio.wait_for(
                    self.execute(**kwargs),
                    timeout=self.config.timeout
                )
                
                execution_time = time.time() - start_time
                result.execution_time = execution_time
                
                if result.success:
                    self.logger.info(f"Agent {self.name} completed successfully")
                    return result
                else:
                    self.logger.warning(f"Agent {self.name} failed: {result.error}")
                    
            except asyncio.TimeoutError:
                self.logger.error(f"Agent {self.name} timed out")
                return AgentResult(
                    success=False,
                    error="Execution timeout",
                    execution_time=time.time() - start_time
                )
            except Exception as e:
                self.logger.error(f"Agent {self.name} error: {e}")
                if attempt == self.config.max_retries - 1:
                    return AgentResult(
                        success=False,
                        error=str(e),
                        execution_time=time.time() - start_time
                    )
                    
        return AgentResult(
            success=False,
            error="Max retries exceeded",
            execution_time=time.time() - start_time
        )