---
title: 보강 - 정보보안·최신 네트워크 기술
cert: network-manager-2
order: 5
---

# 보강. 정보보안 · 최신 네트워크 기술

> ❓ **근거 수준 안내**: "2025년 8월부터 출제기준 변경 적용", "2026년 실기 1회차에 정보보안(NGFW 등) 신유형 다수 출제" 라는 내용을 검색 요약에서 확인했습니다. 세부 변경 항목은 공식 출제기준을 열람하지 못해 확인하지 못했습니다. 아래는 그에 대비해 **정보보안 + 최신 기술을 폭넓게 정리**한 것입니다. 공식 출제기준으로 반드시 대조하세요.

## 1. 정보보안 기본
- **CIA 3요소**: 기밀성(Confidentiality) · 무결성(Integrity) · 가용성(Availability). 추가로 인증, 부인방지(Non-repudiation)
- **접근통제**: DAC(임의, 소유자 결정) / MAC(강제, 등급·레이블) / RBAC(역할 기반)
- **인증 요소**: 지식(암호) · 소유(OTP, 토큰, 인증서) · 존재(생체). 2개 이상 조합 = **MFA**
- **AAA**: 인증(Authentication) · 인가(Authorization) · 계정관리(Accounting)
  | | RADIUS | TACACS+ |
  |---|---|---|
  | 전송 | UDP 1812(인증)/1813(계정) (구 1645/1646) | **TCP 49** |
  | 암호화 | 패스워드만 | **패킷 전체** |
  | 특징 | AAA 결합, 무선·VPN 표준 | 인증/인가/계정 분리, 장비 관리 접속에 적합(Cisco) |
  - Diameter: RADIUS 후속(TCP/SCTP 3868)
- **802.1X**: 포트 기반 접근 제어. **Supplicant**(단말) – **Authenticator**(스위치/AP) – **Authentication Server**(RADIUS). EAP 방식(EAP-TLS, PEAP)
- **NAC**: 접속 단말의 상태(백신·패치)를 점검해 허용/격리

## 2. 방화벽의 진화
| 세대 | 동작 | 계층 |
|---|---|---|
| 패킷 필터링 | IP·포트·프로토콜만 검사, 상태 없음 | 3~4 |
| **스테이트풀 인스펙션** | 연결 상태 테이블 유지, 응답 트래픽 자동 허용 | 3~4 |
| 애플리케이션 게이트웨이(프록시) | 응용 프로토콜 이해, 내용 검사, 성능 낮음 | 7 |
| **UTM** | 방화벽+IPS+안티바이러스+웹필터+VPN 통합 | 3~7 |
| **NGFW** | 애플리케이션 식별(App-ID), **사용자 식별**(User-ID), IPS, **SSL/TLS 복호화 검사**, 위협 인텔리전스, 샌드박스 | 3~7 |
| **WAF** | HTTP/HTTPS 웹 공격(SQL 인젝션, XSS, CSRF, 파일 업로드) 방어, 웹 서버 앞단 | 7 |

- **DMZ**: 외부 공개 서버(웹·메일·DNS)를 내부망과 분리한 중간 영역. 구조 `인터넷 – 방화벽 – DMZ / 내부망`(3-leg) 또는 이중 방화벽
- **방화벽 정책 원칙**
  - 위에서 아래로 검사하며 **첫 번째 일치 규칙**을 적용 → 구체적인 규칙을 위에, 포괄 규칙 아래
  - **기본 거부(Default Deny)**, 최소 권한, 불필요 규칙 정기 정리
  - 예 (출발지, 목적지, 서비스, 동작)
    | # | 출발지 | 목적지 | 서비스 | 동작 |
    |---|---|---|---|---|
    | 1 | 내부망 | DMZ 웹서버 | HTTP/HTTPS | Allow |
    | 2 | 인터넷 | DMZ 웹서버 | HTTPS(443) | Allow |
    | 3 | 관리자 IP | 전체 | SSH(22) | Allow |
    | 4 | Any | Any | Any | **Deny** |
- **NAT/PAT, 포트 포워딩(DNAT)**, VPN 터널 통과 정책

## 3. 침입 탐지·대응
- **IDS**(탐지·경보, 미러링/탭 방식) vs **IPS**(인라인 차단)
- 탐지 방식: **오용(시그니처) 탐지** – 알려진 공격에 정확, **제로데이 탐지 곤란** / **이상(Anomaly) 탐지** – 새로운 공격 탐지 가능, 오탐 많음
- **NIDS**(네트워크: Snort, Suricata) vs **HIDS**(호스트: OSSEC, Tripwire 무결성)
- **SIEM**(로그 수집·상관분석), **SOC**(관제), **허니팟**(미끼), **샌드박스**(악성코드 격리 실행)
- 로그·모니터링: **syslog** 심각도 0 Emergency · 1 Alert · 2 Critical · 3 Error · 4 Warning · 5 Notice · 6 Informational · 7 Debug (UDP 514), **NetFlow/sFlow**(트래픽 흐름 분석), **Wireshark/tcpdump**(패킷 캡처)
  - Wireshark 표시 필터 예: `ip.addr == 10.0.0.5`, `tcp.port == 80`, `http`, `tcp.flags.syn == 1`

## 4. 공격 유형 (추가)
| 공격 | 설명 | 대응 |
|---|---|---|
| **MITM** | 통신 중간 가로채기·변조 | TLS, 인증서 검증, DAI |
| **ARP 스푸핑** | 가짜 ARP 응답으로 MAC 위조 | **DAI**, 정적 ARP |
| **DNS 스푸핑/캐시 포이즈닝** | 위조된 DNS 응답 | **DNSSEC** |
| **MAC 플러딩** | CAM 테이블 고갈 → 허브처럼 동작 | **Port Security** |
| **VLAN 호핑** | 더블 태깅/스위치 스푸핑 | 트렁크 명시 설정, 네이티브 VLAN 변경, 미사용 포트 shutdown |
| **DHCP 스타베이션/스푸핑** | 주소 고갈 / 가짜 DHCP 서버 | **DHCP Snooping** |
| **STP 조작** | 가짜 BPDU로 루트 탈취 | **BPDU Guard, Root Guard** |
| **DDoS** | 분산 서비스 거부, 봇넷 | 트래픽 스크러빙, CDN, Rate limit |
| 세션 하이재킹, 스니핑, 피싱, 랜섬웨어, SQL 인젝션, XSS, CSRF | | |
| **Rogue AP / Evil Twin** | 가짜 AP 로 유인 | 802.1X, WIPS |

### 스위치 보안 설정 (Cisco 예)
```
interface g0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation shutdown    ! restrict / protect / shutdown
 spanning-tree portfast
 spanning-tree bpduguard enable
ip dhcp snooping
ip dhcp snooping vlan 10
interface g0/24
 ip dhcp snooping trust                         ! DHCP 서버 쪽 포트만 trust
ip arp inspection vlan 10                       ! DAI (DHCP snooping 바인딩 테이블 사용)
```
- 미사용 포트 `shutdown` 및 별도 VLAN, 관리 접속은 **SSH**(`transport input ssh`), 암호 `service password-encryption`, `enable secret`, 배너, `login block-for`

## 5. 암호 · PKI · TLS
- **대칭키**(암복호화 키 동일, 빠름): DES(56bit), 3DES, **AES(128/192/256)**, SEED, ARIA(국산)
- **비대칭키**(공개키/개인키): **RSA**, ECC, DSA, Diffie-Hellman(키 교환)
  - 기밀성: **수신자 공개키로 암호화** → 수신자 개인키로 복호화
  - **전자서명**(부인방지·무결성): **송신자 개인키로 서명** → 송신자 공개키로 검증
- **해시**: MD5(128bit, 취약), SHA-1(취약), **SHA-256/SHA-3**. 무결성 확인, 암호 저장(+솔트)
- **PKI**: CA(인증기관), RA, **X.509 인증서**, CRL/OCSP(폐기 확인), 체인 검증
- **TLS**: 핸드셰이크 = 협상(암호 스위트) → 서버 인증서 검증 → 키 교환 → 대칭키로 데이터 암호화. **TLS 1.3 권장**(1.0/1.1, SSL 폐기). HTTPS=HTTP+TLS(443)
- **IPsec**: AH(프로토콜 51, 인증·무결성), ESP(프로토콜 50, 암호화+인증), 전송 모드/터널 모드, **IKE**(UDP 500, NAT-T UDP 4500)
- VPN: Site-to-Site(IPsec), Remote Access(SSL VPN, 443), L2TP/IPsec, WireGuard(UDP, 최신)

## 6. 최신 네트워크 기술
### Wi-Fi 6/6E/7
| 세대 | 표준 | 핵심 |
|---|---|---|
| Wi-Fi 5 | 802.11ac | 5GHz, MU-MIMO(다운링크) |
| **Wi-Fi 6** | 802.11ax | **OFDMA**, 상·하향 MU-MIMO, **BSS Coloring**, **TWT**(절전), 1024-QAM, 밀집 환경 효율 |
| **Wi-Fi 6E** | 802.11ax | **6GHz 대역** 추가 |
| **Wi-Fi 7** | 802.11be | 320MHz 채널, 4096-QAM, **MLO**(다중 링크) |
- **WPA3**: 개인용 **SAE**(동등 인증, 오프라인 사전공격 방어), Enterprise 192-bit, **OWE**(개방망 암호화), WPS 는 취약 → 비활성화
- 이더넷: 2.5G/5G(802.3bz), 10G(802.3an), 25/40/100G(광), **PoE 802.3af(15.4W) / at(30W) / bt(60~90W)**

### 기타
- **SDN**: 제어 평면(Control)과 데이터 평면(Data) 분리, 중앙 컨트롤러, **OpenFlow**, 노스바운드/사우스바운드 API. **NFV**: 네트워크 기능 가상화
- **클라우드/가상화**: IaaS/PaaS/SaaS, VPC, 가상 스위치, VXLAN
- **IoT 프로토콜**: MQTT(TCP 1883/8883, 발행/구독), CoAP(UDP 5683), LoRaWAN, Zigbee, BLE
- **이동통신**: 5G(eMBB, URLLC, mMTC), 네트워크 슬라이싱, 4G LTE
- **제로 트러스트(ZTNA)**: "절대 신뢰하지 말고 항상 검증", 사용자·기기·컨텍스트 기반 최소 권한. **SASE**: 네트워크+보안 클라우드 통합
- **IPv6 전환**: 듀얼스택, 터널링, NAT64/DNS64
- **QoS**: DSCP/ToS, 큐잉(FIFO, PQ, WFQ), 트래픽 셰이핑 vs 폴리싱
- **이중화·고가용성**: HSRP/VRRP(가상 게이트웨이), LACP 링크 묶음, 스택/VSS, STP → RSTP

## 7. 실기 대비 (❓ 유형 미확인, 예상)
- 장비 설정: 라우터/스위치 CLI(인터페이스 IP, 정적·동적 라우팅, VLAN, 트렁크, ACL, NAT), 서버 계정·서비스 설정
- **정보보안 신유형(NGFW 등)**: 정책 작성(허용/차단 규칙 순서), 로그 분석으로 공격 유형 판별, 보안 장비 배치 구성도
- 대비: 최근 기출 8회분(2년치)을 풀고, 교재에 없는 보안 장비 개념(NGFW/WAF/UTM/NAC/SIEM)의 **정의·기능·배치 위치**를 정리

## ✍️ 연습문제
1. 응용 계층까지 식별하고 사용자 단위로 통제하며 SSL 복호화도 지원하는 방화벽은? → **NGFW**
2. 웹 애플리케이션 공격(SQL 인젝션, XSS)을 방어하는 장비는? → **WAF**
3. TACACS+ 의 전송 프로토콜과 포트? → **TCP 49**
4. 스위치에서 불법 DHCP 서버를 막는 기능은? → **DHCP Snooping**
5. 전자서명 생성에 쓰는 키는? → **송신자의 개인키**
6. Wi-Fi 6 의 핵심 다중 접속 기술은? → **OFDMA**
