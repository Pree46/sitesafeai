const hostname =
  typeof window !== "undefined"
    ? window.location.hostname
    : "localhost";

const API_BASE = `http://${hostname}:8000/api`;

async function fetchJson(url) {
  const res = await fetch(url);

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export const dashboardApi = {

  // ================= METRICS =================
  getMetrics: () =>
    fetchJson(`${API_BASE}/metrics/overview`),

  // ================= WORKERS =================
  getWorkers: () =>
    fetchJson(`${API_BASE}/workers`),

  getTopViolators: () =>
    fetchJson(`${API_BASE}/workers/top-violators`),

  // ================= LIVE FEED =================
  getViolationFeed: () =>
    fetchJson(`${API_BASE}/violations/feed`),

  // ================= ANALYTICS =================
  getSeverityDist: () =>
    fetchJson(`${API_BASE}/analytics/severity`),

  getZoneAnalytics: () =>
    fetchJson(`${API_BASE}/analytics/zone`),

  getDailyViolations: () =>
    fetchJson(`${API_BASE}/analytics/daily`),

  getSafetyScore: () =>
    fetchJson(`${API_BASE}/analytics/safety-score`),

  getInsights: () =>
    fetchJson(`${API_BASE}/analytics/insights`),

  // ================= ZONES =================
  getZones: () =>
    fetchJson(`${API_BASE}/zones`),

  // ================= EXPORT =================
  exportCsv: () =>
    `${API_BASE}/export/csv`,
};