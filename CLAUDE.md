# My Agents - 고도화 아키텍처 가이드

## 🎯 프로젝트 비전
확장 가능하고 유지보수 가능한 멀티 에이전트 시스템 구축

---

## 🐍 Python 환경 관리

### uv 기반 환경 설정
```bash
# 개발 환경 설정
uv sync --extra dev --extra notebook

# 프로덕션 환경
uv sync --frozen

# VSCode 인터프리터 설정
# Command Palette → "Python: Select Interpreter" → ./.venv/bin/python 선택
```

### 의존성 관리 원칙
- **Core dependencies**: 최소한의 필수 패키지만
- **Optional dependencies**: 기능별로 그룹화 (dev, notebook, web, etc.)
- **Version pinning**: 보안 패키지는 정확한 버전 고정

---

## 🔍 코드 품질 관리

### Type Hinting 의무화
```python
from typing import Dict, List, Optional, Union, Protocol
from pydantic import BaseModel

# ✅ 모든 함수/메서드에 타입 힌트 필수
async def process_data(data: Dict[str, Any], config: AgentConfig) -> AgentResult:
    pass

# ✅ 클래스 속성도 타입 힌트
class Agent:
    name: str
    config: AgentConfig
    _client: Optional[LLMClient] = None
```

### Linting & Formatting 설정
```bash
# 설치된 도구들
uv add --dev ruff black mypy pre-commit

# 실행 순서
ruff check .          # 린팅 (import 정렬 포함)
black .               # 포맷팅
mypy .                # 타입 체킹
pytest --cov=. .      # 테스트 + 커버리지
```

### pyproject.toml 추가 설정
```toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM", "PIE"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
disallow_untyped_defs = true

[tool.coverage.run]
source = ["agents", "core"]
omit = ["tests/*", "notebooks/*"]
```

---

## 🏗️ 아키텍처 구조

### 1. 레이어드 아키텍처
```
┌─────────────────────────────────────┐
│           Presentation Layer        │  ← CLI, Web API, Jupyter
├─────────────────────────────────────┤
│           Application Layer         │  ← Agent Orchestrator, Workflows
├─────────────────────────────────────┤
│            Domain Layer             │  ← Core Business Logic, Agents
├─────────────────────────────────────┤
│         Infrastructure Layer        │  ← Database, LLM, External APIs
└─────────────────────────────────────┘
```

### 2. 확장된 디렉토리 구조
```
my-agents/
├── agents/                    # Domain Layer
│   ├── base/                  # 공통 인터페이스
│   ├── registry.py            # 에이전트 레지스트리
│   └── {agent_name}/          # 개별 에이전트
│       ├── agent.py
│       ├── config.py
│       ├── schemas.py         # Pydantic 모델
│       └── tests/
├── core/                      # Infrastructure Layer
│   ├── clients/               # 외부 서비스 클라이언트
│   ├── database/              # DB 관련
│   ├── monitoring/            # 로깅, 메트릭
│   ├── security/              # 인증, 암호화
│   └── utils/
├── workflows/                 # Application Layer
│   ├── orchestrator.py        # 워크플로우 관리
│   ├── scheduler.py           # 스케줄링
│   └── pipelines/
├── interfaces/                # Presentation Layer
│   ├── cli/
│   ├── web/                   # FastAPI
│   └── notebooks/
├── config/
│   ├── environments/          # 환경별 설정
│   └── schemas/               # 설정 스키마
└── deployment/
    ├── docker/
    ├── kubernetes/
    └── terraform/
```

### 3. 핵심 디자인 패턴

#### 플러그인 시스템
```python
# agents/registry.py
from typing import Dict, Type
from agents.base.interfaces import BaseAgent

class AgentRegistry:
    _agents: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, name: str):
        def decorator(agent_class: Type[BaseAgent]):
            cls._agents[name] = agent_class
            return agent_class
        return decorator
    
    @classmethod
    def get_agent(cls, name: str) -> Type[BaseAgent]:
        return cls._agents.get(name)

# 사용법
@AgentRegistry.register("naver_blog")
class NaverBlogAgent(BaseAgent):
    pass
```

#### 의존성 주입 (DI)
```python
# core/container.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # 설정
    config = providers.Configuration()
    
    # 클라이언트들
    llm_client = providers.Singleton(LLMClient, config=config.llm)
    db_client = providers.Singleton(DatabaseClient, config=config.database)
    
    # 서비스들
    agent_service = providers.Factory(
        AgentService,
        llm_client=llm_client,
        db_client=db_client
    )
```

---

## 🔐 보안 고려사항

### 시크릿 관리
- **개발**: `.env` 파일 (git에서 제외)
- **프로덕션**: AWS Secrets Manager, HashiCorp Vault
- **컨테이너**: Kubernetes Secrets

### 입력 검증
```python
from pydantic import BaseModel, Field, validator

class AgentInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    
    @validator('query')
    def validate_query(cls, v):
        # SQL 인젝션, XSS 방지
        if any(keyword in v.lower() for keyword in ['drop', 'delete', '<script>']):
            raise ValueError('Invalid input detected')
        return v
```

### API 보안
- Rate limiting
- API 키 인증
- CORS 설정
- 입력 sanitization

---

## 📊 모니터링 & 관찰성

### 로깅 전략
```python
# 구조화된 로깅
logger.info(
    "Agent execution completed",
    extra={
        "agent_name": agent.name,
        "execution_time": result.execution_time,
        "success": result.success,
        "user_id": user_id,
        "trace_id": trace_id
    }
)
```

### 메트릭 수집
- 에이전트별 성공/실패율
- 평균 실행 시간
- 토큰 사용량 (LLM)
- 에러율 및 에러 타입

### 헬스체크
```python
# interfaces/web/health.py
@app.get("/health")
async def health_check():
    checks = {
        "database": await db_client.health_check(),
        "llm": await llm_client.health_check(),
        "redis": await redis_client.ping()
    }
    return {"status": "healthy" if all(checks.values()) else "unhealthy"}
```

---

## 🚀 성능 최적화

### 비동기 처리
```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def agent_pool(max_concurrent: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_agent(agent, **kwargs):
        async with semaphore:
            return await agent.run(**kwargs)
    
    yield run_agent
```

### 캐싱 전략
- LLM 응답 캐싱 (Redis)
- 데이터베이스 쿼리 결과 캐싱
- 설정 정보 메모리 캐싱

### 리소스 관리
```python
# 연결 풀링
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_recycle=3600
)
```

---

## 🧪 테스팅 전략

### 테스트 레벨
1. **Unit Tests**: 개별 함수/클래스
2. **Integration Tests**: 데이터베이스, API 통합
3. **E2E Tests**: 전체 워크플로우
4. **Performance Tests**: 부하 테스트

### 테스트 더블 활용
```python
# tests/conftest.py
@pytest.fixture
async def mock_llm_client():
    client = Mock(spec=LLMClient)
    client.generate_response.return_value = "mocked response"
    return client

# 테스트에서
async def test_agent_execution(mock_llm_client):
    agent = MyAgent(config, llm_client=mock_llm_client)
    result = await agent.run()
    assert result.success
```

---

## 📦 배포 및 CI/CD

### 컨테이너화
```dockerfile
# Dockerfile
FROM python:3.11-slim

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
CMD ["uv", "run", "python", "-m", "interfaces.web.main"]
```

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI/CD
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: uv sync --extra dev
      - name: Run tests
        run: |
          uv run ruff check .
          uv run black --check .
          uv run mypy .
          uv run pytest --cov=.
```

---

## 🔄 지속적 개선 항목

### Phase 1 (현재)
- [x] 기본 아키텍처 구축
- [x] uv 환경 설정
- [x] 코드 품질 도구 설정

### Phase 2 (단기)
- [ ] 의존성 주입 컨테이너 구현
- [ ] 에이전트 레지스트리 시스템
- [ ] 통합 테스트 환경
- [ ] API 서버 (FastAPI)

### Phase 3 (중기)
- [ ] 워크플로우 오케스트레이션
- [ ] 실시간 모니터링 대시보드
- [ ] 다중 환경 배포
- [ ] 성능 최적화

### Phase 4 (장기)
- [ ] 분산 시스템 지원
- [ ] 머신러닝 파이프라인 통합
- [ ] 고급 보안 기능
- [ ] 멀티 테넌시 지원

---

## 🤝 개발 가이드라인

### 코딩 컨벤션
1. **함수명**: snake_case
2. **클래스명**: PascalCase
3. **상수**: UPPER_SNAKE_CASE
4. **파일명**: snake_case
5. **타입 힌트**: 모든 함수 필수

### 커밋 메시지 규칙
```
feat: add naver blog agent
fix: resolve database connection timeout
docs: update architecture guide
test: add unit tests for llm client
refactor: optimize agent registry performance
```

### PR 리뷰 체크리스트
- [ ] 타입 힌트 완성
- [ ] 테스트 커버리지 80% 이상
- [ ] 문서화 완료
- [ ] 보안 취약점 검토
- [ ] 성능 영향 검토

---

> 💡 **이 문서는 프로젝트 진화에 따라 지속적으로 업데이트됩니다.**