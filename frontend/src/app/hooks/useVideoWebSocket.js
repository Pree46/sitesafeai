import { useEffect, useRef } from 'react';

// Usage: <canvas ref={canvasRef} width={640} height={480} />
export function useVideoWebSocket(canvasRef, wsUrl = 'ws://localhost:8000/ws/video') {
  useEffect(() => {
    if (!canvasRef.current) return;
    const ws = new window.WebSocket(wsUrl);
    ws.binaryType = 'arraybuffer';
    const ctx = canvasRef.current.getContext('2d');
    let img = new window.Image();
    img.onload = () => {
      ctx.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
    };
    ws.onmessage = (event) => {
      const blob = new window.Blob([event.data], { type: 'image/jpeg' });
      img.src = URL.createObjectURL(blob);
    };
    return () => {
      ws.close();
    };
  }, [canvasRef, wsUrl]);
}
