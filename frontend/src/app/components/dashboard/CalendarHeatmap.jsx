'use client';

const LEVEL_COLORS = [
    'bg-white/[0.04]',   // 0 - no data
    'bg-emerald-500/30', // 1 - low
    'bg-emerald-500/50', // 2 - moderate
    'bg-amber-500/60',   // 3 - high
    'bg-red-500/70',     // 4 - critical
];

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export function CalendarHeatmap({ data = [] }) {
    // Build a map for quick lookup
    const dateMap = {};
    data.forEach(d => { dateMap[d.date] = d; });

    // Generate last 90 days
    const days = [];
    const now = new Date();
    for (let i = 89; i >= 0; i--) {
        const d = new Date(now);
        d.setDate(d.getDate() - i);
        const key = d.toISOString().split('T')[0];
        days.push({
            date: key,
            count: dateMap[key]?.count || 0,
            level: dateMap[key]?.level || 0,
            dayOfWeek: d.getDay(),
            month: d.getMonth(),
        });
    }

    // Group by weeks
    const weeks = [];
    let currentWeek = [];
    days.forEach((d, i) => {
        if (i === 0) {
            // Pad the first week
            for (let j = 0; j < d.dayOfWeek; j++) {
                currentWeek.push(null);
            }
        }
        currentWeek.push(d);
        if (d.dayOfWeek === 6 || i === days.length - 1) {
            weeks.push(currentWeek);
            currentWeek = [];
        }
    });

    // Find safest and most dangerous
    const withData = data.filter(d => d.count > 0);
    const safest = withData.length ? withData.reduce((a, b) => a.count < b.count ? a : b) : null;
    const worst = withData.length ? withData.reduce((a, b) => a.count > b.count ? a : b) : null;

    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
                Violation Calendar
            </h3>

            {/* Heatmap Grid */}
            <div className="flex gap-1 overflow-x-auto pb-2">
                {weeks.map((week, wi) => (
                    <div key={wi} className="flex flex-col gap-1">
                        {week.map((day, di) => (
                            <div key={di} className="relative group">
                                <div className={`w-3 h-3 rounded-[3px] ${day ? LEVEL_COLORS[day.level] : 'bg-transparent'}
                  transition-all duration-150 hover:ring-1 hover:ring-white/20`}
                                />
                                {day && (
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
                                        <div className="bg-[#1a1f35] border border-white/10 rounded-lg px-2 py-1 text-xs whitespace-nowrap shadow-xl">
                                            <p className="text-white/80">{day.date}</p>
                                            <p className="text-white/40">{day.count} violations</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            {/* Legend */}
            <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-2">
                    <span className="text-[10px] text-white/20">Less</span>
                    {LEVEL_COLORS.map((c, i) => (
                        <div key={i} className={`w-3 h-3 rounded-[3px] ${c}`} />
                    ))}
                    <span className="text-[10px] text-white/20">More</span>
                </div>

                <div className="flex gap-4 text-[10px]">
                    {safest && (
                        <span className="text-emerald-400">
                            Safest: {safest.date} ({safest.count})
                        </span>
                    )}
                    {worst && (
                        <span className="text-red-400">
                            Worst: {worst.date} ({worst.count})
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
