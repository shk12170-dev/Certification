# 학습 웹앱 · 문제은행
저장소 루트 `README.md` 의 학습 노트와 별개로, `content/` 의 요약 노트와 문제은행(317문항)을 보는 정적 웹앱입니다.
(저장소 루트의 `index.html` 이 이 앱의 진입점입니다.)

## 웹앱 실행
빌드가 필요 없는 정적 사이트입니다. `file://` 로는 데이터를 읽지 못하므로 서버로 여세요.
```
python3 -m http.server 8000     # → http://localhost:8000
```
GitHub Pages: 저장소 **Settings → Pages → Deploy from a branch** 에서 브랜치와 `/ (root)` 선택.

기능: 이론 노트(목차·표·읽음 표시) · 과목별 퀴즈(키보드 1~4, Enter) · 전과목 모의고사(랜덤 40문항) · 오답노트 · 전체 검색 · 다크 모드.
진행 기록은 브라우저 `localStorage` 에만 저장됩니다.

## 구조
```
index.html, app/       웹앱 (app.js, style.css, vendor/marked)  ← 루트의 한글 폴더·pdf/ 는 이 앱과 무관
docs/
  exam-info.md         시험 개요 · 검증 상태(✅/❓) · 대비 일정
  sources.md           참고 출처
content/
  index.json           웹앱용 목차 (자격증 → 과목 → 노트/문제)
  network-manager-2/   01 네트워크 일반 · 02 TCP/IP · 03 NOS · 04 운용기기 · 05 보강(정보보안·신기술)
  linux-master-2/      01 일반 · 02 운영·관리 · 03 활용 · 04 보강(Rocky Linux 8 변경점)
  questions/           과목별 문제은행 JSON (4지선다, 317문항)
scripts/validate_questions.py
```

## 문제 추가
`content/questions/<cert>/<NN-subject>.json`
```json
{"cert": "...", "subject": "...", "note": "노트 경로",
 "questions": [{"id": "ip-01", "topic": "IP 주소", "q": "문제", "c": ["보기1","보기2","보기3","보기4"], "a": 2, "e": "해설"}]}
```
`a` 는 정답 보기의 0부터 시작하는 인덱스입니다. 새 과목 파일은 `content/index.json` 에도 등록하세요.
```
python3 scripts/validate_questions.py                        # 형식·중복·정답 인덱스 검증
python3 scripts/validate_questions.py --shuffle 새파일.json   # 새로 추가한 파일만 보기 순서 섞기
```

## 상태
- 이론 노트 9개: 직접 정리한 요약이며 기출·교재 복제 아님
- 예상문제 317문항(직접 작성)
- ⚠️ 시험 일정·문항 수·출제기준 변경은 공식 사이트 미확인(❓) 항목이 있음 → `docs/exam-info.md`

## PDF 재생성
`pdf/` 의 PDF 는 Markdown 노트에서 `scripts/build_pdfs.py` 로 만듭니다 (읽기 편한 글자 크기, 표 행 분리 방지, 합본 목차·북마크).
```
pip install -r scripts/requirements-pdf.txt     # + Noto Sans KR, Nanum Gothic Coding 글꼴, Chromium
python3 scripts/build_pdfs.py                   # 전체 재생성 (끝에 표 깨짐·토막 페이지 자동 검사)
python3 scripts/build_pdfs.py --only 01_네트워크 # 일부만
python3 scripts/build_pdfs.py --check           # 기존 PDF 검사만
```
