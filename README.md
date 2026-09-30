# Certification
2026 하반기 **네트워크관리사 2급 · 리눅스마스터 2급** 대비 학습 자료.

## 구조
```
docs/
  exam-info.md     시험 개요 · 검증 상태(✅/❓) · 대비 일정
  sources.md       참고 출처
content/
  index.json       웹앱용 목차 (자격증 → 과목 → 파일)
  questions/       과목별 문제은행 JSON (4지선다, 총 144문항)
  network-manager-2/   01 네트워크 일반 · 02 TCP/IP · 03 NOS · 04 네트워크 운용기기
  linux-master-2/      01 리눅스 일반 · 02 운영 및 관리 · 03 활용
```
각 노트는 YAML frontmatter(title, cert, order) + Markdown 이며, 끝에 연습문제가 있습니다.

## 문제은행 형식
`content/questions/<cert>/<NN-subject>.json`
```json
{"cert": "...", "subject": "...", "note": "노트 경로",
 "questions": [{"id": "ip-01", "topic": "IP 주소", "q": "문제", "c": ["보기1","보기2","보기3","보기4"], "a": 2, "e": "해설"}]}
```
`a` 는 정답 보기의 0부터 시작하는 인덱스입니다. 문항을 추가한 뒤에는 검증하세요:
```
python3 scripts/validate_questions.py            # 형식·중복·정답 인덱스 검증
python3 scripts/validate_questions.py --shuffle  # 새 문항 추가 직후 보기 순서 섞기 (이미 섞인 파일엔 재실행 금지)
```

## 상태
- 이론 노트 1차 정리 완료 (직접 정리한 요약, 기출 복제 아님)
- ⚠️ 시험 일정·문항 수는 공식 사이트 미확인 항목이 있음 → `docs/exam-info.md` 참고
- 예상문제 144문항(직접 작성) 완료 — 과목당 20~22문항
- 예정: 웹앱 뷰어, 문항 확충
