'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';

export function WorkerTable({ data = [], onSearch }) {
    const [searchTerm, setSearchTerm] = useState('');

    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
        onSearch?.(e.target.value);
    };

    return (
        <div className="bg-[#0f1629]/80 backdrop-blur-sm rounded-xl border border-white/[0.06] p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider">
                    Worker Intelligence
                </h3>
                <div className="relative">
                    <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/20" />
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={handleSearch}
                        placeholder="Search workers..."
                        className="bg-white/[0.04] border border-white/[0.08] rounded-lg pl-8 pr-3 py-1.5 text-xs text-white
              placeholder-white/20 focus:outline-none focus:border-emerald-500/30 transition-colors w-48"
                    />
                </div>
            </div>

            <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
                <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-[#0f1629]">
                        <tr className="border-b border-white/[0.06]">
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">ID</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Name</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Role</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Violations</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Most Common</th>
                            <th className="text-left py-3 px-2 text-white/30 font-medium text-xs uppercase">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((w) => (
                            <tr key={w.id} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                                <td className="py-3 px-2 text-white/40 font-mono text-xs">#{w.id}</td>
                                <td className="py-3 px-2 text-white/80 font-medium">{w.name}</td>
                                <td className="py-3 px-2 text-white/50 text-xs">{w.role}</td>
                                <td className="py-3 px-2">
                                    <span className={`font-semibold ${w.violation_count > 10 ? 'text-red-400' : w.violation_count > 5 ? 'text-amber-400' : 'text-emerald-400'}`}>
                                        {w.violation_count}
                                    </span>
                                </td>
                                <td className="py-3 px-2 text-white/50 text-xs">{w.most_common_violation || '—'}</td>
                                <td className="py-3 px-2">
                                    <span className={`w-2 h-2 rounded-full inline-block ${w.is_active ? 'bg-emerald-400 shadow-[0_0_6px_rgba(34,197,94,0.5)]' : 'bg-white/20'}`} />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
