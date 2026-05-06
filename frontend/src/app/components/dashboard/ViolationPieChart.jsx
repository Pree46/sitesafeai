'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const SEVERITY_COLORS = {
    1: '#22c55e',
    2: '#eab308',
    3: '#ef4444',
};

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#1a1f35]/95 backdrop-blur-sm border border-white/10 rounded-lg px-3 py-2 shadow-xl">
                <p className="text-white text-sm font-medium">{payload[0].name}</p>
                <p className="text-white/60 text-xs">{payload[0].value} violations</p>
            </div>
        );
    }
    return null;
};

export function ViolationPieChart({ data = [] }) {
    const chartData = data.map(d => ({
        name: d.name,
        value: d.value,
        color: d.color,
    }));

    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
                Violation Severity Distribution
            </h3>

            {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={90}
                            paddingAngle={4}
                            dataKey="value"
                            stroke="none"
                        >
                            {chartData.map((entry, index) => (
                                <Cell key={index} fill={entry.color} style={{ filter: `drop-shadow(0 0 6px ${entry.color}60)` }} />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            formatter={(value) => <span className="text-white/60 text-xs">{value}</span>}
                        />
                    </PieChart>
                </ResponsiveContainer>
            ) : (
                <div className="h-64 flex items-center justify-center text-white/20 text-sm">No data available</div>
            )}
        </div>
    );
}
