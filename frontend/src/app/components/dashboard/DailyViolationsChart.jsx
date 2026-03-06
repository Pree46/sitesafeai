'use client';

import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#1a1f35]/95 backdrop-blur-sm border border-white/10 rounded-lg px-3 py-2 shadow-xl">
                <p className="text-white text-xs font-medium mb-1">{label}</p>
                {payload.map((p, i) => (
                    <p key={i} className="text-xs" style={{ color: p.color }}>
                        {p.name}: {p.value}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

export function DailyViolationsChart({ data = [] }) {
    const chartData = data.map(d => ({
        date: d.date?.slice(5) || '', // MM-DD
        Minor: d.grade_1,
        Medium: d.grade_2,
        Critical: d.grade_3,
    }));

    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
                Daily Violations Trend
            </h3>

            {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={chartData} barGap={2}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                        <XAxis
                            dataKey="date" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                        />
                        <YAxis
                            tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                        />
                        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                        <Legend
                            verticalAlign="top" height={36}
                            formatter={(value) => <span className="text-white/50 text-xs">{value}</span>}
                        />
                        <Bar dataKey="Minor" stackId="a" fill="#22c55e" radius={[0, 0, 0, 0]} />
                        <Bar dataKey="Medium" stackId="a" fill="#eab308" radius={[0, 0, 0, 0]} />
                        <Bar dataKey="Critical" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            ) : (
                <div className="h-72 flex items-center justify-center text-white/20 text-sm">No data available</div>
            )}
        </div>
    );
}
