/**
 * Column resize for all data tables.
 * - Adds a drag handle to every <th> (except the last column).
 * - Persists widths per-page in localStorage.
 * - Shows a reset button (bottom-right) per page.
 * Auto-attaches to any <table> that has class ending in "-table".
 */
(function () {
  "use strict";
  const STORAGE_PREFIX = "colw:" + location.pathname + ":";
  const MIN_W = 40;
  const HANDLE_W = 6;

  function getTables() {
    return document.querySelectorAll(
      'table[class$="-table"], table[class*="-table "]'
    );
  }

  function tableId(tbl, idx) {
    const cls = Array.from(tbl.classList).find(c => c.endsWith("-table")) || "tbl";
    return cls + ":" + idx;
  }

  function applySaved(table, key) {
    const saved = localStorage.getItem(STORAGE_PREFIX + key);
    if (!saved) return;
    try {
      const widths = JSON.parse(saved);
      const ths = table.querySelectorAll("thead th");
      ths.forEach((th, i) => {
        if (widths[i]) {
          th.style.width = widths[i];
          th.style.minWidth = widths[i];
        }
      });
    } catch (e) {}
  }

  function saveWidths(table, key) {
    const ths = table.querySelectorAll("thead th");
    const widths = Array.from(ths).map(th => th.style.width || "");
    localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(widths));
  }

  function attach(table, key) {
    if (table.dataset.colResize === "1") return;
    // Skip nested sub-grid — its layout is controlled by CSS (table-layout: fixed).
    if (table.classList.contains("rp-sub-table")) return;
    table.dataset.colResize = "1";
    table.style.tableLayout = "auto";

    applySaved(table, key);

    const ths = table.querySelectorAll("thead th");
    ths.forEach((th, i) => {
      if (i === ths.length - 1) return; // no handle on last column
      if (th.querySelector(".col-resize-handle")) return;

      th.style.position = "relative";

      const handle = document.createElement("div");
      handle.className = "col-resize-handle";
      Object.assign(handle.style, {
        position: "absolute",
        top: "0",
        right: "-3px",
        width: HANDLE_W + "px",
        height: "100%",
        cursor: "col-resize",
        userSelect: "none",
        zIndex: "3",
      });
      th.appendChild(handle);

      let startX, startW;
      const onDown = (e) => {
        e.preventDefault();
        e.stopPropagation();
        startX = e.clientX;
        startW = th.offsetWidth;
        document.body.style.cursor = "col-resize";
        document.body.style.userSelect = "none";
        document.addEventListener("mousemove", onMove);
        document.addEventListener("mouseup", onUp);
      };
      const onMove = (e) => {
        const delta = e.clientX - startX;
        const newW = Math.max(MIN_W, startW + delta);
        th.style.width = newW + "px";
        th.style.minWidth = newW + "px";
      };
      const onUp = () => {
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
        saveWidths(table, key);
      };
      handle.addEventListener("mousedown", onDown);
    });
  }

  function init() {
    const tables = getTables();
    tables.forEach((tbl, idx) => {
      attach(tbl, tableId(tbl, idx));
    });
    ensureResetButton();
  }

  function ensureResetButton() {
    if (document.getElementById("col-resize-reset")) return;
    const btn = document.createElement("button");
    btn.id = "col-resize-reset";
    btn.textContent = "Reset Columns";
    Object.assign(btn.style, {
      position: "fixed",
      bottom: "12px",
      right: "12px",
      zIndex: "9999",
      padding: "6px 12px",
      fontSize: "0.75rem",
      fontWeight: "700",
      background: "#212529",
      color: "#fff",
      border: "1px solid #212529",
      borderRadius: "4px",
      cursor: "pointer",
      opacity: "0.5",
      transition: "opacity 0.15s",
    });
    btn.addEventListener("mouseenter", () => btn.style.opacity = "1");
    btn.addEventListener("mouseleave", () => btn.style.opacity = "0.5");
    btn.addEventListener("click", () => {
      Object.keys(localStorage)
        .filter(k => k.startsWith(STORAGE_PREFIX))
        .forEach(k => localStorage.removeItem(k));
      location.reload();
    });
    document.body.appendChild(btn);
  }

  // Re-apply on dynamically added tables
  let lastCount = -1;
  setInterval(() => {
    const count = getTables().length;
    if (count !== lastCount) {
      lastCount = count;
      init();
    }
  }, 500);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();