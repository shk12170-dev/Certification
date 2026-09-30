---
title: 리눅스 일반
cert: linux-master-2
order: 1
---

# 1과목. 리눅스 일반

## 1. 리눅스의 이해
- 1991 **리누스 토르발스** 커널 공개. UNIX 계열, 멀티유저·멀티태스킹, 오픈소스
- **GPL**(GNU General Public License): 자유로운 사용·수정·배포, 파생물도 GPL(카피레프트). 리처드 스톨만/GNU/FSF
- 커널(Kernel) + 쉘 + 유틸리티 = 배포판. 커널 버전 `주.부.패치`
- 배포판 계열
  | 계열 | 배포판 | 패키지 |
  |---|---|---|
  | Red Hat | RHEL, CentOS Stream, Rocky, Alma, Fedora | rpm / yum / dnf |
  | Debian | Debian, Ubuntu, Mint | dpkg / apt |
  | SUSE | openSUSE, SLES | rpm / zypper |
  | 기타 | Arch(pacman), Slackware, Gentoo(emerge) |
- 커널 구조: 모놀리식(모듈 적재 가능). 모듈 `lsmod`, `modprobe`, `insmod`, `rmmod`, `depmod`

## 2. 설치
- **파티션**: MBR(최대 2TB, 기본 파티션 4개/확장 1개+논리) vs **GPT**(UEFI, 큰 디스크, 128개)
- 디스크 장치명: `/dev/sda`(SCSI/SATA), `/dev/hda`(구 IDE), `/dev/nvme0n1`, `/dev/vda`(가상). `sda1`=첫 파티션, 논리는 `sda5`부터
- 권장 파티션: `/`, `/boot`, `swap`(RAM 대비), `/home`, `/var`
- 설치 방식: CD/USB, 네트워크(PXE, NFS, HTTP, FTP), **Kickstart**(RHEL 무인 설치), preseed(Debian)
- 스왑: 가상 메모리 영역, `mkswap`, `swapon`, `swapoff`, `free -m`

## 3. 부팅 과정
1. BIOS/UEFI POST → 부트 로더 탐색
2. **부트로더**: GRUB(GRUB2: `/boot/grub2/grub.cfg`, 설정 `/etc/default/grub`, 갱신 `grub2-mkconfig`), LILO(구)
3. 커널 로딩 + initramfs → 루트 마운트
4. `init`/**systemd**(PID 1) 기동 → 런레벨/타깃 → 서비스 시작
5. 로그인 프롬프트

### 런레벨 ↔ systemd 타깃
| 런레벨 | 의미 | systemd target |
|---|---|---|
| 0 | 종료 | poweroff.target |
| 1 (S) | 단일 사용자(복구) | rescue.target |
| 2 | 다중 사용자(NFS 없음, 일부) | multi-user |
| 3 | **다중 사용자 CLI** | multi-user.target |
| 4 | 미사용 | |
| 5 | **GUI** | graphical.target |
| 6 | 재부팅 | reboot.target |
- 확인/변경: `runlevel`, `init 3`, `telinit`, `systemctl get-default`, `systemctl set-default graphical.target`, `systemctl isolate`
- 기본 런레벨: `/etc/inittab`(SysV) → `default.target`(systemd)
- 종료: `shutdown -h now`, `shutdown -r +10`, `halt`, `poweroff`, `reboot`, `init 0/6`

## 4. 기본 명령어
| 분류 | 명령 |
|---|---|
| 도움말 | `man`, `info`, `--help`, `whatis`, `apropos` |
| 디렉터리 | `pwd`, `cd`, `ls -alh`, `mkdir -p`, `rmdir`, `tree` |
| 파일 | `cp -r`, `mv`, `rm -rf`, `touch`, `cat`, `tac`, `more`, `less`, `head -n`, `tail -f`, `wc`, `sort`, `uniq`, `cut`, `diff` |
| 정보 | `uname -a`, `hostname`, `whoami`, `who`, `w`, `id`, `last`, `date`, `cal`, `uptime`, `df`, `du`, `free` |
| 기타 | `echo`, `history`, `alias`, `clear`, `which`, `env`, `export` |

- 경로: 절대(`/`시작)/상대, `.` 현재, `..` 상위, `~` 홈, `-` 이전 디렉터리
- 와일드카드: `*`, `?`, `[abc]`
- man 섹션: 1 일반명령, 2 시스템콜, 3 라이브러리, 4 장치, 5 설정파일, 6 게임, 7 기타, 8 관리명령

## ✍️ 연습문제
1. 리눅스 커널을 처음 만든 사람? → **리누스 토르발스**
2. 런레벨 5에 해당하는 systemd 타깃? → **graphical.target**
3. MBR 방식에서 기본 파티션 최대 개수? → **4개**
4. 두 번째 SATA 디스크의 첫 번째 파티션? → `/dev/sdb1`
5. 기본 타깃을 CLI로 바꾸는 명령? → `systemctl set-default multi-user.target`
6. 시스템을 10분 후 재부팅? → `shutdown -r +10`
