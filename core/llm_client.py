from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
from .config import LLMConfig
from .logging import get_logger


class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = get_logger("llm_client")

        if config.provider == "openai":
            self.client = AsyncOpenAI(api_key=config.api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    async def chat_completion(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,  # type: ignore
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["max_tokens", "temperature"]
                },
            )

            content = response.choices[0].message.content
            if response.usage:
                self.logger.info(
                    f"LLM response received (tokens: {response.usage.total_tokens})"
                )
            return content or ""

        except Exception as e:
            self.logger.error(f"LLM request failed: {e}")
            raise

    async def generate_response(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any
    ) -> str:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return await self.chat_completion(messages, **kwargs)

    async def generate_comment(
        self, content: str, context: str = "", tone: str = "friendly"
    ) -> str:
        system_prompt = f"""
        네이버 블로그 이웃의 글에 댓글을 달아주는 역할입니다.
        - 톤: {tone}
        - 자연스럽고 진심이 담긴 댓글을 작성해주세요
        - 너무 길지 않게 1-2문장으로 작성
        - 이모티콘은 적절히 사용
        """

        prompt = f"""
        블로그 글 내용: {content}
        
        추가 컨텍스트: {context}
        
        위 글에 대한 적절한 댓글을 작성해주세요.
        """

        return await self.generate_response(prompt, system_prompt)

    async def generate_sql_response(
        self, query: str, schema_info: str, data_results: Optional[str] = None
    ) -> str:
        system_prompt = """
        SQL 쿼리 결과를 분석하고 사용자 친화적인 답변을 제공하는 AI입니다.
        - 데이터를 명확하게 해석
        - 트렌드나 패턴이 있다면 설명
        - 필요시 차트 생성 제안
        """

        prompt = f"""
        사용자 질문: {query}
        데이터베이스 스키마: {schema_info}
        """

        if data_results:
            prompt += f"\n쿼리 결과:\n{data_results}"

        return await self.generate_response(prompt, system_prompt)
