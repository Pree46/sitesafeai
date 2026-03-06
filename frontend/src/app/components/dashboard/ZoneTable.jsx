'use client';

const RISK_COLORS = {
    high: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20' },
    medium: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
    low: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20' },
};

const TYPE_BADGES = {
    restricted: { bg: 'bg-red-500/15', text: 'text-red-400' },
    warning: { bg: 'bg-amber-500/15', text: 'text-amber-400' },
    safe: { bg: 'bg-emerald-500/15', text: 'text-emerald-400' },
};

export function ZoneTable({ data = [] }) {
    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
                Zone Intelligence
            </h3>

            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-white/[0.06]">
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Zone</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Type</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Today</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Risk</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((zone) => {
                            const risk = RISK_COLORS[zone.risk_level] || RISK_COLORS.low;
                            const type = TYPE_BADGES[zone.zone_type] || TYPE_BADGES.safe;
                            return (
                                <tr key={zone.id} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                                    <td className="py-3 px-2 text-white/80 font-medium">{zone.name}</td>
                                    <td className="py-3 px-2">
                                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${type.bg} ${type.text}`}>
                                            {zone.zone_type}
                                        </span>
                                    </td>
                                    <td className="py-3 px-2">
                                        <span className={`font-semibold ${zone.violations_today > 3 ? 'text-red-400' : zone.violations_today > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                                            {zone.violations_today}
                                        </span>
                                    </td>
                                    <td className="py-3 px-2">
                                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${risk.bg} ${risk.text} ${risk.border}`}>
                                            {zone.risk_level}
                                        </span>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
