const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
const API_BASE = `http://${hostname}:8000/api`;

async function fetchJson(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
}

export const dashboardApi = {
    getMetrics: () => fetchJson(`${API_BASE}/metrics/overview`),
    getWorkers: (search = "") =>
        fetchJson(`${API_BASE}/workers${search ? `?search=${search}` : ""}`),
    getTopViolators: () => fetchJson(`${API_BASE}/workers/top-violators`),
    getViolations: (params = {}) => {
        const qs = new URLSearchParams(params).toString();
        return fetchJson(`${API_BASE}/violations${qs ? `?${qs}` : ""}`);
    },
    getViolationsToday: () => fetchJson(`${API_BASE}/violations/today`),
    getViolationFeed: () => fetchJson(`${API_BASE}/violations/feed`),
    getSeverityDist: () => fetchJson(`${API_BASE}/analytics/severity`),
    getZoneAnalytics: () => fetchJson(`${API_BASE}/analytics/zone`),
    getDailyViolations: (days = 14) =>
        fetchJson(`${API_BASE}/analytics/daily?days=${days}`),
    getCalendar: (days = 90) =>
        fetchJson(`${API_BASE}/analytics/calendar?days=${days}`),
    getSafetyScore: () => fetchJson(`${API_BASE}/analytics/safety-score`),
    getInsights: () => fetchJson(`${API_BASE}/analytics/insights`),
    getZones: () => fetchJson(`${API_BASE}/zones`),
    exportCsv: () => `${API_BASE}/export/csv`,
};
