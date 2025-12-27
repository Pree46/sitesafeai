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
      body: JSON.stringify(zone)
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
  }
};

export function LiveStreamTab({ isStreaming, onStart, onStop }) {
  const imgRef = useRef(null);
  const canvasRef = useRef(null);

  // 🔴 ONLY NEW STATE (logic fix)
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

  // 🔴 ONLY CHANGE: force new MJPEG connection
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
        ctx.fillStyle = 'rgba(255,0,0,0.3)';
        ctx.fill();
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 3;
        ctx.stroke();
      }
    });
  };

  return (
    <div className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl space-y-4">
      {!isStreaming ? (
        <button
          onClick={handleStart}
          className="bg-purple-600 hover:bg-purple-700 transition px-8 py-4 rounded-xl text-lg flex items-center gap-3"
        >
          <FileVideo />
          Start Live Detection
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
              {geofenceEnabled ? <Shield className="w-5 h-5" /> : <ShieldOff className="w-5 h-5" />}
              {geofenceEnabled ? 'Geofence Active' : 'Enable Geofence'}
            </button>

            <button
              onClick={onStop}
              className="bg-red-600 hover:bg-red-700 transition py-3 rounded-xl font-semibold"
            >
              Stop Stream
            </button>
          </div>
        </>
      )}
    </div>
  );
}
