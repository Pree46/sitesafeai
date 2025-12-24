/**
 * Alerts sidebar component - displays recent alerts with type distinction
 */

import { Zap, ShieldAlert, AlertTriangle } from 'lucide-react';

export function AlertsSidebar({ alerts }) {
  return (
    <aside className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl">
      <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Zap className="text-purple-400" />
        Alerts
      </h2>

      {alerts.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-400 text-sm">No alerts yet</p>
          <p className="text-gray-500 text-xs mt-2">
            Alerts will appear here when violations are detected
          </p>
        </div>
      )}

      <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-2">
        {alerts.map(alert => {
          // Determine alert type
          const isGeofence = alert.type === 'geofence' || 
                            alert.message.toLowerCase().includes('zone violation');
          const isPPE = alert.type === 'ppe' || 
                       alert.message.toLowerCase().includes('ppe');
          
          return (
            <div
              key={alert.id}
              className={`
                ${isGeofence 
                  ? 'bg-red-500/10 border-red-500/40 hover:bg-red-500/15' 
                  : 'bg-orange-500/10 border-orange-500/40 hover:bg-orange-500/15'
                }
                border rounded-lg p-3.5 text-sm transition-colors
              `}
            >
              <div className="flex items-start gap-2.5">
                {/* Icon */}
                <div className="flex-shrink-0 mt-0.5">
                  {isGeofence ? (
                    <ShieldAlert className="text-red-400 w-5 h-5" />
                  ) : (
                    <AlertTriangle className="text-orange-400 w-5 h-5" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className={`font-mono font-semibold text-xs ${
                      isGeofence ? 'text-red-300' : 'text-orange-300'
                    }`}>
                      {alert.timestamp}
                    </span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      isGeofence 
                        ? 'bg-red-500/20 text-red-300' 
                        : 'bg-orange-500/20 text-orange-300'
                    }`}>
                      {isGeofence ? 'GEOFENCE' : 'PPE'}
                    </span>
                  </div>
                  
                  <p className="text-gray-200 text-sm leading-relaxed break-words">
                    {alert.message}
                  </p>

                  {/* Additional zone info for geofence alerts */}
                  {isGeofence && alert.zone && (
                    <div className="mt-2 text-xs text-gray-400">
                      Zone: <span className="text-red-300 font-medium">{alert.zone}</span>
                      {alert.object && (
                        <> • Object: <span className="text-red-300 font-medium">{alert.object}</span></>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Alert Summary */}
      {alerts.length > 0 && (
        <div className="mt-4 pt-4 border-t border-purple-500/20">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Total Alerts: {alerts.length}</span>
            <div className="flex gap-3">
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                PPE: {alerts.filter(a => a.type === 'ppe' || a.message.includes('PPE')).length}
              </span>
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                Geofence: {alerts.filter(a => a.type === 'geofence' || a.message.includes('Zone violation')).length}
              </span>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}