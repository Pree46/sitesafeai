'use client';

export function SafetyScore({ score = 0, grade = 'B', trend = 'stable' }) {
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const progress = (score / 100) * circumference;
    const dashOffset = circumference - progress;

    const getColor = (s) => {
        if (s >= 90) return { stroke: '#22c55e', bg: 'rgba(34,197,94,0.1)', label: 'Excellent' };
        if (s >= 80) return { stroke: '#3b82f6', bg: 'rgba(59,130,246,0.1)', label: 'Good' };
        if (s >= 70) return { stroke: '#eab308', bg: 'rgba(234,179,8,0.1)', label: 'Fair' };
        if (s >= 60) return { stroke: '#f97316', bg: 'rgba(249,115,22,0.1)', label: 'Warning' };
        return { stroke: '#ef4444', bg: 'rgba(239,68,68,0.1)', label: 'Critical' };
    };

    const colorInfo = getColor(score);

    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-6">Site Safety Score</h3>

            <div className="flex flex-col items-center">
                <div className="relative w-44 h-44">
                    <svg className="w-full h-full -rotate-90" viewBox="0 0 160 160">
                        {/* Background ring */}
                        <circle cx="80" cy="80" r={radius} fill="none"
                            stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
                        {/* Progress ring */}
                        <circle cx="80" cy="80" r={radius} fill="none"
                            stroke={colorInfo.stroke} strokeWidth="10"
                            strokeLinecap="round"
                            strokeDasharray={circumference}
                            strokeDashoffset={dashOffset}
                            className="transition-all duration-1000 ease-out"
                            style={{ filter: `drop-shadow(0 0 8px ${colorInfo.stroke}40)` }} />
                    </svg>

                    {/* Center text */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-4xl font-bold text-white">{Math.round(score)}</span>
                        <span className="text-xs font-medium mt-1" style={{ color: colorInfo.stroke }}>{colorInfo.label}</span>
                    </div>
                </div>

                {/* Grade badge */}
                <div className="mt-4 flex items-center gap-3">
                    <div className="px-3 py-1 rounded-full text-sm font-bold"
                        style={{ backgroundColor: colorInfo.bg, color: colorInfo.stroke }}>
                        Grade {grade}
                    </div>
                    <span className="text-xs text-white/40">
                        {trend === 'up' ? '↑ Improving' : trend === 'down' ? '↓ Declining' : '→ Stable'}
                    </span>
                </div>
            </div>
        </div>
    );
}
