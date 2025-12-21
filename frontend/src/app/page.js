'use client';

import { useEffect, useRef, useState } from 'react';
import {
  Camera,
  Upload,
  AlertTriangle,
  CheckCircle,
  FileVideo,
  Activity,
  Mail,
  Zap
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace('http', 'ws') + '/ws/alerts';

export default function SiteSafeAI() {
  const wsRef = useRef(null);

  const [isStreaming, setIsStreaming] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  const [processedResult, setProcessedResult] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('live');

  // ================= WEBSOCKET =================
  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setAlerts(prev => [
        {
          id: Date.now(),
          message: data.message,
          timestamp: data.timestamp,
        },
        ...prev.slice(0, 9),
      ]);
    };

    return () => ws.close();
  }, []);

  // ================= STREAM CONTROL =================
  const startStreaming = async () => {
    try {
      await fetch(`${API_URL}/api/start`, { method: 'POST' });
      setIsStreaming(true);
    } catch {
      alert('Failed to start live alerts');
    }
  };

  const stopStreaming = async () => {
    try {
      await fetch(`${API_URL}/api/stop`, { method: 'POST' });
      setIsStreaming(false);
    } catch {
      alert('Failed to stop live alerts');
    }
  };

  // ================= UPLOAD =================
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setProcessedResult(null);
    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    const endpoint = file.type.startsWith('video')
      ? '/api/upload/video'
      : '/api/upload';

    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setProcessedResult(data);
    } catch {
      alert('Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  // ================= REPORT =================
  const requestReport = async () => {
    const res = await fetch(`${API_URL}/api/report`);
    const data = await res.json();
    alert(`Report sent!\nAlerts included: ${data.count ?? 0}`);
  };

  // ================= UI =================
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#3b0764] to-[#0f172a] text-white">
      {/* HEADER */}
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

      {/* MAIN */}
      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* LEFT */}
        <section className="lg:col-span-2 space-y-6">
          {/* TABS */}
          <div className="flex gap-4">
            {['live', 'upload'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-3 rounded-xl font-medium transition ${
                  activeTab === tab
                    ? 'bg-purple-600 shadow-lg'
                    : 'bg-black/40 hover:bg-black/60'
                }`}
              >
                {tab === 'live' ? 'Live Stream' : 'Upload'}
              </button>
            ))}
          </div>

          {/* LIVE STREAM */}
          {activeTab === 'live' && (
            <div className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl space-y-4">
              {!isStreaming ? (
                <button
                  onClick={startStreaming}
                  className="bg-purple-600 hover:bg-purple-700 transition px-8 py-4 rounded-xl text-lg flex items-center gap-3"
                >
                  <FileVideo />
                  Start Live Detection
                </button>
              ) : (
                <>
                  <img
                    src={`${API_URL}/api/stream`}
                    className="w-full rounded-xl border aspect-video object-cover"
                    alt="Live Stream"
                  />
                  <button
                    onClick={stopStreaming}
                    className="w-full bg-red-600 hover:bg-red-700 transition py-3 rounded-xl"
                  >
                    Stop Stream
                  </button>
                </>
              )}
            </div>
          )}

          {/* UPLOAD */}
          {activeTab === 'upload' && (
            <div className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl space-y-4">
              <label className="cursor-pointer flex items-center gap-3 bg-purple-600 hover:bg-purple-700 transition px-6 py-4 rounded-xl w-fit">
                <Upload />
                Upload Image / Video
                <input
                  hidden
                  type="file"
                  accept="image/*,video/*"
                  onChange={handleFileUpload}
                />
              </label>

              {isUploading && <p className="text-purple-300">Processing…</p>}

              {processedResult?.annotated_image && (
                <img
                  src={processedResult.annotated_image}
                  className="rounded-xl border w-full"
                  alt="Annotated"
                />
              )}

              {processedResult?.annotated_video && (
                <video
                  key={processedResult.annotated_video}
                  src={processedResult.annotated_video}
                  controls
                  preload="metadata"
                  playsInline
                  className="rounded-xl border w-full"
                />
              )}

              {processedResult?.violations && (
                <div
                  className={`flex items-center gap-2 text-lg ${
                    processedResult.violations.length
                      ? 'text-red-400'
                      : 'text-green-400'
                  }`}
                >
                  {processedResult.violations.length ? (
                    <AlertTriangle />
                  ) : (
                    <CheckCircle />
                  )}
                  {processedResult.violations.length
                    ? processedResult.violations.join(', ')
                    : 'No violations detected'}
                </div>
              )}
            </div>
          )}
        </section>

        {/* ALERTS */}
        <aside className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap className="text-purple-400" />
            Alerts
          </h2>

          {alerts.length === 0 && (
            <p className="text-gray-400">No alerts yet</p>
          )}

          <div className="space-y-3 max-h-[70vh] overflow-y-auto">
            {alerts.map(a => (
              <div
                key={a.id}
                className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-sm"
              >
                <span className="text-red-300 font-semibold">
                  [{a.timestamp}]
                </span>{' '}
                {a.message}
              </div>
            ))}
          </div>
        </aside>
      </main>
    </div>
  );
}
