/**
 * Alerts sidebar component - displays recent alerts
 */

import { Zap } from 'lucide-react';

export function AlertsSidebar({ alerts }) {
  return (
    <aside className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl">
      <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Zap className="text-purple-400" />
        Alerts
      </h2>

      {alerts.length === 0 && (
        <p className="text-gray-400">No alerts yet</p>
      )}

      <div className="space-y-3 max-h-[70vh] overflow-y-auto">
        {alerts.map(alert => (
          <div
            key={alert.id}
            className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-sm"
          >
            <span className="text-red-300 font-semibold">
              [{alert.timestamp}]
            </span>{' '}
            {alert.message}
          </div>
        ))}
      </div>
    </aside>
  );
}