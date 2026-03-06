'use client';

import { Activity } from 'lucide-react';

const SEVERITY_STYLES = {
    1: { dot: 'bg-emerald-400', text: 'text-emerald-400', label: 'Minor' },
    2: { dot: 'bg-amber-400', text: 'text-amber-400', label: 'Medium' },
    3: { dot: 'bg-red-400', text: 'text-red-400', label: 'Critical' },
};

export function ViolationFeed({ data = [] }) {
    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <div className="flex items-center gap-2 mb-4">
                <div className="relative">
                    <Activity size={16} className="text-cyan-400" />
                    <span className="absolute -top-1 -right-1 w-2 h-2 bg-cyan-400 rounded-full animate-ping" />
                </div>
                <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider">
                    Live Violation Feed
                </h3>
            </div>

            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
                {data.length === 0 && (
                    <p className="text-white/20 text-sm text-center py-8">No recent violations</p>
                )}
                {data.map((v, i) => {
                    const sev = SEVERITY_STYLES[v.severity_grade] || SEVERITY_STYLES[1];
                    const time = v.timestamp?.split(' ')[1]?.slice(0, 5) || '';
                    return (
                        <div key={v.id || i}
                            className="flex items-start gap-3 p-3 rounded-lg bg-white/[0.015] border border-white/[0.03]
                hover:bg-white/[0.03] transition-all duration-200 group"
                            style={{ animationDelay: `${i * 50}ms` }}>
                            <div className="flex flex-col items-center gap-1 mt-0.5">
                                <span className={`w-2 h-2 rounded-full ${sev.dot}`} />
                                {i < data.length - 1 && <div className="w-px h-6 bg-white/[0.06]" />}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-white/30 font-mono">{time}</span>
                                    <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${sev.text} bg-white/[0.04]`}>
                                        {sev.label}
                                    </span>
                                </div>
                                <p className="text-sm text-white/70 mt-1">
                                    <span className="text-white/90 font-medium">{v.worker_name || `Worker #${v.worker_id}`}</span>
                                    {' — '}
                                    <span className={sev.text}>{v.violation_type}</span>
                                </p>
                                {v.zone_name && (
                                    <p className="text-xs text-white/30 mt-0.5">📍 {v.zone_name}</p>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
