// ── Load Campers ─────────────────────────────────────────────────────────────
async function loadCompare() {
  const idsParam = new URLSearchParams(window.location.search).get("ids");
  const ids = idsParam ? idsParam.split(",").map(Number).filter(Boolean) : [];

  if (ids.length < 2) {
    document.getElementById("empty").style.display = "block";
    return;
  }

  document.getElementById("loading").style.display = "flex";

  try {
    const campers = [];
    for (const id of ids) {
      const res = await fetch(`/api/campers/${id}`);
      if (res.ok) campers.push(await res.json());
    }

    document.getElementById("loading").style.display = "none";

    if (campers.length < 2) {
      document.getElementById("empty").style.display = "block";
      return;
    }

    document.title = `Vergelijk: ${campers.map(c => c.parsed_data?.basis?.merk || "Camper").join(" vs ")}`;
    renderCompare(campers);
  } catch (err) {
    console.error("Compare error:", err);
    document.getElementById("loading").style.display = "none";
    document.getElementById("empty").style.display = "block";
  }
}

// ── Render Comparison Table ─────────────────────────────────────────────────
function renderCompare(campers) {
  const props = [
    { label: "Prijs", key: "price_euros", type: "currency", best: "low" },
    { label: "Locatie", key: "location" },
    { label: "Merk", key: "parsed_data.basis.merk" },
    { label: "Model", key: "parsed_data.basis.model" },
    { label: "Bouwjaar", key: "parsed_data.basis.bouwjaar", best: "high" },
    { label: "Kilometerstand", key: "parsed_data.basis.kilometerstand", type: "km", best: "low" },
    { label: "Brandstof", key: "parsed_data.technisch.brandstof" },
    { label: "Transmissie", key: "parsed_data.technisch.transmissie" },
    { label: "Vermogen", key: "parsed_data.technisch.vermogen_PK", type: "pk", best: "high" },
    { label: "Lengte", key: "parsed_data.technisch.lengte_cm", type: "length" },
    { label: "Slaapplaatsen", key: "parsed_data.capaciteit.slaapplaatsen", best: "high" },
    { label: "Zitplaatsen", key: "parsed_data.capaciteit.zitplaatsen", best: "high" },
    { label: "Airco", key: "parsed_data.comfort.airco", type: "bool" },
    { label: "GPS", key: "parsed_data.comfort.GPS", type: "bool" },
    { label: "Parkeersensoren", key: "parsed_data.comfort.parkeersensoren", type: "bool" },
    { label: "Keuken", key: "parsed_data.camper.keuken", type: "bool" },
    { label: "Koelkast", key: "parsed_data.camper.koelkast", type: "bool" },
    { label: "Douche", key: "parsed_data.camper.douche", type: "bool" },
    { label: "Toilet", key: "parsed_data.camper.toilet", type: "bool" },
    { label: "APK geldig", key: "parsed_data.onderhoud.APK_geldig", type: "bool" },
    { label: "Service historie", key: "parsed_data.onderhoud.service_historie", type: "bool" },
  ];

  // Header with images and titles
  let html = `<table><thead><tr><th></th>`;
  campers.forEach(c => {
    const firstImg = Array.isArray(c.image_urls) && c.image_urls.length > 0 ? c.image_urls[0] : null;
    html += `<th style="text-align:center;min-width:200px;">
      ${firstImg ? `<img src="${escapeHtml(firstImg)}" alt="" style="width:100%;max-width:200px;border-radius:var(--radius);margin-bottom:0.5rem;">` : '<div style="font-size:3rem;margin-bottom:0.5rem;">🚐</div>'}
      <div><a href="/camper/${c.id}" style="font-weight:600;">${escapeHtml(c.title || "Camper")}</a></div>
    </th>`;
  });
  html += `</tr></thead><tbody>`;

  // Rows
  props.forEach(p => {
    const values = campers.map(c => getNestedValue(c, p.key));
    const bestIdx = findBest(values, p);

    html += `<tr><td><strong>${p.label}</strong></td>`;
    campers.forEach((c, i) => {
      const formatted = formatValue(values[i], p.type);
      const isBest = bestIdx === i && p.best;
      html += `<td${isBest ? ' class="highlight-best"' : ''}>${formatted}</td>`;
    });
    html += `</tr>`;
  });

  html += `</tbody></table>`;
  document.getElementById("compareTable").innerHTML = html;
}

// ── Find best value index ───────────────────────────────────────────────────
function findBest(values, prop) {
  if (!prop.best) return -1;

  const nums = values.map(v => (typeof v === "number" ? v : null));
  const validNums = nums.filter(n => n !== null);
  if (validNums.length < 2) return -1;

  const target = prop.best === "high" ? Math.max(...validNums) : Math.min(...validNums);
  // Only highlight if values actually differ
  if (new Set(validNums).size === 1) return -1;

  return nums.indexOf(target);
}

// ── Helpers ─────────────────────────────────────────────────────────────────
function getNestedValue(obj, path) {
  return path.split(".").reduce((o, k) => (o && o[k] !== undefined) ? o[k] : undefined, obj);
}

function formatValue(v, type) {
  if (v === null || v === undefined) return '<span style="color:var(--text-light)">—</span>';
  switch (type) {
    case "currency":
      return `€${Number(v).toLocaleString("nl-NL")}`;
    case "km":
      return `${Number(v).toLocaleString("nl-NL")} km`;
    case "pk":
      return `${v} PK`;
    case "length":
      return `${(Number(v) / 100).toFixed(1)}m`;
    case "bool":
      return v ? "✅ Ja" : "❌ Nee";
    default:
      return escapeHtml(String(v));
  }
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ── Start ───────────────────────────────────────────────────────────────────
loadCompare();
