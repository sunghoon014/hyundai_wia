# Automatic QA Generation

## 1. 실행 방법

### 1.1. 파이썬 개발 환경 설정

1. [uv](https://docs.astral.sh/uv/) 설치
2. [pyenv](https://github.com/pyenv/pyenv) 또는 uv 활용하여 파이썬 3.12.x 설치
3. uv 활용하여 가상환경 설정

````bash
uv sync

4. 가상 환경 실행

```bash
source .venv/bin/activate
````

### 1.2. 환경변수 설정

1. 개발 환경 정의

   - 로컬 환경
     - `backbone/app/config/local.yaml` 파일 설정
     - `.env` 파일 안에서 `ENV` 변수를 `local`으로 설정
   - 운영 환경
     - `backbone/app/config/prod.yaml` 파일 설정
     - `.env` 파일 안에서 `ENV` 변수를 `prod`으로 설정

2. 로그 레벨 설정

- `.env` 파일 안에서 `LOG_LEVEL` 변수를 설정

3. 프로젝트 루트 경로 설정

- `.env` 파일 안에서 `PROJECT_ROOT` 변수를 설정

4. Full Example

```text
# .env

ENV=local or prod
LOG_LEVEL=DEBUG or INFO or WARNING or ERROR
PROJECT_ROOT=/path/to/backbone_project
...
```

> 현재는 개발 편의를 위해 local.yaml만 사용. 추후 환경별 설정값 분리 필요

### 1.3. Milvus(Standalone) 설치

> PoC 단계이므로 검색해야 할 데이터가 적어 self-hosted Milvus 사용.

- [Milvus Standalone Docker 설치 가이드](https://milvus.io/docs/install_standalone-docker.md)

### 1.4. 실행

- 기본 실행

```bash
# 명령형 인자(`-p`, `--port`)로 포트 설정
# 만약 설정하지 않으면 기본값으로 8000 포트 사용됨.
python -m main
```

- SSL 설정 필요 시, SSL keyfile, certfile 경로 추가

```bash
python -m main --ssl-keyfile=... --ssl-certfile=...
```

## 2. 시스템 아키텍처 및 파일 구조

본 프로젝트는 계층적 모듈형 아키텍처를 채택하여 각 컴포넌트의 역할을 명확히 분리하고, 유지보수성과 확장성을 높였습니다. 크게 API 엔드포인트와 비즈니스 로직을 담당하는 **`domains`**, AI 에이전트의 핵심 추론 및 실행을 담당하는 **`agents`**, 그리고 공통 기능을 제공하는 **`common`**으로 구성됩니다.

```text
ax-qa-generation/
├── app/                                    # 애플리케이션 핵심 소스 코드
│   ├── agents/                             # AI 에이전트의 핵심 로직, 상태, 도구 정의
│   │   ├── adaptor/                        # LLM 추상화 계층 (LLM 교체 용이)
│   │   ├── context/                        # 에이전트 상태, 메모리, 토큰 등 컨텍스트 관리
│   │   ├── domains/                        # BaseAgent, ReAct 등 에이전트의 구체적인 행동 양식 정의
│   │   ├── mcp/                            # 외부 도구 서버와 통신하는 MCP(Meta-Cognitive Primitives) 클라이언트
│   │   ├── sandbox/                        # 코드 실행을 위한 보안 샌드박스 (Docker 기반)
│   │   └── tools/                          # 에이전트가 사용하는 도구(웹 검색, RAG 등) 정의
│   │
│   ├── common/                             # 여러 도메인에서 공통으로 사용되는 모듈
│   │   ├── llm_clients/                    # OpenAI 등 LLM 서비스 API와 직접 통신하는 저수준 클라이언트
│   │   ├── repositories/                   # 데이터베이스 CRUD를 위한 리포지토리 패턴 구현
│   │   └── messaging/                      # SSE 스트리밍을 위한 메시지 큐
│   │
│   ├── config/                             # 환경 변수, 프롬프트, 로컬 설정 등 관리
│   │
│   └── domains/                            # 비즈니스 로직 및 API 엔드포인트
│       ├── chat/                           # 채팅 세션 관리 및 메시징 API
│       ├── document/                       # 문서 업로드, 파싱, 인덱싱 파이프라인 API
│       └── index/                          # 헬스체크 등 공통 API
│
├── data/                                   # 로컬 데이터 및 임시 파일
├── logs/                                   # 애플리케이션 로그
├── main.py                                 # FastAPI 애플리케이션 실행 엔트리 포인트
└── pyproject.toml                          # 프로젝트 의존성 및 메타데이터 관리
```

### 2.1. 주요 디렉토리 설명

**`app/agents`**: AI 에이전트의 "두뇌"에 해당하는 부분입니다. 다양한 모듈들을 오케스트레이션하는 역할도 합니다.

- **`adaptor`**: 에이전트가 특정 LLM 구현에 종속되지 않도록 `ILLMAdapter` 인터페이스를 통해 LLM을 추상화합니다.
- **`domains`**: `BaseAgent`와 `ReActAgent`를 기반으로, 실제 태스크를 수행하는 `KearneyAgent`와 같은 구체적인 에이전트를 정의합니다.
- **`mcp` 및 `tools`**: 에이전트가 사용할 수 있는 능력을 정의합니다. 특히 **MCP(Meta-Cognitive Primitives)** 프로토콜을 통해 웹 검색, RAG와 같은 무거운 도구들을 별도의 서버 프로세스로 분리하여, 에이전트의 핵심 로직과 독립적으로 확장 및 관리할 수 있는 구조를 가지고 있습니다.
- **`sandbox`**: `python_execute`와 같이 잠재적으로 위험한 코드를 Docker 컨테이너 내부의 격리된 환경에서 안전하게 실행시키는 역할을 합니다.

---

**`app/domains/chat`**: `chat` 도메인은 사용자와의 실시간 상호작용을 담당하는 핵심 비즈니스 로직을 포함합니다. 주요 역할은 **문서 인덱싱**과 **AI 에이전트 실행**입니다.

- **문서 인덱싱**: 사용자가 문서를 선택하여 새로운 채팅 세션을 시작하면, `chat` 도메인은 `document` 도메인에서 미리 처리해 둔 문서 데이터를 가져와 **Milvus에 벡터 인덱스를 생성**합니다. 이 인덱스는 해당 채팅 세션에서 RAG(Retrieval-Augmented Generation)를 수행하는 데 사용됩니다.
- **AI 에이전트 실행**: 사용자 메시지를 받아 AI 에이전트를 활성화하고, 에이전트의 실행 과정을 SSE(Server-Sent Events)를 통해 클라이언트에게 스트리밍합니다.
- **`apis/`**: `/sessions` (채팅 세션 생성 및 문서 인덱싱 트리거), `/stream` (채팅 메시지 전송 및 SSE 스트리밍) 등 클라이언트와 직접 통신하는 FastAPI 엔드포인트를 정의합니다.
- **`services/`**:
  - `ChatService`: 채팅 요청의 전체 흐름을 조율합니다. 세션 생성 시 `MilvusIndexer`를 호출하여 문서를 인덱싱하고, 채팅 중에는 에이전트 어댑터를 호출하여 에이전트 실행을 시작하는 등 역할을 합니다.
  - `AgentAdapter`: `domains` 계층의 `ChatService`와 `agents` 계층의 `Agent` 사이를 연결하는 **어댑터(Adapter)** 역할을 합니다. 도메인에서 사용하는 데이터 모델을 에이전트가 이해할 수 있는 형식으로 변환하고, 에이전트 실행을 위한 컨텍스트(메시지 기록, MCP 도구 설정 등)를 구성합니다.
- **`schemas/`**: API 요청/응답 모델(`ChatRequest`, `CreateSessionResponse`)과 도메인 내부에서 사용하는 데이터 구조(`Message`, `ChatSession`)를 Pydantic으로 정의합니다.
- **`repositories/`**: MongoDB와 상호작용하여 채팅 세션 및 메시지 기록을 영속적으로 저장하고 조회하는 로직을 담당합니다.

---

**`app/domains/document`**: `document` 도메인은 PDF와 같은 복잡한 문서를 처리하기 위한 비동기 파이프라인 아키텍처를 구현합니다. 문서 업로드 요청을 받으면, 여러 단계의 처리 과정을 거쳐 최종적으로 **검색 및 인덱싱에 사용될 데이터**를 생성하고 데이터베이스에 저장합니다. 전체 과정은 SSE를 통해 클라이언트에게 실시간으로 진행 상황을 보고합니다.

- **`apis/`**: `/documents` (문서 업로드, 조회, 삭제) 엔드포인트를 제공합니다. 특히 문서 생성 API는 요청을 즉시 반환하고, 실제 처리는 백그라운드에서 비동기적으로 수행됩니다.
- **`services/`**:
  - `DocumentService`: 문서 생성, 조회, 삭제 등 전체적인 문서 관리 로직을 담당합니다. `ParsingService`를 호출하여 실제 파싱 파이프라인을 실행시킵니다.
  - `ParsingService`: 문서 처리의 핵심입니다. **StateGraph**를 기반으로 문서 처리 단계를 **`Node`**로 정의하고, 이들을 연결하여 파이프라인을 구성합니다.
- **`handlers/node`**: 파이프라인을 구성하는 각 처리 단계를 `BaseNode`를 상속받아 구현합니다. 각 노드는 하나의 명확한 책임을 가집니다. (예: `SplitPDFFilesNode` - PDF 페이지 분할, `UpstageParseNode` - OCR 수행, `PageSummaryNode` - 페이지별 요약 생성).
- **`handlers/langchain`**: `chain.py` 와 `adapter.py` 를 통해 Langchain 라이브러리를 활용한 LLM 호출 로직을 추상화하여, 요약 생성 등과 같은 LLM 기반 처리 노드에서 쉽게 사용할 수 있도록 돕습니다.
- **`schemas/`**: `ParseState`는 파이프라인의 각 노드를 거치며 처리되는 데이터의 상태를 정의합니다. 이를 통해 각 단계 간 데이터 흐름을 명확하게 관리합니다.

---

### 2.2. 설정 파일 가이드 (`local.yaml` & `prompts.yaml`)

#### `app/config/local.yaml`: 시스템 동작 및 모델 설정

`local.yaml` 파일은 애플리케이션의 핵심 동작 방식을 제어하는 파라미터를 정의합니다. 모델 선택, 기능별 파라미터, 파이프라인 노드 설정 등을 관리하며, 이 파일을 통해 코드 변경 없이 시스템의 동작을 유연하게 변경할 수 있습니다.

**주요 설정 규칙:**

1.  **계층적 구조 준수**: 설정은 `agent`, `document`, `milvus` 등 명확한 최상위 키로 그룹화됩니다. 새로운 설정을 추가할 때는 가장 관련성이 높은 그룹 하위에 배치해야 합니다.
2.  **모델 및 프로바이더 명시**: LLM을 사용하는 모든 기능(`agent`, `page_summary_node` 등)은 사용할 `model`과 API 제공자인 `provider`를 명시적으로 선언해야 합니다.
3.  **파라미터 분리**:
    *   `params`: LLM API에 직접 전달될 파라미터(예: `max_tokens`, `temperature`)를 정의합니다. OpenAI API와 호환되는 파라미터만 포함해야 합니다.
    *   `config`: LLM API 호출 외에, 시스템 내부 로직에서 사용될 파라미터(예: `max_input_tokens`)를 정의합니다.
4.  **`list`는 기록용**: 각 설정 그룹 하위의 `list` 키(예: `document.list`)는 해당 기능에서 사용되는 모듈 목록을 기록하는 용도입니다. 실제 시스템 동작에 영향을 주지 않으므로, 기능 변경 시 해당 목록도 함께 업데이트하여 최신 상태를 유지하는 것을 권장합니다.

---

#### `app/config/prompts.yaml`: 프롬프트 중앙 관리

`prompts.yaml` 파일은 시스템의 모든 프롬프트를 중앙에서 관리합니다.

**주요 작성 규칙:**

1.  **`local.yaml`과의 연동**: 프롬프트는 `local.yaml`의 설정과 연관됩니다. 예를 들어, `agent_prompts.kearney` 하위의 프롬프트들은 `local.yaml`에서 `agent.domain`이 `kearney`로 설정되었을 때 사용됩니다. 이처럼 설정 파일과 프롬프트 파일 간의 구조적 일관성을 유지해야 합니다.
2.  **명확한 역할 부여 (Role & Goal)**: 좋은 프롬프트는 AI에게 명확한 역할과 목표를 부여하는 것에서 시작합니다. 프롬프트 상단에 주석이나 명시적인 지시문(`# Role & Goal`)을 통해 AI가 수행해야 할 역할을 구체적으로 정의해야 합니다.
3.  **구조화된 출력 형식 (Output Format)**: LLM이 예측 가능한 형식으로 응답을 생성하도록 유도하기 위해, `<tag></tag>`나 Markdown, JSON 형식을 사용하여 명확한 출력 구조를 프롬프트 내에 정의해야 합니다. 이는 후처리 과정을 단순화하고 안정성을 높입니다.
    *   예시: `document_prompts.page_summary_node.system_prompt_2`는 `<one_line_summary>`, `<key_topics>` 등의 XML 태그를 사용하여 구조화된 출력을 요구합니다.
4.  **구체적인 지침과 제약 조건**: "무엇을 하지 말아야 하는지(Negative Constraints)"를 명시하는 것이 중요합니다. 예를 들어, `agent_prompts.kearney.frontier.vanila.system_prompt`의 "Internal Process Secrecy" 섹션은 AI가 내부 동작 과정을 노출하지 않도록 명확하게 지시합니다.
5.  **YAML 멀티라인 문법 활용**: 길고 복잡한 프롬프트는 가독성을 위해 `|-` (줄바꿈 유지) 또는 `>` (줄바꿈을 공백으로 변환)와 같은 YAML의 멀티라인 블록 스칼라 문법을 사용해야 합니다.
