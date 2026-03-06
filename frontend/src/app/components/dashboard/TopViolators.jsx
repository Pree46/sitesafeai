'use client';

import { Trophy } from 'lucide-react';

const MEDAL_COLORS = ['#eab308', '#94a3b8', '#cd7f32'];

export function TopViolators({ data = [] }) {
    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <div className="flex items-center gap-2 mb-4">
                <Trophy size={16} className="text-amber-400" />
                <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider">
                    Top Violators
                </h3>
            </div>

            <div className="space-y-3">
                {data.map((w, i) => (
                    <div key={w.id}
                        className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.04] transition-colors">
                        <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                            style={{
                                backgroundColor: i < 3 ? `${MEDAL_COLORS[i]}20` : 'rgba(255,255,255,0.05)',
                                color: i < 3 ? MEDAL_COLORS[i] : 'rgba(255,255,255,0.3)',
                            }}>
                            {i + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white/80 truncate">{w.name}</p>
                            <p className="text-xs text-white/30">{w.role}</p>
                        </div>
                        <div className="text-right">
                            <span className="text-lg font-bold text-red-400">{w.violation_count}</span>
                            <p className="text-[10px] text-white/20">violations</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
