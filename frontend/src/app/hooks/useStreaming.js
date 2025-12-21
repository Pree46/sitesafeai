/**
 * Streaming hook - manages live stream state and controls
 */

import { useState } from 'react';
import { api } from '../services/api';

export function useStreaming() {
  const [isStreaming, setIsStreaming] = useState(false);

  const startStreaming = async () => {
    try {
      await api.startStream();
      setIsStreaming(true);
    } catch {
      alert('Failed to start live alerts');
    }
  };

  const stopStreaming = async () => {
    try {
      await api.stopStream();
      setIsStreaming(false);
    } catch {
      alert('Failed to stop live alerts');
    }
  };

  return { isStreaming, startStreaming, stopStreaming };
}