import { Camera, Mail } from 'lucide-react';
import { api } from '../services/api';

export function Header({ isConnected }) {
  const requestReport = async () => {
    const data = await api.requestReport();
    alert(`Report sent!\nAlerts included: ${data.count ?? 0}`);
  };

  return (
    <header
      className="
        sticky top-0 z-50
        w-full
        bg-black/80 backdrop-blur-md
        border-b border-white/10
      "
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* LEFT: Branding */}
          <div className="flex items-center gap-3">
            <div className="
              flex items-center justify-center 
              w-9 h-9 
              rounded-lg
              bg-purple-500/10
              border border-purple-500/20
            ">
              <Camera className="text-purple-400 w-5 h-5" />
            </div>

            <span className="text-xl font-bold tracking-tight text-white">
              SiteSafe<span className="text-purple-400">AI</span>
            </span>
          </div>

          {/* RIGHT: Actions */}
          <div className="flex items-center gap-4">
            
            {/* Status Indicator */}
            <div className="flex items-center gap-2 px-2">
               <span className="relative flex h-2 w-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isConnected ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${isConnected ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
              </span>
              <span className={`text-sm font-medium ${isConnected ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isConnected ? 'System Online' : 'Offline'}
              </span>
            </div>

            {/* Vertical Divider */}
            <div className="h-6 w-px bg-white/10 mx-1"></div>

            {/* NEW BUTTON STYLE: "Ghost Tech" */}
            <button
              onClick={requestReport}
              className="
                group
                relative
                flex items-center gap-2
                px-4 py-2
                rounded-md
                border border-white/10
                bg-white/5
                text-gray-300
                hover:text-white
                hover:bg-purple-600/20
                hover:border-purple-500/50
                transition-all duration-200
              "
            >
              <Mail 
                size={16} 
                className="text-gray-400 group-hover:text-purple-300 transition-colors" 
              />
              <span className="text-sm font-medium">
                Email Report
              </span>
            </button>
            
          </div>
        </div>
      </div>
    </header>
  );
}