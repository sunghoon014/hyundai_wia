STEP_1_1_PREPROCESSING_PROMPT = """# Role
당신은 BMA(Battery Module Assembly) 공정의 자율주행 로봇(AMR) 시스템을 위한 **수석 테크니컬 라이터(Senior Technical Writer)**입니다.
주어진 [Context]를 학습용 데이터로 적합한 **완결된 기술 서술 문단**으로 재작성하십시오.

# Rules
1. **주어의 구체화 (Contextualization):**
   - 문장의 주어에 상위 목차의 핵심 정보(AMR 모델명: 0.3T/1T, 공정 위치, 장비명, 알람 코드 등)를 반드시 포함하십시오.
   - 상위 목차에 모델명이 없다면, 문맥상 적절한 기종이나 'BMA 공정의 AMR'과 같은 일반 주어를 사용하십시오.

2. **사실(Fact)과 행동(Action)의 구분 (Critical):**
   - **사실/원인/증상 설명:** 절대적인 진술로 작성하십시오. 조건문을 붙이지 마십시오.
     (예: "70012 에러는 센서 중복 감지를 의미한다.")
   - **조치/해결 방법:** 물리적 버튼 조작, HMI 터치 등 사람의 개입이 필요한 경우에만 **"시스템 자동 복구가 실패하여 수동 조작이 필요한 경우,"**라는 전제 조건을 문장 앞에 붙이십시오.

3. **지시어 구채화 (Disambiguation):**
   - '이것', '그 센서', '해당 위치' 등을 구체적인 명사(예: '리프트 상한 센서', '도킹 위치')로 치환하십시오.

4. **문체:**
   - 감정을 배제한 건조하고 명확한 기술 문서체('~한다', '~이다')를 사용하십시오.

# Examples (Few-shot Learning)

**Case 1: 단순 사실 (Fact)**
- Input Context: ["5. Model Specific", "5.2. 1T AMR", "센서 사양"]
- Input Text: "리프트 센서는 지면에서 100mm 높이에 있습니다."
- **Output:** "BMA 공정 1T AMR (Pallet Lift)의 리프트 감지 센서는 지면 기준 100mm 높이에 설치되어 있다."

**Case 2: 조치 방법 (Action)**
- Input Context: ["2. Trouble Shooting", "2.1. Call 생성 불가"]
- Input Text: "HMI에서 Call Cancel 버튼을 누르세요."
- **Output:** "**시스템 자동 복구가 실패하여 수동 조작이 필요한 경우,** 운영자는 설비 HMI 화면의 [Call Cancel] 버튼을 눌러 호출 신호를 초기화해야 한다."

# Output
(재작성된 텍스트만 출력)"""

STEP_1_2_SYNTHETIC_TEXTBOOK_PROMPT = """# Role
당신은 현대자동차그룹 BMA(Battery Module Assembly) 공정의 자동화 시스템을 설계한 **수석 아키텍트(Chief Architect)**이자 **공학 교수**입니다.
제공된 [입력 텍스트]는 BMA 공정 내 AMR(자율주행 로봇), PLC, 관제 시스템(ACS/MCS)에 관한 정제된 사실(Fact)들의 집합입니다.

이 파편화된 사실들을 연결하여, 신입 엔지니어가 시스템의 **'작동 원리(Mechanism)'**, **'논리적 인과관계(Logical Causality)'**, **'데이터 흐름(Data Flow)'**을 심층적으로 이해할 수 있도록 **전문적인 기술 백서(Technical Whitepaper)**의 한 챕터를 작성하십시오.

# Goal
입력된 정보의 단순한 나열이나 요약이 아닙니다.
**"Why(왜 발생하는가?)"**와 **"How it works(어떤 원리로 작동하는가?)"**에 집중하여, 원본 텍스트의 분량을 **5배~10배**로 확장하고 논리적 깊이를 더하십시오.

# Expansion Guidelines (확장 및 심층 서술 가이드)

1.  **시스템 아키텍처 관점의 재해석:**
    - 단순한 에러 코드를 설명할 때, 그것이 시스템의 어느 레이어(Physical, Sensor, PLC, Network, Application)에서 발생하는지 구조적으로 분석하십시오.
    - 예: "70012 에러" → 단순한 '시간 초과'가 아니라, "PLC와 AMR 간의 Handshaking 프로토콜에서 신호 동기화가 실패하여 발생하는 Timeout 메커니즘"으로 확장 서술.

2.  **물리적/공학적 배경지식 통합 (Physics & Engineering):**
    - 센서(Lidar, IR, Camera)나 하드웨어(Motor, Battery)가 언급되면, 해당 부품의 일반적인 공학적 작동 원리(예: ToF 방식, 광학적 반사 특성, 리튬이온 배터리의 전압 강하 특성 등)를 BMA 공정 환경과 결합하여 설명하십시오.
    - 예: "V-Marker 인식 실패" → "Lidar 센서가 V-Marker의 기하학적 형상을 스캔하는 과정에서 발생하는 광학적 노이즈와, 정밀 주행(Navigation) 알고리즘의 상관관계" 서술.

3.  **인과관계의 논리적 사슬 (Chain of Causality):**
    - 현상만을 서술하지 말고, **[조건] -> [트리거] -> [내부 로직 수행] -> [결과/에러] -> [시스템의 안전장치 동작]** 순으로 인과관계를 완벽하게 연결하십시오.
    - 특정 조작(Action)이 왜 필요한지, 이를 수행하지 않았을 때 시스템에 어떤 교착 상태(Deadlock)나 물리적 충돌이 발생하는지 이론적으로 설명하십시오.

4.  **매뉴얼 투(Manual Tone) 지양:**
    - "버튼을 누르세요" 같은 지침서 스타일을 피하십시오.
    - 대신, "운영자가 리셋 신호를 인가하면, 시스템은 에러 레지스터를 소거(Clear)하고 초기 상태로 복귀한다"와 같이 **시스템의 반응을 객관적으로 서술**하십시오.

# Constraints
1.  **용어 및 코드의 정확성:** 제공된 텍스트에 있는 고유 명사(장비명: 0.3T/1T AMR, 알람 코드: 70012, 80024 등)는 절대 변경하지 말고 정확히 인용하십시오.
2.  **환각 방지 (No Fact Hallucination):** BMA 공정에 존재하지 않는 가상의 스펙(구체적인 배터리 용량 수치 등)을 만들어내지 마십시오. 단, **일반적인 공학 원리나 이론을 덧붙여 설명을 풍부하게 하는 것은 적극 권장**합니다.

# Input Data (Refined Fact List)
{grouped_text}

# Output Format (Markdown)"""

STEP_1_2_SYNTHETIC_SPECIFIC_PROMPT = """# Role
당신은 BMA 시스템의 **수석 소프트웨어 아키텍트**이자 **API 문서화 전문가(Documentation Specialist)**입니다.
입력된 [API Raw Data]를 바탕으로, 개발자와 에이전트가 참고할 수 있는 **상세한 API 기술 명세서(Technical Specification)**를 작성하십시오.

# Goal
입력된 API 정보를 단순 나열하지 말고, **"이 API가 언제 쓰이며, 어떤 데이터를 주고받는지"** 명확하게 기술하십시오.

# Writing Guidelines
1. **정의(Definition):** 해당 API의 기능과 목적을 한 문장으로 명확히 정의하십시오.
2. **기술적 상세(Technical Details):** Endpoint, HTTP Method, Header, Body 파라미터의 데이터 타입과 필수 여부를 서술하십시오.
3. **사용 사례(Use Case):** 이 API가 실제 BMA 공정 시나리오에서 어떤 상황(예: 에러 리셋, 좌표 보정)에 사용되는지 예시를 들어 설명하십시오.
4. **스타일:** 건조하고 정확한 기술 문서체("~한다", "~을 반환한다")를 사용하십시오.

# Output Example
## [API] 작업 취소 명령 (Cancel Command)

**1. 개요**
`PUT /api/command/cancel` API는 특정 AMR(Target)에 할당된 현재 작업을 즉시 중단시키는 비상 제어 명령이다. 주로 충돌 위험이 감지되거나 프로세스 교착 상태(Deadlock)를 해소하기 위한 안전 조치로 사용된다.

**2. 요청 명세 (Request Specification)**
- **Endpoint:** `/api/command/cancel`
- **Method:** `PUT`
- **Header:** `Authorization: Bearer {Token}` (JWT 인증 필수)
- **Body Parameters:**
  - `Target` (String, Required): 제어 대상 로봇의 네트워크 ID (예: "R_101").

**3. 동작 메커니즘**
이 명령이 수신되면 ACS 서버는 해당 로봇의 모터 제어기에 Stop 신호를 전송하고, 실행 중인 미션 스택을 초기화한다. 성공 시 `{"Success": true}`를 반환하며, 로봇은 Idle 상태로 전환된다."""

STEP_1_2_SYNTHETIC_SOP_PROMPT = """# Role
당신은 BMA 공정의 **표준 운영 절차(SOP) 관리자**이자 **프로세스 엔지니어**입니다.
입력된 [시나리오]는 현장 엔지니어를 위한 요약된 절차 목록입니다. 이를 **완결된 줄글 형태의 표준 운영 절차서(SOP Document)**로 확장하여 작성하십시오.

# Goal
단순히 "A 하고 B 한다"가 아니라, **"왜 A 다음에 B를 해야 하는지"**에 대한 인과관계와 당위성을 설명하여, 읽는 이가 프로세스의 흐름을 논리적으로 이해하도록 하십시오.

# Writing Guidelines
1. **흐름 서술(Flow Description):** 번호 매기기 대신, "우선 ~를 수행한다. 그 후 ~가 확인되면 ~를 실행한다"와 같은 자연스러운 연결어미를 사용하십시오.
2. **목적 명시(Purpose):** 각 단계가 왜 필요한지 설명하십시오.
   - (예: "안전 사고 방지를 위해 Cancel을 먼저 수행한다", "데이터 정합성을 위해 Status를 먼저 조회한다")
3. **전문 용어 유지:** `dock_reset`, `Retry` 등의 고유 용어는 그대로 사용하십시오.

# Output Example
## [SOP] 차상 작업 전 신호 오류 복구 절차 (Scenario 3)

**1. 절차 개요**
본 절차는 AMR이 도킹에 성공했으나, 설비(PLC)와의 신호 인터페이스(U_REQ, READY 등)가 동기화되지 않아 작업이 지연될 때 수행하는 표준 복구 프로세스다.

**2. 상세 수행 절차**
가장 먼저 시스템은 `GET /api/object/status`를 통해 AMR의 현재 위치와 Rack 정보를 파악해야 한다. 이는 후속 조치인 리셋 명령의 대상을 특정하기 위함이다.
대상 확인 후, 즉시 `PUT /api/command/cancel`을 호출하여 대기 중인 잘못된 신호를 소거한다. 이후 설비 PLC의 레지스터를 초기화하기 위해 `dock_reset` 명령을 전송하고, 연속해서 `dock_ok` 신호를 인가함으로써 핸드쉐이킹 준비 상태를 강제로 동기화한다.
마지막으로 MCS에 미션 재시도(`CallRetry`)를 요청하여 정상적인 작업 흐름으로 복귀시킨다."""


STEP_1_3_QUESTION_GENERATION_PROMPT = """# Role
당신은 BMA 공정 자동화 시스템 학습 데이터를 구축하는 **Data Specialist**입니다.
입력된 텍스트는 특정 주제에 대한 **상세한 기술 백서(Technical Whitepaper)**입니다.

이 **긴 텍스트 전체**를 답변으로 제시해도 자연스러울 만큼, **깊이 있고 포괄적인 질문(Instruction)** 3가지를 생성하십시오.

# Input Text
{content}

# Task: 3가지 유형의 Deep-Dive 질문 생성
**순서를 섞지 마십시오. 아래 정의된 순서대로 리스트를 구성해야 합니다.**

**[Index 0] 포괄적 요청 (General Request)**
   - 주제: 해당 텍스트의 핵심 주제(Title) 전체.
   - 의도: "기술 백서 형식으로 상세히 서술해달라"는 포괄적 요청.
   - 필수 어미: "~에 대해 기술 백서 형식으로 상세히 서술하시오."

**[Index 1] 메커니즘 심층 탐구 (Deep Mechanism)**
   - 주제: 텍스트 내의 핵심 기술(센서, 알고리즘)의 작동 원리.
   - 의도: 특정 기술이 **"전체 시스템 내에서 어떻게 상호작용하는지"** 그 흐름을 묻는 질문.
   - 필수 어미: "~의 작동 원리와 시스템적 상호작용을 공학적으로 분석하시오."

**[Index 2] 논리적 인과관계 분석 (Causal Analysis)**
   - 주제: 에러 상황, 예외 처리, 안전 로직.
   - 의도: **"왜 그런 문제가 발생하며, 시스템은 어떤 로직으로 대응하는가"**에 대한 근본 원인 분석 요청.
   - 필수 어미: "~상황 발생 시 시스템의 논리적 판단 과정과 대응 메커니즘을 서술하시오."

# Constraints (매우 중요)
1. **No Simple Questions:** "T4 에러란 무엇인가?"와 같은 단답형 질문을 절대 만들지 마십시오. 사용자가 **"긴 설명"을 듣고 싶어 한다는 뉘앙스**를 풍겨야 합니다.
2. **Order enforcement:** 출력 리스트의 **첫 번째는 반드시 [포괄적 요청], 두 번째는 [메커니즘], 세 번째는 [인과관계]**여야 합니다. 순서를 바꾸면 시스템 오류가 발생합니다.
3. **Context-Aware:** 질문은 반드시 입력 텍스트 내용을 근거로 생성해야 합니다.
4. **Format:** 오직 **Python List 형태의 JSON**만 출력하십시오. (Key값 없이 문자열 리스트로만 출력)

# Output Example
[
    "BMA 공정의 'AMR 정밀 도킹 시스템' 전반에 대해 기술 백서 형식으로 상세히 서술하시오.",
    "도킹 과정에서 Lidar 센서와 V-Marker 간의 인식 실패가 발생하는 광학적 원리와, 이를 보정하기 위한 시스템적 상호작용을 분석하시오.",
    "도킹 타임아웃(Timeout) 발생 시 안전 인터락(Interlock)이 발동되는 논리적 인과관계와 시스템의 단계별 대응 메커니즘을 상세히 설명하시오."
]"""
