import asyncio
import click
from typing import Dict, Any

from core.config import load_config
from core.logging import setup_logging, get_logger


@click.command()
@click.option("--agent", "-a", required=True, help="에이전트 이름")
@click.option("--config", "-c", help="설정 파일 경로")
@click.option("--params", "-p", help="에이전트 파라미터 (JSON 형태)")
@click.option("--log-level", default="INFO", help="로그 레벨")
def main(agent: str, config: str, params: str, log_level: str) -> None:
    """에이전트 실행 도구"""

    # 로깅 설정
    setup_logging(level=log_level)
    logger = get_logger("runner")

    logger.info(f"Starting agent: {agent}")

    try:
        # 설정 로드
        system_config = load_config(config)
        logger.info("Configuration loaded")

        # 파라미터 파싱
        agent_params = {}
        if params:
            import json

            agent_params = json.loads(params)

        # 에이전트 동적 로드 및 실행
        asyncio.run(run_agent(agent, system_config, agent_params))

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise click.ClickException(str(e))


async def run_agent(agent_name: str, config: Any, params: Dict[str, Any]) -> Any:
    """에이전트 실행 함수"""
    logger = get_logger("runner")

    try:
        # 에이전트 모듈 동적 임포트
        module = __import__(f"agents.{agent_name}.agent", fromlist=[""])

        # 에이전트 클래스 찾기 (관례상 Agent 클래스)
        agent_class = getattr(module, "Agent")

        # 에이전트 설정 생성
        from agents.base.interfaces import AgentConfig

        agent_config = AgentConfig(
            name=agent_name, description=f"{agent_name} agent", **params
        )

        # 에이전트 인스턴스 생성 및 실행
        agent = agent_class(agent_config)
        result = await agent.run(**params)

        if result.success:
            logger.info(f"Agent completed successfully: {result.data}")
        else:
            logger.error(f"Agent failed: {result.error}")

        return result

    except ImportError as e:
        raise ValueError(f"Agent '{agent_name}' not found: {e}")
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        raise


if __name__ == "__main__":
    main()
