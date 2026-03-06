'use client';

import { useState, useEffect, useCallback } from 'react';
import {
    Users, AlertTriangle, ShieldAlert, MapPin, ShieldCheck, Activity,
    RefreshCw
} from 'lucide-react';

import { dashboardApi } from '../services/dashboardApi';
import { Sidebar } from '../components/dashboard/Sidebar';
import { MetricCard } from '../components/dashboard/MetricCard';
import { SafetyScore } from '../components/dashboard/SafetyScore';
import { ViolationPieChart } from '../components/dashboard/ViolationPieChart';
import { DailyViolationsChart } from '../components/dashboard/DailyViolationsChart';
import { ZoneViolationsChart } from '../components/dashboard/ZoneViolationsChart';
import { ZoneTable } from '../components/dashboard/ZoneTable';
import { WorkerTable } from '../components/dashboard/WorkerTable';
import { TopViolators } from '../components/dashboard/TopViolators';
import { ViolationFeed } from '../components/dashboard/ViolationFeed';
import { CalendarHeatmap } from '../components/dashboard/CalendarHeatmap';
import { InsightsPanel } from '../components/dashboard/InsightsPanel';
import { ExportButtons } from '../components/dashboard/ExportButtons';

export default function DashboardPage() {
    const [activeSection, setActiveSection] = useState('dashboard');
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
    const [calendarData, setCalendarData] = useState([]);
    const [safetyScore, setSafetyScore] = useState(null);
    const [insights, setInsights] = useState([]);

    const fetchAllData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const [
                metricsRes, workersRes, topRes, sevRes,
                dailyRes, zoneRes, zonesRes, feedRes,
                calRes, scoreRes, insightsRes
            ] = await Promise.all([
                dashboardApi.getMetrics(),
                dashboardApi.getWorkers(),
                dashboardApi.getTopViolators(),
                dashboardApi.getSeverityDist(),
                dashboardApi.getDailyViolations(),
                dashboardApi.getZoneAnalytics(),
                dashboardApi.getZones(),
                dashboardApi.getViolationFeed(),
                dashboardApi.getCalendar(),
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
            setCalendarData(calRes);
            setSafetyScore(scoreRes);
            setInsights(insightsRes);
            setLastUpdated(new Date());
        } catch (err) {
            console.error('Failed to fetch dashboard data:', err);
            setError('Failed to connect to the dashboard API. Make sure the backend is running on port 8001.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAllData();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchAllData, 30000);
        return () => clearInterval(interval);
    }, [fetchAllData]);

    const handleWorkerSearch = async (term) => {
        try {
            const res = await dashboardApi.getWorkers(term);
            setWorkers(res);
        } catch (err) {
            console.error('Worker search failed:', err);
        }
    };

    // Error state
    if (error) {
        return (
            <div className="min-h-screen bg-[#060611] flex items-center justify-center">
                <div className="bg-[#0f1629]/80 rounded-2xl border border-red-500/20 p-8 max-w-lg text-center">
                    <ShieldAlert size={48} className="text-red-400 mx-auto mb-4" />
                    <h2 className="text-white text-xl font-bold mb-2">Connection Error</h2>
                    <p className="text-white/50 text-sm mb-6">{error}</p>
                    <button onClick={fetchAllData}
                        className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 text-sm font-medium hover:bg-red-500/30 transition-colors">
                        Retry Connection
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#060611] text-white">
            <Sidebar activeSection={activeSection} onSectionChange={setActiveSection} />

            {/* Main Content */}
            <main className="ml-[240px] p-6 min-h-screen">
                {/* Header bar */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-2xl font-bold text-white tracking-tight">Safety Intelligence</h1>
                        <p className="text-sm text-white/30 mt-1">
                            Real-time monitoring & analytics
                            {lastUpdated && (
                                <span className="ml-2">
                                    · Updated {lastUpdated.toLocaleTimeString()}
                                </span>
                            )}
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <ExportButtons />
                        <button onClick={fetchAllData}
                            className={`p-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/40
                hover:text-white/80 hover:bg-white/[0.08] transition-all duration-200
                ${loading ? 'animate-spin' : ''}`}>
                            <RefreshCw size={16} />
                        </button>
                    </div>
                </div>

                {loading && !metrics ? (
                    <div className="flex items-center justify-center h-96">
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-10 h-10 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
                            <p className="text-white/30 text-sm">Loading dashboard data...</p>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {/* ─── METRIC CARDS ─── */}
                        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                            <MetricCard
                                title="Total Workers" value={metrics?.total_workers || 0}
                                icon={Users} color="blue"
                                trend={1} trendLabel="Registered"
                            />
                            <MetricCard
                                title="Active On-Site" value={metrics?.active_workers || 0}
                                icon={Activity} color="emerald"
                                trend={1} trendLabel="Currently active"
                            />
                            <MetricCard
                                title="Violations Today" value={metrics?.violations_today || 0}
                                icon={AlertTriangle} color="yellow"
                                trend={metrics?.violations_today <= (metrics?.violations_yesterday || 0) ? 1 : -1}
                                trendLabel={`${metrics?.violations_yesterday || 0} yesterday`}
                            />
                            <MetricCard
                                title="High Severity" value={metrics?.high_severity_today || 0}
                                icon={ShieldAlert} color="red"
                                trend={metrics?.high_severity_today === 0 ? 1 : -1}
                                trendLabel="Grade 3 today"
                            />
                            <MetricCard
                                title="Total Zones" value={metrics?.total_zones || 0}
                                icon={MapPin} color="purple"
                                trend={1} trendLabel="Monitored"
                            />
                            <MetricCard
                                title="PPE Compliance" value={`${metrics?.ppe_compliance_rate || 0}%`}
                                icon={ShieldCheck} color="cyan"
                                trend={metrics?.ppe_compliance_rate >= 80 ? 1 : -1}
                                trendLabel={metrics?.ppe_compliance_rate >= 80 ? 'Good' : 'Needs attention'}
                            />
                        </div>

                        {/* ─── ROW 2: Charts + Safety Score ─── */}
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

                        {/* ─── ROW 3: Pie + Zone Chart + Insights ─── */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <ViolationPieChart data={severityDist} />
                            <ZoneViolationsChart data={zoneAnalytics} />
                            <InsightsPanel data={insights} />
                        </div>

                        {/* ─── ROW 4: Calendar Heatmap ─── */}
                        <CalendarHeatmap data={calendarData} />

                        {/* ─── ROW 5: Feed + Top Violators ─── */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <div className="lg:col-span-2">
                                <ViolationFeed data={violationFeed} />
                            </div>
                            <TopViolators data={topViolators} />
                        </div>

                        {/* ─── ROW 6: Zone Table ─── */}
                        <ZoneTable data={zones} />

                        {/* ─── ROW 7: Worker Table ─── */}
                        <WorkerTable data={workers} onSearch={handleWorkerSearch} />
                    </div>
                )}
            </main>
        </div>
    );
}
