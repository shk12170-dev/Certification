---
title: 리눅스 활용 (네트워크·서버·X)
cert: linux-master-2
order: 3
---

# 3과목. 리눅스 활용

## 1. X 윈도우 / 데스크톱
- **X Window System**: 클라이언트-서버 구조(X 서버가 화면 담당, X 클라이언트=응용). X 서버 포트 6000+N. 프로토콜 X11
- 구성: X 서버(Xorg) + 윈도우 매니저(twm, fvwm, Metacity, Mutter, KWin, Xfwm) + 데스크톱 환경(**GNOME, KDE, Xfce, LXDE**)
- 디스플레이 매니저(로그인 화면): gdm, kdm, lightdm, xdm
- 설정: `/etc/X11/xorg.conf`(현대는 자동), `startx`, `xinit`, `~/.xinitrc`, `DISPLAY=host:0.0`, `xhost +`, `xauth`
- 원격 GUI: SSH `-X`, VNC(5900+N), XDMCP, xrdp
- Wayland: X의 후속
- 오피스/응용: LibreOffice, Firefox, Thunderbird, GIMP

## 2. 네트워크 설정
- `ifconfig`(구) / `ip addr`, `ip link`, `ip route`, `ip a add 192.168.1.10/24 dev eth0`
- `ifup/ifdown`, `nmcli`, `nmtui`, NetworkManager
- RHEL 설정 파일: `/etc/sysconfig/network-scripts/ifcfg-eth0`
  ```
  DEVICE=eth0
  BOOTPROTO=static|dhcp
  IPADDR=192.168.1.10
  NETMASK=255.255.255.0
  GATEWAY=192.168.1.1
  DNS1=8.8.8.8
  ONBOOT=yes
  ```
- 호스트: `/etc/hosts`, `/etc/hostname`, `hostnamectl`, `/etc/resolv.conf`(nameserver), `/etc/nsswitch.conf`(조회 순서), `/etc/services`(포트), `/etc/protocols`
- 진단: `ping -c 4`, `traceroute`, `netstat -tnlp` / `ss -tnlp`(리스닝 포트), `nslookup`/`dig`/`host`, `arp`, `route -n`, `tcpdump`, `nc`, `nmap`, `curl`/`wget`, `ethtool`, `mtr`
- 라우팅: `route add default gw 192.168.1.1`, `ip route add`, 포워딩 `net.ipv4.ip_forward=1`(`/proc/sys/net/ipv4/ip_forward`)
- 본딩/브리지/VLAN 개념

## 3. 서비스 관리
- **xinetd**(슈퍼데몬): `/etc/xinetd.d/서비스`, `disable = yes/no`, `/etc/xinetd.conf`. 구형 **inetd**: `/etc/inetd.conf`
- **TCP Wrapper**: `/etc/hosts.allow` → `/etc/hosts.deny` 순으로 검사 (allow 우선, 둘 다 없으면 허용)
- systemd 서비스 관리는 2과목 참조

## 4. 주요 서버
### 4-1. 웹 서버 Apache (httpd)
- 설정 `/etc/httpd/conf/httpd.conf` (Debian: `/etc/apache2/apache2.conf`)
- `Listen 80`, `ServerName`, `DocumentRoot "/var/www/html"`, `DirectoryIndex`, `ServerRoot`, `User/Group apache`, `ErrorLog`, `CustomLog`
- `<VirtualHost *:80>` 가상 호스트, `.htaccess`(`AllowOverride`), `UserDir`(~user 홈페이지 `public_html`)
- 문법 검사 `httpd -t`, `apachectl configtest|graceful`
- 모듈 DSO, MPM(prefork/worker/event), 로그 `/var/log/httpd/access_log, error_log`
- 대안 Nginx

### 4-2. 파일 서버
- **Samba**(SMB/CIFS, 포트 137/138 UDP, 139/445 TCP): 데몬 `smbd`(파일·인쇄), `nmbd`(NetBIOS 이름). 설정 `/etc/samba/smb.conf` — `[global]`(workgroup, security), `[homes]`, 공유 섹션. `smbpasswd -a`, `testparm`(문법 검사), `smbclient -L`, `smbstatus`
- **NFS**: 유닉스 간 공유. `/etc/exports` (`/data 192.168.1.0/24(rw,sync,no_root_squash)`), `exportfs -ra`, `showmount -e`, `mount -t nfs srv:/data /mnt`, 데몬 rpcbind(111), nfsd(2049), mountd
- **FTP**: **vsftpd** `/etc/vsftpd/vsftpd.conf` (`anonymous_enable`, `local_enable`, `write_enable`, `chroot_local_user`), 금지 사용자 `/etc/vsftpd/ftpusers`, `user_list`. 포트 20/21, Active/Passive. proftpd, sftp(SSH)

### 4-3. DNS 서버 BIND (named)
- `/etc/named.conf`(options, zone), 존 파일 `/var/named/`
- 레코드: SOA, NS, A, AAAA, MX, CNAME, PTR, TXT
- 순방향 존 / 역방향 존(`1.168.192.in-addr.arpa`), 마스터/슬레이브, 캐싱 전용
- 확인 `named-checkconf`, `named-checkzone`, `rndc reload`, `dig`/`nslookup`
- 포트 53 UDP/TCP

### 4-4. DHCP 서버
- `/etc/dhcp/dhcpd.conf` : `subnet 192.168.1.0 netmask 255.255.255.0 { range ...; option routers ...; option domain-name-servers ...; default-lease-time 600; }`
- 고정 할당 `host x { hardware ethernet ..; fixed-address ..; }`
- 임대 DB `/var/lib/dhcpd/dhcpd.leases`, 데몬 `dhcpd`, UDP 67/68

### 4-5. 메일 서버
- **MTA**: sendmail(`/etc/mail/sendmail.cf`, `aliases`, `access`), **postfix**(`/etc/postfix/main.cf`), qmail, exim
- **MDA**: procmail, **MUA**: mutt, mail, thunderbird
- 수신: POP3(110), IMAP(143) — dovecot
- 별칭 `/etc/aliases` 수정 후 `newaliases`, 큐 `mailq`, 전달 `~/.forward`, SMTP 25(제출 587)

### 4-6. SSH
- `sshd`, 설정 `/etc/ssh/sshd_config` (`Port 22`, `PermitRootLogin no`, `PasswordAuthentication`, `PubkeyAuthentication`, `AllowUsers`), 클라이언트 `/etc/ssh/ssh_config`
- 키: `ssh-keygen`, `ssh-copy-id`, `~/.ssh/authorized_keys`, `known_hosts`, `ssh -p -X -L`, `scp`, `sftp`

### 4-7. 기타
- NTP/chrony, 프록시 **Squid**(3128), 데이터베이스 MySQL/MariaDB(3306)·PostgreSQL(5432), 프린터 **CUPS**(631, `lpr`, `lpq`, `lprm`, `lpstat`), LDAP, 가상화(KVM), 컨테이너(Docker) 개요

## 5. 방화벽 · 보안
- **iptables**: 테이블 filter/nat/mangle, 체인 INPUT / OUTPUT / FORWARD / PREROUTING / POSTROUTING
  ```
  iptables -L -n -v
  iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
  iptables -A INPUT -j DROP
  iptables -P INPUT DROP
  iptables -D INPUT 3 / -I INPUT 1 ... / -F
  iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  service iptables save
  ```
  - 타깃 ACCEPT / DROP(무응답) / REJECT(거부 응답) / LOG. 규칙은 위에서 아래로 첫 일치 적용
- **firewalld**: `firewall-cmd --add-service=http --permanent`, `--reload`, `--list-all`, 존(zone)
- ufw(Ubuntu) `ufw allow 22`
- **SELinux**: `getenforce`, `setenforce 0|1`, `/etc/selinux/config`(enforcing/permissive/disabled), `chcon`, `restorecon`, `sestatus`
- 보안 도구: fail2ban, `chage`, PAM(`/etc/pam.d`), `last`, `lastb`, 패킷 분석 tcpdump/wireshark, nmap, Tripwire(무결성), rkhunter, **John the Ripper**(암호 점검), Snort(IDS)
- 원격 root 금지, 불필요 서비스 중지, 패치

## 6. 기타 활용
- 스크립트 자동화(cron), 백업 전략(전체/증분/차등), `rsync -avz`, `tar`
- 셸 스크립트로 계정 일괄 생성, 로그 분석
- 가상화: KVM, Xen, VirtualBox / 컨테이너: Docker(`docker run`, `ps`, `images`) 개요
- 오픈소스 라이선스: GPL, LGPL, BSD, MIT, Apache

## ✍️ 연습문제
1. Apache 기본 문서 루트(RHEL)? → `/var/www/html`
2. Samba 설정 문법 검사 명령? → `testparm`
3. NFS 공유 설정 파일? → `/etc/exports`
4. TCP Wrapper 검사 순서? → **hosts.allow → hosts.deny**
5. SSH root 직접 로그인 금지 설정? → `PermitRootLogin no`
6. iptables로 NAT 주소 위장 체인? → **POSTROUTING + MASQUERADE**
7. DHCP 서버 설정 파일? → `/etc/dhcp/dhcpd.conf`
8. 현재 열린 TCP 리스닝 포트를 보는 명령? → `ss -tnlp` (`netstat -tnlp`)
