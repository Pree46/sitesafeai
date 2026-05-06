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
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Violations</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((zone, i) => (
                            <tr
                                key={i}
                                className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors"
                            >
                                <td className="py-3 px-2 text-white/80 font-medium">
                                    {zone.name}
                                </td>

                                <td className="py-3 px-2">
                                    <span className="text-red-400 font-semibold">
                                        {zone.violations}
                                    </span>
                                </td>

                                <td className="py-3 px-2">
                                    <span className="
                                        px-2 py-1 rounded-full text-xs
                                        bg-red-500/10 text-red-400
                                    ">
                                        ACTIVE
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
