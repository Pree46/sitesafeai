'use client';

import { useState, useEffect, useCallback } from 'react';
import {
    Users, AlertTriangle, ShieldAlert, MapPin, ShieldCheck, Activity,
    RefreshCw, Download, FileText
} from 'lucide-react';

import { dashboardApi } from '../services/dashboardApi';

// Dashboard sub-components
import { MetricCard } from './dashboard/MetricCard';
import { SafetyScore } from './dashboard/SafetyScore';
import { ViolationPieChart } from './dashboard/ViolationPieChart';
import { DailyViolationsChart } from './dashboard/DailyViolationsChart';
import { ZoneViolationsChart } from './dashboard/ZoneViolationsChart';
import { ZoneTable } from './dashboard/ZoneTable';
import { WorkerTable } from './dashboard/WorkerTable';
import { TopViolators } from './dashboard/TopViolators';
import { ViolationFeed } from './dashboard/ViolationFeed';
import { InsightsPanel } from './dashboard/InsightsPanel';

export function DashboardTab() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    // Data state
    const [metrics, setMetrics] = useState(null);
    const [workers, setWorkers] = useState([]);
    const [topViolators, setTopViolators] = useState([]);
    const [severityDist, setSeverityDist] = useState([]);
    const [dailyViolations, setDailyViolations] = useState([]);
    const [zoneAnalytics, setZoneAnalytics] = useState([]);
    const [zones, setZones] = useState([]);
    const [violationFeed, setViolationFeed] = useState([]);
    const [safetyScore, setSafetyScore] = useState(null);
    const [insights, setInsights] = useState([]);

    const fetchAllData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const [
                metricsRes, workersRes, topRes, sevRes,
                dailyRes, zoneRes, zonesRes, feedRes,
                scoreRes, insightsRes
            ] = await Promise.all([
                dashboardApi.getMetrics(),
                dashboardApi.getWorkers(),
                dashboardApi.getTopViolators(),
                dashboardApi.getSeverityDist(),
                dashboardApi.getDailyViolations(),
                dashboardApi.getZoneAnalytics(),
                dashboardApi.getZones(),
                dashboardApi.getViolationFeed(),
                dashboardApi.getSafetyScore(),
                dashboardApi.getInsights(),
            ]);

            setMetrics(metricsRes);
            setWorkers(workersRes);
            setTopViolators(topRes);
            setSeverityDist(sevRes);
            setDailyViolations(dailyRes);
            setZoneAnalytics(zoneRes);
            setZones(zonesRes);
            setViolationFeed(feedRes);
            setSafetyScore(scoreRes);
            setInsights(insightsRes);
            setLastUpdated(new Date());
        } catch (err) {
            console.error('Dashboard fetch failed:', err);
            setError('Failed to connect to the dashboard API. Make sure the backend is running on port 8000.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAllData();
        const interval = setInterval(() => {
            fetchAllData();
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    const handleWorkerSearch = async () => {
        try {
            const res = await dashboardApi.getWorkers();
            setWorkers(res);
        } catch (err) {
            console.error('Worker search failed:', err);
        }
    };

    const handleCsvExport = () => {
        window.open(dashboardApi.exportCsv(), '_blank');
    };

    // ── Error State ──
    if (error) {
        return (
            <div className="rounded-2xl bg-white/5 border border-red-500/20 backdrop-blur-sm p-8 text-center">
                <ShieldAlert size={48} className="text-red-400 mx-auto mb-4" />
                <h2 className="text-white text-xl font-bold mb-2">Connection Error</h2>
                <p className="text-white/50 text-sm mb-6">{error}</p>
                <button onClick={fetchAllData}
                    className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 text-sm font-medium hover:bg-red-500/30 transition-colors">
                    Retry Connection
                </button>
            </div>
        );
    }

    // ── Loading State ──
    if (loading && !metrics) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="flex flex-col items-center gap-3">
                    <div className="w-10 h-10 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
                    <p className="text-white/30 text-sm">Loading dashboard data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* ── Header Row ── */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight bg-gradient-to-r from-purple-300 via-pink-300 to-purple-300 bg-clip-text text-transparent">
                        Safety Dashboard
                    </h2>
                    <p className="text-sm text-white/30 mt-1">
                        Real-time monitoring and analytics for workplace safety
                        {lastUpdated && (
                            <span className="ml-2">· Updated {lastUpdated.toLocaleTimeString()}</span>
                        )}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <button onClick={handleCsvExport}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium
              bg-white/5 border border-white/10 text-white/50
              hover:bg-white/10 hover:text-white/80 transition-all duration-200">
                        <Download size={14} />
                        CSV
                    </button>
                    <button onClick={() => window.print()}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium
              bg-white/5 border border-white/10 text-white/50
              hover:bg-white/10 hover:text-white/80 transition-all duration-200">
                        <FileText size={14} />
                        PDF
                    </button>
                    <button onClick={fetchAllData}
                        className={`p-2 rounded-lg bg-white/5 border border-white/10 text-white/40
              hover:text-white/80 hover:bg-white/10 transition-all duration-200
              ${loading ? 'animate-spin' : ''}`}>
                        <RefreshCw size={14} />
                    </button>
                </div>
            </div>

            {/* ── METRIC CARDS ── */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    title="Registered Workers" value={metrics?.total_workers || 0}
                    icon={Users} color="blue"
                    trend={1} trendLabel="Active personnel"
                />
                <MetricCard
                    title="Total Violations" value={metrics?.violations_today || 0}
                    icon={AlertTriangle} color="red"
                    trend={metrics?.violations_today <= (metrics?.violations_yesterday || 0) ? 1 : -1}
                    trendLabel={`Today: ${metrics?.violations_today || 0}`}
                />
                <MetricCard
                    title="Restricted Zones" value={metrics?.total_zones || 0}
                    icon={MapPin} color="yellow"
                    trend={1} trendLabel={`${metrics?.high_severity_today || 0} High Risk`}
                />
                <MetricCard
                    title="PPE Compliance" value={`${metrics?.ppe_compliance_rate || 0}%`}
                    icon={ShieldCheck} color="emerald"
                    trend={metrics?.ppe_compliance_rate >= 80 ? 1 : -1}
                    trendLabel={metrics?.ppe_compliance_rate >= 80 ? 'Good' : 'Needs attention'}
                />
            </div>

            {/* ── ROW 2: Charts + Safety Score ── */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <DailyViolationsChart data={dailyViolations} />
                </div>
                <SafetyScore
                    score={safetyScore?.score || 0}
                    grade={safetyScore?.grade || 'N/A'}
                    trend={safetyScore?.trend || 'stable'}
                />
            </div>

            {/* ── ROW 3: Pie + Zone Chart + Insights ── */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <ViolationPieChart data={severityDist} />
                <ZoneViolationsChart data={zoneAnalytics} />
                <InsightsPanel data={insights} />
            </div>

            {/* ── Feed + Top Violators ── */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <ViolationFeed data={violationFeed} />
                </div>
                <TopViolators data={topViolators} />
            </div>

            {/* ── Zone Table ── */}
            <ZoneTable data={zones} />

            {/* ── Worker Table ── */}
            <WorkerTable data={workers} onSearch={handleWorkerSearch} />
        </div>
    );
}
