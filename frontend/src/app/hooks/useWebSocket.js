/**
 * WebSocket hook - manages WebSocket connection and alerts
 */

import { useEffect, useRef, useState } from 'react';
import { WS_URL, MAX_ALERTS } from '../constants/config';

export function useWebSocket() {
  const wsRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [alerts, setAlerts] = useState([]);

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
        ...prev.slice(0, MAX_ALERTS - 1),
      ]);
    };

    return () => ws.close();
  }, []);

  return { isConnected, alerts };
}