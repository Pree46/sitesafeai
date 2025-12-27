import { useState, useRef, useEffect } from 'react';
import { FileVideo, Shield, ShieldOff, Trash2, Save, X } from 'lucide-react';

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
    <div className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl space-y-4">
      {!isStreaming ? (
        <button
          onClick={handleStart}
          className="bg-purple-600 hover:bg-purple-700 transition px-8 py-4 rounded-xl text-lg flex items-center gap-3"
        >
          <FileVideo /> Start Live Detection
        </button>
      ) : (
        <>
          <div className="relative bg-black rounded-xl overflow-hidden">
            <img
              key={streamKey}
              ref={imgRef}
              src={`${API_URL}/api/stream?ts=${streamKey}`}
              className="w-full aspect-video object-contain"
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

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={toggleGeofence}
              className={`${
                geofenceEnabled
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-gray-600 hover:bg-gray-700'
              } transition py-3 rounded-xl flex items-center justify-center gap-2 font-semibold`}
            >
              {geofenceEnabled ? <Shield /> : <ShieldOff />}
              {geofenceEnabled ? 'Geofence Active' : 'Enable Geofence'}
            </button>

            <button
              onClick={onStop}
              className="bg-red-600 hover:bg-red-700 transition py-3 rounded-xl font-semibold"
            >
              Stop Stream
            </button>
          </div>

          {/* ZONE PANEL */}
          <div className="border-t border-purple-500/20 pt-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-purple-300">
                Geofence Zones {zones.length > 0 && `(${zones.length})`}
              </h3>
              {zones.length > 0 && !isDrawing && (
                <button
                  onClick={deleteAllZones}
                  className="text-xs text-red-400 hover:text-red-300 transition flex items-center gap-1"
                >
                  <Trash2 className="w-3 h-3" /> Clear All
                </button>
              )}
            </div>

            {!isDrawing ? (
              <button
                onClick={() => setIsDrawing(true)}
                className="w-full bg-purple-600 hover:bg-purple-700 transition py-2.5 rounded-lg text-sm font-medium"
              >
                + Draw New Zone
              </button>
            ) : (
              <div className="space-y-3 bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
                <input
                  value={zoneName}
                  onChange={(e) => setZoneName(e.target.value)}
                  placeholder="Zone Name"
                  className="w-full bg-black/50 border border-purple-500/30 rounded-lg px-3 py-2 text-sm"
                />

                <div className="text-xs text-gray-400">
                  <span className="font-semibold text-yellow-400">
                    {points.length}
                  </span>{' '}
                  points drawn
                  {points.length < 3 && (
                    <span className="text-red-400"> (min 3 required)</span>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={saveZone}
                    disabled={points.length < 3 || !zoneName.trim()}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-1"
                  >
                    <Save className="w-4 h-4" /> Save
                  </button>

                  <button
                    onClick={clearDrawing}
                    className="bg-gray-600 hover:bg-gray-700 transition py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-1"
                  >
                    <X className="w-4 h-4" /> Cancel
                  </button>

                  <button
                    onClick={() => setPoints(points.slice(0, -1))}
                    disabled={points.length === 0}
                    className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition py-2 rounded-lg text-sm font-medium"
                  >
                    Undo
                  </button>
                </div>

                <p className="text-xs text-gray-400 italic">
                  💡 Click on the video to add points. Create a polygon by clicking at least 3 points.
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
