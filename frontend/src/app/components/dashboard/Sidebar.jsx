'use client';

import { useState } from 'react';
import {
    LayoutDashboard, Users, AlertTriangle, MapPin,
    BarChart3, FileText, Settings, Shield, ChevronLeft,
    ChevronRight
} from 'lucide-react';

const NAV_ITEMS = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'workers', label: 'Workers', icon: Users },
    { id: 'violations', label: 'Violations', icon: AlertTriangle },
    { id: 'zones', label: 'Zones', icon: MapPin },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ activeSection, onSectionChange }) {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <aside
            className={`fixed left-0 top-0 h-screen z-40 transition-all duration-300 ease-in-out
        ${collapsed ? 'w-[72px]' : 'w-[240px]'}
        bg-[#0a0a1a]/90 backdrop-blur-xl border-r border-white/[0.06]
        flex flex-col`}
        >
            {/* Logo */}
            <div className="flex items-center gap-3 px-5 h-16 border-b border-white/[0.06]">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center flex-shrink-0">
                    <Shield size={18} className="text-white" />
                </div>
                {!collapsed && (
                    <span className="text-white font-semibold text-sm tracking-wide whitespace-nowrap">
                        SiteSafeAI
                    </span>
                )}
            </div>

            {/* Nav Items */}
            <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
                {NAV_ITEMS.map(item => {
                    const Icon = item.icon;
                    const active = activeSection === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => onSectionChange(item.id)}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                transition-all duration-200 group
                ${active
                                    ? 'bg-gradient-to-r from-emerald-500/20 to-cyan-500/10 text-emerald-400 shadow-[inset_0_0_0_1px_rgba(52,211,153,0.15)]'
                                    : 'text-white/50 hover:text-white/80 hover:bg-white/[0.04]'
                                }`}
                        >
                            <Icon size={18} className={active ? 'text-emerald-400' : 'text-white/40 group-hover:text-white/60'} />
                            {!collapsed && <span>{item.label}</span>}
                        </button>
                    );
                })}
            </nav>

            {/* Collapse Toggle */}
            <button
                onClick={() => setCollapsed(!collapsed)}
                className="mx-3 mb-4 p-2 rounded-lg text-white/30 hover:text-white/60 hover:bg-white/[0.04] transition-colors"
            >
                {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>
        </aside>
    );
}
