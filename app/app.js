/* 자격증 스터디 웹앱 — 빌드 없는 정적 SPA (해시 라우팅)
 * 데이터: content/index.json, content/**.md, content/questions/**.json
 */
(function () {
  "use strict";

  const STORE_KEY = "cert-study-v1";
  const MOCK_SIZE = 40;
  const app = document.getElementById("app");

  /* ---------- 저장소 (localStorage 실패 대비) ---------- */
  let memoryStore = null;
  function loadStore() {
    if (memoryStore) return memoryStore;
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (raw) { memoryStore = JSON.parse(raw); return memoryStore; }
    } catch (e) { /* 무시 */ }
    memoryStore = { read: {}, scores: {}, wrong: {} };
    return memoryStore;
  }
  function saveStore() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(loadStore())); } catch (e) { /* 무시 */ }
  }

  /* ---------- 유틸 ---------- */
  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === false || v == null) continue;
      if (k === "class") el.className = v;
      else if (k === "html") el.innerHTML = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const c of children.flat()) {
      if (c == null || c === false) continue;
      el.append(c.nodeType ? c : document.createTextNode(String(c)));
    }
    return el;
  }
  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
  function render(...nodes) {
    app.replaceChildren(...nodes.flat());
    window.scrollTo(0, 0);
    app.focus({ preventScroll: true });
  }
  function parseHash() {
    const raw = location.hash.replace(/^#\/?/, "");
    const [path, query = ""] = raw.split("?");
    return { parts: path.split("/").filter(Boolean).map(decodeURIComponent), params: new URLSearchParams(query) };
  }

  /* ---------- 데이터 로딩 (캐시) ---------- */
  const cache = new Map();
  async function fetchCached(path, type) {
    if (!cache.has(path)) {
      cache.set(path, fetch(path).then((r) => {
        if (!r.ok) throw new Error(`${path} 불러오기 실패 (${r.status})`);
        return type === "json" ? r.json() : r.text();
      }));
    }
    return cache.get(path);
  }
  const getIndex = () => fetchCached("content/index.json", "json");
  const getQuestions = (subject) => fetchCached("content/" + subject.questions, "json");

  function stripFrontmatter(md) {
    return md.replace(/^---\n[\s\S]*?\n---\n/, "");
  }

  /* ---------- 홈 ---------- */
  async function viewHome() {
    const index = await getIndex();
    const store = loadStore();
    const cards = await Promise.all(index.certs.map(async (cert) => {
      const readCount = cert.subjects.filter((s) => store.read[s.file]).length;
      const pct = Math.round((readCount / cert.subjects.length) * 100);
      const wrongCount = Object.values(store.wrong).filter((w) => w.cert === cert.id).length;
      const counts = await Promise.all(cert.subjects.map((s) => getQuestions(s).then((d) => d.questions.length)));
      const total = counts.reduce((a, b) => a + b, 0);

      const rows = cert.subjects.map((s, i) => {
        const score = store.scores[s.questions];
        return h("div", { class: "subject" },
          h("div", { class: "name" }, s.title, h("small", {}, `문제 ${counts[i]}개`)),
          s.supplement && h("span", { class: "badge sup" }, "보강"),
          store.read[s.file] && h("span", { class: "badge ok" }, "읽음"),
          score && h("span", { class: "badge" }, `최고 ${score.best}점`),
          h("a", { class: "btn", href: `#/note/${cert.id}/${i}` }, "노트"),
          h("a", { class: "btn primary", href: `#/quiz/${cert.id}/${i}` }, "퀴즈"));
      });

      return h("section", { class: "card" },
        h("h2", {}, cert.title),
        h("div", { class: "muted" }, `${cert.organizer} · 노트 ${readCount}/${cert.subjects.length} 읽음`),
        h("div", { class: "progress", role: "progressbar", "aria-valuenow": pct, "aria-valuemin": 0, "aria-valuemax": 100 },
          h("span", { style: `width:${pct}%` })),
        rows,
        h("div", { class: "btn-row" },
          h("a", { class: "btn primary", href: `#/quiz/${cert.id}/mock` }, `모의고사 (랜덤 ${Math.min(MOCK_SIZE, total)}문항)`),
          h("a", { class: "btn", href: `#/quiz/${cert.id}/wrong` }, `오답노트 (${wrongCount})`)));
    }));

    render(
      h("h1", {}, "2026 하반기 자격증 대비"),
      h("p", { class: "muted" }, "노트로 이론을 읽고, 과목별 퀴즈와 모의고사로 확인하세요. 진행 상황은 이 브라우저에만 저장됩니다."),
      h("div", { class: "cards" }, cards),
      h("div", { class: "btn-row" },
        h("a", { class: "btn", href: "#/doc/exam-info" }, "시험 개요·검증 상태"),
        h("a", { class: "btn", href: "#/doc/sources" }, "참고 출처"),
        h("button", { class: "btn", type: "button", onclick: resetProgress }, "진행 기록 초기화")));
  }

  function resetProgress() {
    if (!confirm("읽음 표시, 점수, 오답노트를 모두 지울까요?")) return;
    memoryStore = { read: {}, scores: {}, wrong: {} };
    saveStore();
    viewHome();
  }

  /* ---------- 문서/노트 ---------- */
  function enhanceDoc(root) {
    root.querySelectorAll("table").forEach((t) => {
      const wrap = h("div", { class: "table-wrap" });
      t.replaceWith(wrap);
      wrap.append(t);
    });
    const heads = [...root.querySelectorAll("h2, h3")];
    heads.forEach((el, i) => { el.id = "sec-" + i; });
    return heads;
  }

  function buildToc(heads) {
    const body = h("div", { class: "toc-body" },
      heads.filter((e) => e.tagName === "H2").map((e) => h("a", { href: "#", onclick: (ev) => {
        ev.preventDefault();
        e.scrollIntoView({ behavior: "smooth", block: "start" });
      } }, e.textContent)));
    const toc = h("nav", { class: "toc", "aria-label": "목차" },
      h("div", { class: "toc-title", onclick: () => toc.classList.toggle("open") }, "목차"), body);
    return toc;
  }

  function highlight(root, q) {
    if (!q) return;
    const needle = q.toLowerCase();
    const target = [...root.querySelectorAll("p, li, td, th, h2, h3, pre")].find((e) => e.textContent.toLowerCase().includes(needle));
    if (target) {
      target.classList.add("hit");
      setTimeout(() => target.scrollIntoView({ block: "center" }), 50);
    }
  }

  async function viewMarkdown({ path, title, crumb, footer, query }) {
    const md = stripFrontmatter(await fetchCached(path, "text"));
    const doc = h("article", { class: "doc", html: marked.parse(md, { gfm: true }) });
    const heads = enhanceDoc(doc);
    render(
      crumb && h("div", { class: "breadcrumb" }, crumb),
      h("div", { class: "layout" }, heads.length > 2 ? buildToc(heads) : h("div"), h("div", {}, doc, footer)));
    highlight(doc, query);
    document.title = `${title} · 자격증 스터디`;
  }

  async function viewNote(certId, idx, params) {
    const index = await getIndex();
    const cert = index.certs.find((c) => c.id === certId);
    const subject = cert && cert.subjects[Number(idx)];
    if (!subject) return viewNotFound();
    const store = loadStore();
    const prev = cert.subjects[Number(idx) - 1];
    const next = cert.subjects[Number(idx) + 1];

    const readBtn = h("button", { class: "btn", type: "button", onclick: () => {
      store.read[subject.file] = !store.read[subject.file];
      if (!store.read[subject.file]) delete store.read[subject.file];
      saveStore();
      readBtn.textContent = store.read[subject.file] ? "✅ 읽음 (취소)" : "읽음으로 표시";
    } }, store.read[subject.file] ? "✅ 읽음 (취소)" : "읽음으로 표시");

    const footer = h("div", { class: "btn-row" },
      readBtn,
      h("a", { class: "btn primary", href: `#/quiz/${certId}/${idx}` }, "이 과목 퀴즈 풀기"),
      prev && h("a", { class: "btn", href: `#/note/${certId}/${Number(idx) - 1}` }, "← " + prev.title),
      next && h("a", { class: "btn", href: `#/note/${certId}/${Number(idx) + 1}` }, next.title + " →"));

    await viewMarkdown({
      path: "content/" + subject.file, title: subject.title,
      crumb: h("span", {}, h("a", { href: "#/" }, "홈"), ` › ${cert.title} › ${subject.title}`),
      footer, query: params.get("q"),
    });
  }

  async function viewDoc(name) {
    const titles = { "exam-info": "시험 개요·검증 상태", sources: "참고 출처" };
    if (!titles[name]) return viewNotFound();
    await viewMarkdown({
      path: `docs/${name}.md`, title: titles[name],
      crumb: h("span", {}, h("a", { href: "#/" }, "홈"), ` › ${titles[name]}`),
      footer: h("div", { class: "btn-row" }, h("a", { class: "btn", href: "#/" }, "← 홈")),
    });
  }

  /* ---------- 퀴즈 ---------- */
  let quiz = null;

  async function startQuiz(certId, mode, params) {
    const index = await getIndex();
    const cert = index.certs.find((c) => c.id === certId);
    if (!cert) return viewNotFound();
    const store = loadStore();
    let title, questions, scoreKey = null;

    if (/^\d+$/.test(mode)) {
      const subject = cert.subjects[Number(mode)];
      if (!subject) return viewNotFound();
      const data = await getQuestions(subject);
      title = `${cert.title} · ${subject.title}`;
      questions = data.questions.map((q) => ({ ...q, _file: subject.questions }));
      scoreKey = subject.questions;
    } else {
      const all = (await Promise.all(cert.subjects.map(async (s) =>
        (await getQuestions(s)).questions.map((q) => ({ ...q, _file: s.questions, _subject: s.title }))))).flat();
      if (mode === "mock") {
        title = `${cert.title} · 모의고사`;
        questions = shuffle(all).slice(0, MOCK_SIZE);
        scoreKey = `mock:${certId}`;
      } else if (mode === "wrong") {
        title = `${cert.title} · 오답노트`;
        questions = all.filter((q) => store.wrong[q.id]);
        if (!questions.length) {
          return render(h("h1", {}, title), h("p", {}, "오답노트가 비어 있습니다. 🎉"),
            h("a", { class: "btn", href: "#/" }, "← 홈"));
        }
      } else return viewNotFound();
    }
    quiz = {
      certId, title, scoreKey, cur: 0, answers: [], done: false,
      questions: params.get("order") === "seq" ? questions : shuffle(questions),
    };
    viewQuiz();
  }

  function recordAnswer(q, chosen) {
    const store = loadStore();
    if (chosen === q.a) {
      delete store.wrong[q.id];
    } else {
      store.wrong[q.id] = { cert: quiz.certId, file: q._file };
    }
    saveStore();
  }

  function viewQuiz() {
    if (!quiz) return location.hash = "#/";
    if (quiz.done) return viewResult();
    const q = quiz.questions[quiz.cur];
    const answered = quiz.answers[quiz.cur] !== undefined;
    const chosen = quiz.answers[quiz.cur];
    const last = quiz.cur === quiz.questions.length - 1;

    const choiceBtns = q.c.map((text, i) => {
      const cls = answered ? (i === q.a ? "correct" : i === chosen ? "wrong" : "") : "";
      return h("button", { class: `choice ${cls}`, type: "button", disabled: answered, onclick: () => choose(i) },
        h("span", { class: "no" }, String(i + 1)), h("span", {}, text));
    });

    const explain = answered && h("div", { class: "explain", role: "status" },
      h("strong", { class: chosen === q.a ? "ok" : "bad" }, chosen === q.a ? "정답! " : `오답 — 정답은 ${q.a + 1}번. `),
      q.e);

    render(
      h("div", { class: "quiz-head" },
        h("span", {}, quiz.title),
        h("span", {}, `${quiz.cur + 1} / ${quiz.questions.length}`)),
      h("div", { class: "progress" }, h("span", { style: `width:${((quiz.cur + (answered ? 1 : 0)) / quiz.questions.length) * 100}%` })),
      h("div", { class: "q-card" },
        h("div", { class: "q-topic" }, [q._subject, q.topic].filter(Boolean).join(" · ")),
        h("div", { class: "q-text" }, q.q),
        choiceBtns, explain),
      h("div", { class: "btn-row" },
        h("button", { class: "btn primary", type: "button", disabled: !answered, onclick: next }, last ? "결과 보기" : "다음 문제 (Enter)"),
        h("a", { class: "btn", href: "#/" }, "그만하기")));
  }

  function choose(i) {
    if (!quiz || quiz.answers[quiz.cur] !== undefined) return;
    quiz.answers[quiz.cur] = i;
    recordAnswer(quiz.questions[quiz.cur], i);
    viewQuiz();
  }
  function next() {
    if (quiz.answers[quiz.cur] === undefined) return;
    if (quiz.cur === quiz.questions.length - 1) quiz.done = true; else quiz.cur++;
    viewQuiz();
  }

  function viewResult() {
    const total = quiz.questions.length;
    const correct = quiz.questions.filter((q, i) => quiz.answers[i] === q.a).length;
    const pct = Math.round((correct / total) * 100);
    if (quiz.scoreKey) {
      const store = loadStore();
      const prev = store.scores[quiz.scoreKey] || { best: 0, runs: 0 };
      store.scores[quiz.scoreKey] = { best: Math.max(prev.best, pct), last: pct, runs: prev.runs + 1 };
      saveStore();
    }
    const wrongs = quiz.questions.map((q, i) => ({ q, i })).filter(({ q, i }) => quiz.answers[i] !== q.a);
    render(
      h("h1", {}, "결과"),
      h("div", { class: "muted" }, quiz.title),
      h("div", { class: "score" }, `${pct}점`),
      h("p", {}, `${total}문제 중 ${correct}문제 정답 · 합격 기준(60점) ${pct >= 60 ? "✅ 충족" : "❌ 미달"}`),
      h("div", { class: "btn-row" },
        h("a", { class: "btn primary", href: "#/" }, "홈으로"),
        h("a", { class: "btn", href: `#/quiz/${quiz.certId}/wrong` }, "오답노트 풀기")),
      wrongs.length > 0 && h("h2", {}, `틀린 문제 (${wrongs.length})`),
      wrongs.map(({ q, i }) => h("div", { class: "review-item" },
        h("div", { class: "q-text" }, q.q),
        h("div", {}, `내 답: ${q.c[quiz.answers[i]]}`),
        h("div", {}, h("strong", { class: "ok" }, `정답: ${q.c[q.a]}`)),
        h("div", { class: "muted" }, q.e))));
  }

  document.addEventListener("keydown", (e) => {
    if (!quiz || quiz.done || !location.hash.startsWith("#/quiz/")) return;
    if (e.target.tagName === "INPUT") return;
    if (/^[1-4]$/.test(e.key)) choose(Number(e.key) - 1);
    else if (e.key === "Enter") next();
  });

  /* ---------- 검색 ---------- */
  async function viewSearch(q) {
    const query = (q || "").trim();
    if (!query) return viewHome();
    const index = await getIndex();
    const needle = query.toLowerCase();
    const results = [];
    await Promise.all(index.certs.map((cert) => Promise.all(cert.subjects.map(async (s, i) => {
      const lines = stripFrontmatter(await fetchCached("content/" + s.file, "text")).split("\n");
      const hits = lines.map((l, n) => ({ l, n })).filter(({ l }) => l.toLowerCase().includes(needle));
      if (hits.length) results.push({ cert, s, i, hits });
    }))));
    results.sort((a, b) => b.hits.length - a.hits.length);

    const mark = (line) => {
      const t = line.replace(/[|#*`>]/g, " ").replace(/\s+/g, " ").trim();
      const at = t.toLowerCase().indexOf(needle);
      const start = Math.max(0, at - 30);
      const frag = document.createDocumentFragment();
      frag.append(start ? "…" : "", t.slice(start, at));
      frag.append(h("mark", {}, t.slice(at, at + needle.length)));
      frag.append(t.slice(at + needle.length, at + needle.length + 70));
      return frag;
    };

    render(
      h("h1", {}, `"${query}" 검색 결과`),
      results.length === 0 && h("p", { class: "muted" }, "일치하는 노트가 없습니다."),
      results.map(({ cert, s, i, hits }) => h("div", { class: "result" },
        h("a", { class: "title", href: `#/note/${cert.id}/${i}?q=${encodeURIComponent(query)}` }, `${cert.title} › ${s.title}`),
        h("span", { class: "muted" }, ` (${hits.length}건)`),
        hits.slice(0, 3).map(({ l }) => h("div", { class: "line" }, mark(l))))));
  }

  function viewNotFound() {
    render(h("h1", {}, "페이지를 찾을 수 없습니다"), h("a", { class: "btn", href: "#/" }, "← 홈"));
  }

  /* ---------- 라우터 ---------- */
  async function route() {
    const { parts, params } = parseHash();
    const [page, a, b] = parts;
    document.title = "자격증 스터디 - 네트워크관리사 · 리눅스마스터";
    try {
      if (!page) { quiz = null; return await viewHome(); }
      if (page === "note") { quiz = null; return await viewNote(a, b, params); }
      if (page === "doc") { quiz = null; return await viewDoc(a); }
      if (page === "search") { quiz = null; return await viewSearch(params.get("q")); }
      if (page === "quiz") return await startQuiz(a, b, params);
      return viewNotFound();
    } catch (err) {
      render(h("h1", {}, "오류"), h("p", {}, String(err.message || err)),
        h("p", { class: "muted" }, "파일을 직접 열면(file://) 데이터를 읽지 못합니다. 로컬 서버 또는 GitHub Pages 로 열어주세요."));
    }
  }
  window.addEventListener("hashchange", route);

  /* ---------- 검색창 · 테마 ---------- */
  document.getElementById("search-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const q = document.getElementById("search-input").value.trim();
    location.hash = q ? `#/search?q=${encodeURIComponent(q)}` : "#/";
  });
  document.getElementById("theme-toggle").addEventListener("click", () => {
    const root = document.documentElement;
    const dark = root.dataset.theme
      ? root.dataset.theme === "dark"
      : matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("cert-study-theme", root.dataset.theme); } catch (e) { /* 무시 */ }
  });
  try {
    const t = localStorage.getItem("cert-study-theme");
    if (t) document.documentElement.dataset.theme = t;
  } catch (e) { /* 무시 */ }

  route();
})();
