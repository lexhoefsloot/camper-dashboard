// ── State ────────────────────────────────────────────────────────────────────
let currentImageIndex = 0;
let images = [];

// ── Load Camper Data ─────────────────────────────────────────────────────────
async function loadCamper() {
  try {
    const res = await fetch(`/api/campers/${CAMPER_ID}`);
    if (!res.ok) throw new Error("Not found");
    const camper = await res.json();
    renderCamper(camper);
  } catch (err) {
    document.getElementById("detailTitle").textContent = "Niet gevonden";
    document.querySelector(".detail-main").innerHTML = `
      <div class="empty">
        <div class="empty-icon">🔍</div>
        <p>Camper niet gevonden.</p>
        <a href="/" class="btn btn-primary" style="margin-top:1rem;">← Terug naar overzicht</a>
      </div>
    `;
  }
}

// ── Render Camper Detail ─────────────────────────────────────────────────────
function renderCamper(c) {
  // Title
  document.title = `${c.title || "Camper"} — Camper Dashboard`;
  document.getElementById("detailTitle").textContent = c.title || "Camper";

  // Favorite button
  const favBtn = document.getElementById("favBtn");
  updateFavButton(favBtn, c.is_favorite);
  favBtn.addEventListener("click", () => toggleFavorite(c.id, favBtn));

  // Marktplaats link
  const mpLink = document.getElementById("mpLink");
  if (c.url && c.url !== "#") {
    mpLink.href = c.url;
  } else {
    mpLink.style.display = "none";
  }

  // Gallery
  renderGallery(c);

  // Price bar
  renderPriceBar(c);

  // Key specs
  renderSpecs(c);

  // Features grid
  renderFeatures(c);

  // All parsed data sections
  renderAllData(c);

  // Raw description
  renderDescription(c);
}

// ── Gallery ──────────────────────────────────────────────────────────────────
function renderGallery(c) {
  images = Array.isArray(c.image_urls) ? c.image_urls : [];
  const gallery = document.getElementById("gallery");
  const galleryMain = document.getElementById("galleryMain");
  const galleryThumbs = document.getElementById("galleryThumbs");

  if (images.length === 0) {
    gallery.innerHTML = `
      <div class="gallery-main" style="display:flex;align-items:center;justify-content:center;background:var(--bg);">
        <div style="text-align:center;color:var(--text-muted);">
          <div style="font-size:4rem;margin-bottom:0.5rem;">🚐</div>
          <p>Geen foto's beschikbaar</p>
        </div>
      </div>
    `;
    return;
  }

  // Main image with nav arrows
  galleryMain.innerHTML = `
    <img src="${escapeHtml(images[0])}" id="mainImage" alt="">
    ${images.length > 1 ? `
      <button class="gallery-nav gallery-nav-prev" onclick="prevImage()">‹</button>
      <button class="gallery-nav gallery-nav-next" onclick="nextImage()">›</button>
      <div class="gallery-counter" id="galleryCounter">1 / ${images.length}</div>
    ` : ""}
  `;

  // Thumbnails
  if (images.length > 1) {
    galleryThumbs.innerHTML = images.map((img, i) => `
      <div class="gallery-thumb${i === 0 ? " active" : ""}" data-index="${i}">
        <img src="${escapeHtml(img)}" alt="" loading="lazy">
      </div>
    `).join("");

    galleryThumbs.querySelectorAll(".gallery-thumb").forEach(thumb => {
      thumb.addEventListener("click", () => {
        setImage(parseInt(thumb.dataset.index));
      });
    });
  } else {
    galleryThumbs.style.display = "none";
  }

  // Keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") prevImage();
    if (e.key === "ArrowRight") nextImage();
  });
}

function setImage(idx) {
  if (idx < 0 || idx >= images.length) return;
  currentImageIndex = idx;

  const mainImg = document.getElementById("mainImage");
  mainImg.src = images[idx];

  const counter = document.getElementById("galleryCounter");
  if (counter) counter.textContent = `${idx + 1} / ${images.length}`;

  document.querySelectorAll(".gallery-thumb").forEach((t, i) => {
    t.classList.toggle("active", i === idx);
  });

  // Scroll active thumb into view
  const activeThumb = document.querySelector(`.gallery-thumb[data-index="${idx}"]`);
  activeThumb?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
}

function prevImage() {
  setImage(currentImageIndex <= 0 ? images.length - 1 : currentImageIndex - 1);
}

function nextImage() {
  setImage(currentImageIndex >= images.length - 1 ? 0 : currentImageIndex + 1);
}

// ── Price Bar ────────────────────────────────────────────────────────────────
function renderPriceBar(c) {
  const container = document.getElementById("priceBar");
  if (!container) return;

  container.innerHTML = `
    <div class="detail-price">€${(c.price_euros || 0).toLocaleString("nl-NL")}</div>
    <div class="detail-price-actions">
      <span style="color:var(--text-muted);font-size:0.875rem;">
        📍 ${escapeHtml(c.location || "Onbekend")}
      </span>
    </div>
  `;
}

// ── Key Specs ────────────────────────────────────────────────────────────────
function renderSpecs(c) {
  const pd = c.parsed_data || {};
  const basis = pd.basis || {};
  const tech = pd.technisch || {};
  const cap = pd.capaciteit || {};

  const specs = [
    { icon: "🏭", label: "Merk", value: basis.merk },
    { icon: "📋", label: "Model", value: basis.model },
    { icon: "📅", label: "Bouwjaar", value: basis.bouwjaar },
    { icon: "🛣️", label: "Km-stand", value: basis.kilometerstand ? `${basis.kilometerstand.toLocaleString("nl-NL")} km` : null },
    { icon: "⛽", label: "Brandstof", value: tech.brandstof },
    { icon: "⚙️", label: "Transmissie", value: tech.transmissie },
    { icon: "🐎", label: "Vermogen", value: tech.vermogen_PK ? `${tech.vermogen_PK} PK` : null },
    { icon: "📏", label: "Lengte", value: tech.lengte_cm ? `${(tech.lengte_cm / 100).toFixed(1)}m` : null },
    { icon: "🛏️", label: "Slaapplaatsen", value: cap.slaapplaatsen },
    { icon: "💺", label: "Zitplaatsen", value: cap.zitplaatsen },
  ];

  document.getElementById("detailSpecs").innerHTML = specs
    .filter(s => s.value != null)
    .map(s => `
      <div class="spec-box">
        <div class="icon">${s.icon}</div>
        <div class="label">${s.label}</div>
        <div class="value">${escapeHtml(String(s.value))}</div>
      </div>
    `).join("");
}

// ── Features Grid ────────────────────────────────────────────────────────────
function renderFeatures(c) {
  const pd = c.parsed_data || {};
  const comfort = pd.comfort || {};
  const camper = pd.camper || {};
  const onderhoud = pd.onderhoud || {};

  const features = [
    { icon: "❄️", label: "Airco", value: comfort.airco },
    { icon: "🗺️", label: "GPS/Navigatie", value: comfort.GPS },
    { icon: "📡", label: "Parkeersensoren", value: comfort.parkeersensoren },
    { icon: "🍳", label: "Keuken", value: camper.keuken },
    { icon: "🧊", label: "Koelkast", value: camper.koelkast },
    { icon: "🚿", label: "Douche", value: camper.douche },
    { icon: "🚽", label: "Toilet", value: camper.toilet },
    { icon: "✅", label: "APK geldig", value: onderhoud.APK_geldig },
    { icon: "📒", label: "Service historie", value: onderhoud.service_historie },
  ];

  const container = document.getElementById("detailFeatures");
  if (!container) return;

  container.innerHTML = `
    <h2>Voorzieningen</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:0.5rem;">
      ${features.map(f => `
        <div style="display:flex;align-items:center;gap:0.75rem;padding:0.625rem 0.75rem;border-radius:var(--radius);background:${f.value ? '#f0fdf4' : 'var(--bg)'};border:1px solid ${f.value ? '#bbf7d0' : 'var(--border-light)'};">
          <span style="font-size:1.25rem;">${f.icon}</span>
          <span style="font-size:0.875rem;${f.value ? 'color:var(--success);font-weight:500;' : 'color:var(--text-light);text-decoration:line-through;'}">${f.label}</span>
        </div>
      `).join("")}
    </div>
  `;
}

// ── All Parsed Data ─────────────────────────────────────────────────────────
function renderAllData(c) {
  const pd = c.parsed_data || {};
  const sections = [
    { title: "Basis", icon: "📋", data: pd.basis || {} },
    { title: "Capaciteit", icon: "👥", data: pd.capaciteit || {} },
    { title: "Technisch", icon: "⚙️", data: pd.technisch || {} },
  ];

  const formatValue = v => {
    if (v === null || v === undefined) return null;
    if (typeof v === "boolean") return v ? "✅ Ja" : "❌ Nee";
    if (typeof v === "number") return v.toLocaleString("nl-NL");
    return String(v);
  };

  document.getElementById("detailData").innerHTML = sections
    .filter(s => Object.keys(s.data).length > 0)
    .map(s => `
      <div class="data-section">
        <h3>${s.icon} ${s.title}</h3>
        ${Object.entries(s.data)
          .filter(([_, v]) => v !== null && v !== undefined)
          .map(([k, v]) => {
            const formatted = formatValue(v);
            if (!formatted) return "";
            return `
              <div class="data-row">
                <span class="label">${formatLabel(k)}</span>
                <span class="value">${escapeHtml(formatted)}</span>
              </div>
            `;
          }).join("")}
      </div>
    `).join("");
}

function formatLabel(key) {
  const labels = {
    merk: "Merk",
    model: "Model",
    bouwjaar: "Bouwjaar",
    kilometerstand: "Kilometerstand",
    kenteken: "Kenteken",
    slaapplaatsen: "Slaapplaatsen",
    zitplaatsen: "Zitplaatsen",
    vaste_bedden: "Vaste bedden",
    opklap_bedden: "Opklapbedden",
    brandstof: "Brandstof",
    transmissie: "Transmissie",
    vermogen_PK: "Vermogen (PK)",
    lengte_cm: "Lengte (cm)",
  };
  return labels[key] || key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
}

// ── Description ──────────────────────────────────────────────────────────────
function renderDescription(c) {
  const raw = c.raw_html || "";
  const container = document.getElementById("rawHtml");
  if (!raw) {
    container.closest(".detail-description")?.remove();
    return;
  }
  container.textContent = raw;
}

// ── Toggle Favorite ─────────────────────────────────────────────────────────
async function toggleFavorite(camperId, btn) {
  const isFav = btn.dataset.fav === "1";
  const method = isFav ? "DELETE" : "POST";

  try {
    await fetch(`/api/campers/${camperId}/favorite`, { method });
    updateFavButton(btn, !isFav);
  } catch (err) {
    console.error("Favorite error:", err);
  }
}

function updateFavButton(btn, isFav) {
  btn.textContent = isFav ? "⭐ Favoriet" : "☆ Favoriet";
  btn.dataset.fav = isFav ? "1" : "0";
  if (isFav) {
    btn.classList.add("btn-primary");
    btn.classList.remove("btn-outline");
  } else {
    btn.classList.remove("btn-primary");
    btn.classList.add("btn-outline");
  }
}

// ── Utility ─────────────────────────────────────────────────────────────────
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ── Start ───────────────────────────────────────────────────────────────────
loadCamper();
