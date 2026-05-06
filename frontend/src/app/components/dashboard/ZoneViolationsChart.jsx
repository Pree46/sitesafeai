'use client';

import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#1a1f35]/95 backdrop-blur-sm border border-white/10 rounded-lg px-3 py-2 shadow-xl">
                <p className="text-white text-xs font-medium">{label}</p>
                <p className="text-cyan-400 text-xs">{payload[0].value} violations</p>
            </div>
        );
    }
    return null;
};

export function ZoneViolationsChart({ data = [] }) {
    const chartData = data.map(d => ({
        name: d.name,
        violations: d.value,
        fill: '#ef4444',
    }));

    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
                Zone Violations
            </h3>

            {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={chartData} layout="vertical" barSize={16}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                        <XAxis
                            type="number"
                            tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                        />
                        <YAxis
                            dataKey="name" type="category" width={120}
                            tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                        />
                        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                        <Bar dataKey="violations" radius={[0, 6, 6, 0]}>
                            {chartData.map((entry, index) => (
                                <Cell key={index} fill={entry.fill} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            ) : (
                <div className="h-64 flex items-center justify-center text-white/20 text-sm">No data available</div>
            )}
        </div>
    );
}
