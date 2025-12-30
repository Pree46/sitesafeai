import { Activity, Upload } from 'lucide-react';
import { TABS } from '../constants/config';

export function TabNavigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: TABS.LIVE, label: 'Live Monitoring', icon: Activity },
    { id: TABS.UPLOAD, label: 'Upload & Analyze', icon: Upload }
  ];

  return (
    // OUTER WRAPPER: Handles alignment with Header
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      
      {/* INNER CONTAINER 
         gap-2: Adds space BETWEEN the buttons
         p-1.5: Adds slightly more padding around the group
      */}
      <div className="inline-flex items-center p-1.5 gap-2 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
        {tabs.map(tab => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                relative flex items-center gap-2 
                px-5 py-2
                rounded-lg 
                text-sm font-medium 
                transition-all duration-200
                focus:outline-none
                ${
                  isActive
                    ? 'bg-purple-500/20 text-purple-300 shadow-sm ring-1 ring-inset ring-purple-500/50'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                }
              `}
            >
              <Icon size={16} className={isActive ? 'text-purple-400' : 'text-gray-500'} />
              {tab.label}
            </button>
          );
        })}
      </div>
      
    </div>
  );
}