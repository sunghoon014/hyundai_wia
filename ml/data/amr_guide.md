# 1. Daily Operating

## 1.1. System Start-up

### Place Cycle - Turn ON/OFF

[WEB ACS 설정 절차]

1. 오른쪽 톱니바퀴 클릭
2. Place Cycle 메뉴 선택
3. 검색창에서 제어할 Place 이름 검색
4. Logistics 스위치를 On으로 전환
5. Run 상를을 RUNNING으로 전환

[운영 규칙]

- ON 시점: 생산 시작 전 Logistics/Run 버튼을 `ON`으로 활성화
- OFF 시점: 생산 완료(종업) 후 `OFF`로 변경

[용어 설명]

- 물류 (Logistics): ON/OFF 전환
    - 시스템이 미션을 생성하고 AMR이 이를 수신하여 수행하도록 활성화하는 기능입니다.
    - 가동 중일 때는 반드시 `ON`, 비가동(종업) 시에는 `OFF`여야 합니다.
- RUN: ON 활성화
    - 가동 중인 생산 라인의 경우 필수적으로 켜야 합니다. (대부분 상시 `ON`)
- Note: AMR 동작은 RUN과 Logistics가 모두 `ON`일 때만 가능합니다.

*Reference: 5 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### Place Cycle - Logistics Auto ON/Auto OFF

[기능 설명]

- AUTO ON/OFF: `RUN`이 활성화된 항목들에 대해 자동으로 Logistics를 ON/OFF 하는 기능입니다.
- 확인 사항: 실제 가동 라인에서 `RUN`이 `ON` 상태인지 확인하십시오. (사용하지 않는 장소는 `RUN OFF`)

[설정 경로]

- (WEB ACS) 오른쪽 톱니바퀴 클릭 → Place Cycle

*Reference: 5 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

## 1.2. System Shutdown

### AMR Power Management (End of work)

1. 충전 중인 AMR (Docked)

- (금지) 충전기에 도킹된 상태에서는 절대로 전원을 끄지 마십시오.

2. 미션 대기 중인 AMR (Undocked)

- 충전기 외부에 있는 AMR은 전원을 꺼야 합니다.
- 종료 절차 (WEB ACS):
    1. 해당 AMR 클릭 → Call Cancel (미션 반환 및 대기)
    2. Job Cancel 클릭
    3. Power OFF 클릭

3. 주말 및 공휴일 (Long-term Shutdown)

- 모든 AMR을 충전기에서 분리(Disconnect Charger, 200mm 이상 이동) 후 전원을 끄십시오.
- 전원을 끄기 전 남은 임무를 완료하거나 삭제해야 합니다.

**4. 작업 재개 시 (Start-up)**

- (WEB ACS) 해당 AMR 클릭 → Power ON → Call-Retry 실행

*Reference: 6~7 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### **Battery Circuit Breaker Recovery**

충전기가 도킹된 상태에서 강제로 AMR을 껐을 경우, 과전류 보호를 위해 **배터리 회로 차단기**가 내려갈 수 있습니다. AMR이 켜지지 않을 경우 아래 절차를 따르십시오.

1. AMR 전면 커버를 제거한 후 배터리를 분리합니다.
2. 배터리 뒷면의 차단기 스위치를 켭니다 (ON).
3. 배터리 재조립 후 AMR 전원이 정상적으로 켜지는지 확인합니다.

*Reference: 6~7 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

# 2. Trouble Shooting: Call Assignment

## 2.1. Call 생성 불가 (Signal & Configuration Issue)

**증상:** Call Request 신호가 컨베이어나 설비에 들어오지만, ACS 상에서 Call이 생성되지 않는 경우. Place Cycle was not activated, Call type is different

1. Place Cycle 활성화 확인

- (WEB ACS) 오른쪽 톱니바퀴 → Place Cycle
- 해당 설비(또는 컨베이어)의 Logistics와 RUN이 모두 `ON` / `RUNNING` 상태인지 확인합니다.

2. Call Type 일치 여부 확인

- (WEB ACS) PLC 탭 → BMA Line EQP(예: BM01_PLC01) 또는 Cell Conveyor(예: CS01_PLC01) 클릭
- 설비/컨베이어의 Call Type 값과 AMR의 Call Type 값이 일치하는지 대조합니다.
    - *예시: MC11 PLC Call Type : 14000 vs CS22 PLC Call Type : 14000*
- 조치: 값이 다를 경우 설비(EQP) 또는 컨베이어의 Call Type을 올바른 값으로 수정해야 합니다.

3. Call Create Pause 확인

- (EQP HMI) 화면 우측의 “Call Create Pause” 버튼이 활성화되어 있는지 확인합니다. 활성화 시 콜을 생성하지 않습니다.

4. AMR Idle 상태 확인

- (WEB ACS) 오른쪽 톱니바퀴 → Work Orders
- 해당 AMR의 상태가 `Idle`인지 확인합니다. 만약 이전 작업이 남아있다면 해당 Work Order를 삭제(Delete) 합니다.

*Reference: 8 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

## 2.2. 자재 준비 지연 (Warehouse Delay)

증상: AMR이 할당되지 않고 대기 중이며, 창고 측 준비가 늦어지는 경우.

1. 작업 상태 확인

- (WEB ACS) Mission 탭 → Status 확인

2. 창고 상태 점검

- Process Delay: 창고 내 부품 준비가 지연되고 있는지 확인합니다.
- Preparation Fail: 창고 내 부품 준비 실패 시, 부품 재고 부족 여부 및 창고 설비 에러 상태를 확인합니다.

*Reference: 8 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

## 2.3. 로봇 할당 실패 및 대기

### 로봇 상태 확인 (Check Robot Status)

MCS 상에서 LOAD 명령은 있지만 로봇이 할당되지 않는 경우 다음을 점검합니다.

1. 수동 미션 및 타 미션 간섭

- (WEB ACS) AMR에 수동 미션이 설정되어 있어 ACS가 자동 미션을 할당할 수 없는지 확인합니다.
- 화면 하단 Mission List에서 목적지에 이미 다른 미션이 할당되어 있는지 확인합니다.

2. AUTO 모드 확인

- (WEB ACS) 해당 AMR 클릭 → AMR Info 확인
- AMR이 AUTO 모드일 때만 MCS 미션을 수행할 수 있습니다.

*Reference: 9 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### Way Point(WP) 장기 대기 (Wait at WP)

AMR이 WP에서 장시간 대기하는 경우, 목적지 점유 또는 창고 로직 문제일 수 있습니다.

1. 선행 AMR 작업 대기

- 목적지에 이미 도킹 중이거나 작업을 기다리는 다른 AMR이 있는지 확인합니다. (후속 AMR은 WP에서 대기하게 됨)
    - *예시: AMR A가 MW11에서 작업 중이면, MW11에 할당된 AMR B는 WP에서 대기.*

2. 창고 모드 및 로직 확인

- 창고가 수동 모드이거나 목적지 위치를 제공하지 못하는 경우 → 창고 보전 담당자에게 연락하십시오.
- 로직: AMR이 WP에 도착하면 창고에서 적재 위치(#1 or #2)를 결정합니다. 창고가 위치를 지정해주지 않으면 AMR은 대기합니다.

*Reference: 9 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

## 2.4. 공정 변경 및 오조작 대응

### 차종 변경 시 자재 회수 (Model Replacement)

**주의:** BMA 공급 프로세스(BMA 부품, BSA용 공급, 배터리 셀)의 AMR은 회수 가능하지만, **L/C(Lower Case) 공급 AMR은 회수할 수 없습니다.**

**1. 차종** 변경 시작 시 (Start)

- (EQP HMI) Call Create Pause `ON` → Call Cancel → Work Reset

2. 차종 변경 완료 후 작업 재개 (Resume)

- (EQP HMI) Call Create Pause `OFF`

3. 이미 로드된 자재 회수 프로세스

- Option 1: 작업자 수동 조치
    - (EQP HMI) Call Create Pause `ON` → Call Cancel → Work Reset
    - 작업자가 지게차/Cart를 이용해 수동 Unload → Call Create Pause `OFF`
- Option 2: AMR 및 설비 자동 조치
    - 이미 Load된 자재를 NG 처리하여 배출 포트로 내보냅니다.
    - 해당 배출 포트 (EQP HMI)에서 “Call Priority” 버튼을 눌러 AMR을 호출, 창고로 배출합니다.

*Reference: 10 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 작업자의 실수로 미션 삭제 시 (Accidental Deletion)

AMR이 적재물을 싣고 있는 상태에서 미션이 삭제된 경우, AMR은 즉시 정지합니다. 다음 절차로 복구하십시오.

**Ca**se 1: BMA Pallets (자동 창고로 수동 회수)

- (WEB ACS) 해당 AMR 클릭 → Change to Manual Mode
- BMA Loaded Pallets: MW 11 또는 MW 21 우클릭 → Unload 클릭 → Auto Mode 전환
- BMA Empty Pallets: MW 13 또는 MW 213 우클릭 → Unload 클릭 → Auto Mode 전환

Case 2: BMA Parts Boxes (부품 창고 반환)

- (WEB ACS) 해당 AMR 클릭 → Change to Manual Mode
- MS25(회수 포트) 우클릭 → Unload 클릭 → 드롭다운에서 Unload2 선택 → Auto Mode 전환

Case 3: L/C 및 BSA 완제품

- (WEB ACS) 해당 AMR 클릭 → 목표 지점 우클릭 → Unload 클릭 → Auto Mode 전환
- 또는 지게차를 이용하여 수동으로 배출합니다.

*Reference: 10 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

# 3. Trouble Shooting: Navigation & Obstacle

## 3.1. 경로 이탈 및 위치 상실

### [11] ACS_ERROR_WHILE_NAVIGATING_THE_ROUTE

- 상세 원인: WEB ACS 상에서 관리자가 AMR을 선택하고 Move 명령을 보낼 때, 목적지로 지정한 지점이 정상 경로(Path) 위가 아닌 흰색 배경(주행 불가 영역)인 경우 발생합니다.
- **조치 절차:**
    1. (WEB ACS) 상단의 Job Cancel 버튼을 클릭하여 현재 작업을 취소합니다.
    2. JOG 모드를 활성화하여, AMR을 수동 조작으로 정상 주행 경로(색상이 있는 라인) 위로 이동시킵니다.
    3. AMR이 경로 위에 위치하면, 다시 일반 경로 상의 지점을 목적지로 선택하여 Move 명령을 실행합니다.
- Reference: 16 Page of [KR]AMR Trouble Shoot_v6.1.pptx

### **[80002] ERROR_NOT_ON_PATH**

- **상세 원인:** AMR이 물리적으로 지정된 주행 경로를 벗어난 상태에서 주행을 시도할 때 발생합니다.
- **조치 절차:**
    1. **(WEB ACS)** **Job Cancel**을 클릭하여 작업을 취소합니다.
    2. 현장에서 AMR을 수동으로 밀거나 JOG를 이용하여 **정상 주행 경로 내부**로 다시 옮깁니다.
    3. **(WEB ACS)** **CALL-RETRY** 버튼을 클릭하거나 AMR 모드를 **AUTO**로 전환하여 작업을 재개합니다.
- *Reference: 16 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### [80003] ERROR_CONFIDENCE_LOW (위치 신뢰도 낮음)

- **상세 원인:** AMR이 현재 자신의 위치를 확신하지 못하는 상태입니다. 주로 두 가지 경우에 발생합니다.
    1. AMR이 맵(Map)에 기록되지 않은 미지의 영역(정상 주행경로 밖)으로 이동했을 때.
    2. 주변의 일시적인 장애물(예: 적재된 BMA 팔레트, 이동식 장비 등)이 맵에 기록된 고정된 벽이나 지형지물을 가려서, 라이다 센서가 위치 대조를 할 수 없을 때.
    - *실제 발생 사례: BMA 자동창고 뒷편(임시로 적재된 PLT로 인해 티칭된 Map과 환경이 상이함), BSA#2라인과 L/C 창고 사이 공간(AMR 주행 경로가 아닌 구역)*
- **조치 절차:**
    1. 장애물 제거: 로봇 주변의 시야를 가리는 장애물(팔레트 등)을 제거합니다.
    2. 위치 확인: AMR을 일반 주행 경로 내부로 이동시킨 후, 제자리에서 360도 회전시킵니다. 이때 ACS 상의 로봇 위치가 실제 현장 위치와 일치하는지 확인합니다.
    3. Init Pose 수행: 위 단계를 수행해도 로봇이 위치를 잡지 못하면, 수동으로 위치를 지정해주는 'Init Pose'를 수행합니다.
- **[상세 가이드] Init Pose 수행 방법 (WEB ACS):**
    1. 해당 AMR을 클릭합니다.
    2. 하단 정보창의 Command 탭 MODE에서 Init Position 항목을 선택합니다.
    3. 초기 위치를 지정합니다.
        - Location (Rack/Node): 특정 랙이나 노드 이름을 선택하여 지정.
        - Location (Map icon): 맵 상의 실제 위치를 마우스로 클릭하여 지정.
    4. Heading: AMR이 현재 바라보고 있는 방향(헤딩) 값을 입력합니다. (범위: 0 ~ 360도)
    5. APPLY: 버튼을 눌러 AMR에 명령을 전송합니다.
        - *성공 시: 맵 상의 AMR 위치 아이콘이 지정한 위치로 즉시 변경됩니다.*
- *Reference: 15 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### [80014] ERROR_ENCODER_NOT_UPDATE

- **상세 원인:** 주행 중 모터의 회전수를 감지하는 엔코더 데이터가 정상적으로 업데이트되지 않아, 안전을 위해 AMR이 멈추는 현상입니다.
- 조치 절차:
    1. (WEB ACS) Job Cancel을 클릭합니다.
    2. AMR 기체 측면에 있는 물리적인 RESET 버튼을 누릅니다.
    3. (WEB ACS) CALL-RETRY 또는 AUTO 모드를 실행합니다.
    - *주의사항: 이 알람이 자주 발생하는 경우 하드웨어 문제일 수 있으므로 HYUNDAI-WIA S/V 담당자에게 문의하십시오.*
- *Reference: 16 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

## 3.2. 장애물 감지 및 일시 정지 (Obstacle Detection)

라이다(LIDAR) 또는 3D 카메라 센서가 주행 경로상의 장애물을 감지하여 로봇이 일시 정지하거나 에러를 발생시킨 상황입니다.

### [20004] Obstacles in the AMR path (LIDAR Detection Error)

- 상세 원인: 주행 경로 상에 장애물이 있어 라이다 센서가 이를 감지하고 안전을 위해 정지한 상태입니다. 경로 상에 장애물이 없어야 정상 주행이 가능합니다.
- **조치 절차 (Trouble Shooting):**
    1. 주행 경로 상의 장애물을 제거하십시오.
- *Reference: 11 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### [20014] Stop due to HOKUYO Lidar obstacle detection

- 상세 원인: HOKUYO Lidar가 주변의 장애물, 특히 빛을 강하게 반사하는 안전 반사판(테이프)을 장애물로 인식하여 AMR의 속도를 늦추거나 멈춘 상태입니다.
    - *감지 대상:* 안전콘에 부착된 반사판(은색), 작업자 안전조끼의 반사 테이프(은색) 등
- **조치 절차 (Trouble Shooting):**
    1. 주변의 장애물이나 반사경을 AMR로부터 2m 이상 분리한 후, AMR 측면에 있는 RESET 버튼을 눌러주세요.
    2. Lidar 렌즈에 이물질이 묻었는지 확인하고 제거하세요. (전용 렌즈 클리너나 깨끗하고 부드러운 천으로 부드럽게 닦아주세요.)
    3. 위 두 단계를 완료했는데도 OSSD가 해제되지 않으면 AMR의 전원을 껐다가 다시 켜세요.
    4. AMR을 재시작한 후에도 OSSD 오류가 지속되면 HYUNDAI-WIA의 S/V 담당자에게 문의하세요.
- *Reference: 11 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### [30020] OSSD LIDAR ERROR

- 상세 원인: AMR 근처에 장애물이 있거나 센서 오염으로 인해 OSSD(안전 비상 정지) 신호가 발생하여 이동이 차단된 상태입니다.
- 실제 발생 사례 (Actual Case):
    - AMR 사이드 커버 상단에 이물질이 감지되어 OSSD 알람 발생 → 이물질 제거 필요
    - LIDAR 렌즈의 오염 또는 손상 → 전용 렌즈 클리너로 닦아주세요
- **조치 절차 (Trouble Shooting):**
    1. 주변의 장애물이나 반사경을 2m 이상 분리한 후, AMR 측면에 있는 RESET 버튼을 눌러주세요.
    2. Lidar 렌즈에서 이물질을 제거하세요. (전용 렌즈 클리너나 깨끗하고 부드러운 천으로 부드럽게 닦아주세요.)
    3. 위 두 단계를 완료했는데도 OSSD가 해제되지 않으면 AMR의 전원을 껐다가 다시 켜세요.
    4. AMR을 재시작한 후에도 OSSD 오류가 지속되면 HYUNDAI-WIA의 S/V 담당자에게 문의하세요.
- *Reference: 14 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### **[80025] PAUSED_BY_LIDAR_OBSTACLE / [80005] PAUSED_BY_OBSTACLE / [80029] PAUSED_BY_DOCK_OUT_T_ZONE_OBSTACLE**

- 상세 원인: Lidar에 감지된 물체가 로봇의 '충돌 감지 영역(Safety Zone)'과 겹칠 때 발생합니다. 충돌 감지 영역은 주행 방향 앞의 공간을 모니터링하며, 도킹 및 도킹아웃 프로세스 중에 범위가 변동됩니다.
- 실제 발생 사례 (Actual Case):
    - 도킹 포인트 내부 이물질 검출로 인한 도킹 실패 (실, 팔레트 조각 등)
    - 도킹아웃 시 T-Zone(안전영역) 내 Palette(장애물) 감지로 인한 실패
    - 금속 설비에서 반사된 빛 반사(Light Reflection)를 장애물로 오인
    - AMR 주행 경로 내 장애물 존재
- 조치 절차 (Trouble Shooting):
    1. 실제 로봇 주변에 장애물이 있는지 확인해 주세요.
    2. 도킹 시: 도킹 구역 내부에 장애물이 있는지 확인해 주세요.
    3. 도킹 아웃 시: 로봇 앞과 옆면의 넓은 영역에서 장애물을 감지합니다. 장애물을 제거하세요.
    4. 금속에서 반사된 빛이 장애물로 감지되면 의심되는 모든 구역을 덮습니다. (필요한 경우 비반사 필름을 부착합니다.)
    5. 도킹 시도 중에 발생하는 경우, 도킹을 해제(Undocking)하고 Web ACS에서 Call-Retry를 실행하세요.
- *Reference: 12 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### [80026] PAUSE_BY_CAMERA_OBSTACLE

- 상세 원인: 3D 카메라가 감지한 물체가 로봇의 충돌 감지 영역과 겹칠 때 발생합니다. 주행 중에는 전면의 장애물을, 도킹 중에는 도킹 위치까지의 장애물을 감지합니다. 이 에러는 높이가 있는 공중의 객체도 감지하므로 바닥뿐만 아니라 상부도 확인해야 합니다.
- 실제 발생 사례 (Actual Case):
    - (설비 HMI) 패널 등이 AMR 도킹 위치로 튀어나와 장애물로 인식되어 도킹이 안 되는 경우 → 위치 이동 필요
    - 주행 경로 상에 늘어진 케이블, 호스 등의 방해물이 있는 경우 → 제거 필요
- 조치 절차 (Trouble Shooting):
    1. 실제 로봇 근처에 장애물이 있는지 확인해 주세요.
    2. 도킹하는 경우: 도킹 구역 내부에 장애물이 있는지 확인하세요.
    3. 도킹 아웃 시: 로봇 앞과 옆면의 넓은 영역에서 장애물을 감지합니다. 장애물을 제거하세요.
- *Reference: 13 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

# 4. Trouble Shooting: Docking & H/W

## 4.1. 도킹 실패 및 센서 에러 **(Docking Failure & Sensor Error)**

도킹 관련 에러는 주로 로봇의 하드웨어(IR 센서)와 설비 측의 물리적 가이드(도그플레이트, V마커) 간의 정렬 문제로 발생합니다.

### [10015] Docking failure due to IR sensor detection failure

- **상세 원인:** AMR 밑면에 부착된 IR 센서가 설비 스토퍼의 도그플레이트(Dog Plate)를 정상적으로 감지하지 못해 도킹에 실패한 경우입니다.
- 실제 발생 사례 (Actual Case):
    - 설비의 도그플레이트가 파손된 경우. (작업자가 밟거나 발로 차는 등 강한 충격을 받지 않도록 주의가 필요합니다.)
    - V-마커(V-Marker)의 위치가 틀어지거나 정렬이 맞지 않는 경우.
    - AMR의 IR 센서 높이 설정이 잘못되었거나 동작에 이상이 있는 경우.
- 조치 절차 (Trouble Shooting):
    - Step 1. 진행 중인 도킹 임무 완료 (소프트웨어 조치)
        - (WEB ACS) 상에서 현재 도킹 상태를 확인하고 상황에 맞게 조치합니다.
        - Case A: 완료된 도킹 위치가 '올바른 위치'에 있는 경우
            1. JOB CANCEL 클릭
            2. ERROR RESET 클릭
            3. After Docking 상태로 변경하여 작업 완료 처리
        - Case B: 도킹 위치가 '비정상적인 위치'에 있는 경우
            1. JOB CANCEL 클릭
            2. ERROR RESET 클릭
            3. Docking-Out (Move 명령을 통해 AMR을 도킹 해제)
            4. Before 상태로 변경하여 재시도 준비
    - Step 2. 하드웨어 점검 및 조치
        - 임무 완료/취소 후, 반복적인 에러 발생 시 다음 항목을 점검합니다.
            1. 도그플레이트: 올바른 위치에 있는지 확인하고 파손 여부를 점검합니다.
            2. V-마커: 기울어지거나 회전되지 않았는지 확인하고, 정위치로 조정합니다.
            3. IR 센서: AMR 하단의 센서가 정상 작동하는지, 높이가 적절한지 검사합니다.
- [상세 가이드] WEB ACS에서 도킹 센서 감지 여부 확인 방법
    1. 해당 AMR 클릭 → Information 탭 선택
    2. Category를 IO로 변경하여 센서 신호를 확인합니다.
    - 0.3T AMR (IO sensor for Dock):
        - 후면(문쪽) 도킹만 가능합니다.
        - DOCK OK 조건: 보라색 표시 항목인 Rear와 Front2가 모두 `ON` 되어야 합니다.
        - *WEB ACS 표기:* `rear_docking_check_sensor`, `front_docking_check_sensor2`
    - 1T AMR (IO sensor for Dock):
        - 전방 또는 후방 도킹이 가능합니다.
        - DOCK OK 조건: 도킹 방향에 따라 해당 센서가 `ON` 되어야 합니다.
        - *WEB ACS 표기:* `front_docking_check_sensor1`, `rear_docking_check_sensor`
- *Reference: 17~18 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### [80015] ERROR_DOCKING_HEADING_CTR_EXCEEDED

- 상세 원인: 도킹 시도 중 AMR의 진입 각도(Heading)가 허용 오차 범위를 초과하여 도킹을 중단한 상태입니다.
- 조치 절차 (Trouble Shooting):
    1. (WEB ACS) Job Cancel을 클릭하여 작업을 취소합니다.
    2. 로봇을 수동(Manual/JOG)으로 조작하여 도킹 스테이션에서 완전히 빠져나옵니다(Docking-Out).
    3. CALL-RETRY를 클릭하여 도킹을 처음부터 다시 시도합니다.
- *Reference: 16 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### [80018] ERROR_DOCK_NOT_FIND

- 상세 원인: 도킹 시도 중, 맵(Map) 상의 티칭 좌표와 로봇 센서가 실제로 감지한 V-마커(V-Marker)의 위치가 일치하지 않아 도킹 대상을 찾지 못한 경우입니다.
- 실제 발생 사례 (Actual Case):
    - V-Marker가 수평 또는 수직 방향으로 정렬되지 않고 비뚤어진 경우.
    - (중요 주의사항): 작업자가 이동 중 V-Marker를 밟거나 강한 충격을 주어 위치가 변형되지 않도록 주의해야 합니다.
- 조치 절차 (Trouble Shooting):
    1. (WEB ACS) Job Cancel을 클릭하여 작업을 취소합니다.
    2. 로봇을 수동으로 조작하여 도킹 스테이션에서 빠져나옵니다(Docking-Out).
    3. Before Docking (도킹 전) 상태로 되돌립니다.
    4. (반복 시 조치) 해당 에러가 자주 발생한다면 V-Marker 자체에 문제가 있을 가능성이 높습니다. 마커의 정렬 상태를 교정하거나 필요시 교체해야 합니다.
- *Reference: 19 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

# 5. Trouble Shooting: Model Specific

AMR의 기구적 특성(Box Conveyor vs Pallet Lift)에 따라 발생하는 특화 에러 및 조치 방법입니다.

## 5.1. 0.3T AMR (Box Conveyor)

- **주요 내용:**
    - 단순 작업 중단 및 박스 끼임 (RESUME)
    - 설비 문제로 인한 AMR 대기 (Traffic Jam 해결)
    - 2열 공급/회수 미션 에러 (Port Full, 1단 작업 멈춤, 빈 박스 없음 등)
- **조치:** AMR/설비 HMI 조작 및 Payload 수동 설정.

### 단순 작업 중단 및 박스 끼임 현상 발생 시

- 상세 내용: 컨베이어 이송 중 박스가 단순하게 걸리거나, 작업 지연 알람이 발생하여 멈춘 경우입니다.
- 조치 절차 (Trouble Shooting):
    1. (0.3T AMR HMI) 화면 좌측 하단 끝에 있는 **Main 버튼(F1)**을 클릭합니다.
    2. Main 화면 중앙에 있는 RESUME 버튼을 클릭하여 작업을 재개합니다.
- *Reference: 23 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 설비 문제로 AMR 대기 발생 시 대처 방법 (Traffic Jam)

- 상세 내용: 설비(EQP) 측의 문제로 AMR이 도킹하지 못하고 대기하고 있어, 후속 AMR의 임무 수행이나 이동 경로를 방해하는 경우입니다.
- 조치 절차 (설비 HMI):
    1. AMR INTERFACE 메뉴를 선택합니다.
    2. Call Cancel 클릭 → Call Create Pause 활성화(ON) → Work Reset을 순서대로 실행합니다.
    3. AMR을 **MS25(회수 포트)**로 복귀시킵니다. (Return AMR MS25)
    4. 설비 점검 완료 후 Check and Call → Create Pause OFF
    5. 긴급한 경우 HMI Call Priority 버튼을 사용하여 우선 호출합니다.
- *Reference: 23 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 2열 공급미션 작업 중: 작업을 수행하지 못하는 경우 (Port Full)

- 상세 내용: AMR은 2단계(2열) 공급 임무를 받고 도착했으나, 해당 설비 포트에 이미 물품이 가득 차 있어(Full) 공급을 수행할 수 없는 상황입니다.
- 조치 절차 (Trouble Shooting):
    1. (WEB ACS) JOB Cancel → Error Reset을 실행합니다.
    2. (0.3T AMR HMI) 도킹이 해제되면 컨베이어 도어가 열려있을 수 있으므로 닫아야 합니다.
        - Manual button (F2) 클릭 → 우측 Manual 모드로 전환
        - 인터페이스 화면에서 Close ALL 클릭 (모든 도어 닫힘)
        - 우측 AUTO 모드로 다시 전환
    3. (설비 HMI) Call Cancel → Work Reset
    4. (WEB ACS) Call Retry (창고로 복귀하거나 다음 미션 수행)
- *Reference: 24 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 2열 공급미션 작업 중: 1단 작업만 수행하고 알람이 떠있는 상태

- 상세 내용: 2단 공급 미션을 생성했으나, AMR 도착 전 작업자의 수동 공급 등으로 인해 1단 작업만 수행하고 알람이 발생하여 멈춘 상태입니다.
- 조치 절차 (Trouble Shooting):
    1. (WEB ACS) JOB Cancel → Error Reset
    2. (0.3T AMR HMI)
        - Manual 모드로 전환
        - Close all door 클릭하여 도어 닫기
        - AUTO 모드로 전환
    3. (WEB ACS) Conveyor 탭 선택 → Payload Setting 수정
        - *설정 값:* `1EA – Full` (공급하지 못한 자재), `1EA – None` (공급 완료된 칸)
        - 설정 후 JOB Complete (강제 완료) 클릭
    4. (설비 HMI) Call Cancel → Work Reset
    5. (WEB ACS) AUTO Mode 복귀
- *Reference: 25 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 2열 회수미션 작업 중: 해당 회수포트에 빈 박스가 없어 작업을 못하는 경우

- 상세 내용: 2열 회수 임무를 가지고 도착했으나, 설비 회수 포트에 회수할 빈 박스(Empty Box)가 없어서 작업을 수행할 수 없는 경우입니다.
- 조치 절차 (Trouble Shooting):
    1. (설비 HMI) Call Cancel → Work Reset
    2. (WEB ACS) JOB Cancel → Error Reset
    3. (WEB ACS) Conveyor 탭 선택 → Payload All Clear (적재물 없음으로 설정)
    4. Job complete → Auto Mode
- *Reference: 26 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 2열 회수미션 작업 중: 해당 회수포트에 1단 회수작업만 진행하고 알람이 발생하는 경우

- 상세 내용: 2단 회수 미션을 수행하려 했으나, AMR 도착 전 수동 배출 등으로 인해 1단 작업만 회수하고 알람이 발생한 상태입니다.
- 조치 절차 (Trouble Shooting):
    1. (설비 HMI) Call Cancel → Work Reset
    2. (WEB ACS) JOB Cancel → Error Reset
    3. (0.3T AMR HMI)
        - Manual 모드로 전환
        - 적재 위치 확인 후 Conveyor Door All close
    4. (WEB ACS) Payload Setting 수정
        - *설정 값:* `#1 : Empty` (회수된 박스), `#2 : None` (미회수)
    5. (WEB ACS) MS25(회수 포트) 우클릭 → 드롭다운 메뉴에서 Select Unload 1 클릭
    6. (0.3T AMR HMI) AUTO 모드로 전환
- *Reference: 26 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

## 5.2. 1T AMR (Pallet Lift)

### [70010] 설비 신호 이상으로 작업 시작 지연

- 상세 내용: 설비 측에서 비정상적인 PLC 신호(예: Unload Request 신호 미수신 등)로 인해, AMR이 도킹했음에도 작업을 시작하지 못하고 시간 초과(Time Over) 알람이 발생한 경우입니다.
- 조치 절차 (Trouble Shooting):
    1. (WEB ACS) Job Cancel → Error Reset을 실행합니다.
    2. (설비 HMI) Work Reset을 실행하여 설비 신호를 초기화합니다.
    3. (WEB ACS) AMR 상태를 After Docking으로 변경하여 미션을 재시도하거나 완료 처리합니다.
- *Reference: 27 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 지게차 작업 등 수동 작업으로 인한 Work 없음 (작업 지연)

- 상세 내용: AMR이 도킹되었으나, 지게차 작업 등 작업자의 간섭으로 인해 실제 들어 올려야 할 제품(Work)이 없는 경우입니다.
    - *주요 발생 구역:* BSA Outlet, BMA Outlet, BPA Empty SKID Outlet
- 조치 절차 (Trouble Shooting):
    - Case A: 해당 제품(Work)이 실제로 없어 알람이 발생한 경우
        1. (설비 HMI) Call Cancel → Work Reset
        2. (WEB ACS) Job Cancel → Error Reset → After Docking
    - Case B: 알람 발생 후, 해당 포트에 제품이 다시 준비되어 작업 재개가 가능한 경우
        1. (설비 HMI) Work Reset
        2. (WEB ACS) Job Cancel → Error Reset → After Docking
- *Reference: 27 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 제품 감지 센서(On-board Sensor) 감지 실패 또는 잔류

- 상세 내용: 리프트 Up/Down 작업 후, 제품(SKID) 감지 센서가 켜지지 않거나(미감지), 제품이 없는데도 센서 값이 지워지지 않는(잔류 감지) 경우입니다.
- 조치 절차 (Trouble Shooting):
    - Loading 작업 시 (SKID 휨 등으로 센서 미감지):
        1. (WEB ACS) Job Cancel → Error Reset → Lift down
        2. (설비 HMI) Call Cancel → Work Reset
        3. (현장 조치) AMR을 점검 장소로 이동시킨 후, 해당 PLT를 작업자가 지게차 등을 이용해 수동 배출합니다.
    - Loading 작업 시 (AMR 센서 조정 필요):
        1. (WEB ACS) JOB Cancel → Work Reset → Lift down
        2. (설비 HMI) Call Cancel → Work Reset
        3. (현장 조치) AMR을 점검 장소로 이동시켜 AMR Sensor를 점검합니다. (해당 SKID 이송을 위해 다른 AMR을 할당합니다.)
    - Unload 작업 시 (AMR 센서 조정 필요/잔류 감지):
        1. (WEB ACS) Job Cancel → Error Reset → Lift down
        2. (WEB ACS) Job Complete (강제 완료) → Payload Clear (적재물 없음 처리)
        3. (설비 HMI) Work Reset
        4. (현장 조치) AMR을 점검 장소로 이동시켜 AMR Sensor를 점검합니다.
- *Reference: 28 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### Lift UP/DOWN Sensor 감지 안 됨

- 상세 내용: 리프트 구동 중 상한(Up) 또는 하한(Down) 센서가 감지되지 않아 동작이 멈춘 경우입니다.
- 조치 절차 (Trouble Shooting):
    - Loading 작업 시:
        1. (WEB ACS) Job Cancel → Error Reset → Lift down
        2. (설비 HMI) Call Cancel → Work Reset
        3. (현장 조치) AMR을 점검 장소로 이동하여 센서 점검.
    - Unloading 작업 시:
        1. (WEB ACS) Job Cancel → Error Reset → Lift down
        2. (WEB ACS) Job Complete → Payload Clear
        3. (설비 HMI) Work Reset
        4. (현장 조치) AMR을 점검 장소로 이동하여 센서 점검.
    - Note: 점검이 완료된 AMR은 반드시 이상 유무 확인 후 후공정에 투입하십시오.
- *Reference: 28 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### [진단 가이드] WEB ACS에서 On-board 및 Lift 센서 확인 방법

AMR의 물리적 센서가 정상적으로 신호를 보내는지 WEB ACS에서 확인할 수 있습니다.

1. (WEB ACS) 확인하려는 해당 AMR 클릭
2. Information 탭 선택 → Category를 IO로 변경
3. 아래 센서 항목의 점등 여부(ON/OFF) 확인
    - On board (제품 감지):
        - `mobis_1ton_onboard_sensor 1`
        - `mobis_1ton_onboard_sensor 2`
    - Lift (리프트 위치):
        - `mobis_1ton_lift_up_sensor`
        - `mobis_1ton_lift_down_sensor`

### Lift UP/DOWN 후 Lift 작업이 완료되지 않은 경우 (동작 미완료)

- 상세 내용: 리프트 Up/Down 물리적 동작 후 AMR 센서는 정상이지만, 시스템상에서 리프트 작업 완료 처리가 되지 않는 경우입니다.
- 원인: 주로 장비(EQP) 측의 "Unload REQ / Load REQ" 신호가 AMR로 정상 수신되지 않을 때 발생합니다. (장비 측 센서나 PLC 문제)
- 조치 절차 (Trouble Shooting):
    1. (WEB ACS) Job Cancel → Error Reset
    2. AMR Initial status를 확인하고, 작업 전 상태(Lift Down/Up)로 원복합니다.
    3. After Docking 상태로 변경합니다.
    4. (설비/PLC) PLC Manager Interface를 통해 수동 작업으로 Interface signal ON/OFF 점검이 필요합니다.

# 6. Operational Manual: Control Tools (조작 및 유지보수 매뉴얼)

현장 운영자가 설비(EQP) 및 시스템(ACS)을 제어하는 방법과, AMR의 센서 및 도킹 설비를 유지보수하는 상세 가이드입니다.

## 6.1. EQP HMI 기능 가이드 (설비 인터페이스)

설비 화면(HMI) 우측의 AMR Interface 메뉴에서 사용하는 핵심 기능들입니다. 각 기능의 정의와 구체적인 사용 시나리오를 숙지하십시오.

### 1. Call Cancel (콜 취소)

- 정의: 설비에서 이미 생성된 AMR 호출(Call)을 취소합니다. AMR이 도킹하기 전에 수행해야 합니다. 도킹 후에는 `Job Cancel`을 사용해야 합니다.
- 조작 방법 (설비 HMI):
    1. 우측 Call Cancel 버튼 클릭.
    2. 좌측 하단 **화살표(>)**를 눌러 명령 실행.
    3. 상태창에서 Response Call Cancel 및 Bit Clear 확인. (Request ID, Call Request, Call Response, Robot Assigned, Call Cancel 상태 확인)
- 주요 사용 케이스 및 문제 상황 해결:
    - A. 차종 교체 (Model Replacement):
        - *(상황)* 설비 AUTO 상태에서 이전 차종(예: 2P6S) 콜이 생성된 상태에서, 설비를 Manual로 전환하여 신규 차종(예: 3P4S)으로 교체한 경우.
        - *(문제)* 설비를 다시 AUTO로 돌려도 신규 차종 콜이 생성되지 않음.
        - *(해결)* Call Cancel 실행 후 신규 차종 작업 시작.
    - B. 시업 및 라인 재개 (Start of Shift):
        - *(상황)* 종업 후 작업자가 수동으로 재공을 채우거나 비운 경우, 혹은 재고 조사 후 설비 상태가 변경된 경우.
        - *(문제)* 설비 AUTO 전환 시 이전 공급 콜이 그대로 유지됨.
        - *(해결)* Call Cancel 실행하여 잘못된 콜 삭제.
    - C. 라인 점검 (Line Check):
        - *(상황)* 설비 에러 발생 및 조치 시간이 길어지는 경우.
        - *(문제)* 대기 중인 AMR이 경로를 막아 물류 정체 발생.
        - *(해결)* Call Cancel을 실행하여 AMR을 복귀시킴.
- *Reference: 20~22 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 2. Call Create Pause (콜 생성 일시 정지)

- 정의: 설비가 자재가 필요하거나 배출해야 할 조건이 충족되어도, AMR 호출 신호를 생성하지 않도록 막는 기능입니다. (이미 콜이 생성된 경우는 Call Cancel 사용)
- 조작 방법 (설비 HMI):
    - 우측 Call Create Pause 클릭 → 버튼 활성화(ON) 확인.
- 주요 사용 케이스:
    - AMR 자동 공급이 불필요한 경우 (예: 리워크 제품 연속 투입).
    - 작업자가 지게차 등을 이용해 수동으로 자재를 투입/배출하는 동안.
- *Reference: 20~22 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 3. Call Priority (우선 호출)

- 정의: 특정 설비의 호출을 최우선 순위로 설정하여, 대기 중인 AMR을 가장 먼저 할당받게 합니다.
    - *주의:* 1회만 활성화되며, 해당 작업 완료 후 다음 콜은 정상 우선순위(Priority)가 적용됩니다.
- 조작 방법 (설비 HMI):
    1. 우측 Call Priority 버튼 클릭.
    2. 좌측 하단 **화살표(>)**를 눌러 명령 실행.
    3. 상태창에서 Call Priority 활성화 확인.
- 주요 사용 케이스:
    - 긴급 자재 공급이 필요한 경우.
    - 설비 막힘(Blocking) 해소: NG 팔레트, 셀 공팔레트, BMA 완제품/공팔레트 등이 배출되지 않아 설비가 멈춰 있는 경우 긴급 배출.
- *Reference: 20~22 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

### 4. Forced Docking (강제 도킹)

- 정의: 설비와 AMR의 Call Type이 일치하지 않아도 강제로 도킹 및 작업을 진행하게 합니다.
    - *주의:* 1회만 활성화되며, 다음 도킹부터는 정상 로직(Call Type 일치 확인)이 적용됩니다.
- 조작 방법 (설비 HMI):
    1. 우측 Forced Docking 클릭.
    2. 좌측 상태창에서 Call Request, Call Response, Robot Assigned 확인.
- 주요 사용 케이스 및 추가 참고사항:
    - A. 타 라인 긴급 지원 / 리워크 투입:
        - 기존 라인의 콜을 무시하고, 다른 라인의 AMR을 수동으로 투입하여 작업해야 할 때 사용.
        - *(문제 상황)* BSA #1라인 자동 공급 중 작업을 취소하고(Job Cancel), 강제로 BSA #2라인에 수동 공급하려는 경우.
        - *(해결)* BSA #1라인 Call Cancel 실행(기존 콜 제거) → BSA #2라인에서 Forced Docking 또는 Priority 실행.
    - B. 지게차 수동 투입/회수 시:
        - *(투입 문제)* 지게차로 수동 투입 시 컨베이어가 작동하지 않는 경우 → HMI에서 컨베이어 수동 구동 필요.
        - *(회수 문제)* 공 팔레트 회수 미션이 이미 생성되었으나 지게차로 먼저 회수한 경우 → 배출부 Call Cancel 실행 필수.
- *Reference: 20~22 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

## 6.2. ACS & Manual 기능 가이드 (시스템 제어)

AMR이 BMA 배출 라인에서 품질 검사를 위해 잠시 정차하거나 수동으로 위치를 조정해야 할 때 사용합니다.

- 조작 절차:
    1. (WEB ACS) 해당 AMR 호기 선택.
    2. [중요] BMA 배출 포트에서 Docking-OUT이 완전히 완료된 후 JOB CANCEL을 클릭하십시오.
        - *주의:* 도킹 아웃 도중 취소 시 PLC 신호 꼬임(Interface Error)이 발생할 수 있습니다.
    3. Unlock 버튼 클릭 → JOG 버튼이 활성화되면 키보드나 화면 버튼으로 수동 조작(운전).
        - *주의:* 조작 시 주변 장애물 충돌에 주의하십시오.
    4. 검사 완료 후, CALL-RETRY 버튼을 클릭하여 자동 미션으로 복귀시킵니다. (BMA 배출 → BMA 자동창고)
- *Reference: 32 Page of [KR]AMR Trouble Shoot_v6.1.pptx*

## 6.3. AMR Sensor 점검 & V-marker ASSY current Status and Management

- AMR 센서 사양 및 위치


    | **no** | **NAME** | **SPEC** | **MAKER** | **Quantity** |
    | --- | --- | --- | --- | --- |
    | 1 | 차상 제품감지센서 | SOEG-RTH-M18-PS-K-2L | FESTO | 2 ea |
    | 2 | 근접센서 (리프트 센서) | SIEH-M12B-PS-S-L | FESTO | 2 ea |
    | 3 | 근접센서 (도킹 센서) | PRT12-8DN2 | AUTONICS | 2 ea |

### [1T AMR] 차상 제품감지센서 점검 및 조정

### Type A: 콘-타입 (Cone Type) - BMA/BSA SKID용 (호기: R_107~135)

1. **분해:** T-렌치를 사용하여 커버(1), 커버(2)의 나사를 풉니다. (커버1: 2.5mm, 커버2: 3mm T-렌치 사용)
    - *주의:* 나사가 마모되지 않도록 주의하고, 커버 제거 시 센서가 떨어지지 않도록 잡아야 합니다.
2. **동작 확인:** 센서 후면의 LED 상태를 확인합니다.
    - **대기 (미감지):** 녹색 LED
    - **동작 (감지):** 녹색 + 노란색 LED
3. **감지 높이 조정:** 일자 정밀드라이버를 사용합니다. (시계방향 회전 시 감지 높이 증가 +)
    - ① 반시계 방향으로 돌려 최소 높이로 설정 후, 시계 방향으로 돌려가며 맞춥니다.
    - ② **[중요] SKID별 권장 세팅 높이:**
        - **BMA SKID:** 20 ~ 25 mm
        - **BSA SKID:** 95 ~ 100 mm (프레임이 없어 PLT 하부 커버를 감지해야 함)
    - *주의:* 100mm를 초과 설정 시, 리프트가 내려간 상태에서도 제품을 오감지할 수 있으므로 주의하십시오.
4. **최종 확인 (WEB ACS):** 조립 후 ACS의 `Information` → `IO` 탭에서 센서 동작을 확인합니다.
    - **감지 시:** 녹색 / **미검출 시:** 빨간색
    - `onboard_sensor_1` (전방), `onboard_sensor_2` (후방)

### Type B: 어태치-타입 (Attach Type) - 셀 공급/회수용 (호기: R_101~106)

1. **분해:** ① 상부 커버 제거 → ② Push 버튼 제거 → ③ 센서 브라켓 제거 순서로 탈거합니다.
2. **동작 확인:** 녹색(대기) / 녹색+노란색(동작) LED 확인.
3. **감지 범위 설정:** 센서 버튼을 누른 상태에서 감지가 확인되는 지점까지 조정합니다.
    - **권장 설정 높이:** 5 mm
4. **최종 확인:** 조립 후 WEB ACS `IO` 탭에서 정상 동작 여부를 확인합니다.

### 근접센서 점검 (리프트 & 도킹)

### 1. 리프트 UP/DOWN 센서

1. **점검:** 보전용 커버를 탈거하고(2.5mm T-렌치), 리프트 Up/Down 동작 시 센서 LED가 점등되는지 확인합니다.
2. **위치 조정:**
    - 17mm 스패너로 고정 너트를 풀고, **검출체(프레임)와 센서 간 거리를 2mm**로 조정합니다.
    - **센서 간 높이:** Down 센서를 기준으로 Up 센서까지의 거리는 **100mm**여야 합니다. (녹색 표시 볼트로 조정)

### 2. 도킹 검지 센서

1. **위치:** 1T AMR은 전/후방 각 1개, 0.3T AMR은 후방에 2개 장착되어 있습니다.
2. **높이 조정:**
    - 지면 기준 높이: **16mm** (브라켓 기준 19mm)
    - 바닥에 16mm 높이 세팅용 지그(Zig)를 놓고 센서 높이를 맞춘 후 너트를 조입니다.
3. **동작 확인:** 실제 도킹 포인트에 진입하여 ACS `IO` 탭에서 센서가 감지되는지 확인합니다.

### V-marker ASSY 관리 가이드

- **구성:** V-marker, 오버런 스토퍼, 도그플레이트 ASSY, 자동충전기 브라켓.
- **주요 불량 원인 및 조치:**
    1. **V-Marker:** 위치나 각도가 틀어지면 AMR이 도킹 위치를 찾지 못합니다.
        - **[경고]** 작업자가 V-Marker를 밟거나 발로 차지 않도록 교육하십시오.
        - *조치:* 정렬 상태 점검 및 재조립/교체.
    2. **도그플레이트:** 각도가 틀어지면 도킹을 완료해도 '센서 미감지' 에러(10015)가 발생합니다.
        - *조치:* 위치 교정 및 파손 시 교체.

# 7. Appendix

## 7.1. Reference (용어사전)

| **용어** | **정의** |
| --- | --- |
| **MCS (Material Control System)** | 부품 재고를 관리하고 작업 할당을 내리는 최상위 제어 시스템. PLC(**Programmable Logic Controller**) 신호를 통해 "부품이 더 필요하다"와 같은 요청을 ACS에 전달 |
| **PLC** | 공장 자동화 시스템에서 기계나 장비의 동작을 제어하는데 사용되는 산업용 컴퓨터. 센서 등에서 입력 신호를 받아, 프로그래밍된 로직에 따라 순차적·논리적 연산을 수행하고, 그 결과로 모터, 밸브 등 외부 장치를 제어 |
| WMS (Warehouse Management System) | 창고 내의 재고, 입출고, 보관 위치 등을 효율적으로 관리하는 시스템 |
| BMA | Battery Module Assembly의 약자로, 배터리 모듈 조립 공정을 의미합니다. 배터리 셀들을 모아 하나의 모듈로 만드는 핵심 공정 라인이에요. |
| BSA | Battery System Assembly의 약자로, 배터리 시스템 조립 공정을 의미합니다. BMA에서 만들어진 배터리 모듈들을 차량에 장착할 수 있는 최종 배터리 시스템으로 조립하는 공정 라인입니다. |
| CELL | 배터리 셀을 의미합니다. 배터리의 가장 기본적인 단위로, 에너지를 저장하고 방출하는 역할을 합니다. |
| L/C | Lower Case의 약자로, 하부 케이스를 의미합니다. 배터리 시스템의 하단부를 구성하는 부품 |
| LWR CASE (LL) | Lower Case의 약자로, L/C와 유사하게 하부 케이스를 지칭하는 것으로 보입니다. 문서에서는 `LL`이라는 약어로도 사용되었어요.  |
| SKID RETURN (RC) | 스키드 리턴을 의미합니다. '스키드(Skid)'는 물품을 운반하는 데 사용되는 일종의 운반대나 팔레트를 말하는데, `SKID RETURN`은 사용된 스키드를 회수하거나 재활용하는 라인 또는 구역을 지칭하는 것으로 보입니다. 문서에서는 `RC`라는 약어로도 사용되었어요.  |
| MS (부품 창고) | Material Storage의 약자로, 부품 창고를 의미합니다. BMA나 BSA 공정에 필요한 다양한 부품들을 보관하는 곳이에요.  |
| CS (BMA CELL) | Cell Storage 또는 Cell Supply의 약어로 추정되며, BMA CELL 공정을 지칭합니다. 배터리 셀이 BMA 공정으로 공급되거나 처리되는 구역일 수 있습니다.  |
| MC (BMA) | Module Control 또는 Module Cell의 약어로 추정되며, BMA 공정을 지칭합니다. 배터리 모듈이 조립되는 핵심 공정 구역입니다.  |
| MW (BMA 자동 창고) | Module Warehouse의 약어로 추정되며, BMA 자동 창고를 의미합니다. BMA 공정에서 사용되거나 생산된 모듈을 자동으로 보관하고 관리하는 창고입니다.  |
| BP (BSA) | Battery Pack 또는 Battery Process의 약어로 추정되며, BSA 공정을 지칭합니다. 배터리 시스템이 조립되는 핵심 공정 구역입니다.  |
| SL (BSA) | System Line 또는 System Load의 약어로 추정되며, BSA 공정을 지칭합니다. BSA 공정 내의 특정 라인이나 로드 지점일 수 있습니다.  |
| SP (BSA) | System Production 또는 System Point의 약어로 추정되며, BSA 공정을 지칭합니다. BSA 공정 내의 특정 생산 지점일 수 있습니다.  |
| SC (완제품 창고) | System Complete 또는 Storage Complete의 약어로 추정되며, 완제품 창고를 의미합니다. 최종 조립이 완료된 배터리 시스템을 보관하는 창고입니다 |
| EQP(Equipment) | 물건을 가공하거나 조립하는 물리적인 장비 본체(Hardware/PLC) |
| EQP HMI(Human-Machine Interface) | **작업자가 물리적인 생산 장비(EQP)를 제어, 모니터링 및 관리할 수 있도록 해주는 사용자 인터페이스(S/W 및 터치 패널 하드웨어)** |
| AMR(Autonomous Mobile Robot) | 부품을 실어 나르는 자율주행 운반 로봇  |
| Web ACS(AMR Control System): | AMR을 관리하는 웹 기반 중앙 통제 시스템. 경로 지정, 작업 할당, 실시간 모니터링 |
| **PLT (Pallet)** | 물품을 적재하고 운반하는 데 사용되는 **운반대** |
| **OK (Good)** | **정상품** 또는 **정상적인 상태**를 의미 |
| **NG (Not Good)** | **불량품** 또는 **정상적이지 않은 상태**를 의미 |

## 7.2. Flow Chart (트러블 슈팅 흐름도)

### 1. 도킹 전 트래픽 발생 시 (Pre-Docking Traffic)

AMR이 이동 중 멈춰 서 있거나 경로가 막힌 경우입니다.

- Case A: 설비(Product Line) 문제인 경우
    1. **(설비)** Call Create Pause **ON**
    2. **(설비)** Call Cancel
    3. **(설비)** Work Reset
    4. **(설비)** 라인 점검 및 문제 해결 (Production Line Check)
    5. **(설비)** Call Create Pause **OFF**
    6. **(설비)** 필요시 Call Priority 실행 → **종료(End)**
- **Case B: 창고(Warehouse) 문제인 경우**
    1. **(AMR)** Job Cancel 실행
    2. **(AMR)** 주행 경로 밖으로 이동 (Move AMR Out of Path)
    3. **(창고)** 문제 해결 (Warehouse Trouble Solved)
    4. **(AMR)** 주행 경로 안으로 이동 (Move AMR into Path)
    5. **(AMR)** 상태를 **Before Docking**으로 변경 → **종료(End)**
- 도킹 전
    - AMR 트래픽 발생 → (Judgement) Product Line: Yes → (Product Line) Call Create Pause On → (Product Line) Call Cancel → (Product Line) Work Reset → (Product Line) Production Line Check → (Product Line) Call Create Pause OFF → (Product Line) Call Priority (If necessary) → End
    - AMR 트래픽 발생 → (Judgement) Product Line: No → Warehouse → (AMR) Job Cancel → Move AMR Out of Path → (Product Line) Warehouse Trouble Solved → Move AMR into Path → (AMR) Before Docking  → End

### 2. 도킹 후 에러 발생 시 - 0.3T AMR (Box Conveyor)

- **Step 1: 도킹 상태 확인 (Docking OK?)**
    - **No (실패):** [4.1. 도킹 실패 및 센서 에러] 섹션의 조치 절차 수행.
    - **Yes (성공):** 0.3T HMI 메인 화면에서 **RESUME** 버튼 클릭.
- **Step 2: RESUME 후 해결 여부 (Trouble Solved?)**
    - **Yes (해결됨):** **종료(End)**
    - **No (해결 안 됨):** 1차 초기화 진행
        - (설비) Work Reset → (AMR) Job Cancel → Error Reset → Door Close → **After Docking** 상태 변경.
- **Step 3: 1차 초기화 후 해결 여부 (Trouble Solved?)**
    - **Yes (해결됨):** **종료(End)**
    - **No (해결 안 됨):** 2차 완전 초기화 진행
        - (설비) Call Create Pause ON → Call Cancel → Work Reset
        - (AMR) Job Cancel → Error Reset
- **Step 4: 작업 시점 판단 (Before WORK?)**
    - **Case A: 작업 전 (Yes)**
        1. **(AMR)** After Docking 설정
        2. **(AMR)** 공급(Supply) 미션인 경우: **MS25(회수 포트)**로 복귀 / 회수(Return) 미션인 경우: **복귀(Go back)**
        3. **(설비)** 라인 점검 → Call Create Pause OFF → (필요시) Call Priority → **종료(End)**
    - **Case B: 작업 중 (No)**
        1. **(AMR)** 박스 위치 점검 → 도어 닫기(Door Close) → **Payload 값 수동 설정**
        2. **적재 상태(Load Status) 판단:**
            - **빈 박스(Empty Box):** MS25 Unload 수행 → Auto 전환 → (이후 Case A의 3번 절차와 동일하게 복귀 및 라인 재개)
            - **실물 박스(Full Box) 또는 없음(Nothing):** 즉시 창고 복귀(Go Back) → (이후 Case A의 3번 절차와 동일하게 라인 재개)
- 도킹 후
    - AMR Error 발생 → (Judgement) Docking OK: No → (Judgement) Follow the Docking Trouble shooting
    - AMR Error 발생 → (Judgement) Docking OK: Yes → (AMR) RESUME (on 0.3t AMR HMI) → (Judgement) Trouble Solved: Yes → End
    - AMR Error 발생 → (Judgement) Docking OK: Yes → (AMR) RESUME (on 0.3t AMR HMI) → (Judgement) Trouble Solved: No → (Product Line) Work Reset → (AMR) Job Cancel → (AMR) Error Reset → (AMR) Door Close → (AMR) After Docking
        - → (Judgement) Trouble Solved: Yes → End
        - → (Judgement) Trouble Solved: No → (Product Line) Call Create Pause On → (Product Line) Call Cancel → (Product Line) Work Reset → (AMR) Job Cancel → (AMR) Error Reset
            - → (Judgement) BeforeWORK: Yes → (AMR) After Docking / Supply: MS25 Return / Return: Go back → (Product Line) Production Line Check → (Product Line) Call Create Pause OFF → (Product Line) Call Priority (If necessary) → End
            - → (Judgement) BeforeWORK: No → (AMR) 박스 위치 점검 → (AMR) 도어 닫기 → (AMR) Payload값 설정
                - → (Judgement) Load Status: Empty Box → (AMR) MS25 Unload → (AMR) Auto 전환 / Return MS25 Return → (AMR) After Docking / Supply: MS25 Return / Return: Go back → (Product Line) Production Line Check → (Product Line) Call Create Pause OFF → (Product Line) Call Priority (If necessary) → End
                - → (Judgement) Load Status: Full Box or Nothing → (AMR) After Docking / Supply: MS25 Return / Return: Go back → (Product Line) Production Line Check → (Product Line) Call Create Pause OFF → (Product Line) Call Priority (If necessary) → End

### 3. 도킹 후 에러 발생 시 - 1T AMR (Pallet Lift)

- Step 1: 도킹 상태 확인 (Docking OK?)
    - No (실패): [4.1. 도킹 실패 및 센서 에러] 섹션의 조치 절차 수행.
    - Yes (성공): 제품(SKID) 유무 확인 단계로 진입.
- Step 2: 제품이 있는 경우 (SKID Present: Yes)
    1. (설비) Work Reset
    2. (AMR) Job Cancel → Error Reset → After Docking 상태 변경
    3. 해결 여부 판단 (Trouble Solved?):
        - Yes: 종료(End)
        - No: AMR 센서 점검(Sensor Check) 진행
            - 센서 이상(No): [5.2 센서 점검] 가이드에 따라 조치.
            - 센서 정상(OK): 설비 PLC 및 센서 점검 → (AMR) Lift 상태 초기화(작업 전 상태로 Up/down) → (설비) Work Reset → (AMR) Job Cancel/Error Reset/After Docking 재수행 → 종료(End)
- Step 3: 제품이 없는 경우 (SKID Present: No)
    - Case A: 설비(Product Line) 문제인 경우
        1. (설비) Call Create Pause ON → Call Cancel → Work Reset
        2. (AMR) Job Cancel → Error Reset → After Docking
        3. (설비) 라인 점검 → Call Create Pause OFF → (필요시) Call Priority → 종료(End)
    - Case B: 창고(Warehouse) 문제인 경우
        - 보전반(Call Maintenance) 호출.
- 도킹 후
    - AMR Error 발생 → (Judgement) Docking OK: No → (Judgement) Follow the Docking Trouble shooting
    - AMR Error 발생 → (Judgement) Docking OK: Yes
        - → (Judgement) SKID Present: Yes → (Product Line) Work Reset → (AMR) Job Cancel → (AMR) Error Reset → (AMR) After Docking
            - → (Judgement) Trouble Solved: Yes → End
            - → (Judgement) Trouble Solved: No
                - → (Judgement) AMR Sensor Check: No → Follow the Sensor Trouble shooting
                - → (Judgement) AMR Sensor Check: OK → (Product Line) 설비 PLC 및 Sensor 점검 → (AMR) Lift 상태 초기화 (Up/down the lift to restore the situation before operation) → (Product Line) Work Reset → (AMR) Job Cancel → (AMR) Error Reset → (AMR) After Docking → End
        - → (Judgement) SKID Present: No
            - → (Judgement) Product Line: Yes → (Product Line) Call Create Pause On → (Product Line) Call Cancel → (Product Line) Work Reset → (AMR) Job Cancel → (AMR) Error Reset → (AMR) After Docking → (Product Line) Production Line Check → (Product Line) Call Create Pause OFF → (Product Line) Call Priority (If necessary) → End
            - → (Judgement) Product Line: No → If the Warehouse, Call Maintenance
