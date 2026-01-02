# MCS.Backend API 문서

## 개요
MCS(Material Control System) Backend API 문서입니다. 이 API는 AMR(Autonomous Mobile Robot) 시스템을 제어하고 모니터링하기 위한 RESTful API를 제공합니다.

---

## 목차
1. [PLCController](#plccontroller)
2. [ObjectController](#objectcontroller)
3. [CommandController](#commandcontroller)

---

## PLCController

PLC(Programmable Logic Controller) 센서 값을 관리하는 API입니다.

### 1. PUT /api/PLC/sensorvalue

센서 값을 업데이트합니다.

**Endpoint:** `PUT /api/PLC/sensorvalue`

**Request Body:**
```json
{
  "SensorId": 1001,
  "Current": "25.5"
}
```

**Response:**
```json
{
  "Success": true,
  "Error": null
}
```

**인증:** JWT Token 필요

**설명:**
- 사용자 정보는 JWT Token에서 추출됩니다.
- 센서 값을 PLC에 기록하고 결과를 반환합니다.

---

## ObjectController

시스템 객체(장소, 호출, 미션 등)를 관리하는 API입니다.

### 1. GET /api/Object/Hello

서버 연결 테스트용 헬로우 API입니다.

**Endpoint:** `GET /api/Object/Hello`

**Response:**
```json
"Hello, World"
```

**인증:** 불필요

---

### 2. GET /api/Object/places

모든 장소(Place) 정보를 조회합니다.

**Endpoint:** `GET /api/Object/places`

**Response:**
```json
[
  {
    "Code": "P001",
    "AlarmState": "Normal",
    "ModeState": "Auto",
    "PlaceRunState": "Run",
    "LogisticsState": "Available"
  },
  {
    "Code": "P002",
    "AlarmState": "Warning",
    "ModeState": "Manual",
    "PlaceRunState": "Stop",
    "LogisticsState": "Unavailable"
  }
]
```

**인증:** 불필요

**설명:**
- 시스템에 등록된 모든 장소 정보를 반환합니다.
- 비동기로 처리됩니다.

---

### 3. PUT /api/Object/place

장소 정보를 업데이트합니다.

**Endpoint:** `PUT /api/Object/place`

**Request Body:**
```json
{
  "Code": "P001",
  "AlarmState": "Normal",
  "ModeState": "Auto",
  "PlaceRunState": "Run",
  "LogisticsState": "Available"
}
```

**Response:**
```json
{
  "Result": true,
  "Message": "Place updated successfully"
}
```

**인증:** JWT Token 필요

**설명:**
- 특정 장소의 정보를 업데이트합니다.
- 사용자 정보는 JWT Token에서 추출됩니다.

---

### 4. GET /api/Object/Call

모든 호출(Call) 정보를 조회합니다.

**Endpoint:** `GET /api/Object/Call`

**Response:**
```json
[
  {
    "CODE": "AA001_20250319_P001",
    "CALL_DT": "20250319",
    "CALL_ID": "AA001",
    "CALL_TYPE": "1",
    "CALLER": "PLC_01",
    "CALL_PLACE": "P001",
    "PARAM": "0",
    "CALL_QUANTITY": 1,
    "CALL_PRIORITY": 5,
    "REPEAT_COUNT": 0,
    "REPEAT_DELAY": 0,
    "USE_YN": "Y",
    "STS": "A",
    "REG_ID": "SYSTEM",
    "REG_DT": "2025-03-19T10:30:00",
    "MOD_ID": "SYSTEM",
    "MOD_DT": "2025-03-19T10:30:00",
    "MISSION": "M001",
    "SUBMISSION": "SUB001",
    "STATE": "ASSIGNED",
    "UPDATE_DT": "2025-03-19T10:30:15",
    "GROUP": "GROUP_A"
  }
]
```

**인증:** 불필요

**설명:**
- 시스템의 모든 호출 정보를 반환합니다.
- 비동기로 처리됩니다.
- 500ms 캐싱이 적용됩니다.

---

### 5. GET /api/Object/Mission

모든 미션(Mission) 정보를 조회합니다.

**Endpoint:** `GET /api/Object/Mission`

**Response:**
```json
[
  {
    "CODE": "CMD_20250319_001",
    "CONTROLLER": "RCS_01",
    "SUBJECT": "MOVE",
    "CONTENT": "{\"from\":\"P001\",\"to\":\"P002\"}",
    "PARAM1": "P001",
    "PARAM2": "P002",
    "NEED_ACK_YN": "Y",
    "USE_YN": "Y",
    "STS": "A",
    "REG_ID": "SYSTEM",
    "REG_DT": "2025-03-19T10:30:00",
    "MOD_ID": "SYSTEM",
    "MOD_DT": "2025-03-19T10:30:00",
    "RUN_STATE": "RUNNING",
    "RETRY_COUNT": 0,
    "ASSIGNED_WORKER": "AMR_001",
    "RESPONSE_CONTROLLER": "RCS_01",
    "RESPONSE_SUBJECT": "MOVE_ACK",
    "RESPONSE_MESSAGE": "Command received",
    "START_DT": "2025-03-19T10:30:05",
    "END_DT": "0001-01-01T00:00:00",
    "DATA_1": "MOVING",
    "DATA_2": null,
    "UPDATE_DT": "2025-03-19T10:30:15"
  }
]
```

**인증:** 불필요

**설명:**
- 시스템의 모든 미션(명령) 정보를 반환합니다.
- 비동기로 처리됩니다.
- 500ms 캐싱이 적용됩니다.

---

### 6. GET /api/Object/callplaces

호출 장소의 상태 정보를 조회합니다.

**Endpoint:** `GET /api/Object/callplaces`

**Response:**
```json
[
  {
    "Place": "P001",
    "MachineRequest": 1,
    "AMRResponse": 2,
    "PLCMode": 1,
    "DockRequest": 0
  },
  {
    "Place": "P002",
    "MachineRequest": 258,
    "AMRResponse": 1,
    "PLCMode": 2,
    "DockRequest": 1
  }
]
```

**인증:** 불필요

**설명:**
- 각 장소의 PLC 태그 정보를 조회합니다.
- 캐싱 기능이 적용되어 있습니다 (1.5초 간격).
- MachineRequest는 여러 태그의 값을 합산합니다 (MachineRequest01, MachineRequest02, MachineRequest03).
- DockRequest는 Docking Out 상태 표시를 위해 추가되었습니다.

**PLC 태그 매핑:**
- `{Place}.MachineRequest01`: 기계 요청 값 (하위 바이트)
- `{Place}.MachineRequest02`: 기계 요청 값 (중위 바이트) × 256
- `{Place}.MachineRequest03`: 기계 요청 값 (상위 바이트) × 256²
- `{Place}.AMRResponse` 또는 `{Place}.AMRResponse01`: AMR 응답 값
- `{Place}.DockStatus`: PLC 모드
- `{Place}.DockRequest`: 도킹 요청 값

---

### 7. GET /api/Object/mcsalarms

MCS 알람 정보를 조회합니다.

**Endpoint:** `GET /api/Object/mcsalarms`

**Response:**
```json
[
  {
    "Id": "ALM_20250319_001",
    "AlarmCode": "1001",
    "Publisher": "MCS_SYSTEM",
    "AlarmSource": "P001",
    "AlarmData": "Communication timeout with PLC",
    "AlarmRunState": 1,
    "AlarmDt": "2025-03-19T10:25:30",
    "ReleaseDt": null,
    "Releaser": null
  },
  {
    "Id": "ALM_20250319_002",
    "AlarmCode": "2001",
    "Publisher": "AMR_001",
    "AlarmSource": "AMR_001",
    "AlarmData": "Low battery warning",
    "AlarmRunState": 1,
    "AlarmDt": "2025-03-19T10:30:00",
    "ReleaseDt": null,
    "Releaser": null
  }
]
```

**인증:** 불필요

**설명:**
- MCS 시스템의 알람 정보를 반환합니다.
- 비동기로 처리됩니다.

---

## CommandController

AMR 명령 및 시스템 제어 명령을 처리하는 API입니다.

### 1. PUT /api/Command/Move

AMR 이동 명령을 전송합니다.

**Endpoint:** `PUT /api/Command/Move`

**Request Body:**
```json
{
  "Target": "AMR_001",
  "Command": "move",
  "Node": {
    "ObjNo": 1001,
    "X": 1500,
    "Y": 2000
  }
}
```

**Response:**
```json
{
  "Success": true,
  "Error": null
}
```

**인증:** JWT Token 필요

**설명:**
- AMR에게 이동 명령을 전송합니다.
- 사용자 정보는 JWT Token에서 추출됩니다.

---

### 2. PUT /api/Command/CallState

호출 상태를 변경합니다.

**Endpoint:** `PUT /api/Command/CallState`

**Request Body:**
```json
{
  "id": "REQ_001",
  "call": "AA001_20250319_P001",
  "state": "CANCELLED"
}
```

**Response:**
```json
{
  "Result": true,
  "Message": "Call state changed successfully"
}
```

**인증:** JWT Token 필요

**설명:**
- 호출의 상태를 변경합니다.
- 사용자 정보는 JWT Token에서 추출됩니다.
- state 값: WAITING, ASSIGNED, COMPLETED, CANCELLED 등

---

### 3. PUT /api/Command/CommandState

명령 상태를 변경합니다.

**Endpoint:** `PUT /api/Command/CommandState`

**Request Body:**
```json
{
  "id": "REQ_002",
  "mission": "CMD_20250319_001",
  "state": "PAUSED"
}
```

**Response:**
```json
{
  "Result": true,
  "Message": "Command state changed successfully"
}
```

**인증:** JWT Token 필요

**설명:**
- 명령의 상태를 변경합니다.
- 사용자 정보는 JWT Token에서 추출됩니다.
- state 값: READY, RUNNING, PAUSED, COMPLETED, FAILED 등

---

### 4. PUT /api/Command/manualcall

수동 호출을 생성합니다.

**Endpoint:** `PUT /api/Command/manualcall`

**Request Body:**
```json
{
  "id": "MANUAL_REQ_001",
  "code": "MC001",
  "place": "P001",
  "payloadType": "PALLET",
  "quantity": "2",
  "param": "0",
  "repeatCount": 1,
  "repeatDelay": 0
}
```

**Response:**
```json
{
  "Result": true,
  "Message": "Manual call created successfully"
}
```

**인증:** JWT Token 필요

**설명:**
- 수동으로 호출을 생성합니다.
- 사용자 정보는 JWT Token에서 추출됩니다.
- repeatCount: 반복 횟수, repeatDelay: 반복 간 지연시간(초)

---

### 5. PUT /api/Command/manualcommand

수동 명령을 생성합니다.

**Endpoint:** `PUT /api/Command/manualcommand`

**Request Body:**
```json
{
  "id": "MANUAL_CMD_001",
  "subject": "MOVE",
  "start": "P001",
  "dest": "P002",
  "robot": "AMR_001",
  "code": "MANUAL_MOVE_001"
}
```

**Response:**
```json
{
  "Result": true,
  "Message": "Manual command created successfully"
}
```

**인증:** JWT Token 필요

**설명:**
- 수동으로 명령을 생성합니다.
- 사용자 정보는 JWT Token에서 추출됩니다.
- subject: 명령 종류 (MOVE, CHARGE, DOCK 등)

---

### 6. PUT /api/Command/retrycommand

명령을 재시도합니다.

**Endpoint:** `PUT /api/Command/retrycommand`

**Request Body:**
```json
{
  "id": "RETRY_REQ_001",
  "mission": "CMD_20250319_001",
  "robot": "AMR_002"
}
```

**Response:**
```json
{
  "Result": true,
  "Message": "Command retry initiated successfully"
}
```

**인증:** JWT Token 필요

**설명:**
- 실패한 명령을 재시도합니다.
- 사용자 정보는 JWT Token에서 추출됩니다.
- robot 파라미터로 다른 로봇에 재할당 가능

---

## 공통 정보

### 인증
- JWT(JSON Web Token) 기반 인증을 사용합니다.
- 인증이 필요한 API는 요청 헤더에 JWT Token을 포함해야 합니다.
- Token에서 사용자 정보(UserId)를 추출하여 사용합니다.

### 응답 형식
- 모든 응답은 JSON 형식입니다.
- Content-Type: `application/json`
- Encoding: `UTF-8`
- Formatting: `Indented` (가독성을 위한 들여쓰기)

### HTTP 상태 코드
- `200 OK`: 요청이 성공적으로 처리됨
- 기타 상태 코드는 인증 실패 등의 경우 반환될 수 있음

### 비동기 처리
- `ObjectController`의 대부분의 GET 메서드는 비동기(`async/await`)로 처리됩니다.
- 대용량 데이터 조회 시에도 서버 성능에 영향을 최소화합니다.

### 캐싱
- `callplaces` API는 1.5초 캐싱을 적용하여 PLC 조회 부하를 줄입니다.

---

## 버전 정보
- 마지막 업데이트: 2025-03-19
- DockRequest 필드 추가 (Docking Out 상태 표시용)

---

## 참고사항
- 일부 조회 API(places, Call, Mission)는 인증 로직이 구현되어 있지 않아 인증 없이 접근 가능합니다.
- 프로덕션 환경에서는 모든 API에 적절한 인증을 적용하는 것을 권장합니다.
