/**
 * Live stream tab component - displays live video feed
 */

import { FileVideo } from 'lucide-react';
import { API_URL } from '../constants/config';

export function LiveStreamTab({ isStreaming, onStart, onStop }) {
  return (
    <div className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl space-y-4">
      {!isStreaming ? (
        <button
          onClick={onStart}
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
            onClick={onStop}
            className="w-full bg-red-600 hover:bg-red-700 transition py-3 rounded-xl"
          >
            Stop Stream
          </button>
        </>
      )}
    </div>
  );
}