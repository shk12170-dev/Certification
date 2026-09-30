#!/usr/bin/env python3
"""content/questions/**/*.json 문제은행 검증 (+ 선택지 섞기).

사용법:
  python3 scripts/validate_questions.py            # 검증만
  python3 scripts/validate_questions.py --shuffle  # 선택지 순서를 섞어 저장 (새 문항 추가 직후에만 사용)
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content" / "questions"
REQUIRED = {"id", "topic", "q", "c", "a", "e"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(path, data, seen_ids):
    errors = []
    for key in ("cert", "subject", "note", "questions"):
        if key not in data:
            errors.append(f"{path.name}: '{key}' 누락")
    for i, q in enumerate(data.get("questions", [])):
        where = f"{path.name}[{i}] {q.get('id', '?')}"
        missing = REQUIRED - q.keys()
        if missing:
            errors.append(f"{where}: 필드 누락 {sorted(missing)}")
            continue
        if q["id"] in seen_ids:
            errors.append(f"{where}: id 중복")
        seen_ids.add(q["id"])
        if len(q["c"]) != 4 or len(set(q["c"])) != 4:
            errors.append(f"{where}: 보기는 서로 다른 4개여야 함")
        if not isinstance(q["a"], int) or not 0 <= q["a"] < len(q["c"]):
            errors.append(f"{where}: 정답 인덱스 오류")
    return errors


def shuffle(path, data):
    rng = random.Random(path.name)  # 파일명 시드. 이미 섞인 파일에 다시 실행하면 순서가 또 바뀜
    for q in data["questions"]:
        correct = q["c"][q["a"]]
        rng.shuffle(q["c"])
        q["a"] = q["c"].index(correct)
    head = {k: v for k, v in data.items() if k != "questions"}
    lines = [json.dumps(q, ensure_ascii=False) for q in data["questions"]]
    body = ",\n    ".join(lines)
    head_json = json.dumps(head, ensure_ascii=False, indent=2)[:-2]  # 마지막 "}" 제거
    path.write_text(f'{head_json},\n  "questions": [\n    {body}\n  ]\n}}\n', encoding="utf-8")


def main():
    do_shuffle = "--shuffle" in sys.argv
    files = sorted(ROOT.rglob("*.json"))
    errors, seen, dist, total = [], set(), Counter(), 0
    for path in files:
        data = load(path)
        errors += validate(path, data, seen)
        if do_shuffle and not errors:
            shuffle(path, data)
            data = load(path)
        for q in data["questions"]:
            dist[q["a"]] += 1
        total += len(data["questions"])
        print(f"{path.relative_to(ROOT)}: {len(data['questions'])}문항")
    print(f"총 {total}문항, 정답 위치 분포(0~3): {[dist[i] for i in range(4)]}")
    if errors:
        print("\n".join(["오류:"] + errors))
        sys.exit(1)
    print("검증 통과")


if __name__ == "__main__":
    main()
