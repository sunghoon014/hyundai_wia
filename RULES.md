## 개요

- Your are very smart and helpful KOREAN developer with extensive expertise in software engineering.
- You're gonna code following the following rules(Korean).

## 공식 문서

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Dependency Injector](https://python-dependency-injector.ets-labs.org/)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [MCP](https://modelcontextprotocol.io/specification/2025-06-18)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [ruff](https://docs.astral.sh/ruff/)
- [uv](https://docs.astral.sh/uv/)
- In text separated by comma.

```text
fastapi.tiangolo.com,
sqlalchemy.org,
python-dependency-injector.ets-labs.org,
docs.pydantic.dev,
modelcontextprotocol.io,
google.github.io,
docs.astral.sh,
```

## 파이썬 개발 환경

1. Python 버전: 3.12+
2. 의존성 관리: uv
3. 주요 의존성(세부 내용은 `pyproject.toml` 참고):
   1. 웹 프레임워크: **FastAPI**
   2. Object–Relational Mapping(ORM): **SQLAlchemy**
   3. Dependency Injection Container: **Dependency Injector**
   4. Data Modeling: **Pydantic**
   5. Testing: **Pytest**, **Playwright**
   6. Logging: **Loguru**
   7. Formatting: **ruff**

## 파이썬 코딩 컨벤션

1. **Google Python 스타일 가이드**와 **PEP 8**을 따르고, 변수, 함수, 클래스 이름은 스스로 설명가능한(self-descriptive), 의미있는(meaningful) 네이밍 사용.
2. 만약 pyproejct.toml의 ruff 설정과 내용이 충돌한다면, 해당 ruff 설정이 우선함.
3. 주석

   1. **(Optional)** 패키지 주석: 패키지 폴더에 `README.md` 생성 후 패키지 내에서 통용되는 개념 작성
   2. **(Optional)** 모듈 주석: 모듈(`*.py`) 최상단에 multiline string 형식으로 모듈 관련 설명 작성
   3. 함수/클래스 주석: Google 형식의 docstring(요약문+빈 줄+세부 설명)을 작성.

      ```python
      def greet_user(name: str) -> str:
          """주어진 사용자 이름으로 인사문 생성.

          이름을 대문자로 변환하여 일관성 유지

          Args:
              name (str): 사용자 이름

          Returns:
              str: 대문자로 시작하는 인사문
          """
          if not name:
              raise ValueError("이름은 필수입니다.")

          return f"Hello, {name.capitalize()}!"
      ```

   4. **(Optional)** 인라인 주석
      1. 복잡한 로직에 대해서만 상세 주석 작성, 불필요한 주석 남발 금지
      2. 코드를 읽으면 이해할 수 있도록 최대한 자기해설적(self-documenting) 코드를 작성
      3. 중요한 주석은 `# NOTE:` 접두사 사용

4. 네이밍: 변수, 함수, 클래스 이름은 스스로 설명가능한(self-descriptive), 의미있는(meaningful) 이름을 선택
5. 단순성: 복잡성을 피하고, 간단하고 명확한 코드를 작성합니다.
6. 보안성: 보안 취약점과 버그 최소화
7. 리스트 컴프리헨션 사용: 적절할 때 전통적인 루프 대신 리스트 컴프리헨션을 사용합니다.
8. 예외 처리: try-except 블록을 사용하여 예외를 우아하게 처리합니다.
9. 타입 힌트 사용: 코드 가독성과 타입 검사를 위해 타입 힌트를 사용합니다.
10. 전역 변수 지양: 전역 변수 사용을 최소화하여 사이드 이펙트를 줄입니다.
11. 테스팅
    1. 테스트 주도 개발(Test-Driven Development, TDD)을 지향하여, 구현하고자 하는 기능에 대한 API 테스트 작성
    2. 기존에 작성된 API 테스트 코드 스타일에 일관된 스타일로 작성
12. 로깅
    1. 로깅 레벨: DEBUG, INFO, WARNING, ERROR
    2. `.env` 파일의 `LOG_LEVEL` 환경변수에 따라 `app/main.py`에서 로깅 레벨 설정하며, 포맷은 loguru 기본 포맷
    3. DEBUG
       1. 개발 및 디버깅 목적의 상세 정보
       2. 함수 진입/종료, 변수 값, 조건 분기 등 코드 흐름 추적용
       3. 서비스 운영 시 일반적으로 INFO 레벨 이상부터 로깅할 것이며, 해당 레벨의 로그는 생성되지 않음.
       4. 예시: 외부 API 요청/응답(DB 트랜잭션, LLM API 호출 등)
    4. INFO
       1. 정상적인 서비스 흐름에서의 주요 이벤트
       2. 비즈니스 로직 수행 시 의미 있는 상태 변화나, 의미 있는 결과가 반환되었을 때 로깅
       3. 시스템이 정상적으로 동작하고 있음을 알리는 메시지
       4. 예시: 조건 검색 요청 수신, 조건 검색 비즈니스 로직 내 세부 로직들의 중간 결과, 조건 검색 결과 반환 등
    5. WARNING
       1. 치명적이지 않으나, 주의가 필요한 상황
       2. 곧 문제로 발전할 수 있는 잠재적 이슈, 또는 문제가 발생했지만 복구 가능한 상황
       3. 예시: 외부 서비스 응답 지연, 외부 서비스 호출 실패 등
    6. ERROR
       1. 클라이언트 요청 처리 실패, 예외 발생 등 심각한 문제
       2. 비즈니스 로직상 복구 불가, 사용자에게 에러 응답 반환
       3. 예시: 필수 데이터 누락, 처리 불가한 예외, 원인을 알 수 없는 오류, 여러 번 시도 후 외부 서비스 호출 실패 등

## 프로젝트 컨텍스트

1. 최상단 프로젝트 폴더의 `README.md`에서 **프로젝트 파일 구조**와 **주요 비즈니스 로직**
2. 프로젝트 내 각 패키지 내 `README.md`
3. 프로젝트 내 각 모듈 내 최상단에 위치한 multiline String 형식의 주석
4. 프로젝트 내 각 함수, 클래스 내 docstring
5. 인라인 주석
6. 도메인 패키지 내 모듈 설계: `app/domains/example`
7. 데이터베이스 패턴:
   - **RDB**: SQLAlchemy ORM, RDBBaseRepository 사용, `app/domains/example/repositories/rdb_*` 참고
   - **MongoDB**: Motor + MongoBaseRepository 사용, `app/domains/project/repositories/mongo_*` 참고
8. 설정(Configuration) 시스템:
   - **환경변수**: `.env` 파일 + Pydantic BaseSettings 사용, `app/config/env_config.py` 참고
   - **YAML 설정**: 환경별 설정 파일 `app/config/{ENV}.yaml` (예: `local.yaml`)
   - **프롬프트 설정**: 프롬프트 `app/config/prompts.yaml`
   - **DI 통합**: `init_config(config)` 호출로 모든 설정을 DI Container에 주입
   - **설정 접근**: `config.service.key()` 형태로 접근 (예: `config.langfuse.host()`, `config.prompts.evaluation()`)
   - **패턴**: 모든 Container에서 동일한 방식으로 설정 초기화

## 개발 순서

1. Context: 프로젝트 컨텍스트 파악
2. Plan: 주어진 요구사항을 어떻게 구현할지 인간 개발자와 논의
3. TDD: 만들기로 논의된 API를 테스트 코드로 작성
4. Implement: 테스트 코드를 통과하는 API와 그 안의 비즈니스 로직 작성
5. Debug: 테스트 코드가 통과할 때까지 디버깅하며 수정 및 구현
6. Finish: 테스트 코드가 통과하면 완료. 부족했거나 오래된 프로젝트 컨텍스트가 있었다면 보강하기

## 주의사항

1. 현재 요구사항에 해당하는 코드만 변경하며, 이외 코드 변경은 되도록 삼가하기

## 팀 협업 가이드라인

- TBD
