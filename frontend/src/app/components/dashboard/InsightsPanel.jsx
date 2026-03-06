'use client';

import {
    AlertTriangle, MapPin, User, Shield, TrendingUp, Brain
} from 'lucide-react';

const ICON_MAP = {
    AlertTriangle, MapPin, User, Shield, TrendingUp,
};

export function InsightsPanel({ data = [] }) {
    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <div className="flex items-center gap-2 mb-4">
                <Brain size={16} className="text-purple-400" />
                <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider">
                    AI Safety Insights
                </h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.map((insight, i) => {
                    const Icon = ICON_MAP[insight.icon] || AlertTriangle;
                    return (
                        <div key={i}
                            className="flex items-start gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.04]
                hover:bg-white/[0.04] transition-all duration-200">
                            <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                                style={{ backgroundColor: `${insight.color}15` }}>
                                <Icon size={16} style={{ color: insight.color }} />
                            </div>
                            <div className="min-w-0">
                                <p className="text-[11px] text-white/30 font-medium uppercase tracking-wider">{insight.title}</p>
                                <p className="text-sm text-white/80 font-medium mt-0.5 truncate">{insight.value}</p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
