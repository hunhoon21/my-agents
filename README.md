# My Agents

다양한 자동화 에이전트들을 구축하고 관리하는 프레임워크입니다.

## 특징

- **uv 기반** Python 환경 관리
- **확장 가능한 구조**로 새로운 에이전트 쉽게 추가
- **통합 설정 관리** (YAML + 환경변수)
- **구조화된 로깅** 시스템
- **Jupyter 노트북** 통합 개발환경
- **다양한 데이터베이스** 지원 (PostgreSQL, MySQL)

## 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
uv sync

# Jupyter 노트북 의존성 설치 (선택사항)
uv sync --extra notebook

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 설정하세요
```

### 2. Jupyter 노트북으로 테스트

```bash
# Jupyter 실행
uv run jupyter lab

# notebooks/agent_testing.ipynb 파일 열기
```

### 3. 에이전트 실행

```bash
# 기본 실행
uv run run-agent --agent your_agent_name

# 파라미터와 함께 실행
uv run run-agent --agent your_agent_name --params '{"param1": "value1"}'

# 설정 파일 지정
uv run run-agent --agent your_agent_name --config configs/custom.yaml
```

## 디렉토리 구조

```
my-agents/
├── agents/                 # 개별 에이전트 구현
│   ├── base/              # 베이스 클래스
│   ├── naver_blog_commenter/  # 네이버 블로그 댓글 에이전트
│   └── sql_agent/         # SQL 쿼리 에이전트
├── core/                  # 공통 유틸리티
│   ├── config.py          # 설정 관리
│   ├── logging.py         # 로깅 시스템
│   ├── llm_client.py      # LLM 클라이언트
│   └── database.py        # 데이터베이스 클라이언트
├── notebooks/             # Jupyter 노트북
├── scripts/               # 실행 스크립트
├── configs/               # 설정 파일
└── tests/                 # 테스트
```

## 새로운 에이전트 추가하기

1. `agents/` 디렉토리에 새 폴더 생성
2. `BaseAgent`를 상속받는 클래스 구현
3. 필요한 설정을 `configs/config.yaml`에 추가
4. `notebooks/agent_testing.ipynb`에서 테스트

## 설정

- `configs/config.yaml`: 메인 설정 파일
- `.env`: 환경변수 (API 키, DB 접속 정보 등)
- 각 에이전트별 개별 설정 가능

## 요구사항

- Python 3.11+
- uv package manager
