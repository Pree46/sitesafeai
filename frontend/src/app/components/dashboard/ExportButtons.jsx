'use client';

import { Download, FileText } from 'lucide-react';
import { dashboardApi } from '../../services/dashboardApi';

export function ExportButtons() {
    const handleCsvExport = () => {
        window.open(dashboardApi.exportCsv(), '_blank');
    };

    const handlePdfExport = () => {
        // Print-based PDF export
        window.print();
    };

    return (
        <div className="flex items-center gap-2">
            <button
                onClick={handleCsvExport}
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium
          bg-white/[0.04] border border-white/[0.08] text-white/60
          hover:bg-white/[0.08] hover:text-white/80 transition-all duration-200"
            >
                <Download size={14} />
                Export CSV
            </button>
            <button
                onClick={handlePdfExport}
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium
          bg-white/[0.04] border border-white/[0.08] text-white/60
          hover:bg-white/[0.08] hover:text-white/80 transition-all duration-200"
            >
                <FileText size={14} />
                PDF Report
            </button>
        </div>
    );
}
