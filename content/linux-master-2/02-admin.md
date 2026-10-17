---
title: 리눅스 운영 및 관리
cert: linux-master-2
order: 2
---

# 2과목. 리눅스 운영 및 관리

> 2차 시험 중심 과목 (48문항으로 보고된 비중이 가장 큼 ❓). 명령어와 옵션, 설정 파일 위치를 정확히 암기.

## 1. 파일 시스템 · 디렉터리 (FHS)
| 경로 | 용도 | 경로 | 용도 |
|---|---|---|---|
| `/bin` | 기본 명령 | `/etc` | 설정 파일 |
| `/sbin` | 관리자 명령 | `/var` | 로그·스풀·캐시 |
| `/usr` | 프로그램/라이브러리 | `/tmp` | 임시 |
| `/home` | 사용자 홈 | `/dev` | 장치 파일 |
| `/root` | root 홈 | `/proc` | 커널·프로세스 가상 FS |
| `/boot` | 커널·부트로더 | `/sys` | 장치/드라이버 가상 FS |
| `/lib` | 공유 라이브러리 | `/mnt`,`/media` | 마운트 지점 |
| `/opt` | 추가 패키지 | `/srv` | 서비스 데이터 |

- 파일 시스템: ext2 → ext3(저널링) → **ext4**, XFS(RHEL7+ 기본), Btrfs, vfat, NTFS(ntfs-3g), ISO9660, NFS, swap
- **inode**: 파일 메타데이터(권한, 소유자, 크기, 시간, 블록 포인터). **파일명은 포함 안 함** (디렉터리 엔트리에 있음). `ls -i`, `df -i`, `stat`
- 슈퍼블록: FS 전체 정보. `dumpe2fs`, `tune2fs`
- 링크: **하드링크**(같은 inode, 다른 FS/디렉터리 불가) `ln A B` / **심볼릭**(경로 저장, 다른 FS 가능) `ln -s A B`
- 파일 종류 (`ls -l` 첫 글자): `-` 일반, `d` 디렉터리, `l` 링크, `b` 블록, `c` 문자, `s` 소켓, `p` 파이프

## 2. 권한
```
-rwxr-xr-- 1 user group ...
 u  g  o      r=4 w=2 x=1 → 754
```
- `chmod 755 f` / `chmod u+x,g-w f` / `chmod -R`
- 특수 권한: **SUID**(4000, 소유자 권한으로 실행, `s`) · **SGID**(2000) · **Sticky**(1000, 삭제 제한, `/tmp` 의 `t`)
  - 예: `chmod 4755 f`, `chmod u+s`, `chmod +t dir`
- `chown user:group f`, `chgrp`, **`umask`** (기본 022: 파일 666−022=644, 디렉터리 777−022=755)
- `lsattr`/`chattr +i`(불변)

## 3. 검색 · 텍스트 처리 · 리다이렉션
- `find / -name "*.conf" -user root -perm -4000 -size +10M -mtime -7 -type f -exec cmd {} \;`
- `grep -i -n -r -v -c -E pattern file`, `egrep`, `fgrep`
- 정규식: `^` 시작, `$` 끝, `.` 임의 1자, `*` 0회 이상, `[ ]`, `[^ ]`
- `locate`(DB `updatedb`), `which`, `whereis`, `type`
- **표준 입출력**: 0 stdin, 1 stdout, 2 stderr
  - `>` 덮어쓰기, `>>` 추가, `<` 입력, `2>` 에러, `2>&1`, `&>`, `/dev/null`
  - 파이프 `|`, `tee`, `xargs`
- 텍스트 도구: `sort -n -r -k`, `uniq -c`, `cut -d: -f1`, `tr`, `wc -l`, `sed 's/a/b/g'`, `awk '{print $1}'`, `diff`

## 4. vi 에디터
- 모드: **명령** / **입력**(`i a o I A O`) / **ex(`:`)**
- 저장종료: `:w`, `:q`, `:wq`, `ZZ`, `:q!`, `:w!`
- 이동: `h j k l`, `0`, `$`, `gg`, `G`, `:숫자`, `w`, `b`
- 편집: `x`, `dd`, `yy`, `p`, `u`, `dw`, `cw`, `D`, `.`
- 검색: `/문자`, `?문자`, `n`, `N`, 치환 `:%s/a/b/g`
- `:set nu`, `:set ai`

## 5. 쉘 · 스크립트
- 쉘: **bash**(기본), sh, csh, ksh, zsh. 확인 `echo $SHELL`, `/etc/shells`
- 설정 파일: `/etc/profile`(전체) → `~/.bash_profile`(로그인) → `~/.bashrc`(비로그인), `~/.bash_logout`
- 변수: `VAR=val`, `export`, `$VAR`, `$?`(종료값), `$$`(PID), `$0`, `$1..`, `$#`, `$@`
- 환경변수 PATH, HOME, PS1, LANG, USER
- 스크립트: 첫 줄 `#!/bin/bash`, 실행권한 필요
```bash
#!/bin/bash
for i in 1 2 3; do echo $i; done
if [ -f /etc/passwd ]; then echo yes; else echo no; fi
while [ $n -lt 5 ]; do n=$((n+1)); done
case $1 in start) ... ;; *) ... ;; esac
```
- 비교: 숫자 `-eq -ne -gt -lt -ge -le`, 문자열 `= != -z -n`, 파일 `-e -f -d -r -w -x`
- 작업제어: `&`, `jobs`, `fg`, `bg`, `Ctrl+Z`(정지), `Ctrl+C`, `nohup`

## 6. 프로세스
- `ps aux`, `ps -ef`, `top`(`k` kill, `M` 메모리 정렬, `P` CPU), `pstree`, `pgrep`, `pidof`
- PID 1 = init/systemd. 상태: R 실행, S 대기, D 불가대기, **T 정지**, **Z 좀비**
- **시그널** `kill -l`: 1 HUP(재읽기), 2 INT, 9 **KILL**(강제), 15 **TERM**(기본), 18 CONT, 19 STOP
- `killall`, `pkill`, `nice -n`(−20~19, 낮을수록 우선), `renice`
- **cron**: `crontab -e/-l/-r`, 형식 `분 시 일 월 요일 명령` (`*/5 * * * *`), 설정 `/etc/crontab`, `/etc/cron.d`, 제한 `cron.allow/deny`
- `at`(1회 예약, `atq`, `atrm`), `batch`
- 백그라운드/데몬, 부하 `uptime`(load average 1·5·15분), `vmstat`, `iostat`, `sar`

## 7. 패키지 관리
| 구분 | RPM 계열 | DEB 계열 |
|---|---|---|
| 저수준 | `rpm -ivh/-Uvh/-e/-qa/-qi/-ql/-qf/-V` | `dpkg -i/-r/-P/-l/-L/-S` |
| 고수준 | `yum`/`dnf install/remove/update/search/info/list/provides` | `apt install/remove/update/upgrade/search` |
| 저장소 | `/etc/yum.repos.d/*.repo` | `/etc/apt/sources.list` |
- 소스 설치: `tar xvzf` → `./configure` → `make` → `make install`
- 압축/백업: `tar c/x/t/v/z/j/f`, `gzip/gunzip`(.gz), `bzip2`(.bz2), `xz`, `zip/unzip`, `cpio`, `dd`, `rsync`, `dump/restore`

## 8. 사용자 · 그룹
| 파일 | 내용 |
|---|---|
| `/etc/passwd` | `user:x:UID:GID:설명:홈:쉘` (7필드) |
| `/etc/shadow` | `user:암호해시:마지막변경:최소:최대:경고:비활성:만료` |
| `/etc/group` | `그룹:x:GID:멤버` |
| `/etc/skel` | 신규 계정 기본 파일 |
| `/etc/login.defs`, `/etc/default/useradd` | 기본값 |
- UID: root 0, 시스템 1~999(RHEL7+), 일반 1000~
- `useradd -u -g -G -d -s -m -c`, `usermod -aG -L -U -s`, `userdel -r`, `passwd -l/-u/-S/-e`, `chage -l/-M/-E`, `groupadd/groupmod/groupdel`, `gpasswd`, `newgrp`, `id`, `groups`
- `su -`, `sudo` (`/etc/sudoers`, `visudo`)

## 9. 디스크 · 마운트 · 쿼터 · LVM · RAID
- `fdisk -l`, `fdisk /dev/sdb`(n p t w), `parted`, `mkfs -t ext4`/`mkfs.xfs`, `fsck`/`e2fsck`(언마운트 상태), `mkswap`
- `mount -t ext4 -o ro /dev/sdb1 /mnt`, `umount`, `mount -a`, 확인 `/etc/mtab`, `/proc/mounts`
- **/etc/fstab**: `장치 마운트지점 FS종류 옵션 dump fsck순서` (6필드). 옵션 defaults, ro, noexec, nosuid, **usrquota,grpquota**
- **쿼터**: `quotacheck -cug`, `edquota -u`, `quotaon/off`, `repquota`, `quota`
- **LVM**: `pvcreate` → `vgcreate` → `lvcreate -L 10G -n lv vg` → `mkfs` → mount. 확장 `lvextend -r`, `vgextend`
- **RAID**: 0 스트라이프(속도), 1 미러, 5 분산패리티(3+), 6, 10. 소프트웨어 RAID `mdadm`, `/proc/mdstat`
- 사용량: `df -h`, `du -sh`, `lsblk`, `blkid`

## 10. 커널 · 시스템 관리 · 로그
- 커널 파라미터: `sysctl -a`, `/etc/sysctl.conf`, `/proc/sys/`
- 하드웨어 정보: `lspci`, `lsusb`, `lscpu`, `dmesg`, `/proc/cpuinfo`, `/proc/meminfo`, `/proc/version`, `/proc/interrupts`
- **syslog**: `/etc/rsyslog.conf` (`facility.priority  대상`), 우선순위 emerg > alert > crit > err > warning > notice > info > debug
- 주요 로그: `/var/log/messages`(일반), `secure`(인증; Debian `auth.log`), `maillog`, `cron`, `boot.log`, `dmesg`, `wtmp`(`last`), `btmp`(`lastb`), `lastlog`
- `journalctl -u 서비스`, `-b`, `-f`, 로그 순환 `logrotate` (`/etc/logrotate.conf`)
- **systemctl**: `start/stop/restart/reload/status/enable/disable/is-enabled/list-units`, 유닛 `/etc/systemd/system`, `/usr/lib/systemd/system`
- SysV: `chkconfig --list/--level 35 httpd on`, `service httpd start`, `/etc/init.d`, `/etc/rc.d/rcN.d`(S=시작, K=종료)
- 시간: `date`, `hwclock`, `ntpdate`, `chronyd`, `timedatectl`

## ✍️ 연습문제
1. `/etc/passwd` 의 필드 수? → **7**
2. 소유자만 읽고 쓰기 가능하게? → `chmod 600`
3. 모든 프로세스를 전체 형식으로 보는 명령? → `ps -ef`
4. 프로세스를 정상 종료(TERM) 시그널 번호? → **15**
5. 매일 새벽 3시 30분 실행 cron? → `30 3 * * * 명령`
6. 하드링크가 불가능한 경우? → **다른 파일시스템, 디렉터리**
7. LVM 생성 순서? → **PV → VG → LV**
8. 마운트 시 쿼터 사용 옵션? → `usrquota,grpquota`
