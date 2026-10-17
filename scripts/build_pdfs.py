#!/usr/bin/env python3
"""학습 노트(Markdown) → PDF 재생성 도구.

- 읽기 편한 글자 크기(본문 약 9.5pt), 표 행이 페이지 중간에서 잘리지 않도록 정리
- 표 머리글은 페이지가 넘어가도 반복, 제목은 다음 내용과 같은 페이지에 유지
- 합본 PDF: 표지(쪽번호 없음) + 쪽수가 있는 목차 + 장별 새 페이지, PDF 북마크 포함
- 개별 PDF에도 PDF 북마크(제목 계층) 추가
- 생성 후 검사: 표 원문 노출(`|---`), 거의 빈 마지막 페이지

필요한 것 (scripts/requirements-pdf.txt):
    pip install -r scripts/requirements-pdf.txt
    글꼴: Noto Sans KR(본문), Nanum Gothic Coding(코드·도표)를 시스템에 설치
    브라우저: Chromium (PLAYWRIGHT_BROWSERS_PATH 로 이미 설치돼 있으면 자동 사용,
              그 외 CHROMIUM_PATH 환경변수로 실행 파일 지정)

사용법:
    python3 scripts/build_pdfs.py                 # 전체 재생성
    python3 scripts/build_pdfs.py --only 01_네트워크   # 파일명에 포함된 것만
    python3 scripts/build_pdfs.py --check         # 기존 pdf/ 검사만 (재생성 안 함)
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path

import pymupdf
from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pdf"
CERTS = ["네트워크관리사 2급", "리눅스마스터 2급"]

CSS = """
@page { size: A4; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0; color: #1f2933;
  font-family: "Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", "NanumGothic", sans-serif;
  font-size: 9.6pt; line-height: 1.62; word-break: keep-all; overflow-wrap: break-word;
}
h1, h2, h3, h4 { line-height: 1.35; break-after: avoid; break-inside: avoid; }
h1 { font-size: 19pt; margin: 0 0 10pt; padding-bottom: 6pt; border-bottom: 2.2pt solid #2f4f7f; color: #1d3557; }
h2 { font-size: 13.2pt; margin: 18pt 0 7pt; padding: 3pt 8pt; background: #eef3fb; border-left: 3.5pt solid #2f6fbf; color: #1d3557; }
h3 { font-size: 11pt; margin: 13pt 0 5pt; color: #22456f; }
h4 { font-size: 10pt; margin: 10pt 0 4pt; color: #22456f; }
p { margin: 4pt 0 6pt; }
ul, ol { margin: 3pt 0 7pt; padding-left: 17pt; }
li { margin: 1.5pt 0; }
li > ul, li > ol { margin: 1pt 0 2pt; }
hr { border: 0; border-top: 0.6pt solid #cfd6df; margin: 10pt 0; }
a { color: #1d5fa8; text-decoration: none; }
.ref { color: #1f2933; }
strong { color: #111827; }
code {
  font-family: "NanumGothicCoding", "Nanum Gothic Coding", "D2Coding", "DejaVu Sans Mono", "Noto Sans KR", monospace;
  font-size: 0.9em; background: #f0f3f7; padding: 0.5pt 2.5pt; border-radius: 2pt; word-break: break-all;
}
pre {
  margin: 5pt 0 9pt; padding: 6pt 8pt; background: #f4f6f9; border: 0.6pt solid #d9dfe7; border-left: 3pt solid #8aa4c8;
  border-radius: 3pt; font-size: 8.3pt; line-height: 1.5; white-space: pre-wrap; overflow-wrap: anywhere; word-break: normal;
}
pre code { background: none; padding: 0; font-size: inherit; word-break: normal; }
pre.keep { break-inside: avoid; }
blockquote {
  margin: 6pt 0 9pt; padding: 5pt 10pt; background: #fff7e6; border-left: 3.5pt solid #f0a020; border-radius: 0 3pt 3pt 0;
  break-inside: avoid;
}
blockquote > :first-child { margin-top: 0; } blockquote > :last-child { margin-bottom: 0; }
table { border-collapse: collapse; width: 100%; margin: 5pt 0 10pt; font-size: 8.7pt; line-height: 1.5; }
table.keep { break-inside: avoid; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th, td { border: 0.6pt solid #c9d1dc; padding: 3pt 6pt; text-align: left; vertical-align: top; overflow-wrap: break-word; word-break: keep-all; }
th { background: #e3ebf6; color: #1d3557; font-weight: 700; }
tbody tr:nth-child(even) td { background: #f8fafc; }
td code, th code { font-size: 0.92em; }
td pre { margin: 2pt 0; }

.chapter { break-before: page; }
.chapter:first-of-type { break-before: auto; }
.toc h1 { margin-bottom: 14pt; }
.toc ol { list-style: none; padding: 0; margin: 0; }
.toc li { display: flex; align-items: baseline; gap: 6pt; margin: 0; padding: 5.5pt 0; border-bottom: 0.5pt dotted #b8c2d0; font-size: 10.6pt; }
.toc .t { flex: 0 1 auto; }
.toc .d { flex: 1 1 auto; border-bottom: 0; }
.toc .p { flex: 0 0 auto; font-variant-numeric: tabular-nums; color: #22456f; font-weight: 700; }
.cover { height: 247mm; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
.cover .k { font-size: 11pt; letter-spacing: 2pt; color: #2f6fbf; margin-bottom: 14pt; }
.cover .h { font-size: 30pt; font-weight: 700; color: #1d3557; line-height: 1.3; }
.cover .s { margin-top: 14pt; font-size: 11pt; color: #52606d; }
.cover .rule { width: 60pt; border-top: 3pt solid #2f6fbf; margin: 18pt 0; }
"""

FOOTER = (
    '<div style="width:100%;padding:0 16mm;font-family:\'Noto Sans KR\',sans-serif;font-size:7.5pt;color:#7b8794;'
    'display:flex;justify-content:space-between;">'
    "<span>{label}</span><span><span class=\"pageNumber\"></span> / <span class=\"totalPages\"></span></span></div>"
)
NO_FOOTER = '<div style="font-size:1px"></div>'


# ----------------------------------------------------------------- markdown → html
def make_md():
    md = MarkdownIt("commonmark", {"html": True, "typographer": False}).enable(["table", "strikethrough"])
    return md


def render_md(md, text):
    tokens = md.parse(text)
    for tk in tokens:
        stack = []
        for ch in tk.children or []:
            if ch.type == "link_open":
                # 다른 .md 문서로 가는 링크는 PDF 에서 의미가 없으므로 일반 텍스트(span)로 바꾼다
                is_doc = (ch.attrGet("href") or "").split("#")[0].lower().endswith(".md")
                stack.append(is_doc)
                if is_doc:
                    ch.type, ch.content = "html_inline", '<span class="ref">'
            elif ch.type == "link_close":
                if stack.pop():
                    ch.type, ch.content = "html_inline", "</span>"
    return mark_unbreakable(md.renderer.render(tokens, md.options, {}))


def mark_unbreakable(body):
    """짧은 표/코드블록은 페이지 중간에서 쪼개지지 않게 'keep' 클래스를 붙인다."""

    def table(m):
        rows = m.group(0).count("<tr>")
        return m.group(0).replace("<table>", '<table class="keep">', 1) if rows <= 9 else m.group(0)

    def pre(m):
        lines = m.group(0).count("\n")
        return m.group(0).replace("<pre>", '<pre class="keep">', 1) if lines <= 22 else m.group(0)

    body = re.sub(r"<table>.*?</table>", table, body, flags=re.S)
    body = re.sub(r"<pre>.*?</pre>", pre, body, flags=re.S)
    return body


def page_html(inner, title):
    return (
        f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{html.escape(title)}</title>'
        f"<style>{CSS}</style></head><body>{inner}</body></html>"
    )


def headings(md_text):
    """(level, text) — 코드 펜스 밖의 #, ## 제목."""
    out, in_code = [], False
    for line in md_text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
        m = None if in_code else re.match(r"^(#{1,2})\s+(.+?)\s*#*\s*$", line)
        if m:
            out.append((len(m.group(1)), re.sub(r"[*`]", "", m.group(2)).strip()))
    return out


# ----------------------------------------------------------------- pdf helpers
def locate_headings(doc, heads, start_page=0):
    """문서 순서대로 제목이 나오는 페이지를 찾는다. 큰 글씨 span 의 텍스트가 제목과 같을 때만 인정."""
    result, page_i = [], start_page
    for level, text in heads:
        key = re.sub(r"\s+", "", text)
        found = None
        for pi in range(page_i, len(doc)):
            for block in doc[pi].get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    t = "".join(s["text"] for s in line["spans"])
                    size = max(s["size"] for s in line["spans"]) if line["spans"] else 0
                    lk = re.sub(r"\s+", "", t)
                    # 제목이 두 줄로 접히면 첫 줄은 제목의 앞부분이므로 양방향 접두어 비교
                    if size >= 11.5 and len(lk) >= 4 and (key.startswith(lk) or lk.startswith(key)):
                        found = pi
                        break
                if found is not None:
                    break
            if found is not None:
                break
        if found is None:
            result.append((level, text, None))
        else:
            result.append((level, text, found))
            page_i = found
    return result


def to_pdf(page, inner, title, label, path, footer=True, scale=1.0):
    page.set_content(page_html(inner, title), wait_until="load")
    page.evaluate("document.fonts.ready")
    page.pdf(
        path=str(path),
        format="A4",
        margin={"top": "15mm", "bottom": "17mm", "left": "16mm", "right": "16mm"},
        display_header_footer=footer,
        header_template=NO_FOOTER,
        footer_template=FOOTER.format(label=html.escape(label)) if footer else NO_FOOTER,
        print_background=True,
        prefer_css_page_size=False,
        scale=scale,
    )


def set_bookmarks(path, located, offset=0, title=None):
    doc = pymupdf.open(path)
    toc, last = [], 1
    for level, text, pi in located:
        if pi is None:
            continue
        lvl = min(level, last + 1) if toc else 1
        toc.append([lvl, text, pi + 1 + offset])
        last = lvl
    if toc:
        doc.set_toc(toc)
    if title:
        doc.set_metadata({"title": title, "producer": "scripts/build_pdfs.py"})
    doc.save(str(path) + ".tmp", garbage=3, deflate=True)
    doc.close()
    os.replace(str(path) + ".tmp", path)


def has_stub_last_page(path, min_words=30):
    doc = pymupdf.open(path)
    n = len(doc)
    stub = n > 1 and len(doc[n - 1].get_text("words")) < min_words
    doc.close()
    return stub


def to_pdf_fit(page, inner, title, label, path):
    """마지막 쪽에 몇 줄만 남는 '토막 페이지'가 생기면 내용 배율을 3%씩 줄여 가며 없앤다(최소 0.88)."""
    for scale in (1.0, 0.97, 0.94, 0.91, 0.88):
        to_pdf(page, inner, title, label, path, scale=scale)
        if not has_stub_last_page(path):
            return scale
    to_pdf(page, inner, title, label, path)  # 해결 못 하면 원래 배율 유지
    return 1.0


# ----------------------------------------------------------------- 문서 목록
def sources():
    """(md 경로, 출력 pdf 경로, 라벨) 목록과 합본 정의."""
    items = [(ROOT / "README.md", OUT / "README(전체 개요).pdf", "자격증 준비 2026 하반기 · README")]
    for f in sorted((ROOT / "00_공통").glob("*.md")):
        items.append((f, OUT / "00_공통" / (f.stem + ".pdf"), f"자격증 준비 2026 하반기 · 00_공통 · {f.stem}"))
    combos = {}
    for cert in CERTS:
        d = ROOT / cert
        files = sorted(d.glob("*.md"), key=lambda p: (p.name != "README.md", p.name))
        combos[cert] = files
        for f in files:
            name = "00_README(시험 개요)" if f.name == "README.md" else f.stem
            items.append((f, OUT / cert / (name + ".pdf"), f"{cert} · {name if f.name != 'README.md' else 'README'}"))
    return items, combos


# ----------------------------------------------------------------- 검사
def check_pdf(path):
    problems = []
    doc = pymupdf.open(path)
    n = len(doc)
    for i, p in enumerate(doc):
        t = p.get_text()
        if re.search(r"\|\s*-{2,}\s*\|", t) or re.search(r"\|-+\|", t):
            problems.append(f"{i + 1}쪽: 표 구분선(|---|)이 그대로 노출됨")
        words = p.get_text("words")
        if words and max(w[2] for w in words) > p.rect.width - 12:
            problems.append(f"{i + 1}쪽: 본문이 오른쪽 여백 밖으로 나감")
        if i == n - 1 and n > 1 and len(words) < 30 and "합본" not in path.name:
            problems.append(f"{i + 1}쪽(마지막): 내용이 거의 없음(단어 {len(words)}개)")
    return problems


def check_all():
    bad = 0
    for f in sorted(OUT.rglob("*.pdf")):
        pr = check_pdf(f)
        if pr:
            bad += 1
            print(f"✗ {f.relative_to(OUT)}")
            for x in pr:
                print("    ", x)
    total = len(list(OUT.rglob("*.pdf")))
    print(f"검사 완료: {total}개 중 문제 {bad}개")
    return bad


# ----------------------------------------------------------------- 메인
def build(only):
    items, combos = sources()
    md = make_md()
    exe = os.environ.get("CHROMIUM_PATH")
    if not exe:
        base = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
        cands = sorted(base.glob("chromium-*/chrome-linux/chrome"))
        exe = str(cands[-1]) if cands else None
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=exe, args=["--no-sandbox"]) if exe else pw.chromium.launch()
        page = browser.new_page()

        # 개별 PDF
        for src, dst, label in items:
            if only and only not in str(src):
                continue
            text = src.read_text(encoding="utf-8")
            dst.parent.mkdir(parents=True, exist_ok=True)
            scale = to_pdf_fit(page, render_md(md, text), src.stem, label, dst)
            heads = headings(text)
            set_bookmarks(dst, locate_headings(pymupdf.open(dst), heads), title=heads[0][1] if heads else src.stem)
            print(f"  {dst.relative_to(ROOT)}  {len(pymupdf.open(dst))}쪽" + (f"  (배율 {scale})" if scale != 1.0 else ""))

        # 합본 PDF
        for cert, files in combos.items():
            if only and only not in cert + "합본":
                continue
            build_combined(page, md, cert, files)
        browser.close()


def build_combined(page, md, cert, files):
    texts = [f.read_text(encoding="utf-8") for f in files]
    chapters = []  # (title, html)
    for f, t in zip(files, texts):
        h = headings(t)
        title = h[0][1] if h else f.stem
        chapters.append((title, render_md(md, t)))
    body_title = f"{cert} 학습 자료 합본"

    def body_html(page_numbers):
        toc = "".join(
            f'<li><span class="t">{html.escape(t)}</span><span class="d"></span><span class="p">{page_numbers[i]}</span></li>'
            for i, (t, _) in enumerate(chapters)
        )
        note = '<p style="margin-top:12pt;font-size:8.5pt;color:#7b8794">쪽 번호는 표지를 제외한 본문 기준이며 각 페이지 하단의 번호와 같습니다. PDF 뷰어의 북마크(개요)로도 이동할 수 있습니다.</p>'
        parts = [f'<section class="toc"><h1>목차</h1><ol>{toc}</ol>{note}</section>']
        parts += [f'<section class="chapter">{h}</section>' for _, h in chapters]
        return "".join(parts)

    tmp = OUT / cert / "_합본_body.pdf"
    # 1차: 쪽수 자리표시자로 렌더링 → 장 시작 페이지 계산 → 2차: 실제 쪽수로 다시 렌더링
    nums = ["00"] * len(chapters)
    for _ in range(2):
        to_pdf(page, body_html(nums), body_title, body_title, tmp)
        doc = pymupdf.open(tmp)
        ch_heads = [(1, t) for t, _ in chapters]
        loc = locate_headings(doc, ch_heads, start_page=1)
        nums = [str(pi + 1) if pi is not None else "-" for _, _, pi in loc]
        doc.close()

    # 표지(쪽번호 없음) + 본문 병합, 북마크
    cover_html = (
        '<div class="cover"><div class="k">2026 하반기 시험 대비</div>'
        f'<div class="h">{html.escape(cert)}<br>학습 자료 합본</div><div class="rule"></div>'
        f'<div class="s">{len(chapters)}개 문서 · 마크다운 노트를 한 권으로 묶은 PDF</div></div>'
    )
    cover = OUT / cert / "_합본_cover.pdf"
    to_pdf(page, cover_html, body_title, "", cover, footer=False)

    all_heads = []
    for t in texts:
        all_heads += [h for h in headings(t) if h[0] <= 2]
    out = OUT / cert / f"{cert}_전체(합본).pdf"
    merged = pymupdf.open(cover)
    merged.insert_pdf(pymupdf.open(tmp))
    merged.save(out)
    merged.close()
    # 북마크: 표지(1쪽) + 목차(본문 1쪽 = 전체 2쪽) + 장·절. 본문 쪽 → 전체 쪽은 +1(표지) 오프셋
    body_loc = locate_headings(pymupdf.open(tmp), all_heads, start_page=1)
    set_bookmarks(out, [(1, "표지", -1), (1, "목차", 0)] + body_loc, offset=1, title=body_title)
    cover.unlink()
    tmp.unlink()
    print(f"  {out.relative_to(ROOT)}  {len(pymupdf.open(out))}쪽")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="경로에 이 문자열이 포함된 문서만 생성")
    ap.add_argument("--check", action="store_true", help="기존 pdf/ 만 검사")
    args = ap.parse_args()
    if not args.check:
        build(args.only)
    sys.exit(1 if check_all() else 0)


if __name__ == "__main__":
    main()
