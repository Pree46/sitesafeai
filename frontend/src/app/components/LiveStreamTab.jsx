import { useState, useRef, useEffect } from 'react';
import { FileVideo, Shield, ShieldOff, Trash2, Save, X, RotateCcw, PenTool } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000';

const api = {
  enableGeofence: async () => {
    const res = await fetch(`${API_URL}/api/geofence/enable`, { method: 'POST' });
    return await res.json();
  },
  disableGeofence: async () => {
    const res = await fetch(`${API_URL}/api/geofence/disable`, { method: 'POST' });
    return await res.json();
  },
  getGeofenceStatus: async () => {
    const res = await fetch(`${API_URL}/api/geofence/status`);
    return await res.json();
  },
  saveZone: async (zone) => {
    const res = await fetch(`${API_URL}/api/geofence/zones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(zone),
    });
    return await res.json();
  },
  getZones: async () => {
    const res = await fetch(`${API_URL}/api/geofence/zones`);
    return await res.json();
  },
  clearAllZones: async () => {
    const res = await fetch(`${API_URL}/api/geofence/zones`, { method: 'DELETE' });
    return await res.json();
  },
};

export function LiveStreamTab({ isStreaming, onStart, onStop }) {
  const imgRef = useRef(null);
  const canvasRef = useRef(null);

  // 🔑 MJPEG reconnect fix
  const [streamKey, setStreamKey] = useState(Date.now());

  const [geofenceEnabled, setGeofenceEnabled] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);
  const [points, setPoints] = useState([]);
  const [zones, setZones] = useState([]);
  const [zoneName, setZoneName] = useState('');

  useEffect(() => {
    loadZones();
    checkGeofenceStatus();
  }, []);

  useEffect(() => {
    if (isStreaming) {
      const interval = setInterval(drawOverlay, 100);
      return () => clearInterval(interval);
    }
  }, [points, zones, isStreaming]);

  const handleStart = async () => {
    await onStart();
    setStreamKey(Date.now());
  };

  const loadZones = async () => {
    const data = await api.getZones();
    setZones(data.zones || []);
  };

  const checkGeofenceStatus = async () => {
    const data = await api.getGeofenceStatus();
    setGeofenceEnabled(data.enabled);
  };

  const toggleGeofence = async () => {
    if (geofenceEnabled) {
      await api.disableGeofence();
      setGeofenceEnabled(false);
    } else {
      await api.enableGeofence();
      setGeofenceEnabled(true);
    }
  };

  const handleCanvasClick = (e) => {
    if (!isDrawing) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    setPoints([...points, [x, y]]);
  };

  const drawOverlay = () => {
    const canvas = canvasRef.current;
    const img = imgRef.current;
    if (!canvas || !img || !img.naturalWidth) return;

    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    zones.forEach(zone => {
      if (zone.points?.length > 2) {
        ctx.beginPath();
        ctx.moveTo(zone.points[0][0], zone.points[0][1]);
        zone.points.forEach(([x, y]) => ctx.lineTo(x, y));
        ctx.closePath();

        const [r, g, b] = zone.color || [255, 0, 0];
        ctx.fillStyle = `rgba(${r},${g},${b},${zone.alpha || 0.3})`;
        ctx.fill();
        ctx.strokeStyle = `rgb(${r},${g},${b})`;
        ctx.lineWidth = 3;
        ctx.stroke();

        const text = zone.name;
        ctx.font = 'bold 16px sans-serif';
        const metrics = ctx.measureText(text);
        const tx = zone.points[0][0];
        const ty = zone.points[0][1] - 10;

        ctx.fillStyle = 'rgba(0,0,0,0.7)';
        ctx.fillRect(tx - 5, ty - 20, metrics.width + 10, 25);
        ctx.fillStyle = 'white';
        ctx.fillText(text, tx, ty);
      }
    });

    if (points.length > 0) {
      ctx.beginPath();
      ctx.moveTo(points[0][0], points[0][1]);

      points.forEach(([x, y], idx) => {
        ctx.lineTo(x, y);
        ctx.fillStyle = 'yellow';
        ctx.fillRect(x - 4, y - 4, 8, 8);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 12px sans-serif';
        ctx.fillText(String(idx + 1), x + 8, y - 8);
      });

      if (points.length > 2) ctx.closePath();
      ctx.strokeStyle = 'yellow';
      ctx.lineWidth = 3;
      ctx.setLineDash([5, 5]);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  };

  const saveZone = async () => {
    if (points.length < 3 || !zoneName.trim()) return;

    await api.saveZone({
      name: zoneName,
      points,
      color: [255, 0, 0],
      alpha: 0.3,
    });

    await loadZones();
    setPoints([]);
    setZoneName('');
    setIsDrawing(false);
  };

  const clearDrawing = () => {
    setPoints([]);
    setZoneName('');
    setIsDrawing(false);
  };

  const deleteAllZones = async () => {
    if (!confirm('⚠️ Delete all zones?')) return;
    await api.clearAllZones();
    await loadZones();
  };

  return (
    <div className="w-full max-w-7xl mx-auto">
      {!isStreaming ? (
        <div className="flex flex-col items-center justify-center min-h-[400px] bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm p-8 text-center space-y-6">
          <div className="w-20 h-20 bg-purple-500/10 rounded-full flex items-center justify-center border border-purple-500/20">
            <FileVideo className="w-10 h-10 text-purple-400" />
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-semibold text-white">Ready to Monitor</h3>
            <p className="text-gray-400 max-w-md mx-auto">
              Start the live stream to detect safety violations and manage geofence zones in real-time.
            </p>
          </div>
          <button
            onClick={handleStart}
            className="
              group relative overflow-hidden
              bg-purple-600 hover:bg-purple-500
              text-white font-semibold
              px-8 py-3 rounded-xl
              transition-all duration-300
              shadow-[0_0_20px_rgba(147,51,234,0.3)]
              hover:shadow-[0_0_30px_rgba(147,51,234,0.5)]
            "
          >
            <span className="relative z-10 flex items-center gap-2">
              <FileVideo size={20} /> Start Live Detection
            </span>
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* MAIN VIDEO FEED CONTAINER */}
          <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-black">
            {/* Header / Status Bar over Video */}
            <div className="absolute top-4 left-4 z-10 flex gap-2">
              <div className="px-3 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 flex items-center gap-2 text-xs font-medium text-red-400">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                </span>
                LIVE FEED
              </div>
              {geofenceEnabled && (
                <div className="px-3 py-1 rounded-full bg-green-900/60 backdrop-blur-md border border-green-500/30 flex items-center gap-2 text-xs font-medium text-green-400">
                  <Shield size={12} /> GEOFENCE ACTIVE
                </div>
              )}
            </div>

            <img
              key={streamKey}
              ref={imgRef}
              src={`${API_URL}/api/stream?ts=${streamKey}`}
              className="w-full aspect-video object-contain bg-neutral-900"
              alt="Live Stream"
              onLoad={drawOverlay}
            />
            <canvas
              ref={canvasRef}
              onClick={handleCanvasClick}
              className={`absolute top-0 left-0 w-full h-full ${
                isDrawing ? 'cursor-crosshair' : 'cursor-default'
              }`}
              style={{ pointerEvents: isDrawing ? 'auto' : 'none' }}
            />
          </div>

          {/* CONTROLS GRID */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* LEFT: Stream Controls */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm space-y-4 h-fit">
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Stream Controls</h3>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={toggleGeofence}
                  className={`
                    flex flex-col items-center justify-center gap-2 p-4 rounded-lg border transition-all duration-200
                    ${geofenceEnabled 
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20' 
                      : 'bg-white/5 border-white/5 text-gray-400 hover:border-white/20 hover:text-white'
                    }
                  `}
                >
                  {geofenceEnabled ? <Shield size={24} /> : <ShieldOff size={24} />}
                  <span className="text-xs font-semibold">{geofenceEnabled ? 'Active' : 'Enable Geofence'}</span>
                </button>

                <button
                  onClick={onStop}
                  className="
                    flex flex-col items-center justify-center gap-2 p-4 rounded-lg
                    bg-rose-500/10 border border-rose-500/20 text-rose-400
                    hover:bg-rose-500/20 hover:border-rose-500/40
                    transition-all duration-200
                  "
                >
                  <div className="w-6 h-6 rounded-md bg-rose-500/20 flex items-center justify-center">
                    <div className="w-2.5 h-2.5 bg-current rounded-sm" />
                  </div>
                  <span className="text-xs font-semibold">Stop Stream</span>
                </button>
              </div>
            </div>

            {/* RIGHT: Geofence Editor (Spans 2 cols) */}
            <div className="lg:col-span-2 bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm flex flex-col justify-between">
              
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-purple-500/20 rounded-lg">
                    <PenTool size={16} className="text-purple-400" />
                  </div>
                  <h3 className="text-sm font-semibold text-white">
                    Zone Editor <span className="text-gray-500 font-normal ml-1">({zones.length} active)</span>
                  </h3>
                </div>
                
                {zones.length > 0 && !isDrawing && (
                  <button
                    onClick={deleteAllZones}
                    className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1.5 px-2 py-1 hover:bg-rose-500/10 rounded transition-colors"
                  >
                    <Trash2 size={12} /> Clear All
                  </button>
                )}
              </div>

              {/* Drawing UI */}
              {!isDrawing ? (
                <div className="flex-1 flex items-center justify-center border-2 border-dashed border-white/10 rounded-lg bg-black/20 p-6">
                  <button
                    onClick={() => setIsDrawing(true)}
                    className="
                      flex items-center gap-2 px-5 py-2.5 
                      bg-purple-600 text-white rounded-lg 
                      hover:bg-purple-500 transition-colors shadow-lg shadow-purple-900/20
                    "
                  >
                    <PenTool size={16} /> Draw New Zone
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Instructions */}
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm">
                    <span className="mt-0.5">💡</span>
                    <p>Click points on the video feed to define a polygon. You need at least <strong>3 points</strong> to save.</p>
                  </div>

                  {/* Input & Actions */}
                  <div className="flex flex-col sm:flex-row gap-3">
                    <div className="flex-1 relative">
                      <input
                        value={zoneName}
                        onChange={(e) => setZoneName(e.target.value)}
                        placeholder="Enter Zone Name (e.g., 'Restricted Area')"
                        className="
                          w-full h-full min-h-[42px]
                          bg-black/40 border border-white/10 rounded-lg 
                          px-4 text-sm text-white placeholder:text-gray-500
                          focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/50
                        "
                      />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
                        {points.length} pts
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={saveZone}
                        disabled={points.length < 3 || !zoneName.trim()}
                        className="
                          h-[42px] px-8 rounded-lg bg-emerald-600 text-white text-sm font-medium
                          hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed
                          flex items-center gap-1 transition-colors
                        "
                      >
                        <Save size={16} /> Save
                      </button>

                      <button
                        onClick={() => setPoints(points.slice(0, -1))}
                        disabled={points.length === 0}
                        className="
                          h-[42px] w-[42px] flex items-center justify-center rounded-lg 
                          bg-white/5 border border-white/10 text-gray-300
                          hover:bg-white/10 hover:text-white disabled:opacity-30
                          transition-colors
                        "
                        title="Undo last point"
                      >
                        <RotateCcw size={16} />
                      </button>

                      <button
                        onClick={clearDrawing}
                        className="
                          h-[42px] w-[42px] flex items-center justify-center rounded-lg 
                          bg-white/5 border border-white/10 text-gray-300
                          hover:bg-rose-500/20 hover:border-rose-500/30 hover:text-rose-400
                          transition-colors
                        "
                        title="Cancel"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}