const API_BASE = "http://localhost:8000";

let allElements = [];
let currentLayerFilter = "all";

document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  fetchPlatformData();
  setInterval(checkBackendHealth, 10000);
});

// View Navigation
function switchView(viewName) {
  document.querySelectorAll(".content-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));

  const targetView = document.getElementById(`view-${viewName}`);
  const targetNav = document.getElementById(`nav-${viewName}`);

  if (targetView) targetView.classList.add("active");
  if (targetNav) targetNav.classList.add("active");

  const titles = {
    dashboard: ["Overview & Platform Health", "Real-time status of multi-agent pipeline and legacy systems."],
    trigger: ["Trigger Ingestion Pipeline", "Launch top-level orchestrator across all 5 ArchiMate layers."],
    browser: ["ArchiMate Element Browser", "Explore extracted motivation, business, application & technology elements."],
    artifacts: ["Artifact Versions & Pull Requests", "Track merged model versions and GitHub PR status."]
  };

  if (titles[viewName]) {
    document.getElementById("page-title").textContent = titles[viewName][0];
    document.getElementById("page-desc").textContent = titles[viewName][1];
  }
}

// Check Backend API Health
async function checkBackendHealth() {
  const dot = document.getElementById("backend-status-dot");
  const text = document.getElementById("backend-status-text");

  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      dot.style.background = "var(--accent-emerald)";
      text.textContent = "Online (Healthy)";
    } else {
      throw new Error();
    }
  } catch (e) {
    dot.style.background = "#f87171";
    text.textContent = "Offline (Reconnecting...)";
  }
}

// Fetch Initial Platform Data
async function fetchPlatformData() {
  fetchElements("system-demo");
}

// Fetch Elements from REST API
async function fetchElements(systemId) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/elements/${systemId}`);
    if (res.ok) {
      allElements = await res.json();
      document.getElementById("metric-elements-count").textContent = allElements.length;
      renderElements();
    }
  } catch (e) {
    console.warn("Could not fetch elements from backend:", e);
  }
}

// Render Element Cards (Task I3)
function renderElements() {
  const container = document.getElementById("elements-grid");
  const searchQuery = document.getElementById("browser-search").value.toLowerCase();

  const filtered = allElements.filter(elem => {
    const matchesLayer = currentLayerFilter === "all" || elem.layer.toLowerCase() === currentLayerFilter;
    const matchesSearch = elem.name.toLowerCase().includes(searchQuery) || elem.archimate_type.toLowerCase().includes(searchQuery);
    return matchesLayer && matchesSearch;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<div class="card" style="grid-column: 1 / -1;"><p class="text-muted">No ArchiMate elements found matching criteria.</p></div>`;
    return;
  }

  container.innerHTML = filtered.map(elem => `
    <div class="element-card">
      <div class="element-header">
        <span class="badge badge-${elem.layer.toLowerCase()}">${elem.layer}</span>
        <code style="font-size: 11px; color: var(--text-muted);">${elem.id}</code>
      </div>
      <h4 class="element-name">${elem.name}</h4>
      <div style="font-size: 13px; color: var(--accent-cyan); font-weight: 500;">
        Type: ${elem.archimate_type}
      </div>
      <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">
        📂 ${elem.git_path || 'test-fixtures/'}
      </div>
    </div>
  `).join("");
}

// Layer Filter Pills
function setLayerFilter(layer, btnElement) {
  currentLayerFilter = layer;
  document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
  btnElement.classList.add("active");
  renderElements();
}

function filterElements() {
  renderElements();
}

// Trigger Ingestion Job Form (Task I2)
async function handleTriggerJob(e) {
  e.preventDefault();
  const systemId = document.getElementById("select-system").value;
  const statusContainer = document.getElementById("job-status-container");
  const submitBtn = document.getElementById("btn-submit-job");

  submitBtn.disabled = true;
  submitBtn.textContent = "⚡ Triggering...";

  try {
    const res = await fetch(`${API_BASE}/api/v1/jobs?system_id=${systemId}`, {
      method: "POST"
    });

    if (res.ok) {
      const job = await res.json();
      statusContainer.innerHTML = `
        <div class="job-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong>Job ID: ${job.job_id}</strong>
            <span class="badge badge-info">${job.status}</span>
          </div>
          <p style="font-size: 13px;" class="text-muted">Type: ${job.job_type} | Target System: ${job.system_id}</p>
          <p style="font-size: 12px; color: var(--accent-emerald); margin-top: 6px;">✅ Orchestration job successfully queued into async thread runner.</p>
        </div>
      `;
      document.getElementById("metric-jobs-count").textContent = "1";
    }
  } catch (err) {
    statusContainer.innerHTML = `<p class="text-danger">❌ Failed to trigger job. Ensure backend REST API is online.</p>`;
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "⚡ Launch Ingestion Job";
  }
}
