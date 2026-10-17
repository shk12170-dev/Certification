# 04. NOS (Network Operating System)

> 📌 **실기 대비는 [08_실기_서버 명령어.md](08_실기_서버%20명령어.md)** 의 「윈도우 서버 GUI 8대 영역」(IIS·FTP·DHCP·DNS·사용자/그룹·로컬 보안 정책·서비스·IP 계산)을 보세요. 이 파일은 필기(개념) 중심입니다.

> 윈도우 서버와 리눅스 서버 관리 과목입니다.
> 리눅스 부분은 리눅스마스터 2급과 대부분 겹치므로 [../리눅스마스터 2급/](../리눅스마스터%202급/) 자료를 함께 보세요.

---

## 1. NOS 개요

**네트워크 운영체제(NOS)** = 네트워크 자원(파일·프린터·사용자)을 공유·관리하는 OS

| 구분 | 예 |
|---|---|
| 서버용 윈도우 | Windows Server 2012 / 2016 / 2019 / 2022 |
| 유닉스 계열 | Solaris, AIX, HP-UX |
| 리눅스 계열 | RHEL, CentOS, Rocky, Ubuntu Server, SUSE |
| 기타 | Novell NetWare(구형) |

### 네트워크 모델
| 모델 | 설명 |
|---|---|
| **P2P (동배간)** | 모든 PC가 서버이자 클라이언트. 소규모(10대 이하), 중앙 관리 어려움 |
| **Client/Server** | 전용 서버가 자원 제공. **중앙 집중 관리**, 보안 우수, 대규모에 적합 |

---

## 2. Windows Server — Active Directory

### 핵심 개념 (출제 단골 ★)
| 용어 | 의미 |
|---|---|
| **Active Directory (AD)** | 사용자·컴퓨터·자원을 중앙에서 관리하는 **디렉터리 서비스** |
| **도메인(Domain)** | AD의 기본 관리 단위. 공통 보안 정책 적용 |
| **트리(Tree)** | 연속된 이름 공간을 가진 도메인 집합 |
| **포리스트(Forest)** | 하나 이상의 트리 집합. **AD의 최상위 보안 경계** |
| **OU (조직 구성 단위)** | 도메인 내부의 논리적 그룹. GPO 적용 단위 |
| **도메인 컨트롤러(DC)** | AD 데이터베이스를 보유·인증 처리하는 서버 |
| **GPO (그룹 정책 개체)** | 사용자·컴퓨터에 일괄 적용하는 정책 |
| **글로벌 카탈로그(GC)** | 포리스트 전체 객체의 부분 복제본 |
| **신뢰 관계(Trust)** | 도메인 간 인증 공유 |

### 트러스트(Trust) 종류 (2026-3회 36번)
**트러스트** = 도메인·포리스트 사이에서 **한쪽의 사용자를 다른 쪽이 인증·신뢰할지**를 나타내는 관계입니다.
**전이(Transitive)**: A↔B, B↔C이면 A↔C도 신뢰됨 / **방향**: 단방향(One-way)·양방향(Two-way)

| 종류 | 전이성 | 설명 |
|---|---|---|
| **부모-자식(Parent-Child)** | 양방향·**전이** | 같은 트리 안의 도메인 사이. **자동 생성** |
| **트리 루트(Tree-Root)** | 양방향·**전이** | 같은 포리스트의 다른 트리 루트 사이. **자동 생성** |
| 단축(Shortcut) | 전이 | 같은 포리스트 안에서 인증 경로를 단축 (관리자 생성) |
| 외부(External) | **비전이** | 다른 포리스트의 특정 도메인과 연결 (관리자 생성) |
| 포리스트(Forest) | 전이 | 포리스트 전체 간 관계 (관리자 생성) |

> **같은 포리스트 안의 도메인 사이에는 상호 양방향 전이 트러스트가 자동으로 설정**됩니다 (기출 36번 정답: 트러스트).

### AD가 사용하는 프로토콜·포트
| 프로토콜 | 포트 | 역할 |
|---|---|---|
| **LDAP** | 389 (LDAPS 636) | 디렉터리 조회 |
| **Kerberos** | 88 | 인증 |
| **DNS** | 53 | AD는 **DNS에 절대적으로 의존** |
| SMB | 445 | 파일 공유, GPO 배포 |
| Global Catalog | 3268 | |

> 출제 포인트: **Active Directory는 DNS 없이 동작할 수 없습니다.**

### AD 구축 절차
```
1. 고정 IP 설정
2. DNS 서버 설치 (또는 지정)
3. 서버 관리자 → 역할 추가 → Active Directory Domain Services
4. dcpromo (구) / 도메인 컨트롤러로 승격 마법사
5. 도메인 이름·포리스트 기능 수준 설정
6. 재부팅
```

---

## 3. Windows Server 주요 역할(Role)

| 역할 | 설명 |
|---|---|
| **AD DS** | Active Directory 도메인 서비스 |
| **DNS 서버** | 이름 해석 |
| **DHCP 서버** | IP 자동 할당 (범위/Scope, 예약, 임대 기간 설정) |
| **IIS (웹 서버)** | Internet Information Services — HTTP/HTTPS, FTP |
| **파일 서비스** | 공유 폴더, DFS, FSRM(할당량) |
| **인쇄 서비스** | 프린터 공유 |
| **원격 데스크톱 서비스** | RDP (3389) |
| **Hyper-V** | 가상화 |
| **NPS** | 네트워크 정책 서버(RADIUS) |
| **WSUS** | 업데이트 배포 |

### Hyper-V (2026-3회 45번)
Windows Server의 **서버 가상화 역할(하이퍼바이저)** 입니다.

| 기능 | 설명 |
|---|---|
| **검사점(Checkpoint)** | VM의 **특정 시점 상태를 저장**하고 나중에 그 시점으로 **복원** (테스트·업데이트 전 되돌리기). 구 명칭 스냅샷. 종류: 표준 / 프로덕션 |
| **내보내기(Export)** | VM을 파일로 내보내 **복사·이전·백업** |
| 가져오기(Import) | 내보낸 VM을 다시 등록 |
| **가상 스위치** | **외부**(물리 NIC 연결·외부망 통신) / **내부**(호스트↔VM) / **개인**(VM끼리만) |
| 가상 하드 디스크 | VHD / VHDX (VHDX 최대 64TB) |
| 세대(Generation) | 1세대(BIOS) / 2세대(UEFI) |
| 동적 메모리 | 사용량에 따라 VM 메모리 조절 |
| 라이브 마이그레이션 | 실행 중인 VM을 다른 호스트로 이동 |

> 기출 45번: 특정 시점 상태 저장·복원 = **검사점(Checkpoint)**. ‘롤백(Rollback)’·‘타임머신(Time Machine)’은 Hyper-V 기능 명칭이 아닙니다(보기 함정). 2026-2회 45번에서도 **검사점**이 다시 출제되었습니다(악성코드 실행 전 시점으로 복원).

### Hyper-V 추가 특징 (2026-1회 33번)
| 특징 | 설명 |
|---|---|
| **스토리지 마이그레이션** | **VHD/VHDX를 VM이 실행 중에도 다른 저장소로 이동** ← 기출 정답 |
| 라이브 마이그레이션 | 실행 중인 VM을 다른 Hyper-V 호스트로 이동 |
| **Hyper-V 복제본(Replica)** | VM을 다른 서버로 **복제**(재해 복구) — ‘복제할 수 없다’는 ✗ |
| 서버 통합 | 한 물리 서버에 **여러 VM**을 운영해 **하드웨어 자원 사용률을 높임**(‘사용률이 낮아진다’는 ✗) |

### 컨테이너 vs 가상 머신 (2026-2회 29번)
| 구분 | 설명 |
|---|---|
| **Windows Containers** | 호스트 OS **커널을 공유**하는 **경량 격리 실행 환경**. 애플리케이션 실행에 필요한 최소 구성만 포함해 **VM보다 가볍고 빠르게** 생성. 격리 방식: 프로세스 격리 / Hyper-V 격리 |
| **가상 머신(VM)** | **완전한 운영 체제를 포함**하는 독립 컴퓨터 |
| Nano Server | 컨테이너용으로 쓰이는 **경량 서버 OS 이미지** |
| IIS | 웹 서버 역할 (가상화 기술 아님) |

> 기출 2회 29번 지문: ‘애플리케이션 실행에 필요한 경량화된 운영 체제 환경을 포함하는 가상화 기술’ → **Windows Containers**.

### 파일 시스템 권한 (NTFS)
| 권한 | 설명 |
|---|---|
| 모든 권한(Full Control) | 모든 작업 + 권한 변경 + 소유권 |
| 수정(Modify) | 읽기·쓰기·삭제 |
| 읽기 및 실행 | 읽기 + 프로그램 실행 |
| 읽기(Read) | 내용 보기 |
| 쓰기(Write) | 파일 생성·수정 |
| 목록 보기 | 폴더 내용 나열 |

**공유 권한 vs NTFS 권한** (출제 포인트)
- 네트워크로 접근할 때는 **둘 중 더 제한적인 쪽(교집합)이 적용**됩니다.
- 로컬 로그인 시에는 NTFS 권한만 적용됩니다.

### 파일시스템 종류
| 종류 | 특징 |
|---|---|
| **FAT32** | 최대 파일 4GB, 최대 볼륨 32GB(윈도우 포맷 기준). 권한 설정 불가 |
| **NTFS** | 권한·암호화(EFS)·압축·할당량·저널링 지원. **윈도우 서버 표준** |
| **ReFS** | 복원 파일 시스템(대용량·무결성) |
| exFAT | 대용량 이동식 저장장치용 |

---

## 4. Windows 사용자·그룹 관리

### 기본 그룹
| 그룹 | 권한 |
|---|---|
| **Administrators** | 전체 관리 권한 |
| **Users** | 일반 사용자 |
| **Power Users** | 제한적 관리(구형) |
| **Guests** | 최소 권한 |
| **Backup Operators** | 백업·복원 권한 |
| **Remote Desktop Users** | 원격 데스크톱 접속 |
| **Domain Admins** | 도메인 전체 관리 |
| **Enterprise Admins** | 포리스트 전체 관리 |

### 그룹 범위 (AD)
| 범위 | 설명 |
|---|---|
| **도메인 로컬** | 해당 도메인 내 자원 접근 권한 부여용 |
| **글로벌** | 같은 도메인 사용자를 묶음 |
| **유니버설** | 포리스트 전체 |

> 권장 전략: **AGDLP** (Account → Global → Domain Local → Permission)

### 관리 도구
| 도구 | 용도 |
|---|---|
| `compmgmt.msc` | 컴퓨터 관리 |
| `dsa.msc` | AD 사용자 및 컴퓨터 |
| `gpmc.msc` | 그룹 정책 관리 |
| `services.msc` | 서비스 관리 |
| `eventvwr.msc` | 이벤트 뷰어(로그) |
| `diskmgmt.msc` | 디스크 관리 |
| `devmgmt.msc` | 장치 관리자 |
| `perfmon.msc` | **성능 모니터**(카운터·로그 수집) |
| `resmon` | **리소스 모니터** — CPU·메모리·디스크·네트워크 사용량을 **실시간 모니터링** (2026-1회 42번 정답) |
| 서버 관리자(Server Manager) | 서버 역할·기능 설치와 관리를 모으는 중앙 콘솔 |
| 이벤트 뷰어 | 시스템·응용 프로그램·보안 **로그 확인**(실시간 사용량 도구가 아님) |
| `regedit` | 레지스트리 편집기 |
| `msconfig` | 시스템 구성 |
| `taskmgr` | 작업 관리자 |
| `secpol.msc` | 로컬 보안 정책 |
| `dnsmgmt.msc` | DNS 관리 |
| `dhcpmgmt.msc` | DHCP 관리 |

### 이벤트 뷰어 로그 종류
**응용 프로그램 / 보안 / 시스템 / 설치 / 전달된 이벤트**
수준: 정보, 경고, 오류, 심각

---

## 5. Windows 명령어 (실기에도 출제 ★)

### 네트워크 명령
```cmd
ipconfig                    IP 설정 확인
ipconfig /all               상세 정보(MAC, DNS, DHCP) ★
ipconfig /release           DHCP 주소 반납
ipconfig /renew             DHCP 주소 갱신
ipconfig /flushdns          DNS 캐시 삭제 ★
ipconfig /displaydns        DNS 캐시 확인
ipconfig /registerdns       DNS 등록 갱신

ping 8.8.8.8                연결 확인
ping -t host                무한 반복 ★ (Ctrl+C로 중지)
ping -n 10 host             10회 전송
ping -l 1000 host           패킷 크기 지정
ping -a IP                  호스트명 확인

tracert host                경로 추적 ★
pathping host               경로 + 패킷 손실률

netstat -an                 모든 연결·포트(숫자) ★
netstat -ano                PID 포함 ★
netstat -r                  라우팅 테이블
netstat -e                  이더넷 통계
netstat -s                  프로토콜별 통계
netstat -b                  실행 파일명 포함

nslookup domain             DNS 조회 ★
nslookup -type=mx domain    MX 레코드 조회
arp -a                      ARP 캐시 ★
arp -d                      ARP 캐시 삭제
route print                 라우팅 테이블 ★
route add 10.0.0.0 mask 255.0.0.0 192.168.1.1
route delete 10.0.0.0
getmac                      MAC 주소
hostname                    호스트명
nbtstat -n                  NetBIOS 이름 테이블
telnet host 80              포트 연결 테스트

netsh interface ip show config
netsh interface ip set address "이더넷" static 192.168.1.10 255.255.255.0 192.168.1.1
netsh interface ip set dns "이더넷" static 8.8.8.8
netsh wlan show profiles    무선 프로필
```

### 시스템 명령
```cmd
systeminfo                  시스템 정보
tasklist                    프로세스 목록
taskkill /PID 1234 /F       프로세스 강제 종료
sfc /scannow                시스템 파일 검사
chkdsk C: /f                디스크 검사·복구
net user                    사용자 목록
net user user1 /add         사용자 추가
net localgroup administrators user1 /add
net share                   공유 폴더 목록
net use Z: \\server\share   네트워크 드라이브 연결 ★
net start / net stop 서비스명
sc query                    서비스 상태
gpupdate /force             그룹 정책 즉시 적용 ★
gpresult /r                 적용된 정책 확인
shutdown /r /t 0            즉시 재부팅
shutdown /s /t 60           60초 후 종료
```

### PowerShell (2026-3회 30번)
| 항목 | 내용 |
|---|---|
| 정체 | .NET 기반 **명령줄 셸 + 스크립트 언어** (Windows Server 기본 탑재) |
| 명령 형식 | **cmdlet = 동사-명사**: `Get-Process`, `Get-Service`, `Stop-Service`, `Get-NetIPAddress` |
| **기존 명령 호환** | cmd 명령(`dir`, `cd`, `ipconfig`, `ping`)과 별칭(alias: `ls`, `cat`, `cp`)을 **그대로 사용 가능** |
| **대소문자** | **구분하지 않음** (`Get-Process` = `get-process`) |
| 파이프라인 | 텍스트가 아니라 **객체**를 전달 |
| 스크립트 | **텍스트 파일(.ps1)**, 콘솔에서 **대화형**으로도 실행 가능 |
| 실행 정책 | `Get-ExecutionPolicy` / `Set-ExecutionPolicy`로 스크립트 실행 허용 수준 조절 |
| 도움말 | `Get-Help 명령`, `Get-Command` |

```powershell
Get-Process | Where-Object CPU -gt 100       # CPU 사용 많은 프로세스
Get-Service | Where-Object Status -eq Running # 실행 중 서비스
Get-NetIPAddress                              # IP 주소 확인
Test-NetConnection 8.8.8.8 -Port 53           # 포트 연결 테스트
Get-Help Get-Process
```

> 기출 30번: **‘기존 DOS 명령은 사용할 수 없다’가 옳지 않은 설명**입니다. PowerShell에서도 dir·cd·ipconfig 등이 동작합니다.

---

## 6. 리눅스 서버 관리 (요약)

> 상세 내용은 [../리눅스마스터 2급/09_명령어 치트시트.md](../리눅스마스터%202급/09_명령어%20치트시트.md) 참조

### 자주 출제되는 리눅스 항목
| 주제 | 핵심 |
|---|---|
| 계정 파일 | `/etc/passwd`(7필드), `/etc/shadow`(9필드), `/etc/group`(4필드) |
| 계정 명령 | `useradd`, `usermod -aG`, `userdel -r`, `passwd`, `chage` |
| 권한 | `chmod 755`, `chown u:g`, umask (파일 666-, 디렉터리 777-) |
| 특수 권한 | SetUID(4), SetGID(2), Sticky(1) |
| 프로세스 | `ps -ef`, `top`, `kill -9`, `nice`(-20~19) |
| 서비스 | `systemctl start/enable/status` |
| 예약 작업 | `crontab -e` (분 시 일 월 요일) |
| 로그 | `/var/log/messages`, `/var/log/secure`, `journalctl` |
| 패키지 | `rpm -qa`, `yum install`, `apt install` |
| 파일시스템 | ext4, XFS, `/etc/fstab`, `mount`, `df -h`, `du -sh` |
| 네트워크 설정 | `/etc/sysconfig/network-scripts/ifcfg-eth0`, `ONBOOT=yes` |
| DNS 설정 | `/etc/resolv.conf` |
| 호스트 매핑 | `/etc/hosts` |

### 리눅스 ↔ 윈도우 명령어 대응표 (실기 단골 ★)
| 목적 | 리눅스 | 윈도우 |
|---|---|---|
| IP 확인 | `ifconfig` / `ip addr` | `ipconfig /all` |
| 경로 추적 | `traceroute` | `tracert` |
| 포트 확인 | `netstat -antp` / `ss -antp` | `netstat -ano` |
| 라우팅 테이블 | `route -n` / `ip route` | `route print` |
| DNS 조회 | `nslookup` / `dig` | `nslookup` |
| ARP | `arp -a` | `arp -a` |
| DNS 캐시 삭제 | `systemd-resolve --flush-caches` | `ipconfig /flushdns` |
| 프로세스 목록 | `ps -ef` | `tasklist` |
| 프로세스 종료 | `kill -9 PID` | `taskkill /PID n /F` |
| 파일 복사 | `cp` | `copy` / `xcopy` |
| 디렉터리 목록 | `ls` | `dir` |
| 파일 삭제 | `rm` | `del` |
| 디렉터리 생성 | `mkdir` | `mkdir` / `md` |
| 현재 경로 | `pwd` | `cd` |
| 화면 지우기 | `clear` | `cls` |
| 텍스트 출력 | `cat` | `type` |

---

## 7. 주요 서버 서비스 정리

| 서비스 | 윈도우 | 리눅스 | 포트 |
|---|---|---|---|
| **웹** | IIS | Apache(`httpd`) / Nginx | 80/443 |
| **DNS** | DNS 서버 역할 | BIND(`named`) | 53 |
| **DHCP** | DHCP 서버 역할 | `dhcpd` | 67/68 |
| **파일 공유** | SMB/CIFS | **Samba**(`smbd`) / NFS | 445 / 2049 |
| **메일** | Exchange | Postfix, Sendmail + Dovecot | 25/110/143 |
| **FTP** | IIS FTP | vsftpd, proftpd | 20/21 |
| **원격 접속** | RDP | SSH(`sshd`) | 3389 / 22 |
| **DB** | MS SQL Server | MySQL/MariaDB, PostgreSQL | 1433 / 3306 / 5432 |
| **디렉터리** | Active Directory | OpenLDAP | 389 |
| **시간 동기** | W32Time | `ntpd`, `chronyd` | 123 |

### BIND `/etc/named.conf`의 options 지시자 (2026-1회 30번)
```
options {
    listen-on port 53 { any; };        // IPv4 53번 포트, 모든 인터페이스에서 수신
    listen-on-v6 port 53 { ::1; };     // IPv6는 루프백(::1)에서만 수신
    directory "/var/named";            // 작업 디렉터리 (zone 파일 위치)
    dump-file "/var/named/data/cache_dump.db";
    statistics-file "/var/named/data/named_stats.txt";
    allow-query { any; };              // 질의(query)를 허용할 IP 대역 — any = 모두
    recursion yes;                     // 재귀 질의 허용 여부
    dnssec-validation yes;             // DNSSEC 유효성 검사
    masterfile-format text;            // zone 파일 저장 형식 (text / raw)
};
```
| 지시자 | 의미 |
|---|---|
| `listen-on` / `listen-on-v6` | 질의를 받을 **포트·주소** (53번 포트) |
| `directory` | named의 기본 작업 디렉터리 |
| `allow-query` | **질의를 허용할 호스트·대역** (`any`=전부) |
| `recursion` | 재귀 질의 허용 |
| `masterfile-format text` | **zone 파일을 텍스트 형태로** 저장(변환) — slave 동기화 때 영향 |
| `forwarders` | 질의를 넘겨 줄 상위 DNS |

> 기출 1회 30번의 보기: ‘외부 query의 IP 대역 모두 허용(allow-query any)’·‘53번 포트 외부 접근 허용(listen-on any)’·‘zone 파일을 text 형태로 변환(masterfile-format text)’은 **지문과 맞는 설명**이고, 정답(옳지 않은 것)은 ‘유효성 검사 시 오류가 발생하지 않는다’였습니다. 지문의 설정에 DNSSEC 관련 지시자가 없는 점과 관련된 보기로 보이며, 정확한 근거는 확인하지 못했습니다.

### Apache `httpd.conf` 주요 지시자 (2026-1회 31번)
| 지시자 | 의미 |
|---|---|
| **`LimitRequestBody`** | **요청(POST·PUT) 본문의 최대 크기 제한**(바이트, 0=무제한) ← 기출 정답 |
| `LimitRequestFields` / `LimitRequestFieldSize` / `LimitRequestLine` | 요청 헤더 필드 수 / 필드 크기 / 요청 라인 길이 제한 |
| `Listen` | 수신 포트 (예: `Listen 80`) |
| `ServerName` | 서버 호스트명 |
| `ServerRoot` | 서버 설정·로그 루트 디렉터리 |
| `DocumentRoot` | 웹 문서 루트 (기본 `/var/www/html`) |
| `DirectoryIndex` | 기본 문서 (`index.html` 등) |
| `KeepAlive` / `KeepAliveTimeout` | 지속 연결 사용 / 유지 시간 |
| `User` / `Group` | httpd 실행 계정 |
| `ErrorLog` / `CustomLog` | 오류 / 접근 로그 파일 |
| `<VirtualHost>` | 가상 호스트 설정 |

> `KeepRequestSize`·`RestrictBodyRequest`·`PostRequestSize`는 **존재하지 않는 지시자**(기출 오답 보기)입니다.

### NFS vs Samba (출제 단골)
| 구분 | **NFS** | **Samba** |
|---|---|---|
| 용도 | **Unix/Linux ↔ Unix/Linux** | **Linux ↔ Windows** |
| 설정 파일 | `/etc/exports` | `/etc/samba/smb.conf` |
| 포트 | 2049 | 137~139, 445 |
| 프로토콜 | RPC 기반 | SMB/CIFS |

---

## 8. 백업과 RAID

### 백업 종류
| 종류 | 백업 범위 | 백업 시간 | 복구 시간 |
|---|---|---|---|
| **전체(Full)** | 전부 | 김 | **가장 빠름** |
| **증분(Incremental)** | **직전 백업 이후** 변경분 | **가장 짧음** | 가장 김(모든 증분 필요) |
| **차등(Differential)** | **최초 전체 백업 이후** 변경분 전체 | 중간 | 중간(전체+최신 차등만) |

### RAID (운용기기와 중복 출제)
| 레벨 | 방식 | 최소 디스크 | 장애 허용 |
|---|---|---|---|
| **0** | 스트라이핑 | 2 | **없음** (성능만) |
| **1** | 미러링 | 2 | 1개 (용량 50%) |
| **5** | 분산 패리티 | **3** | **1개** |
| **6** | 이중 분산 패리티 | **4** | **2개** |
| **10 (1+0)** | 미러 + 스트라이프 | 4 | 그룹별 1개 |

---

## 9. 마무리 체크 문제

1. AD의 최상위 보안 경계는? → **포리스트(Forest)**
2. AD가 반드시 필요로 하는 서비스는? → **DNS**
3. AD 인증에 쓰이는 프로토콜과 포트? → **Kerberos, 88**
4. LDAP의 포트는? → **389** (LDAPS 636)
5. 공유 권한과 NTFS 권한이 다를 때 적용되는 것은? → **더 제한적인 쪽**
6. NTFS가 FAT32보다 나은 점 3가지? → 권한 설정, 암호화, 저널링(+대용량)
7. 그룹 정책을 즉시 적용하는 명령? → **`gpupdate /force`**
8. DNS 캐시를 삭제하는 윈도우 명령? → **`ipconfig /flushdns`**
9. PID를 포함해 포트를 확인하는 윈도우 명령? → **`netstat -ano`**
10. 윈도우에서 경로를 추적하는 명령? → **`tracert`**
11. 리눅스의 `traceroute`에 해당하는 윈도우 명령? → **`tracert`**
12. 리눅스에서 LISTEN 포트를 확인하는 명령? → `netstat -tulnp` / `ss -tulnp`
13. 윈도우 ↔ 리눅스 파일 공유 서비스는? → **Samba (SMB/CIFS)**
14. Unix 간 파일 공유 서비스와 설정 파일? → **NFS, `/etc/exports`**
15. 백업 시간이 가장 짧은 방식과 복구가 가장 복잡한 방식? → **증분 백업** (둘 다)
16. RAID 5의 최소 디스크 수와 장애 허용? → **3개, 1개**
17. 이벤트 뷰어를 여는 명령? → `eventvwr.msc`
18. 네트워크 드라이브를 연결하는 명령? → `net use Z: \\server\share`
19. P2P 모델의 단점? → **중앙 관리·보안 취약**, 소규모에만 적합
20. RDP의 포트는? → **3389**
