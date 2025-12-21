/**
 * Header component - displays app title and status
 */

import { Camera, Activity, Mail } from 'lucide-react';
import { api } from '../services/api';

export function Header({ isConnected }) {
  const requestReport = async () => {
    const data = await api.requestReport();
    alert(`Report sent!\nAlerts included: ${data.count ?? 0}`);
  };

  return (
    <header className="sticky top-0 z-10 backdrop-blur-xl bg-black/40 border-b border-purple-500/20 px-8 py-5 flex justify-between items-center">
      <div className="flex items-center gap-3 text-xl font-bold">
        <Camera className="text-purple-400" />
        SiteSafeAI
      </div>

      <div className="flex items-center gap-6">
        <span
          className={`px-3 py-1 rounded-full text-sm flex items-center gap-2 ${
            isConnected
              ? 'bg-green-500/20 text-green-300'
              : 'bg-red-500/20 text-red-300'
          }`}
        >
          <Activity size={14} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>

        <button
          onClick={requestReport}
          className="bg-purple-600 hover:bg-purple-700 transition px-5 py-2 rounded-lg flex items-center gap-2 shadow-lg"
        >
          <Mail size={16} />
          Email Report
        </button>
      </div>
    </header>
  );
}