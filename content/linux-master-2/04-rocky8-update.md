---
title: 보강 - Rocky Linux 8 기준 최신 변경점
cert: linux-master-2
order: 4
---

# 보강. Rocky Linux 8 (RHEL 8 계열) 기준 최신 변경점

> ❓ **근거 수준 안내**: "KAIT 가 CentOS 대신 Rocky Linux 8.x 를 출제 기준 환경으로 삼는다"는 내용은 2차 자료(교재·후기 검색 요약)에서 확인했고 공식 출제기준은 열람하지 못했습니다. 아래 명령·설정은 RHEL 8 계열의 실제 동작이며, **구형 명령(CentOS 6/7 시절)도 여전히 출제될 수 있으므로 신·구를 함께 암기**하세요.
>
> ❓ 시험 방식도 변경되었다는 자료가 있습니다: 2급 1차는 정해진 시간에 시작하는 **온라인 감독 시험**(웹캠·스마트폰 카메라, 60분, 50문항 중 30문항 이상), 2차는 시험장 필기. 공식 공지로 재확인하세요.

## 1. 구형 → 신형 명령 대응표 (★ 암기)
| 용도 | 구형 (CentOS 6/7) | RHEL 8 계열 |
|---|---|---|
| 패키지 | `yum` | **`dnf`** (`yum` 은 dnf 로 연결) |
| 서비스 | `service httpd start`, `chkconfig` | **`systemctl start/enable httpd`** |
| IP 확인 | `ifconfig` | **`ip addr`** (`ip a`) |
| 라우팅 | `route -n` | **`ip route`** |
| ARP | `arp -a` | **`ip neigh`** |
| 소켓 | `netstat -tnlp` | **`ss -tnlp`** |
| 시간 | `ntpd`, `ntpdate` | **`chronyd`, `chronyc`** |
| 방화벽 | `iptables` | **`firewalld`(`firewall-cmd`)**, 백엔드는 **nftables** |
| 인증 설정 | `authconfig` | **`authselect`** |
| 컨테이너 | `docker` | **`podman`**, buildah, skopeo |
| 호스트명 | `/etc/sysconfig/network` | **`hostnamectl set-hostname`** |
| 로그 | rsyslog | rsyslog + **journald** (`journalctl`) |
> `net-tools`(ifconfig, netstat, route) 는 선택 설치 패키지가 되었습니다.

## 2. 패키지 관리 dnf
- 저장소: **BaseOS**(핵심 OS), **AppStream**(응용·모듈), extras, EPEL(추가 커뮤니티)
- `/etc/yum.repos.d/*.repo` (`[repoid] name= baseurl= enabled=1 gpgcheck=1 gpgkey=`)
- 기본 명령: `dnf install/remove/update/upgrade/search/info/list/provides/repolist/clean all/makecache`
- `dnf history` (`undo`, `rollback`), `dnf group list / group install "Development Tools"`
- **모듈 스트림**: `dnf module list`, `dnf module enable/install nginx:1.20`, `dnf module reset`
- `dnf config-manager --add-repo/--set-enabled`, `dnf download`, `dnf autoremove`
- rpm: `rpm -qa`, `-qi`, `-ql`, `-qf 파일`, `-V`(검증), `-ivh`, `-Uvh`, `-e`, `--import 키`

## 3. 네트워크 = NetworkManager
- 기본 관리자 **NetworkManager**. 설정 파일 `/etc/sysconfig/network-scripts/ifcfg-*` 는 호환용(RHEL 9 에서는 keyfile `/etc/NetworkManager/system-connections/`)
- **nmcli** 예
  ```bash
  nmcli device status                 # 장치 상태
  nmcli connection show               # 연결 목록
  nmcli connection add type ethernet ifname ens160 con-name lan \
        ipv4.addresses 192.168.10.5/24 ipv4.gateway 192.168.10.1 \
        ipv4.dns 8.8.8.8 ipv4.method manual
  nmcli connection modify lan +ipv4.dns 1.1.1.1
  nmcli connection up lan | down lan | reload
  nmcli general hostname 서버명
  nmtui                               # 텍스트 UI
  ```
- 인터페이스 이름: **예측 가능한 이름**(`ens160`, `enp0s3`), `eth0` 아님 (커널 옵션 `net.ifnames=0` 으로 되돌림)
- 진단: `ip -s link`, `ss -tulnp`, `ping`, `traceroute`, `dig`, `resolvectl`(일부)

## 4. 방화벽 firewalld
```bash
firewall-cmd --state
firewall-cmd --get-active-zones
firewall-cmd --list-all [--zone=public]
firewall-cmd --add-service=http --permanent        # 서비스 허용(영구)
firewall-cmd --add-port=8080/tcp --permanent       # 포트 허용
firewall-cmd --remove-service=ssh --permanent
firewall-cmd --reload                              # 영구 설정 반영
firewall-cmd --add-rich-rule='rule family=ipv4 source address=192.168.1.0/24 service name=ssh accept'
firewall-cmd --add-masquerade --permanent          # NAT 위장
firewall-cmd --add-forward-port=port=80:proto=tcp:toport=8080 --permanent
```
- 옵션 없으면 **런타임(재시작 시 소멸)**, `--permanent` 는 재로드 필요
- 기본 존 `public`. 존: drop < block < public < external < dmz < work < home < internal < trusted
- `nft list ruleset` (nftables), iptables 명령은 호환 계층(iptables-nft)

## 5. 시간 동기화 chrony
- `/etc/chrony.conf` (`pool 2.rocky.pool.ntp.org iburst`, `allow 192.168.0.0/16` 로 서버화)
- `systemctl enable --now chronyd`, `chronyc sources -v`, `chronyc tracking`, `timedatectl set-timezone Asia/Seoul`, `timedatectl set-ntp true`

## 6. 부팅 · GRUB2 · 복구
- 설정: `/etc/default/grub` → `grub2-mkconfig -o /boot/grub2/grub.cfg` (BIOS) / `/boot/efi/EFI/rocky/grub.cfg` (UEFI)
- `grubby --default-kernel`, `grubby --update-kernel=ALL --args="quiet"`
- 커널: `uname -r`, `/boot/vmlinuz-*`, `initramfs`(`dracut -f`)
- **root 암호 분실 복구**: GRUB 에서 `e` → 커널 줄 끝에 `rd.break` → `Ctrl+X` → `mount -o remount,rw /sysroot` → `chroot /sysroot` → `passwd root` → `touch /.autorelabel` → `exit` ×2
- 단일 사용자: `systemd.unit=rescue.target`, `emergency.target`

## 7. systemd 심화
- 유닛 종류: `.service .socket .target .mount .timer .path`
- 위치: `/usr/lib/systemd/system`(패키지) < `/etc/systemd/system`(관리자, 우선)
- 유닛 파일 예
  ```ini
  [Unit]
  Description=My App
  After=network.target
  [Service]
  ExecStart=/usr/local/bin/app
  Restart=on-failure
  User=app
  [Install]
  WantedBy=multi-user.target
  ```
- 수정 후 `systemctl daemon-reload`. `systemctl status/start/stop/restart/reload/enable/disable/mask/is-active/list-unit-files --type=service`, `systemctl edit 유닛`
- **타이머**: `.timer` 로 cron 대체, `systemctl list-timers`
- **journald**: `journalctl -u sshd -b -p err --since "1 hour ago" -f`, 영구 저장은 `/var/log/journal` 디렉터리 생성 또는 `Storage=persistent` (`/etc/systemd/journald.conf`)

## 8. 스토리지 · 파일시스템 (XFS 기본)
- 기본 파일시스템 **XFS** (`mkfs.xfs`). ext4 도 지원. **XFS 는 축소 불가, 확장만 가능 (`xfs_growfs /마운트지점`)**
- 점검: `xfs_repair`(언마운트 상태), `xfs_info`, `xfsdump/xfsrestore`, ext 계열은 `resize2fs`, `e2fsck`
- XFS 쿼터 마운트 옵션 `uquota, gquota, pquota`(ext4 는 `usrquota, grpquota`), 관리 `xfs_quota -x -c 'report -h' /home`
- LVM: `pvcreate/vgcreate/lvcreate -L 5G -n data vg0`, `lvextend -r -L +2G /dev/vg0/data`(`-r` 파일시스템도 확장), `vgs/lvs/pvs`, `lvremove`, 스냅샷 `lvcreate -s`
- `lsblk -f`, `blkid`, UUID 로 `/etc/fstab` 작성 권장, `mount -a` 로 검증
- 스왑 파일: `dd`/`fallocate` → `chmod 600` → `mkswap` → `swapon`
- **Stratis, VDO**: RHEL 8 신규 스토리지 관리(중복제거·압축·풀 관리) — 개념만

## 9. SELinux (RHEL 계열 기본 Enforcing)
- 모드: **Enforcing / Permissive / Disabled**. `getenforce`, `setenforce 0|1`(즉시, 재부팅 시 원복), 영구 `/etc/selinux/config` 의 `SELINUX=`
- 컨텍스트 `사용자:역할:타입:레벨` — 핵심은 **타입**(`httpd_sys_content_t`)
- `ls -Z`, `ps -eZ`, `id -Z`, `chcon -t httpd_sys_content_t 파일`, `restorecon -Rv /var/www`, `semanage fcontext -a -t ... "/web(/.*)?"`
- 불리언: `getsebool -a`, `setsebool -P httpd_can_network_connect on` (`-P` 영구)
- 포트: `semanage port -l | grep http`, `semanage port -a -t ssh_port_t -p tcp 2222`
- 로그 `/var/log/audit/audit.log`, `ausearch -m avc`, `audit2why`, `sealert`

## 10. 사용자 · 인증
- `wheel` 그룹 = sudo 사용 권한 (`usermod -aG wheel user`), 설정 `visudo`, `/etc/sudoers.d/`
- 일반 UID 는 **1000 부터**(`/etc/login.defs` UID_MIN), 시스템 계정 1~999
- `chage -M 90 -m 7 -W 7 -E 2026-12-31 user`, 잠금 `passwd -l`, `usermod -L -e 1`, `faillock`(로그인 실패 잠금, `pam_faillock`), 암호 복잡도 `/etc/security/pwquality.conf`
- **authselect**: `authselect current`, `select sssd with-mkhomedir`
- SSH: `PermitRootLogin`, `PasswordAuthentication`, `AllowUsers`, 키 로그인 `ssh-keygen -t ed25519`, `ssh-copy-id`

## 11. 서비스 서버 패키지 (RHEL 8)
| 서비스 | 패키지/서비스 | 비고 |
|---|---|---|
| 웹 | `httpd`(Apache 2.4), `nginx`(AppStream 모듈) | `/etc/httpd/conf/httpd.conf`, `conf.d/*.conf` |
| DB | `mariadb-server`(mariadb.service), `postgresql-server` | `mysql_secure_installation`, `postgresql-setup --initdb` |
| DNS | `bind` (named.service) | `/etc/named.conf` |
| DHCP | `dhcp-server` (dhcpd.service) | `/etc/dhcp/dhcpd.conf` |
| 파일 | `samba`(smb, nmb), `nfs-utils`(nfs-server), `vsftpd` | 방화벽 `--add-service=samba/nfs` |
| 메일 | `postfix`(기본 MTA), `dovecot` | sendmail 은 선택 |
| 원격 | `openssh-server`(sshd), `cockpit`(웹 콘솔 9090) | `systemctl enable --now cockpit.socket` |
| 프록시 | `squid` | 3128 |
| 컨테이너 | `podman` | `podman run/ps/images/pull`, 루트리스 지원 |
- 서비스 구축 3단계 = **설치 → 설정 → 기동(`enable --now`) → 방화벽/SELinux 허용 → 테스트**

## 12. 시험 대응 요령
- 문제 보기에 **구형·신형 명령이 함께 등장**: 정답 판별은 "기능이 맞는가" 기준. 예) 서비스 부팅 시 자동 시작 = `systemctl enable` (= `chkconfig on`)
- 설정 파일 경로·데몬 이름·포트를 표로 암기 (`docs` 의 핵심 표 참고)
- 명령어 옵션은 **`--help`/man 에서 확인 가능한 것들이 다수** — 옵션의 의미(-r 재귀, -f 강제, -v 상세)를 일반화

## ✍️ 연습문제
1. RHEL 8 계열에서 `yum` 명령이 실제로 사용하는 도구는? → **dnf**
2. 기본 네트워크 관리 서비스는? → **NetworkManager**
3. firewalld 규칙을 재부팅 후에도 유지하려면? → `--permanent` 후 `--reload`
4. XFS 파일시스템을 확장하는 명령? → `xfs_growfs`
5. SELinux 부울을 영구 변경하는 옵션? → `setsebool -P`
