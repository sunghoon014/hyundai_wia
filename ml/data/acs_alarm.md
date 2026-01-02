| Part      | No.   | Contents (Kor)                                             | Contents (Eng)                                                          | LEVEL |
| :-------: | :---: | :--------------------------------------------------------: | :---------------------------------------------------------------------: | :---: |
| 테스크       | 10000 | RFID 감지 안됨                                                 | \[10000\] RFID not detected                                             | Warn  |
| 테스크       | 10001 | 리프트 미션 실패                                                  | \[10001\] Lift mission fail                                             | Warn  |
| 테스크       | 10002 | 턴테이블 미션 실패                                                 | \[10002\] Turntable mission fail                                        | Warn  |
| 테스크       | 10003 | 도킹 중 장애물 감지                                                | \[10003\] Obstacle detected during docking                              | Warn  |
| 테스크       | 10004 | 거치대 도킹 실패                                                  | \[10004\] Wing docking fail                                             | Warn  |
| 테스크       | 10005 | 충전 도킹 실패                                                   | \[10005\] Charge docking fail                                           | Warn  |
| 테스크       | 10006 | 도킹아웃 중 충돌 방지 대기중                                           | \[10006\] Waiting for collision protection during docking out           | Warn  |
| 테스크       | 10007 | 도킹 비정상 완료 감지됨                                              | \[10007\] Docking completion WARN                                       | Warn  |
| 테스크       | 10008 | 설비 인터락으로 인한 정지 상태                                          | \[10008\] Stop-state due to facility interlocks                         | Warn  |
| 테스크       | 10009 | 도킹 인지 실패                                                   | \[10009\] Docking shape recognition fail                                | Warn  |
| 테스크       | 10010 | 도킹 중 장애물 감지용 3d 카메라 연결 실패                                  | \[10010\] Unable to activate cameras during docking                     | Warn  |
| 테스크       | 10011 | 도킹 시작 위치 오차 발생                                             | \[10011\] Docking start position WARN                                   | Info  |
| 테스크       | 10012 | 도킹 센서 감지 안됨 재시도 중                                          | \[10012\] Docking IR sensor not detected. Retrying                      | Info  |
| 테스크       | 10013 | 도킹 시간 초과                                                   | \[10013\] Docking Timeout                                               | Warn  |
| 테스크       | 10014 | 도킹 중 장애물 감지로 인한 일시 정지                                      | \[10014\] Temporary stop due to obstruction detection during docking    | Info  |
| 테스크       | 10015 | 도킹 센서 감지 안됨으로 인한 최종 실패                                     | \[10015\] Docking Fail because IR sensor not detected.                  | Error |
| 테스크       | 10016 | 충전 도킹 실패 재시도 중                                             | \[10016\] Docking CHARGE sensor not detected. Retrying                  | Warn  |
| 테스크       | 10017 | \[PLC\] 에러 리셋                                              | \[10017\] PLC is reset, but Job has not been canceled                   | Error |
| 테스크       | 10018 | 충전 타임아웃                                                    | Charge Timeout                                                          | Info  |
| 주행 (독자)   | 20000 | 경로 재생성                                                     | \[20000\] Try to create path again                                      | Info  |
| 주행 (독자)   | 20001 | 경로 생성 불가                                                   | \[20001\] Unable to create path                                         | Warn  |
| 주행 (독자)   | 20002 | 일시적 주행 제한                                                  | \[20002\] Temporary driving restriction(Not used)                       | Warn  |
| 주행 (독자)   | 20003 | 구동부 슬립 감지                                                  | \[20003\] Wheel slip detected                                           | Warn  |
| 주행 (독자)   | 20004 | 경로 상 장애물 감지로 대기중                                           | \[20004\] Stand by to drive due to obstacle detection on the path       | Info  |
| 주행 (독자)   | 20005 | 주행 시스템 에러                                                  | \[20005\] Driving system WARN                                           | Warn  |
| 주행 (독자)   | 20006 | 주행 중 emergency 혹은 범퍼센서 감지                                  | \[20006\] EMG or Bumper sensor detection while driving(Not used)        | Warn  |
| 주행 (독자)   | 20007 | 주행 중 Cost 처리 지연 중...                                       | \[20007\] Cost handling is delayed while driving                        | Warn  |
| 주행 (독자)   | 20008 | 주행 중 턴테이블 틀어짐                                              | \[20008\] Turntable twisted while driving                               | Warn  |
| 주행 (독자)   | 20009 | 턴테이블 리커버리 실패                                               | \[20009\] Turntable recovery failed                                     | Warn  |
| 카메라       | 20010 | 주행 중 장애물 감지용 3d 카메라 연결 실패                                  | \[20010\] Unable to activate cameras while driving                      | Warn  |
| 주행        | 20011 | 주행 중 후쿠요 센서 감지로 인한 감속                                      | \[20011\] Deceleration due to Fukuyo sensor detects                     | Info  |
| 주행        | 20012 | 주행 중 후쿠요 센서 감지로 인한 정지                                      | \[20012\] Entirely stop due to Fukuyo sensor detects                    | Info  |
| 주행        | 20013 | 주행 중 사전 허가 미획득으로 인한 일시 정지                                  | \[20013\] Pause by pass approval while driving                          | Warn  |
| 주행        | 20014 | 정의되지 않은 후쿠요 센서 데이터 수신으로 인한 일시 정지                           | \[20014\] Pause by undefinded Hokuyo sensor data                        | Warn  |
| H/W       | 30000 | Unicon 보드와의 통신 연결이 끊어짐                                     | \[30000\] Lost communication connection with Unicorn board              | Warn  |
| H/W       | 30001 | 배터리 부족 (20% 이하)                                            | \[30001\] Battery Low (20% or less)                                     | Info  |
| H/W       | 30002 | EMG 버튼                                                     | \[30002\] EMG Button pressed                                            | Info  |
| H/W       | 30003 | BMS로부터 배터리 상태 받지 못함                                        | \[30003\] Battery status not received from BMS                          | Warn  |
| H/W       | 30004 | wrong motor direction                                      | \[30004\] Wrong motor direction                                         | Warn  |
| H/W       | 30005 | Unicon crc 오류                                              | \[30005\] Unicon crc WARN                                               | Warn  |
| H/W       | 30006 | 모터드라이브 리셋 조치됨                                              | \[30006\] Motor drive reset                                             | Warn  |
| H/W       | 30007 | BMS 연결 중                                                   | \[30007\] Connecting with BMS                                           | Warn  |
| H/W       | 30008 | Unicon 연결 시도중                                              | \[30008\] Attempting to connect with Unicon                             | Warn  |
| H/W       | 30009 | 1번 라이다 연결되지 않음                                             | \[30009\] LiDAR1 not connected                                          | Warn  |
| H/W       | 30010 | 2번 라이다 연결되지 않음                                             | \[30010\] LiDAR2 not connected                                          | Warn  |
| H/W       | 30011 | 1번 카메라 연결되지 않음                                             | \[30011\] Camera1 not connected                                         | Warn  |
| H/W       | 30012 | 2번 카메라 연결되지 않음                                             | \[30012\] Camera2 not connected                                         | Warn  |
| H/W       | 30013 | PLC 연결 안됨                                                  | \[30013\] PLC not connected                                             | Warn  |
| H/W       | 30014 | IMU 연결 안됨                                                  | \[30014\] IMU not connected                                             | Warn  |
| H/W       | 30015 | 라이다 데이터 이상                                                 | \[30015\] Wrong lidar data                                              | Warn  |
| H/W       | 30017 | 모터드라이브 CAN통신 에러                                            | \[30017\] Motor drive CAN communication WARN                            | Warn  |
| H/W       | 30018 | MQTT 서버 통신 끊김                                              | \[30018\] MQTT server communication disconnected                        | Warn  |
| H/W       | 30019 | ACS 통신 끊김                                                  | \[30019\] ACS communication disconnected                                | Warn  |
| H/W       | 30020 | OSSD 발생                                                    | \[30020\] OSSD signal                                                   | Info  |
| H/W       | 30021 | 충전 신호 해제로 인한 릴레이 해제 시도                                     | \[30021\] Attempting to turn off relay because the charge signal is off | Info  |
| H/W       | 30030 | 디스크 사용량 70 퍼센트 초과                                          | \[30030\] Disk usage exceeds 70 percent                                 | Info  |
| H/W       | 30031 | 디스크 사용량 80 퍼센트 초과                                          | \[30031\] Disk usage exceeds 80 percent                                 | Warn  |
| H/W       | 30032 | 디스크 사용량 90 퍼센트 초과                                          | \[30032\] Disk usage exceeds 90 percent                                 | Error |
| H/W       | 30033 | 메모리 사용량 70 퍼센트 초과                                          | \[30033\] Memory usage exceeds 70 percent                               | Info  |
| H/W       | 30034 | 메모리 사용량 80 퍼센트 초과                                          | \[30034\] Memory usage exceeds 80 percent                               | Warn  |
| H/W       | 30035 | 메모리 사용량 90 퍼센트 초과                                          | \[30035\] Memory usage exceeds 90 percent                               | Error |
| H/W       | 30036 | 라이다 오류 발생                                                  | \[30036\] LIDAR ERROR Occurred                                          | Error |
| H/W       | 30037 | 라이다 워닝 발생                                                  | \[30037\] LIDAR WARN Occurred                                           | Error |
| H/W       | 30038 | 배터리 온도 이상                                                  | \[30038\] BMS Battery Over Temperature                                  | Error |
| H/W       | 30039 | 배터리 전압 이상                                                  | \[30039\] BMS Battery Over Voltage                                      | Error |
| H/W       | 30040 | 배터리 통신 에러(충전중)                                             | \[30040\] BMS Battery Communication Error (Charging)                    | Error |
| H/W       | 30041 | 배터리 온도 이상(주행중)                                             | \[30041\] BMS Battery High Temperature (Driving)                        | Error |
| 주행모터 드라이버 | 40000 | Over Heat                                                  | \[40000\] Over Heat                                                     | Warn  |
| 주행모터 드라이버 | 40001 | Over Voltage                                               | \[40001\] Over Voltage                                                  | Warn  |
| 주행모터 드라이버 | 40002 | Under Voltage - 응급버튼이 눌린 경우                                | \[40002\] Under Voltage                                                 | Warn  |
| 주행모터 드라이버 | 40003 | Short Circuit                                              | \[40003\] Short Circuit                                                 | Warn  |
| 주행모터 드라이버 | 40004 | Emergency Stop - break 해제 상태                               | \[40004\] Not Ready                                                     | Warn  |
| 주행모터 드라이버 | 40005 | Motor/Sensor ERROR                                         | \[40005\] Motor/Sensor Setup Fault                                      | Warn  |
| 주행모터 드라이버 | 40006 | MOSFET failure                                             | \[40006\] MOSFET failure                                                | Warn  |
| 주행모터 드라이버 | 40007 | Default configuration loaded at startup                    | \[40007\] Default configuration loaded at startup                       | Warn  |
| PLC       | 70000 | \[WIA1000 PLC\] 작업 시작 시간 초과 알람                             | \[70000\] \[WIA1000 PLC\] WORK START TIME OVER ALARM                    | Info  |
| PLC       | 70001 | \[WIA1000 PLC\] T2 시간 초과 알람                                | \[70001\] \[WIA1000 PLC\] T2 TIME OVER ALARM                            | Info  |
| PLC       | 70002 | \[WIA1000 PLC\] T5\&T6 시간 초과 알람                            | \[70002\] \[WIA1000 PLC\] T5 \&T6 TIME OVER ALARM                       | Info  |
| PLC       | 70008 | \[PLC\] U\_REQ/L\_REQ 꺼짐 알람                                | \[70008\] \[PLC\] U\_REQ/L\_REQ OFF ALARM                               | Error |
| PLC       | 70009 | \[PLC\] READY 꺼짐 알람                                        | \[70009\] \[PLC\] READY OFF ALARM                                       | Error |
| PLC       | 70010 | \[PLC\] 작업 시작 시간 초과 알람                                   | \[70010\] \[PLC\] WORK START TIME OVER ALARM                            | Error |
| PLC       | 70011 | \[PLC\] T2 (물건 받기 전 PLC 내부 동작 불가) 시간 초과 알람            | \[70011\] \[PLC\] T2 TIME OVER ALARM                                    | Error |
| PLC       | 70012 | \[PLC\] T4 (물건 받는 중 물건 끼임, 센서 중복 감지) 시간 초과 알람       | \[70012\] \[PLC\] T4 TIME OVER ALARM                                    | Error |
| PLC       | 70013 | \[PLC\] EMG 알람(PIO)                                        | \[70013\] \[PLC\] EMG ALARM(PIO)                                        | Error |
| PLC       | 70016 | \[WIA300 PLC\] 롤러 알람                                       | \[70016\] \[WIA300 PLC\] ROLLER ALARM                                   | Error |
| PLC       | 70017 | \[WIA300 PLC\] 도어 알람                                       | \[70017\] \[WIA300 PLC\] DOOR ALARM                                     | Error |
| PLC       | 70018 | \[WIA300 PLC\] ACS 명령-센서 불일치 알람                            | \[70018\] \[WIA300 PLC\] ACS COMMAND-SENSOR MISSMATCH ALARM             | Error |
| 주행 (나비프라) | 80000 | ERROR\_DRIVER\_NOT\_START                                  | \[80000\] DRIVER\_NOT\_START                                            | Error |
| 주행 (나비프라) | 80001 | ERROR\_LOCALIZATION\_NOT\_START                            | \[80001\] LOCALIZATION\_NOT\_START                                      | Error |
| 주행 (나비프라) | 80002 | ERROR\_NOT\_ON\_PATH                                       | \[80002\] NOT\_ON\_PATH                                                 | Error |
| 주행 (나비프라) | 80003 | ERROR\_CONFIDENCE\_LOW                                     | \[80003\] CONFIDENCE\_LOW                                               | Error |
| 주행 (나비프라) | 80004 | ERROR\_MAP\_NOT\_LOADED                                    | \[80004\] MAP\_NOT\_LOADED                                              | Error |
| 주행 (나비프라) | 80005 | ERROR\_PAUSED\_BY\_OBSTACLE                                | \[80005\] PAUSED\_BY\_OBSTACLE                                          | Info  |
| 주행 (나비프라) | 80006 | ERROR\_MOTOR\_NOTCONNECTED                                 | \[80006\] MOTOR\_NOTCONNECTED                                           | Error |
| 주행 (나비프라) | 80007 | ERROR\_FRONT\_LIDAR\_SIGNAL\_TIMEOUT                       | \[80007\] FRONT\_LIDAR\_SIGNAL\_TIMEOUT                                 | Error |
| 주행 (나비프라) | 80008 | ERROR\_FRONT\_LIDAR\_CLEAN                                 | \[80008\] FRONT\_LIDAR\_CLEAN                                           | Error |
| 주행 (나비프라) | 80009 | ERROR\_REAR\_LIDAR\_SIGNAL\_TIMEOUT                        | \[80009\] REAR\_LIDAR\_SIGNAL\_TIMEOUT                                  | Error |
| 주행 (나비프라) | 80010 | ERROR\_REAR\_LIDAR\_CLEAN                                  | \[80010\] REAR\_LIDAR\_CLEAN                                            | Error |
| 주행 (나비프라) | 80011 | LOCALIZATION\_LARGE\_CORRECTION                            | \[80011\] LOCALIZATION\_LARGE\_CORRECTION                               | Error |
| 주행 (나비프라) | 80012 | ERROR\_NAVICORE\_NOTCONNECTED                              | \[80012\] NAVICORE\_NOTCONNECTED                                        | Error |
| 주행 (나비프라) | 80013 | ERROR\_PAUSE\_BY\_OBSTACLE\_TIMEOUT                        | \[80013\] PAUSE\_BY\_OBSTACLE\_TIMEOUT                                  | Error |
| 주행 (나비프라) | 80014 | ERROR\_ENCODER\_NOT\_UPDATE                                | \[80014\] ENCODER\_NOT\_UPDATE                                          | Info  |
| 주행 (나비프라) | 80015 | ERROR\_DOCKING\_HEADING\_CTR\_EXCEEDED                     | \[80015\] DOCKING\_HEADING\_CTR\_EXCEEDED                               | Error |
| 주행 (나비프라) | 80016 | ERROR\_FRONT\_CAMERA\_TIMEOUT                              | \[80016\] FRONT\_CAMERA\_TIMEOUT                                        | Error |
| 주행 (나비프라) | 80017 | ERROR\_REAR\_CAMERA\_TIMEOUT                               | \[80017\] REAR\_CAMERA\_TIMEOUT                                         | Error |
| 주행 (나비프라) | 80018 | ERROR\_DOCK\_NOT\_FIND                                     | \[80018\] DOCK\_NOT\_FIND                                               | Error |
| 주행 (나비프라) | 80019 | ERROR\_LICENSE\_IS\_NOT\_CHECKED                           | \[80019\] LICENSE\_IS\_NOT\_CHECKED                                     | Error |
| 주행 (나비프라) | 80020 | ERROR\_PATH\_OUT                                           | \[80020\] PATH\_OUT                                                     | Error |
| 주행 (나비프라) | 80021 | ERROR\_UNDEFINED                                           | \[80021\] UNDEFINED                                                     | Error |
| 주행 (나비프라) | 80022 | ERROR\_PATH\_NOT\_CREATED                                  | \[80022\] PATH\_NOT\_CREATED                                            | Error |
| 주행 (나비프라) | 80023 | ERROR\_DOCKING\_POS\_EXCEED                                | \[80023\] DOCKING\_POS\_EXCEED                                          | Error |
| 주행 (나비프라) | 80024 | ERROR\_DOCKING\_TIMEOUT                                    | \[80024\] DOCKING\_TIMEOUT                                              | Error |
| 주행 (나비프라) | 80025 | ERROR\_PAUSE\_BY\_LIDAR\_OBSTACLE                          | \[80025\] PAUSE\_BY\_LIDAR\_OBSTACLE                                    | Info  |
| 주행 (나비프라) | 80026 | ERROR\_PAUSE\_BY\_CAMERA\_OBSTACLE                         | \[80026\] PAUSE\_BY\_CAMERA\_OBSTACLE                                   | Info  |
| 주행 (나비프라) | 80027 | ERROR\_PAUSE\_BY\_ANOTHER\_ROBOT\_OBSTACLE                 | \[80027\] PAUSE\_BY\_ANOTHER\_ROBOT\_OBSTACLE                           | Info  |
| 주행 (나비프라) | 80028 | ERROR\_MOTOR\_DRIVER\_RESPONSE\_TIMEOUT                    | \[80028\] MOTOR\_DRIVER\_RESPONSE\_TIMEOUT                              | Info  |
| 주행 (나비프라) | 80029 | ERROR\_PAUSED\_BY\_DOCK\_OUT\_T\_ZONE\_OBSTACLE            | \[80029\] PAUSED\_BY\_DOCK\_OUT\_T\_ZONE\_OBSTACLE                      | Info  |
| ACS 감지    | 3     | POWER\_OFF                                                 | POWER\_OFF                                                              | Error |
| ACS 감지    | 6     | ROBOT\_MANUAL\_OPERATION\_STATUS                           | ROBOT\_MANUAL\_OPERATION\_STATUS                                        | Error |
| ACS 감지    | 11    | ACS\_ERROR\_WHILE\_NAVIGATING\_THE\_ROUTE                  | ACS\_ERROR\_WHILE\_NAVIGATING\_THE\_ROUTE                               | Warn  |
| ACS 감지    | 12    | ERROR\_OCCURRED\_WHILE\_SENDING\_JOB\_COMMAND              | ERROR\_OCCURRED\_WHILE\_SENDING\_JOB\_COMMAND                           | Warn  |
| ACS 감지    | 30    | WORK\_DELAY                                                | WORK\_DELAY                                                             | Warn  |
| ACS 감지    | 45    | MAP\_VERSION\_IS\_DIFFERENT                                | MAP\_VERSION\_IS\_DIFFERENT                                             | Warn  |
| ACS 감지    | 46    | COMMUNICATION\_ERROR                                       | COMMUNICATION\_ERROR                                                    | Warn  |
| ACS 감지    | 51    | INOPERATIVE\_AFTER\_COMPLETION\_OF\_SENDING\_TASK\_COMMAND | INOPERATIVE\_AFTER\_COMPLETION\_OF\_SENDING\_TASK\_COMMAND              | Warn  |
| ACS 감지    | 100   | HARD\_DISK\_CAPACITY\_EXCEEDED                             | HARD\_DISK\_CAPACITY\_EXCEEDED                                          | Error |
| ACS 감지    | 700   | AMR\_COLLISION\_RISK\_WARNING                              | AMR\_COLLISION\_RISK\_WARNING                                           | Warn  |
| ACS 감지    | 701   | WATING\_FOR\_MISSION\_START\_COLLISION\_AVOIDANCE\_DECTION | WATING\_FOR\_MISSION\_START\_COLLISION\_AVOIDANCE\_DECTION              | Info  |
