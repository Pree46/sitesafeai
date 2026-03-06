'use client';

import { TrendingUp, TrendingDown } from 'lucide-react';

export function MetricCard({ title, value, icon: Icon, trend, trendLabel, color = 'emerald' }) {
    const isPositive = trend > 0;

    // Purple-tinted glassmorphism card with subtle gradient borders
    const colorMap = {
        emerald: { gradient: 'from-emerald-500/20 to-emerald-600/5', iconBg: 'bg-emerald-500/10', iconText: 'text-emerald-400', borderGlow: 'border-emerald-500/15' },
        red: { gradient: 'from-red-500/20 to-red-600/5', iconBg: 'bg-red-500/10', iconText: 'text-red-400', borderGlow: 'border-red-500/15' },
        yellow: { gradient: 'from-amber-500/20 to-amber-600/5', iconBg: 'bg-amber-500/10', iconText: 'text-amber-400', borderGlow: 'border-amber-500/15' },
        blue: { gradient: 'from-blue-500/20 to-blue-600/5', iconBg: 'bg-blue-500/10', iconText: 'text-blue-400', borderGlow: 'border-blue-500/15' },
        purple: { gradient: 'from-purple-500/20 to-purple-600/5', iconBg: 'bg-purple-500/10', iconText: 'text-purple-400', borderGlow: 'border-purple-500/15' },
        cyan: { gradient: 'from-cyan-500/20 to-cyan-600/5', iconBg: 'bg-cyan-500/10', iconText: 'text-cyan-400', borderGlow: 'border-cyan-500/15' },
    };
    const c = colorMap[color] || colorMap.emerald;

    return (
        <div className={`relative group rounded-xl border ${c.borderGlow}
      bg-white/5 backdrop-blur-sm p-5
      transition-all duration-300 hover:scale-[1.02] hover:bg-white/[0.07] overflow-hidden`}>
            {/* Top gradient accent */}
            <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${c.gradient} opacity-80`} />

            <div className="relative flex items-start justify-between">
                <div>
                    <p className="text-xs font-medium text-white/40 uppercase tracking-wider mb-2">{title}</p>
                    <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
                </div>
                <div className={`w-10 h-10 rounded-lg ${c.iconBg} flex items-center justify-center`}>
                    <Icon size={20} className={c.iconText} />
                </div>
            </div>

            {trendLabel && (
                <div className="relative mt-3 flex items-center gap-1.5">
                    {isPositive ? (
                        <TrendingUp size={14} className="text-emerald-400" />
                    ) : (
                        <TrendingDown size={14} className="text-red-400" />
                    )}
                    <span className={`text-xs font-medium ${isPositive ? 'text-emerald-400/70' : 'text-red-400/70'}`}>
                        {trendLabel}
                    </span>
                </div>
            )}
        </div>
    );
}
