# 에러 처리 시나리오
### 1. 도킹 전 알람

- 도킹 하기 전 도킹 위치 정밀 확인 실패
- 알람코드
    - [80018] DOCK_NOT_FIND
- API 활용 에러 클리어 시나리오
    1. AMR 상태 조회

        ```python
        {
            "NetId": “R_101",
            …,
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

        ```

    2. Error Code 확인 : Dock not find
    3. ACS Job Cancel (`PUT /api/command/cancel`)
    4. MCS Command 목록 조회 (`GET /api/Object/Mission`)
    5. MCS CallRetry - 조회된 명령 중 filter

        ```python
          - if (amrNetId &&
                 (e.ASSIGNED_WORKER == amrNetId || e.DATA_1 == amrNetId))
        `PUT /api/Command/retrycommand`
        {
            “mission”: “”,
        // 로봇 미션
            “robot”: “R_101”,
        }

        ```

    6. ACS AMR AUTO로 변환 (`PUT /api/command/mode`)

### 2. 도킹 중 알람

- 도킹 중 하드웨어 등의 이슈로 인해 알람 발생
- 알람코드
    - [80023] DOCKING_POS_EXCEED
    - [80024] DOCKING_TIMEOUT
- API 활용 에러 클리어 시나리오
    1. AMR 상태 조회

        ```python
        {
            "NetId": “R_101",
            …,
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

        ```

    2. Error Code 확인
    3. ACS Job Cancel (`PUT /api/command/cancel`)
    4. 유저에게 충돌 여부 확인 및 수동 이동(Jog 명령) 지시문구 안내
        - 충돌X, 수동 이동으로 안전한 위치로 옮겼다면 아래 부터 실행
    5. MCS Command 목록 조회 (`GET /api/Object/Mission`)
    6. MCS CallRetry – 조회된 명령 중 filter

        ```python
          - if (amrNetId &&
                 (e.ASSIGNED_WORKER == amrNetId || e.DATA_1 == amrNetId))
        `PUT /api/Command/retrycommand`
        {
            “mission”: “”,
        // 로봇 미션
            “robot”: “R_101”,
        }

        ```

    7. ACS AMR AUTO로 변환 (`PUT /api/command/mode`)

### 3. 차상 작업 전 알람

- 적재물 센서 미감지 혹은 설비의 알람 발생 등
- 알람코드
    - [70008] [PLC] U_REQ/L_REQ OFF ALARM
    - [70009] [PLC] READY OFF ALARM
    - [70010] [PLC] WORK START TIME OVER ALARM
    - [70011] [PLC] T2 TIME OVER ALARM
- API 활용 에러 클리어 시나리오
    1. AMR 상태 조회

        ```python
        {
            "NetId": “R_101",
            …,
            "CurrentRackObject": "string",
            "CurrentRackDockOutArea": "string",
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

        ```

    2. Error Code 확인
    3. ACS Job Cancel (`PUT /api/command/cancel`)
    4. 현재 Rack 위치 획득(1번에서 획득한 status)
        - CurrentRackObject 체크
        - 없으면 CurrentRackDockOutArea 체크
    5. PLC 시나리오 실행 – dock_reset (`PUT /api/plc/placecommand` )
        - {Place: Rack, Command: dock_reset}
    6. PLC 시나리오 실행 – dock_ok (`PUT /api/plc/placecommand` )
        - {Place: Rack, Command: dock_ok}
    7. MCS Command 목록 조회 (`GET /api/Object/Mission`)
    8. MCS CallRetry – 조회된 명령 중 filter

        ```python
          - if (amrNetId &&
                 (e.ASSIGNED_WORKER == amrNetId || e.DATA_1 == amrNetId))
        `PUT /api/Command/retrycommand`
        {
            “mission”: “”, // 로봇 미션
            “robot”: “R_101”,
        }

        ```

    9. ACS AMR AUTO로 변환 (`PUT /api/command/mode`)

### 4. 차상 작업 중 알람

- 적재물 이적재 실패 등
- 알람코드
    - [70012] [PLC] T4 TIME OVER ALARM
- API 활용 에러 클리어 시나리오
    1. AMR 상태 조회

        ```python
        {
            "NetId": “R_101",
            …,
            "LoadedState": int,
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

        ```

    2. Error Code 확인
    3. LoadedState 확인
        - 0 : 없음, 1 : 1개(전방), 2: 1개(후방), 3 : 2개(전후방)
    4. ACS Job Cancel (`PUT /api/command/cancel`)
    5. 유저에게 적재물이 정상적으로 적재되었는지 확인 문구
        - 정상적재 되었다면 아래 실행
    6. PLC 시나리오 실행 – dock_reset (`PUT /api/plc/placecommand` )
        - {Place: Rack, Command: dock_reset}
    7. PLC 시나리오 실행 – dock_ok (`PUT /api/plc/placecommand` )
        - {Place: Rack, Command: dock_ok}
    8. 적재물 정보 입력 (`PUT /api/command/payload`)

        ```python
        {
          "Target": “R_101",
          "type": " save",
          "payload": [
            {
              "RackIndex": 0,
              "PLTNo": "",
              "PLTType": "string", // “BMA”
              "PartType": 0,
              "PLTTypeNo": 0,
              "PLTStatus": 0, // 0:None, 1 : Empty, 2 : Full
              "PartID": "",
              "PartNo": "",
              "PartCount": 0,
              "PartStatus": 0 // 1 : OK, 0 : NG
            }
          ]
        }

        ```

    9. ACS AMR AUTO로 변환 (`PUT /api/command/mode`)
