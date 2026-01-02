# HACS.WebBackend API 문서

## 목차
- [1. User Controller](#1-user-controller)
- [2. Work Order Controller](#2-work-order-controller)
- [3. Object Controller](#3-object-controller)
- [4. Mission Controller](#4-mission-controller)
- [5. Command Controller](#5-command-controller)
- [6. Traffic Controller](#6-traffic-controller)
- [7. Resource Controller](#7-resource-controller)
- [8. PLC Controller](#8-plc-controller)
- [9. Record Controller](#9-record-controller)
- [10. System Controller](#10-system-controller)

---

## 1. User Controller

사용자 인증 및 관리 API

### 1.1 사용자 등록
- **Endpoint**: `PUT /api/user/register`
- **설명**: 새로운 사용자 등록
- **Request Body**:
```json
{
  "userInfo": {
    "UserId": "string",
    "UserName": "string",
    "Password": "string",
    "Email": "string"
  }
}
```
- **Response**:
```json
{
  "Success": true/false
}
```
- **Status Code**: 200 OK, 500 Internal Server Error

### 1.2 로그인
- **Endpoint**: `PUT /api/user/login`
- **설명**: 사용자 로그인 및 JWT 토큰 발급
- **Request Body**:
```json
{
  "userInfo": {
    "UserId": "string",
    "Password": "string"
  }
}
```
- **Response**:
```json
{
  "userInfo": {
    "UserId": "string",
    "UserName": "string",
    "Email": "string",
    "TokenLifetime": 0,
    "ClientId": "string",
    "Roles": ["string"]
  },
  "loginInfo": {
    "Success": true,
    "LoginTime": "2024-01-01T00:00:00",
    "AuthToken": "string"
  }
}
```
- **Status Code**: 
  - 200 OK
  - 401 Unauthorized (잘못된 ID/비밀번호)
  - 403 Forbidden (비활성 사용자)
  - 406 Not Acceptable (최대 사용자 수 초과)

### 1.3 로그아웃
- **Endpoint**: `PUT /api/user/logout`
- **설명**: 사용자 로그아웃
- **Headers**: JWT 토큰 필요
- **Response**: 200 OK

---

## 2. Work Order Controller

작업 오더 관리 API

### 2.1 실행중인 작업 조회
- **Endpoint**: `GET /api/workorder/running`
- **설명**: 현재 실행중이거나 대기중인 작업 오더 목록 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "OrderNo": 0,
    "MissionId": 0,
    "MissionName": "string",
    "StartNo": "string",
    "StartNode": "string",
    "DestNo": "string",
    "DestNode": "string",
    "OST": "Idle/Running",
    "RDT": "2024-01-01T00:00:00"
  }
]
```
- **Status Code**: 200 OK, 401/403 (인증 실패)

### 2.2 작업 이력 조회
- **Endpoint**: `GET /api/workorder/history?hours={hours}`
- **설명**: 특정 시간(시간 단위) 동안의 작업 오더 이력 조회
- **Headers**: JWT 토큰 필요
- **Query Parameters**:
  - `hours` (int): 조회할 시간 범위 (예: 24)
- **Response**: 2.1과 동일한 형식의 배열
- **Status Code**: 200 OK, 401/403 (인증 실패)

### 2.3 작업 오더 삭제
- **Endpoint**: `DELETE /api/workorder/order?orderNo={orderNo}`
- **설명**: 작업 오더 삭제 (미션 관리자 권한 필요)
- **Headers**: JWT 토큰 필요
- **Query Parameters**:
  - `orderNo` (long): 삭제할 작업 오더 번호
- **Response**:
```json
{
  "Success": true/false,
  "Message": "string"
}
```
- **Status Code**: 200 OK, 403 Forbidden (권한 없음)

---

## 3. Object Controller

맵 객체 및 AMR 상태 관리 API

### 3.1 기본 테스트 엔드포인트
- **Endpoint**: `GET /api/object/default`
- **설명**: API 테스트용 기본 엔드포인트
- **Response**: "Hello, Default" (문자열)
- **Status Code**: 200 OK

### 3.2 헬로 테스트 엔드포인트
- **Endpoint**: `GET /api/object/hello`
- **설명**: API 테스트용 헬로 엔드포인트
- **Response**: "Hello, World" (문자열)
- **Status Code**: 200 OK

### 3.3 맵 객체 조회
- **Endpoint**: `GET /api/object/map`
- **설명**: 맵 상의 모든 객체 정보 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "LayoutId": 0,
    "ObjId": 0,
    "ObjType": "string",
    "ObjNo": 0,
    "ObjNM": "string",
    "SubType": 0,
    "X": 0,
    "Y": 0,
    "W": 0,
    "H": 0,
    "R": 0.0,
    "Angle": 0.0,
    "Border": 0,
    "Path": "string",
    "Align": 0,
    "ColorSet": 0,
    "FontSet": 0,
    "Properties": "string",
    "PrcsCD": "string"
  }
]
```
- **Status Code**: 200 OK

### 3.4 맵 스타일 조회
- **Endpoint**: `GET /api/object/mapstyle`
- **설명**: 맵 스타일 정보 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "ObjType": "AMR/Node/Rack 등",
    "StyleType": 0,
    "StyleId": 0,
    "Prop": 0,
    "Font": "Arial",
    "FontSize": 12.0,
    "FontStyle": 0,
    "TextColor": 0,
    "BackColor": 0,
    "SelectedColor": 0,
    "HilightColor": 0,
    "BorderColor": 0,
    "SelBorderColor": 0,
    "Opt": 0,
    "IsDefault": true
  }
]
```
- **Status Code**: 200 OK

### 3.5 AMR 목록 조회
- **Endpoint**: `GET /api/object/amr`
- **설명**: AMR 객체 목록 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "amrId": 0,
    "TypeId": 0,
    "NetId": "001",
    "objNo": 0,
    "objNM": "string",
    "rpX": 0,
    "rpY": 0,
    "rpWidth": 500,
    "rpHeight": 500,
    "heading": 0.0,
    "Host": "192.168.1.100",
    "Port": 11000,
    "RealIP": "192.168.1.100",
    "RealPort": 11000,
    "LiftCnt": 0,
    "IsTrafficInclude": true,
    "MDir": 0,
    "Area": "string",
    "Active": true
  }
]
```
- **Status Code**: 200 OK

### 3.6 AMR 상태 조회
- **Endpoint**: `GET /api/object/status`
- **설명**: AMR 상태 정보 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "NetId": "001",
    "ACSMode": "Auto",
    "AMRStatus": "Idle",
    "Battery": 85,
    "AMRManual": false,
    "X": 1000,
    "Y": 2000,
    "H": 90.0,
    "Connected": true,
    "IsStandby": false,
    "Pause": false,
    "IsSlowDown": false,
    "Ready": true,
    "GICCmdId": "string",
    "TaskId": "string",
    "MissionId": 0,
    "MissionType": "string",
    "State": "string",
    "Loaded": false,
    "PalletType": "string",
    "PalletWidth": 0,
    "PalletHeight": 0,
    "PalletLength": 0,
    "PalletColor": 0,
    "Speed": 0.5,
    "Obstacle": 0,
    "AMRLCCSOnOff": 0,
    "AMRLCCSLevel": 0,
    "AlarmVolumeLevel": 0,
    "IsGetGlobalPlanner": false,
    "IsGetLidarData": false,
    "IsGetObstacleData": false,
    "LidarData": [],
    "ObstacleData": [],
    "LidarRange": 10,
    "CartHorCnt": 0,
    "CartVerCnt": 0,
    "TurnTableStatus": 0,
    "LoadedState": 0,
    "CurrentRackObject": "string",
    "CurrentRackDockOutArea": "string",
    "SupportMultiAlramVolume": false,
    "PathList": [
      {
        "X": 0,
        "Y": 0,
        "H": 0.0,
        "Complete": false
      }
    ],
    "Errors": [
      {
        "Type": "string",
        "Level": "string",
        "Code": 0,
        "Message": "string",
        "Time": "2024-01-01T00:00:00"
      }
    ]
  }
]
```
- **Status Code**: 200 OK

### 3.7 그리드 정보 조회
- **Endpoint**: `GET /api/object/gridinfo`
- **설명**: 그리드 레이아웃 정보 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
{
  "OffsetX": 0,
  "OffsetY": 0,
  "Scale": 1.0,
  "Rotate": 0.0,
  "Version": "1.0",
  "OriginX": 0.0,
  "OriginY": 0.0,
  "Resolution": 0.05,
  "ImageWidth": 1920,
  "ImageHeight": 1080
}
```
- **Status Code**: 200 OK

### 3.8 랙 정보 수정
- **Endpoint**: `PUT /api/object/rack`
- **설명**: 랙 정보 수정
- **Headers**: JWT 토큰 필요
- **Request Body**:
```json
{
  "ObjNo": 0,
  "X": 0.0,
  "Y": 0.0,
  "Width": 0.0,
  "Height": 0.0,
  "AngleOffset": 0.0,
  "CenterOffset": 0.0,
  "DisplayName": "string",
  "RackStatus": [
    {
      "PLTNo": "string",
      "PLTType": "string",
      "PLTStatus": "string",
      "TransNo": "string",
      "PartNo": "string",
      "PartID": "string",
      "PartLevel": 0,
      "PartCount": 0,
      "PartStatus": 0
    }
  ]
}
```
- **Response**: 200 OK
- **Status Code**: 200 OK

### 3.9 AMR 확장 속성 조회
- **Endpoint**: `GET /api/object/extraproperties`
- **설명**: AMR 확장 속성 정보 조회 (AMR별 그룹별 속성 목록)
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  [
    [
      ["PropertyName", "PropertyValue"]
    ]
  ]
]
```
- **참고**: 3차원 배열 구조 - [AMR][Group][Properties]
- **Status Code**: 200 OK

### 3.10 파레트 정보 조회
- **Endpoint**: `GET /api/object/pallet`
- **설명**: 파레트 정보 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "PrcsCD": "string",
    "PLTType": "string",
    "PLTNo": "string",
    "PLTTagId": "string",
    "ItemNo": "string",
    "PLTInfo": "string",
    "UYN": true
  }
]
```
- **Status Code**: 200 OK

### 3.11 파레트 타입 조회
- **Endpoint**: `GET /api/object/plttype`
- **설명**: 파레트 타입 정보 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "PrcsCD": "string",
    "PLTType": "string",
    "TypeNo": 0,
    "PLTColor": 0,
    "PW": 1200,
    "PL": 1000,
    "PH": 150,
    "POpt": 0,
    "EmptyWeight": 50,
    "FullWeight": 500
  }
]
```
- **Status Code**: 200 OK

### 3.12 랙 상태 조회
- **Endpoint**: `GET /api/object/rackstate`
- **설명**: 랙 상태 정보 조회 (DB)
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "PrcsCD": "string",
    "RackNo": 0,
    "RackNM": "string",
    "RackIndex": 0,
    "PLTNo": "string",
    "PLTType": "string",
    "PLTTypeNo": 0,
    "PLTStatus": 0,
    "TransNo": "string",
    "PartNo": "string",
    "PartID": "string",
    "PartType": 0,
    "PartLevel": 0,
    "PartCount": 0,
    "PartStatus": 0,
    "PartInfoValue": "string",
    "UpTM": "2024-01-01T00:00:00"
  }
]
```
- **Status Code**: 200 OK

### 3.13 랙 상태 조회 (실시간)
- **Endpoint**: `GET /api/object/rackstate2`
- **설명**: 랙 상태 정보 조회 (실시간)
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "ObjNo": 0,
    "X": 0.0,
    "Y": 0.0,
    "Width": 0.0,
    "Height": 0.0,
    "AngleOffset": 0.0,
    "CenterOffset": 0.0,
    "DisplayName": "string",
    "RackStatus": [
      {
        "PLTNo": "string",
        "PLTType": "string",
        "PLTStatus": "string",
        "TransNo": "string",
        "PartNo": "string",
        "PartID": "string",
        "PartLevel": 0,
        "PartCount": 0,
        "PartStatus": 0
      }
    ],
    "PLCReadList": [],
    "PLCWriteList": []
  }
]
```
- **Status Code**: 200 OK

### 3.14 PLC 맵 조회
- **Endpoint**: `GET /api/object/plcmap`
- **설명**: PLC 맵 정보 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "Item1": {
      "PLCId": 0,
      "PrcsCD": "string",
      "PrcsNM": "string",
      "PLCNM": "string",
      "PLCType": "string",
      "ModelNo": "string",
      "Comm": "string",
      "NetId": "string",
      "UseAuth": false,
      "Host": "192.168.1.100",
      "Port": 502,
      "UseSrvAuth": false,
      "InspPeriod": 0,
      "MgmtId": "string",
      "InDT": "2024-01-01T00:00:00",
      "RegDT": "2024-01-01T00:00:00"
    },
    "Item2": [
      {
        "SensorId": 0,
        "PLCId": 0,
        "Station": "string",
        "Name": "string",
        "TagId": "string",
        "Code": "string",
        "BitIdx": 0,
        "IsGroup": false,
        "Write": false,
        "DataType": "INT",
        "OprMode": 0,
        "Enable": true,
        "Comment": "string",
        "UpDT": "2024-01-01T00:00:00"
      }
    ]
  }
]
```
- **참고**: Tuple 구조 - (PLC, List<PLCSensor>)
- **Status Code**: 200 OK

### 3.15 에러 클리어
- **Endpoint**: `PUT /api/object/clearerror`
- **설명**: 시스템 에러 클리어
- **Headers**: JWT 토큰 필요
- **Response**:
```json
{
  "Success": true/false,
  "Message": "string"
}
```
- **Status Code**: 200 OK

### 3.16 AMR 페이로드 조회
- **Endpoint**: `GET /api/object/payload?id={amrId}`
- **설명**: 특정 AMR의 페이로드 정보 조회
- **Headers**: JWT 토큰 필요
- **Query Parameters**:
  - `id` (string): AMR ID
- **Response**:
```json
[
  {
    "RackIndex": 0,
    "PLTNo": "string",
    "PLTType": "string",
    "PartType": 0,
    "PLTTypeNo": 0,
    "PLTStatus": 0,
    "PartID": "string",
    "PartNo": "string",
    "PartCount": 0,
    "PartStatus": 0
  }
]
```
- **Status Code**: 200 OK

### 3.17 에러 코드 조회
- **Endpoint**: `GET /api/object/errorcode`
- **설명**: 시스템 에러 코드 목록 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "EGroup": "string",
    "ECode": 0,
    "ELevel": 0,
    "EMsg": "string",
    "InspItem": [],
    "InspType": 0,
    "UpDT": "2024-01-01T00:00:00",
    "UseGICYN": false
  }
]
```
- **Status Code**: 200 OK

### 3.18 프로세스 조회
- **Endpoint**: `GET /api/object/prcs`
- **설명**: 프로세스 정보 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "PrcsCD": "string",
    "PlantCD": "string",
    "PrcsNM": "string",
    "Comment": "string"
  }
]
```
- **Status Code**: 200 OK

---

## 4. Mission Controller

미션 관리 API

### 4.1 실행중인 미션 조회
- **Endpoint**: `GET /api/mission/running`
- **설명**: 현재 실행중인 미션 목록 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "MissionNo": 0,
    "TaskId": 0,
    "AMRNetId": "string",
    "RunState": "None/Running/End"
  }
]
```
- **Status Code**: 200 OK

### 4.2 미션 상세 정보 조회
- **Endpoint**: `GET /api/mission/detail?id={missionNo}`
- **설명**: 특정 미션의 상세 정보 조회
- **Headers**: JWT 토큰 필요
- **Query Parameters**:
  - `id` (long): 미션 번호
- **Response**:
```json
{
  "MissionNo": 0,
  "Auto": true,
  "Retry": 0,
  "RunCount": 0,
  "ForceCharge": false,
  "ReturnToAutoMode": false,
  "StartNo": 0,
  "DestNo": 0,
  "State": "None/Running/Complete",
  "Canceled": false,
  "JobNodes": [
    {
      "State": "string",
      "Error": 0,
      "ErrorTime": "2024-01-01T00:00:00",
      "Message": "string",
      "ObjNo": 0,
      "ObjNM": "string",
      "ObjType": "string",
      "JobId": 0,
      "JobType": "string",
      "Seq": 0,
      "SubType": 0,
      "Actions": []
    }
  ],
  "EndJobComplete": false,
  "CreateTime": "2024-01-01T00:00:00",
  "StartTime": "2024-01-01T00:00:00",
  "EndTime": "2024-01-01T00:00:00",
  "ProgressRate": 0,
  "ArrivalTime": "string",
  "AMRName": "string",
  "AMRId": 0,
  "AMRNetId": "001",
  "DisplayName": "string",
  "RunState": "None/Running/End",
  "TaskId": "string",
  "TaskNo": "string",
  "IsPatrolMission": false,
  "IsWaitingMission": false,
  "MissionGoTargetNodeNo": 0
}
```
- **Status Code**: 200 OK, 404 Not Found

### 4.3 AMR 미션 목록 조회
- **Endpoint**: `GET /api/mission/amr?id={amrId}`
- **설명**: 특정 AMR의 미션 목록 조회
- **Headers**: JWT 토큰 필요
- **Query Parameters**:
  - `id` (string): AMR ID
- **Response**:
```json
[
  {
    "AMR": "001",
    "GroupNM": "string",
    "MissionNM": "string",
    "MissionId": 0,
    "StartNodeNo": 0,
    "StartNM": "string",
    "EndNodeNo": 0,
    "EndNM": "string",
    "UserId": "string"
  }
]
```
- **Status Code**: 200 OK

### 4.4 수동 미션 생성
- **Endpoint**: `POST /api/mission/manual`
- **설명**: 수동 미션 생성
- **Headers**: JWT 토큰 필요
- **Request Body**:
```json
{
  "AMR": "001",
  "GroupNM": "string",
  "MissionNM": "string",
  "MissionId": 0,
  "StartNodeNo": 0,
  "StartNM": "string",
  "EndNodeNo": 0,
  "EndNM": "string",
  "UserId": "string"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```
- **Status Code**: 200 OK

### 4.5 Place Job 목록 조회
- **Endpoint**: `GET /api/mission/placejobs`
- **설명**: Place Job 목록 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "MissionId": 0,
    "JobId": 0,
    "Place": "string",
    "PlaceJobType": "string",
    "JobOption": 0
  }
]
```
- **Status Code**: 200 OK, 500 Internal Server Error

### 4.6 Place Job 수정
- **Endpoint**: `PUT /api/mission/placejobs`
- **설명**: Place Job 목록 수정
- **Headers**: JWT 토큰 필요
- **Request Body**:
```json
[
  {
    "MissionId": 0,
    "JobId": 0,
    "Place": "string",
    "PlaceJobType": "string",
    "JobOption": 0
  }
]
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```
- **Status Code**: 200 OK

### 4.7 운영 모드 조회
- **Endpoint**: `GET /api/mission/operationmode`
- **설명**: 운영 모드 정보 조회
- **Response**:
```json
{
  "Active": "string",
  "Modes": [
    {
      "ModeCode": "string",
      "ModeName": "string"
    }
  ]
}
```
- **Status Code**: 200 OK

---

## 5. Command Controller

AMR 제어 명령 API (모든 엔드포인트는 JWT 토큰 필요)

### 5.1 작업 취소
- **Endpoint**: `PUT /api/command/cancel`
- **Request Body**:
```json
{
  "Target": "001"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.2 오더 취소
- **Endpoint**: `PUT /api/command/ordercancel`
- **Request Body**:
```json
{
  "Target": "001"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.3 작업 재개
- **Endpoint**: `PUT /api/command/jobresume`
- **Request Body**:
```json
{
  "Target": "001"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.4 작업 완료
- **Endpoint**: `PUT /api/command/jobcomplete`
- **Request Body**:
```json
{
  "Target": "001"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.5 모드 변경
- **Endpoint**: `PUT /api/command/mode`
- **Request Body**:
```json
{
  "Target": "001",
  "Mode": "Auto/Manual/SemiAuto"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.6 이동 명령
- **Endpoint**: `PUT /api/command/move`
- **Request Body**:
```json
{
  "Target": "001",
  "Node": {
    "ObjNo": 0,
    "X": 0,
    "Y": 0
  }
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.7 연결
- **Endpoint**: `PUT /api/command/connect`
- **Request Body**:
```json
{
  "Target": "001",
  "Type": "string"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.8 위치 초기화
- **Endpoint**: `PUT /api/command/initposition`
- **Request Body**:
```json
{
  "Target": "001",
  "X": 0.0,
  "Y": 0.0,
  "H": 0.0
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.9 일시정지
- **Endpoint**: `PUT /api/command/pause`
- **Request Body**:
```json
{
  "Target": "001"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.10 재개
- **Endpoint**: `PUT /api/command/resume`
- **Request Body**:
```json
{
  "Target": "001"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.11 충전
- **Endpoint**: `PUT /api/command/charge`
- **Request Body**:
```json
{
  "Target": "001",
  "Node": {
    "ObjNo": 0,
    "X": 0,
    "Y": 0
  }
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.12 적재
- **Endpoint**: `PUT /api/command/load`
- **Request Body**:
```json
{
  "Target": "001",
  "Node": {
    "ObjNo": 0,
    "X": 0,
    "Y": 0
  },
  "Level": 0
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.13 하역
- **Endpoint**: `PUT /api/command/unload`
- **Request Body**:
```json
{
  "Target": "001",
  "Node": {
    "ObjNo": 0,
    "X": 0,
    "Y": 0
  },
  "Level": 0
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.14 3D 장애물 설정
- **Endpoint**: `PUT /api/command/obstacle3d`
- **Request Body**:
```json
{
  "Target": "001",
  "data": true/false
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.15 LCCS 설정
- **Endpoint**: `PUT /api/command/lccs`
- **Request Body**:
```json
{
  "Target": "001",
  "data": 0,
  "mode": 0
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.16 속도 제한
- **Endpoint**: `PUT /api/command/limitspeed`
- **Request Body**:
```json
{
  "Target": "001",
  "data": 0.5
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.17 알람 볼륨 설정
- **Endpoint**: `PUT /api/command/alarmvolume`
- **Request Body**:
```json
{
  "Target": "001",
  "data": 5,
  "applyAll": false
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.18 라이다 경로 설정
- **Endpoint**: `PUT /api/command/lidarpath`
- **Request Body**:
```json
{
  "Target": "001",
  "type": "string",
  "data1": true/false,
  "data2": "string"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.19 리프트 상하 제어
- **Endpoint**: `PUT /api/command/liftupdown`
- **Request Body**:
```json
{
  "Target": "001",
  "type": 0,
  "data": 0
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.20 에러 리셋
- **Endpoint**: `PUT /api/command/errorreset`
- **Request Body**:
```json
{
  "Target": "001"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.21 페이로드 설정
- **Endpoint**: `PUT /api/command/payload`
- **Request Body**:
```json
{
  "Target": "001",
  "type": "string",
  "payload": [
    {
      "RackIndex": 0,
      "PLTNo": "string",
      "PLTType": "string",
      "PartType": 0,
      "PLTTypeNo": 0,
      "PLTStatus": 0,
      "PartID": "string",
      "PartNo": "string",
      "PartCount": 0,
      "PartStatus": 0
    }
  ]
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```

### 5.22 깨우기
- **Endpoint**: `PUT /api/command/wakeup`
- **Request Body**:
```json
{
  "Target": "001"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```



---

## 6. Traffic Controller

교통 상태 조회 API

### 6.1 교통 상태 조회
- **Endpoint**: `GET /api/traffic/status`
- **설명**: 현재 교통 상태 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
[
  {
    "CollisionNetId": "001",
    "GoWayNetId": "002",
    "StartTime": "2024-01-01T00:00:00",
    "ElapsedTime": "00:05:30",
    "EndTime": "2024-01-01T00:05:30",
    "CollisionType": "string",
    "CollisionState": "string",
    "CollisionPoint": {
      "X": 1000,
      "Y": 2000
    }
  }
]
```
- **Status Code**: 200 OK

---

## 7. Resource Controller

서버 리소스 모니터링 API

### 7.1 서버 리소스 조회 (방식 1)
- **Endpoint**: `GET /api/resource/serverresource`
- **설명**: 서버 CPU, 메모리 사용량 조회
- **Headers**: JWT 토큰 필요
- **Response**:
```json
{
  "CPU": "50.0",
  "availableRam": "8192.0",
  "totalRam": "16384.0",
  "usedRam": "8192.0",
  "dataTime": "2024-01-01 12:00:00"
}
```
- **Status Code**: 200 OK

### 7.2 서버 리소스 조회 (방식 2)
- **Endpoint**: `GET /api/resource/serverresource2`
- **설명**: 서버 리소스 정보 조회 (WorkStatusManager 사용)
- **Headers**: JWT 토큰 필요
- **Response**:
```json
{
  "CpuUsage": 50.0,
  "AvailableRam": 8192.0,
  "UsedRam": 8192.0,
  "TotalRam": 16384.0,
  "DataTime": "2024-01-01 12:00:00"
}
```
- **Status Code**: 200 OK

---

## 8. PLC Controller

PLC 센서 관리 API

### 8.1 PLC 목록 조회
- **Endpoint**: `GET /api/plc/list`
- **설명**: PLC 장치 목록 조회
- **Response**:
```json
[
  {
    "PLCId": 0,
    "PLCNM": "string",
    "PLCType": "string",
    "Host": "192.168.1.100",
    "Port": 502,
    "Stations": ["string"]
  }
]
```
- **Status Code**: 200 OK

### 8.2 센서 목록 조회
- **Endpoint**: `GET /api/plc/sensors?id={plcId}`
- **설명**: 특정 PLC의 센서 목록 조회
- **Query Parameters**:
  - `id` (long): PLC ID
- **Response**:
```json
[
  {
    "PlCId": 0,
    "Station": "string",
    "SensorId": 0,
    "Write": false,
    "Name": "string",
    "TagId": "string",
    "DataType": "string"
  }
]
```
- **Status Code**: 200 OK

### 8.3 센서 값 조회
- **Endpoint**: `GET /api/plc/sensorvalues?id={plcId}`
- **설명**: 특정 PLC의 센서 값 조회 (캐싱 적용)
- **Headers**: JWT 토큰 필요
- **Query Parameters**:
  - `id` (long): PLC ID
- **Response**: 센서 값 배열
- **Status Code**: 200 OK
- **참고**: 1초 이내 재요청시 캐시된 값 반환

### 8.4 센서 값 쓰기
- **Endpoint**: `PUT /api/plc/sensorvalue`
- **설명**: 센서 값 쓰기
- **Headers**: JWT 토큰 필요
- **Request Body**:
```json
{
  "SensorId": 0,
  "Current": "string"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```
- **Status Code**: 200 OK

### 8.5 Place 명령 처리
- **Endpoint**: `PUT /api/plc/placecommand`
- **설명**: Place 명령 처리
- **Headers**: JWT 토큰 필요
- **Request Body**:
```json
{
  "Command": "string",
  "Place": "string"
}
```
- **Response**:
```json
{
  "Success": true/false,
  "Error": "string"
}
```
- **Status Code**: 200 OK

---

## 9. Record Controller

녹화 데이터 관리 API

### 9.1 녹화 목록 조회
- **Endpoint**: `GET /api/record/list?id={recordId}`
- **설명**: 녹화 파일 목록 조회
- **Query Parameters**:
  - `id` (string): 녹화 ID
- **Response**: 파일명 배열 (문자열)
- **Status Code**: 200 OK, 500 Internal Server Error

### 9.2 녹화 데이터 조회
- **Endpoint**: `GET /api/record/data?id={recordId}`
- **설명**: 녹화 데이터 조회
- **Query Parameters**:
  - `id` (string): 녹화 ID ("current" 또는 14자리 날짜시간 문자열)
- **Response**: Base64 인코딩된 바이너리 데이터
- **Status Code**: 200 OK, 204 No Content, 400 Bad Request, 500 Internal Server Error
- **Content-Type**: application/octet-stream

### 9.3 녹화 헤더 조회
- **Endpoint**: `GET /api/record/header?id={recordId}`
- **설명**: 녹화 헤더 정보 조회
- **Query Parameters**:
  - `id` (string): 녹화 ID
- **Response**: Base64 인코딩된 헤더 데이터
- **Status Code**: 200 OK, 204 No Content, 400 Bad Request, 500 Internal Server Error

### 9.4 AMR 녹화 조회
- **Endpoint**: `GET /api/record/amr?id={recordId}`
- **설명**: AMR 녹화 데이터 조회
- **Query Parameters**:
  - `id` (string): 녹화 ID
- **Response**: Base64 인코딩된 AMR 데이터
- **Status Code**: 200 OK, 204 No Content, 400 Bad Request, 500 Internal Server Error

### 9.5 미션 녹화 조회
- **Endpoint**: `GET /api/record/mission?id={recordId}`
- **설명**: 미션 녹화 데이터 조회
- **Query Parameters**:
  - `id` (string): 녹화 ID
- **Response**: Base64 인코딩된 미션 데이터
- **Status Code**: 200 OK, 204 No Content, 400 Bad Request, 500 Internal Server Error

### 9.6 교통 녹화 조회
- **Endpoint**: `GET /api/record/traffic?id={recordId}`
- **설명**: 교통 녹화 데이터 조회
- **Query Parameters**:
  - `id` (string): 녹화 ID
- **Response**: Base64 인코딩된 교통 데이터
- **Status Code**: 200 OK, 204 No Content, 400 Bad Request, 500 Internal Server Error

### 9.7 랙 녹화 조회
- **Endpoint**: `GET /api/record/rack?id={recordId}`
- **설명**: 랙 녹화 데이터 조회
- **Query Parameters**:
  - `id` (string): 녹화 ID
- **Response**: Base64 인코딩된 랙 데이터
- **Status Code**: 200 OK, 204 No Content, 400 Bad Request, 500 Internal Server Error

---

## 10. System Controller

시스템 관리 API

### 10.1 메모리 최적화
- **Endpoint**: `PUT /api/system/memory-optimize`
- **설명**: 가비지 컬렉션을 통한 메모리 최적화 실행
- **Response**:
```json
{
  "Start": "2024-01-01T00:00:00",
  "End": "2024-01-01T00:00:01",
  "Before": 1024,
  "After": 512
}
```
- **Status Code**: 200 OK, 403 Forbidden (관리자 권한 필요)
- **참고**: Before/After는 MB 단위

---

## 인증 (Authentication)

대부분의 API는 JWT 토큰 기반 인증을 사용합니다.

### 토큰 사용 방법
1. `/api/user/login` 엔드포인트를 통해 로그인
2. 응답에서 받은 `AuthToken`을 요청 헤더에 포함
3. 헤더 형식: `Authorization: Bearer {AuthToken}`

### 권한 레벨
- **일반 사용자**: 기본 조회 권한
- **미션 관리자** (ROLE_MISSION_MANAGER): 미션 및 작업 오더 관리 권한
- **관리자** (ROLE_ADMIN): 시스템 관리 권한

### 에러 코드
- **401 Unauthorized**: 인증 실패 (토큰 없음 또는 유효하지 않음)
- **403 Forbidden**: 권한 부족
- **406 Not Acceptable**: 동시 접속자 수 초과

---

## 공통 Response 형식

### 성공 응답
```json
{
  "Success": true,
  "Message": "작업이 성공적으로 완료되었습니다",
  "Data": { /* 데이터 객체 */ }
}
```

### 에러 응답
```json
{
  "Success": false,
  "Message": "에러 메시지",
  "ErrorCode": "ERROR_CODE"
}
```

---

## 버전 정보
- **API 버전**: 1.0
- **프레임워크**: ASP.NET Web API
- **인증**: JWT (JSON Web Token)
- **데이터 형식**: JSON
- **문자 인코딩**: UTF-8

---

## 참고사항

1. 모든 날짜/시간은 ISO 8601 형식을 사용합니다
2. 녹화 ID는 "YYYYMMDDHHMMSS" 형식의 14자리 문자열 또는 "current"를 사용합니다
3. 센서 값 조회는 1초 캐싱이 적용되어 있습니다
4. 바이너리 데이터는 Base64 인코딩되어 전송됩니다
5. 동시 접속 사용자 수에 제한이 있을 수 있습니다
