/**
 * Tab navigation component - switches between live and upload tabs
 */

import { TABS } from '../constants/config';

export function TabNavigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: TABS.LIVE, label: 'Live Stream' },
    { id: TABS.UPLOAD, label: 'Upload' }
  ];

  return (
    <div className="flex gap-4">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`px-6 py-3 rounded-xl font-medium transition ${
            activeTab === tab.id
              ? 'bg-purple-600 shadow-lg'
              : 'bg-black/40 hover:bg-black/60'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}