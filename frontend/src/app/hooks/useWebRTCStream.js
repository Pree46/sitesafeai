// Minimal WebRTC video stream hook (browser as client)
// This is a skeleton; you must handle offer/answer and ICE candidates in production
import { useEffect, useRef } from 'react';

export function useWebRTCStream(videoRef, offerUrl = 'http://localhost:8000/ws/webrtc-offer') {
  useEffect(() => {
    let pc;
    let video = videoRef.current;
    let stopped = false;
    async function start() {
      pc = new window.RTCPeerConnection();
      pc.ontrack = (event) => {
        if (video && event.streams[0]) {
          video.srcObject = event.streams[0];
        }
      };
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      // Send offer to backend
      const res = await fetch(offerUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sdp: pc.localDescription.sdp, type: pc.localDescription.type })
      });
      const answer = await res.json();
      await pc.setRemoteDescription(new window.RTCSessionDescription(answer));
    }
    start();
    return () => {
      stopped = true;
      if (pc) pc.close();
    };
  }, [videoRef, offerUrl]);
}
