/* DSA Practice Tracker — static dashboard JS */
(function () {
  "use strict";

  const DATA_URL = "data/stats.json";
  let ALL_PROBLEMS = [];

  // ── Helpers ────────────────────────────────────────────────────────────
  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(text) {
    // Build entities via concatenation so auto-formatters don't decode them.
    var AMP = "&" + "amp;";
    var LT = "&" + "lt;";
    var GT = "&" + "gt;";
    var QUOT = "&" + "quot;";
    var APOS = "&" + "#39;";
    return String(text)
      .replace(/&/g, AMP)
      .replace(/</g, LT)
      .replace(/>/g, GT)
      .replace(/"/g, QUOT)
      .replace(/'/g, APOS);
  }

  function barMarkup(label, value, total) {
    const pct = total > 0 ? Math.round((value / total) * 100) : 0;
    return (
      '<div class="bar-item">' +
      '<span class="bar-label" title="' + escapeHtml(label) + '">' + escapeHtml(label) + "</span>" +
      '<div class="bar-track"><div class="bar-fill" style="width:' + pct + '%"></div></div>' +
      '<span class="bar-value">' + value + " (" + pct + "%)</span>" +
      "</div>"
    );
  }

  function badge(text, type) {
    return '<span class="badge ' + type + '">' + escapeHtml(text) + "</span>";
  }

  function problemLink(p) {
    const path = (p.path || "").replace(/^problems\//, "");
    const href = "https://github.com/suren1013/DSA/tree/main/problems/" + encodeURIComponent(path);
    const label = p.title || p.slug || path;
    return '<a href="' + href + '" target="_blank" rel="noopener">' + escapeHtml(label) + "</a>";
  }

  // ── Hero ───────────────────────────────────────────────────────────────
  function renderHero(summary, streak) {
    const rate = Math.round(summary.solve_rate * 100) + "%";
    const last = streak.last_active || "—";
    const streakText = streak.current_streak + " day" + (streak.current_streak === 1 ? "" : "s");

    $("stat-total").textContent = summary.total;
    $("stat-solved").textContent = summary.solved;
    $("stat-rate").textContent = rate;
    $("stat-streak").textContent = streakText;
    $("stat-active").textContent = streak.total_active_days;
    $("stat-last").textContent = last;
  }

  // ── Charts ─────────────────────────────────────────────────────────────
  function renderBarChart(elId, data, total) {
    const el = $(elId);
    const entries = Object.entries(data);
    if (!entries.length) {
      el.innerHTML = '<p class="empty">No data</p>';
      return;
    }
    el.innerHTML = entries
      .map(([label, value]) => barMarkup(label, value, total))
      .join("");
  }

  function renderCharts(stats) {
    renderBarChart("chart-difficulty", stats.by_difficulty, stats.summary.total);
    renderBarChart("chart-topics", topicTotals(stats.by_topic), stats.summary.total);
    renderBarChart("chart-sources", stats.by_source, stats.summary.total);
    renderBarChart("chart-languages", stats.by_language, stats.summary.total);
  }

  function topicTotals(byTopic) {
    const out = {};
    Object.keys(byTopic).forEach(function (topic) {
      out[topic] = byTopic[topic].total;
    });
    return out;
  }

  // ── Search / filter table ──────────────────────────────────────────────
  function matches(p, query) {
    if (!query) return true;
    const q = query.toLowerCase();
    const haystack = [
      p.title,
      p.slug,
      p.topic,
      p.platform,
      p.status,
      p.difficulty,
      (p.tags || []).join(" "),
    ]
      .join(" ")
      .toLowerCase();
    return haystack.indexOf(q) !== -1;
  }

  function renderTable() {
    const query = $("search-input").value.trim();
    const diff = $("filter-difficulty").value;
    const status = $("filter-status").value;

    const filtered = ALL_PROBLEMS.filter(function (p) {
      if (!matches(p, query)) return false;
      if (diff && p.difficulty !== diff) return false;
      if (status && p.status !== status) return false;
      return true;
    });

    $("result-count").textContent =
      filtered.length + " of " + ALL_PROBLEMS.length + " problems";

    const tbody = $("problems-body");
    if (!filtered.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="empty">No problems match your filters.</td></tr>';
      return;
    }

    tbody.innerHTML = filtered
      .map(function (p) {
        const diffBadge = p.difficulty
          ? badge(p.difficulty, "difficulty-" + p.difficulty)
          : "—";
        const statusBadge = p.status
          ? badge(p.status.replace("-", " "), "status-" + p.status)
          : "—";
        const tags = (p.tags || []).map(function (t) {
          return '<span class="tag">' + escapeHtml(t) + "</span>";
        }).join("");
        return (
          "<tr>" +
          "<td>" + problemLink(p) + "</td>" +
          "<td>" + escapeHtml(p.topic) + "</td>" +
          "<td>" + diffBadge + "</td>" +
          "<td>" + statusBadge + "</td>" +
          "<td>" + escapeHtml(p.platform || "—") + "</td>" +
          "<td>" + (tags || "—") + "</td>" +
          "<td>" + escapeHtml(p.solved_date || "—") + "</td>" +
          "</tr>"
        );
      })
      .join("");
  }

  // ── Init ───────────────────────────────────────────────────────────────
  function init() {
    ["search-input", "filter-difficulty", "filter-status"].forEach(function (id) {
      $(id).addEventListener("input", renderTable);
      $(id).addEventListener("change", renderTable);
    });

    fetch(DATA_URL)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (stats) {
        ALL_PROBLEMS = stats.problems || [];
        renderHero(stats.summary, stats.streak);
        renderCharts(stats);
        renderTable();
      })
      .catch(function (err) {
        console.error("Failed to load " + DATA_URL, err);
        $("problems-body").innerHTML =
          '<tr><td colspan="7" class="empty">Failed to load data. Run scripts/build_site.py.</td></tr>';
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();