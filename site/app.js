(() => {
  const DATA = window.MYGO;
  if (!DATA) return;

  const $ = (sel) => document.querySelector(sel);
  const grid = $("#grid");
  const chipsEl = $("#chips");
  const countEl = $("#count");
  const noteEl = $("#section-note");
  const emptyEl = $("#empty");
  const emptyText = $("#empty-text");
  const input = $("#q");
  const clearBtn = $("#clear");
  const sortEl = $("#sort");

  const SHORT = {
    author: "Author",
    ai: "AI & agents",
    dev: "Dev tools",
    writing: "Writing",
    media: "Media",
    productivity: "Productivity",
    system: "System",
    files: "Files",
    network: "Network",
    games: "Games",
    ui: "UI kits",
    more: "More",
  };

  const COLORS = {
    author: "#f472b6",
    ai: "#a78bfa",
    dev: "#60a5fa",
    writing: "#34d399",
    media: "#fbbf24",
    productivity: "#22d3ee",
    system: "#fb7185",
    files: "#a3e635",
    network: "#38bdf8",
    games: "#f59e0b",
    ui: "#c084fc",
    more: "#94a3b8",
  };

  const state = { q: "", cat: "all", sort: "stars" };
  const cats = new Map(DATA.categories.map((c) => [c.id, c]));
  let firstPaint = true;

  /* ---------- helpers ---------- */
  const esc = (s) =>
    String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const fmtStars = (n) => {
    if (n >= 1000) return (n / 1000).toFixed(1).replace(".0", "") + "k";
    return String(n);
  };

  const fmtDate = (iso) => {
    if (!iso) return "";
    const then = new Date(iso + "T00:00:00Z").getTime();
    if (Number.isNaN(then)) return "";
    const days = Math.max(0, Math.floor((Date.now() - then) / 86400000));
    if (days === 0) return "today";
    if (days === 1) return "yesterday";
    if (days < 30) return days + "d ago";
    if (days < 365) return Math.round(days / 30) + "mo ago";
    return Math.round(days / 365) + "y ago";
  };

  /* ---------- chips ---------- */
  const makeChip = (id, label, count) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.setAttribute("role", "tab");
    b.dataset.cat = id;
    b.setAttribute("aria-selected", String(state.cat === id));
    b.innerHTML = `${esc(label)} <b>${count}</b>`;
    b.addEventListener("click", () => {
      state.cat = id;
      syncChips();
      render();
      writeUrl();
    });
    return b;
  };

  const syncChips = () => {
    chipsEl.querySelectorAll(".chip").forEach((c) => {
      c.setAttribute("aria-selected", String(c.dataset.cat === state.cat));
    });
  };

  const buildChips = () => {
    chipsEl.append(makeChip("all", "All", DATA.count));
    DATA.categories
      .filter((c) => c.count > 0)
      .forEach((c) => chipsEl.append(makeChip(c.id, SHORT[c.id] || c.title, c.count)));
  };

  /* ---------- filtering ---------- */
  const matches = (r, tokens) => {
    if (state.cat !== "all" && r.category !== state.cat) return false;
    if (!tokens.length) return true;
    const hay = (r.name + " " + r.description + " " + (r.topics || []).join(" ") + " " + (SHORT[r.category] || "")).toLowerCase();
    return tokens.every((t) => hay.includes(t));
  };

  const sortList = (list) => {
    const byName = (a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase());
    if (state.sort === "name") return list.sort(byName);
    if (state.sort === "updated") return list.sort((a, b) => (b.pushed || "").localeCompare(a.pushed || "") || byName(a, b));
    return list.sort((a, b) => b.stars - a.stars || byName(a, b));
  };

  /* ---------- card ---------- */
  const card = (r) => {
    const [owner, repo] = r.name.split("/");
    const cat = cats.get(r.category);
    const tag = SHORT[r.category] || cat.title;
    const meta = [];
    if (r.license) meta.push(`<span class="lic">${esc(r.license)}</span>`);
    if (r.pushed) meta.push(`<span class="upd">${esc(fmtDate(r.pushed))}</span>`);
    if (r.homepage) meta.push(`<a class="site-link" href="${esc(r.homepage)}" target="_blank" rel="noopener">Website ↗</a>`);

    const el = document.createElement("article");
    el.className = "card";
    el.innerHTML = `
      <div class="card-top">
        <span class="tag" style="--tag:${COLORS[r.category] || "#94a3b8"}">${esc(tag)}</span>
        ${r.stars ? `<span class="stars" title="${r.stars} stars">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="m12 2.6 2.9 5.9 6.5.9-4.7 4.6 1.1 6.5-5.8-3-5.8 3 1.1-6.5L2.6 9.4l6.5-.9L12 2.6Z"/></svg>
          ${fmtStars(r.stars)}
        </span>` : ""}
      </div>
      <h3 class="card-title"><a href="${esc(r.url)}" target="_blank" rel="noopener"><span class="owner">${esc(owner)}/</span>${esc(repo)}</a></h3>
      <p class="card-desc">${esc(r.description)}</p>
      <div class="card-meta">${meta.join("")}</div>
    `;
    return el;
  };

  /* ---------- render ---------- */
  const render = () => {
    const tokens = state.q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const list = sortList(DATA.repos.filter((r) => matches(r, tokens)));

    grid.replaceChildren();
    const frag = document.createDocumentFragment();
    list.forEach((r, i) => {
      const el = card(r);
      if (firstPaint && i < 18) el.style.animationDelay = i * 22 + "ms";
      else el.style.animation = "none";
      frag.append(el);
    });
    grid.append(frag);
    firstPaint = false;

    emptyEl.hidden = list.length > 0;
    if (!list.length) {
      const bits = [];
      if (state.q) bits.push(`“${state.q}”`);
      if (state.cat !== "all") bits.push(SHORT[state.cat] || state.cat);
      emptyText.textContent = bits.length
        ? `No results for ${bits.join(" in ")}. Try a shorter keyword, a different spelling, or reset the filters.`
        : "Try a different keyword, or reset the filters.";
    }

    const cat = cats.get(state.cat);
    if (cat) {
      noteEl.hidden = false;
      noteEl.innerHTML = `${esc(cat.blurb)} <span class="note-count">${list.length} of ${cat.count} shown</span>`;
    } else {
      noteEl.hidden = true;
    }

    countEl.innerHTML = `<b>${list.length}</b> of ${DATA.count}`;
    clearBtn.hidden = !state.q;
    document.querySelector(".search").classList.toggle("has-value", Boolean(state.q));
  };

  /* ---------- url ---------- */
  const writeUrl = () => {
    const p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    if (state.cat !== "all") p.set("cat", state.cat);
    if (state.sort !== "stars") p.set("sort", state.sort);
    const qs = p.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname + location.hash);
  };

  const readUrl = () => {
    const p = new URLSearchParams(location.search);
    const cat = p.get("cat");
    if (cat && cats.has(cat)) state.cat = cat;
    const sort = p.get("sort");
    if (["stars", "updated", "name"].includes(sort)) state.sort = sort;
    const q = p.get("q");
    if (q) {
      state.q = q;
      input.value = q;
    }
    sortEl.value = state.sort;
  };

  /* ---------- stats ---------- */
  const paintStats = () => {
    const stars = DATA.repos.reduce((n, r) => n + r.stars, 0);
    $("#hero-count").textContent = DATA.count;
    $("#hero-stars").textContent = fmtStars(stars);
    $("#stat-projects").textContent = DATA.count;
    $("#stat-stars").textContent = fmtStars(stars);
    $("#stat-cats").textContent = DATA.categories.filter((c) => c.count > 0).length;

    const lic = {};
    DATA.repos.forEach((r) => { if (r.license) lic[r.license] = (lic[r.license] || 0) + 1; });
    const top = Object.entries(lic).sort((a, b) => b[1] - a[1])[0];
    if (top) $("#stat-lic").textContent = top[0];
  };

  /* ---------- events ---------- */
  let timer;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      state.q = input.value;
      render();
      writeUrl();
    }, 90);
  });

  clearBtn.addEventListener("click", () => {
    input.value = "";
    state.q = "";
    render();
    writeUrl();
    input.focus();
  });

  sortEl.addEventListener("change", () => {
    state.sort = sortEl.value;
    render();
    writeUrl();
  });

  $("#reset").addEventListener("click", () => {
    state.q = "";
    state.cat = "all";
    input.value = "";
    syncChips();
    render();
    writeUrl();
  });

  document.querySelectorAll(".quick button").forEach((b) => {
    b.addEventListener("click", () => {
      input.value = b.dataset.q;
      state.q = b.dataset.q;
      render();
      writeUrl();
      input.focus();
    });
  });

  document.addEventListener("keydown", (e) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if (e.key === "/" && !typing) {
      e.preventDefault();
      input.focus();
      input.select();
    }
    if (e.key === "Escape" && document.activeElement === input) {
      input.value = "";
      state.q = "";
      render();
      writeUrl();
      input.blur();
    }
  });

  /* theme */
  const root = document.documentElement;
  const themeBtn = $("#theme-toggle");
  const meta = document.querySelector('meta[name="theme-color"]');
  const applyTheme = (t) => {
    root.dataset.theme = t;
    themeBtn.setAttribute("aria-label", t === "dark" ? "Switch to light theme" : "Switch to dark theme");
    meta.setAttribute("content", t === "dark" ? "#08090c" : "#f6f7fa");
    try { localStorage.setItem("mygo-theme", t); } catch (_) {}
  };
  let saved = null;
  try { saved = localStorage.getItem("mygo-theme"); } catch (_) {}
  const fromUrl = new URLSearchParams(location.search).get("theme");
  applyTheme(fromUrl === "light" || fromUrl === "dark" ? fromUrl : saved || "dark");
  themeBtn.addEventListener("click", () => {
    applyTheme(root.dataset.theme === "dark" ? "light" : "dark");
  });

  /* header shadow */
  const header = document.querySelector(".site-header");
  const onScroll = () => header.classList.toggle("is-stuck", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* repository links come from the build config */
  const repoUrl = DATA.repoUrl || "https://github.com/";
  document.querySelectorAll("#contrib-link").forEach((a) => { a.href = repoUrl + "/issues/new"; });
  document.querySelectorAll("#repo-nav, #repo-footer").forEach((a) => { a.href = repoUrl; });

  /* ---------- boot ---------- */
  readUrl();
  buildChips();
  paintStats();
  render();

  /* Deep links: the list changes the page height after the first paint, so
     re-apply the anchor once the cards are in the DOM. */
  if (location.hash) {
    const target = document.querySelector(location.hash);
    if (target) requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
  }
})();
