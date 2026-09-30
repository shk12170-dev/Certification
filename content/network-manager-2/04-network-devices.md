---
title: 네트워크 운용기기
cert: network-manager-2
order: 4
---

# 4과목. 네트워크 운용기기

## 1. 장비 비교
| 장비 | 계층 | 역할 | 도메인 |
|---|---|---|---|
| 리피터 | 1 | 신호 증폭·재생 | 충돌·브로드캐스트 모두 공유 |
| 허브 | 1 | 멀티포트 리피터 | 충돌 1개 |
| 브리지 | 2 | MAC 학습, 세그먼트 분리 | 충돌 분리 |
| **L2 스위치** | 2 | MAC 테이블 포워딩 | **포트별 충돌 도메인**, 브로드캐스트 1개(VLAN 없을 때) |
| **L3 스위치** | 3 | 스위칭 + 라우팅(VLAN 간) | |
| **라우터** | 3 | 서로 다른 네트워크 연결 | **브로드캐스트 분리** |
| 게이트웨이 | 4~7 | 프로토콜 변환 | |
| 방화벽/IPS | 3~7 | 접근 제어 / 침입 차단 | |

## 2. 스위치 동작
- **Learning**(출발지 MAC 학습) → **Flooding**(목적지 모르면 전체 전송) → **Forwarding** → **Filtering** → **Aging**(기본 300초)
- 스위칭 방식: **Store-and-Forward**(프레임 전체 수신·CRC 검사, 안전·지연 큼) / **Cut-through**(목적지 MAC만 보고 즉시, 빠름·오류 전달) / Fragment-free(64B 확인)
- **VLAN**: 논리적 브로드캐스트 도메인 분리, 802.1Q 태그(4바이트, VLAN ID 12비트=1~4094). 트렁크 포트(태그 전달), 액세스 포트(단일 VLAN). VLAN 간 통신은 L3 필요(Router-on-a-stick, L3 스위치)
- **STP**(802.1D): 루프 방지. 루트 브리지 선출(가장 낮은 Bridge ID = 우선순위+MAC), 포트 상태 Blocking → Listening → Learning → Forwarding. RSTP(802.1w) 빠른 수렴
- 링크 어그리게이션(802.3ad/LACP), 포트 미러링, PoE(802.3af 15.4W / at 30W / bt 60~90W), 포트 보안(MAC 제한)

## 3. 라우터 (Cisco IOS CLI)
### 모드
| 프롬프트 | 모드 | 진입 |
|---|---|---|
| `Router>` | 사용자 EXEC | |
| `Router#` | 특권 EXEC | `enable` |
| `Router(config)#` | 전역 설정 | `configure terminal` |
| `Router(config-if)#` | 인터페이스 | `interface fa0/0` |
| `Router(config-line)#` | 라인 | `line vty 0 4` |

### 기본 설정 예
```
Router> enable
Router# configure terminal
Router(config)# hostname R1
R1(config)# enable secret cisco
R1(config)# interface g0/0
R1(config-if)# ip address 192.168.1.1 255.255.255.0
R1(config-if)# no shutdown
R1(config-if)# exit
R1(config)# ip route 10.0.0.0 255.0.0.0 192.168.1.2      ! 정적 라우팅
R1(config)# router rip / router ospf 1
R1# show running-config | show ip route | show ip interface brief | show interfaces
R1# copy running-config startup-config                   ! 저장 (= write memory)
```
- 설정 파일: running-config(RAM) / startup-config(NVRAM). IOS는 Flash
- 패스워드 복구: ROMMON(컨피그 레지스터 0x2142)
- 원격 접속: Telnet(평문)/SSH, 콘솔 케이블(롤오버)
- **ACL**: 표준(1~99, 출발지만) / 확장(100~199, 프로토콜·포트 포함). 마지막에 암묵적 deny any. 적용 `ip access-group 100 in|out`
  - 와일드카드 마스크: 서브넷 마스크의 반전 (255.255.255.0 → 0.0.0.255)
- NAT: 정적 / 동적 / PAT(overload). `ip nat inside/outside`

## 4. 보안 장비 · 기술
- **방화벽**: 패킷 필터링 → 스테이트풀 → 애플리케이션(프록시) → NGFW. DMZ 구성
- **IDS**(탐지, 수동) vs **IPS**(차단, 인라인). 시그니처/이상 탐지
- **VPN**: IPsec(**AH** 인증·무결성, **ESP** 암호화 포함, 전송/터널 모드, IKE), SSL VPN, L2TP, PPTP
- 대칭키(DES, 3DES, **AES**, SEED) vs 비대칭키(**RSA**, ECC). 해시(MD5, SHA). 전자서명, PKI/인증서
- **공격 유형**
  - DoS/DDoS, **SYN Flooding**(반개방 연결 소진), **Smurf**(ICMP 브로드캐스트 증폭), **Ping of Death**, **Land**(출발=목적 주소), **Teardrop**(단편 오프셋 조작)
  - **ARP 스푸핑**, IP 스푸핑, 스니핑, 세션 하이재킹, DNS 스푸핑
  - 웹: SQL 인젝션, XSS, CSRF / 악성코드: 바이러스·웜·트로이목마·랜섬웨어

## 5. 네트워크 관리 (SNMP)
- 구성: 관리자(NMS) - 에이전트 - **MIB**(관리 정보 트리, OID)
- 포트 UDP 161(질의), 162(Trap)
- 동작: Get, GetNext, GetBulk, Set, Response, **Trap**(에이전트→관리자 자동 통보), Inform
- 버전: v1/v2c(커뮤니티 문자열, 평문), **v3**(인증·암호화)
- 관리 기능 5가지(FCAPS): 장애·구성·계정·성능·보안
- 도구: ping, traceroute, netstat, Wireshark(패킷 분석), tcpdump, iperf(대역폭), 케이블 테스터, OTDR(광)

## 6. 케이블/장비 문제 해결
- 계층별 접근(Bottom-up): 물리(케이블/LED) → 링크(스위치 포트) → IP 설정 → 라우팅 → 응용
- `ping 127.0.0.1`(TCP/IP 스택) → 자신 IP(NIC) → 게이트웨이 → 외부 IP → 도메인(DNS)
- 듀플렉스 불일치, 잘못된 VLAN, 서브넷 마스크 오류, 기본 게이트웨이 누락, IP 충돌이 흔한 원인

## ✍️ 연습문제
1. 브로드캐스트 도메인을 분리하는 장비? → **라우터**(또는 VLAN)
2. 프레임 전체를 받아 CRC 검사 후 전달하는 스위칭? → **Store-and-Forward**
3. 확장 ACL 번호 범위? → **100~199**
4. SNMP 에이전트가 이벤트를 자동 통보하는 메시지? → **Trap**
5. 출발지와 목적지 주소를 같게 만들어 보내는 공격? → **Land Attack**
6. 루프 방지 프로토콜? → **STP(802.1D)**
