---
title: NOS (네트워크 운영체제)
cert: network-manager-2
order: 3
---

# 3과목. NOS

NOS = 윈도우 서버 계열 + 유닉스/리눅스. 출제는 **개념 + 명령어** 위주.

## 1. 운영체제 기본
- 프로세스/스레드, 스케줄링(FCFS, SJF, RR, 우선순위), 교착상태(4조건: 상호배제·점유대기·비선점·환형대기)
- 메모리: 페이징/세그멘테이션, 페이지 교체(FIFO, LRU, LFU), 가상 메모리
- 파일 시스템: FAT32, **NTFS**(권한·암호화·압축·저널링), ext4, XFS

## 2. Windows Server
### 주요 개념
- **도메인/Active Directory(AD DS)**: 중앙 계정·정책 관리, 도메인 컨트롤러(DC), LDAP/Kerberos
- 작업 그룹(P2P) vs 도메인(클라이언트-서버)
- **GPO(그룹 정책)**: 사용자/컴퓨터 설정 중앙 배포 (적용 순서 LSDOU: 로컬→사이트→도메인→OU)
- 계정: 로컬/도메인, 그룹(Administrators, Users, Guests 등), 프로필
- **NTFS 권한** vs **공유 권한**: 둘 다 적용되면 **더 제한적인 것**이 유효. 거부(Deny)가 허용보다 우선
- 권한 상속, 소유권, 디스크 할당량(Quota), 볼륨 섀도 복사
- 역할(Role): DNS, DHCP, IIS(웹), FTP, 파일/인쇄, 원격 데스크톱(RDP 3389), 프린트 서버
- 디스크 관리: 기본/동적 디스크, 볼륨 종류(단순/스패닝/스트라이프 RAID0/미러 RAID1/RAID5)
- 도구: 작업 관리자, 이벤트 뷰어, 서비스(services.msc), 성능 모니터, 레지스트리 편집기(regedit, 5개 루트 HKLM 등), 컴퓨터 관리, 원격 지원

### 네트워크 명령어 (★)
| 명령 | 기능 |
|---|---|
| `ipconfig /all` | IP 전체 정보(MAC, DHCP, DNS) |
| `ipconfig /release` `/renew` | DHCP 주소 반납/갱신 |
| `ipconfig /flushdns` `/displaydns` | DNS 캐시 삭제/표시 |
| `ping` | ICMP 연결 확인 (`-t` 계속, `-n` 횟수, `-l` 크기) |
| `tracert` | 경로 추적 |
| `pathping` | ping+tracert 통계 |
| `nslookup` | DNS 질의 |
| `netstat -an` | 포트/연결 상태 (`-r` 라우팅, `-b` 프로세스) |
| `arp -a` | ARP 캐시 |
| `route print` / `route add` | 라우팅 테이블 |
| `nbtstat` | NetBIOS 정보 |
| `net user` / `net share` / `net use` | 계정/공유/연결 |
| `hostname`, `systeminfo`, `gpupdate /force`, `tasklist`, `taskkill` | 기타 |

## 3. UNIX / Linux (NOS 범위)
### 디렉터리
`/` 루트, `/bin` 기본명령, `/sbin` 관리명령, `/etc` 설정, `/home` 사용자, `/root`, `/var` 로그·가변, `/tmp`, `/usr`, `/dev`, `/proc`, `/mnt`, `/boot`, `/lib`

### 핵심 명령어
| 분류 | 명령 |
|---|---|
| 파일 | `ls -l`, `cp`, `mv`, `rm -r`, `mkdir`, `rmdir`, `touch`, `cat`, `more`, `less`, `head`, `tail -f` |
| 검색 | `find`, `grep`, `locate`, `which`, `whereis` |
| 권한 | `chmod 755`, `chown user:group`, `umask` |
| 프로세스 | `ps -ef`, `top`, `kill -9 PID`, `jobs`, `bg`, `fg` |
| 사용자 | `useradd`, `passwd`, `usermod`, `userdel`, `groupadd`, `su`, `sudo` |
| 네트워크 | `ifconfig`/`ip addr`, `ping`, `netstat`/`ss`, `traceroute`, `nslookup`/`dig` |
| 디스크 | `df -h`, `du -sh`, `mount`, `umount`, `fdisk`, `mkfs` |
| 압축 | `tar cvzf / xvzf`, `gzip`, `zip` |

- 권한: r=4, w=2, x=1. `chmod 644` = rw-r--r--. 기본 umask 022 → 파일 644 / 디렉터리 755
- 계정 파일: `/etc/passwd`(계정), `/etc/shadow`(암호 해시), `/etc/group`
- **inode**, 하드링크/심볼릭 링크(`ln -s`)는 리눅스마스터 노트 참조

## 4. 서버 서비스 (개념)
- DNS(BIND), DHCP, 웹(Apache/IIS), 메일(sendmail/postfix), FTP(vsftpd), 파일공유(Samba=SMB, NFS)
- RAID: 0(스트라이핑, 속도), 1(미러링), 5(패리티, 최소3디스크), 6, 10

## ✍️ 연습문제
1. NTFS 권한 Read, 공유 권한 Full Control → 유효 권한? → **Read**
2. DHCP 주소 갱신 명령? → `ipconfig /renew`
3. `chmod 750 file` 의 그룹 권한? → **r-x**
4. 암호 해시가 저장되는 파일? → `/etc/shadow`
5. 윈도우에서 열린 포트와 연결 상태를 보는 명령? → `netstat -an`
