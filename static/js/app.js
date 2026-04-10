// ── State ────────────────────────────────────────────────────────────────────
let currentPage = 1;
let totalResults = 0;
let selectedCamperIds = new Set();
let filterState = {};
let viewMode = "grid"; // "grid" or "list"

// ── DOM Elements ──────────────────────────────────────────────────────────────
const grid = document.getElementById("camperGrid");
const pagination = document.getElementById("pagination");
const loading = document.getElementById("loading");
const empty = document.getElementById("empty");
const stats = document.getElementById("stats");
const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");

// ── Sidebar Toggle ───────────────────────────────────────────────────────────
document.getElementById("filterToggle")?.addEventListener("click", () => {
  sidebar.classList.add("open");
  sidebar.classList.remove("desktop-closed");
  sidebarOverlay.classList.add("active");
});

document.getElementById("filterClose")?.addEventListener("click", closeSidebar);
sidebarOverlay?.addEventListener("click", closeSidebar);

function closeSidebar() {
  sidebar.classList.remove("open");
  sidebar.classList.add("desktop-closed");
  sidebarOverlay.classList.remove("active");
}

// ── Initialize ───────────────────────────────────────────────────────────────
async function init() {
  await loadStats();
  await loadFilterOptions();
  await loadCampers();
  setupFilterListeners();
}

// ── Load Stats ───────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();
    stats.innerHTML = `
      <span>🚐 <strong>${data.total || 0}</strong> campers</span>
      <span>⭐ <strong>${data.favorites || 0}</strong> favorieten</span>
      ${data.avg_price ? `<span>💰 gem. €${data.avg_price.toLocaleString("nl-NL")}</span>` : ""}
    `;
  } catch (err) {
    console.error("Stats error:", err);
  }
}

// ── Load Filter Options ──────────────────────────────────────────────────────
async function loadFilterOptions() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    const merkSelect = document.getElementById("filterMerk");
    if (merkSelect && data.merken) {
      data.merken.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m;
        opt.textContent = m;
        merkSelect.appendChild(opt);
      });
    }

    const brandstofSelect = document.getElementById("filterBrandstof");
    if (brandstofSelect && data.brandstoffen) {
      data.brandstoffen.forEach(b => {
        const opt = document.createElement("option");
        opt.value = b;
        opt.textContent = b;
        brandstofSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.error("Filter options error:", err);
  }
}

// ── Load Campers ─────────────────────────────────────────────────────────────
async function loadCampers() {
  loading.style.display = "flex";
  grid.innerHTML = "";
  empty.style.display = "none";

  try {
    const params = new URLSearchParams({
      page: currentPage,
      ...buildQueryParams(),
    });

    const res = await fetch(`/api/campers?${params}`);
    const data = await res.json();

    loading.style.display = "none";
    totalResults = data.total;

    // Update results bar
    const resultsBar = document.getElementById("resultsBar");
    if (resultsBar) {
      resultsBar.innerHTML = `<strong>${data.total}</strong> camper${data.total !== 1 ? 's' : ''} gevonden`;
    }

    if (data.campers.length === 0) {
      empty.style.display = "block";
      return;
    }

    renderCampers(data.campers);
    renderPagination(data);
  } catch (err) {
    console.error("Load campers error:", err);
    loading.style.display = "none";
    empty.style.display = "block";
  }
}

// ── Build Query Params from Filters ─────────────────────────────────────────
function buildQueryParams() {
  const params = {};
  const ids = {
    q: "filterQ",
    min_price: "filterMinPrice",
    max_price: "filterMaxPrice",
    merk: "filterMerk",
    min_bouwjaar: "filterMinYear",
    max_bouwjaar: "filterMaxYear",
    min_km: "filterMinKm",
    max_km: "filterMaxKm",
    min_slaapplaatsen: "filterMinSlaap",
    min_zitplaatsen: "filterMinZit",
    brandstof: "filterBrandstof",
    transmissie: "filterTransmissie",
    airco: "filterAirco",
    gps: "filterGps",
    parkeersensoren: "filterParkeer",
    keuken: "filterKeuken",
    koelkast: "filterKoelkast",
    douche: "filterDouche",
    toilet: "filterToilet",
    apk_geldig: "filterApk",
    service_historie: "filterService",
    favorites: "filterFavorites",
    sort: "filterSort",
  };

  for (const [param, id] of Object.entries(ids)) {
    const el = document.getElementById(id);
    if (!el) continue;

    if (el.type === "checkbox") {
      if (el.checked) params[param] = "1";
    } else {
      const val = el.value.trim();
      if (val) params[param] = val;
    }
  }

  return params;
}

// ── Count active filters ────────────────────────────────────────────────────
function countActiveFilters() {
  const params = buildQueryParams();
  let count = 0;
  for (const [key, val] of Object.entries(params)) {
    if (key === "sort") continue;
    if (val && val !== "0") count++;
  }
  return count;
}

// ── Render Campers ───────────────────────────────────────────────────────────
function renderCampers(campers) {
  grid.className = `grid ${viewMode === "list" ? "list-view" : ""}`;

  campers.forEach(c => {
    const card = document.createElement("div");
    card.className = `card${selectedCamperIds.has(c.id) ? " selected" : ""}`;
    card.dataset.id = c.id;

    const images = Array.isArray(c.image_urls) ? c.image_urls : [];
    const firstImage = images.length > 0 ? images[0] : null;
    const pd = c.parsed_data || {};
    const basis = pd.basis || {};
    const tech = pd.technisch || {};
    const cap = pd.capaciteit || {};
    const camperFeatures = pd.camper || {};
    const onderhoud = pd.onderhoud || {};

    // Build tags
    const tags = [];
    if (tech.transmissie) {
      tags.push(`<span class="tag">${escapeHtml(tech.transmissie)}</span>`);
    }
    if (tech.vermogen_PK) {
      tags.push(`<span class="tag">${tech.vermogen_PK} PK</span>`);
    }
    if (cap.slaapplaatsen) {
      tags.push(`<span class="tag">🛏️ ${cap.slaapplaatsen}</span>`);
    }
    if (camperFeatures.douche) {
      tags.push(`<span class="tag tag-success">🚿</span>`);
    }
    if (camperFeatures.toilet) {
      tags.push(`<span class="tag tag-success">🚽</span>`);
    }
    if (onderhoud.APK_geldig === false) {
      tags.push(`<span class="tag tag-danger">APK verlopen</span>`);
    }

    card.innerHTML = `
      <div class="card-favorite${c.is_favorite ? " active" : ""}" data-action="favorite">
        ${c.is_favorite ? "⭐" : "☆"}
      </div>
      <div class="card-image" data-action="detail">
        ${firstImage
          ? `<img src="${escapeHtml(firstImage)}" alt="${escapeHtml(c.title || "")}" loading="lazy">`
          : `<div class="placeholder">🚐</div>`
        }
        ${images.length > 1 ? `<span class="card-image-count">📷 ${images.length}</span>` : ""}
      </div>
      <div class="card-content" data-action="detail">
        <div class="card-title">${escapeHtml(c.title || "Geen titel")}</div>
        <div class="card-price">€${(c.price_euros || 0).toLocaleString("nl-NL")}</div>
        <div class="card-meta">
          ${c.location ? `<span>📍 ${escapeHtml(c.location)}</span>` : ""}
          ${basis.bouwjaar ? `<span>📅 ${basis.bouwjaar}</span>` : ""}
          ${basis.kilometerstand ? `<span>🛣️ ${(basis.kilometerstand / 1000).toFixed(0)}k km</span>` : ""}
        </div>
        ${tags.length > 0 ? `<div class="card-tags">${tags.join("")}</div>` : ""}
      </div>
    `;

    // Card click → detail page
    card.querySelectorAll('[data-action="detail"]').forEach(el => {
      el.addEventListener("click", () => {
        window.location.href = `/camper/${c.id}`;
      });
    });

    // Favorite toggle
    card.querySelector('[data-action="favorite"]')?.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleFavorite(c.id, card.querySelector('[data-action="favorite"]'));
    });

    grid.appendChild(card);
  });
}

// ── Render Pagination ────────────────────────────────────────────────────────
function renderPagination(data) {
  pagination.innerHTML = "";

  if (data.pages <= 1) return;

  const prev = document.createElement("button");
  prev.className = "btn btn-sm";
  prev.textContent = "← Vorige";
  prev.disabled = data.page <= 1;
  prev.addEventListener("click", () => {
    currentPage = Math.max(1, data.page - 1);
    loadCampers();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  pagination.appendChild(prev);

  // Page numbers
  const pages = [];
  for (let i = 1; i <= data.pages; i++) {
    if (i === 1 || i === data.pages || (i >= data.page - 1 && i <= data.page + 1)) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== "...") {
      pages.push("...");
    }
  }

  pages.forEach(p => {
    if (p === "...") {
      const span = document.createElement("span");
      span.textContent = "···";
      span.style.padding = "0 0.25rem";
      span.style.color = "var(--text-light)";
      pagination.appendChild(span);
    } else {
      const btn = document.createElement("button");
      btn.className = `btn btn-sm${p === data.page ? " active" : ""}`;
      btn.textContent = p;
      btn.addEventListener("click", () => {
        currentPage = p;
        loadCampers();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
      pagination.appendChild(btn);
    }
  });

  const next = document.createElement("button");
  next.className = "btn btn-sm";
  next.textContent = "Volgende →";
  next.disabled = data.page >= data.pages;
  next.addEventListener("click", () => {
    currentPage = Math.min(data.pages, data.page + 1);
    loadCampers();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  pagination.appendChild(next);
}

// ── Toggle Favorite ─────────────────────────────────────────────────────────
async function toggleFavorite(camperId, btn) {
  const isFav = btn.classList.contains("active");
  const method = isFav ? "DELETE" : "POST";

  try {
    await fetch(`/api/campers/${camperId}/favorite`, { method });
    btn.textContent = isFav ? "☆" : "⭐";
    btn.classList.toggle("active", !isFav);
    loadStats();
  } catch (err) {
    console.error("Favorite error:", err);
  }
}

// ── Filter Listeners ────────────────────────────────────────────────────────
function setupFilterListeners() {
  // Apply filters button
  document.getElementById("applyFilters")?.addEventListener("click", () => {
    closeSidebar();
    currentPage = 1;
    loadCampers();
  });

  // Reset filters button
  document.getElementById("resetFilters")?.addEventListener("click", () => {
    document.querySelectorAll("#sidebar input, #sidebar select").forEach(el => {
      if (el.type === "checkbox") el.checked = false;
      else if (el.tagName === "SELECT") el.selectedIndex = 0;
      else el.value = "";
    });
    closeSidebar();
    currentPage = 1;
    loadCampers();
  });

  // Enter key in search field
  document.getElementById("filterQ")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      closeSidebar();
      currentPage = 1;
      loadCampers();
    }
  });

  // Compare button
  document.getElementById("compareBtn")?.addEventListener("click", () => {
    if (selectedCamperIds.size >= 2) {
      const ids = Array.from(selectedCamperIds).join(",");
      window.location.href = `/compare?ids=${ids}`;
    }
  });

  // Export CSV button
  document.getElementById("exportCsv")?.addEventListener("click", () => {
    const params = new URLSearchParams(buildQueryParams());
    window.open(`/api/export/csv?${params}`, "_blank");
  });
}

// ── Utility ─────────────────────────────────────────────────────────────────
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ── Start ───────────────────────────────────────────────────────────────────
init();
