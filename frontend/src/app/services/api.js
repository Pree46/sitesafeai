/**
 * API service - handles all HTTP requests
 */

import { API_URL } from '../constants/config';

// 🔴 Holds reference to <img> element showing MJPEG stream
let streamImgElement = null;

export const api = {
  // ===== STREAMING =====

  /**
   * Attach the <img> element used for MJPEG streaming
   * Call this ONCE when component mounts
   */
  attachStreamElement: (imgElement) => {
    streamImgElement = imgElement;
  },

  /**
   * Start live streaming
   */
  startStream: async () => {
    // 1️⃣ Tell backend to start camera + inference
    await fetch(`${API_URL}/api/start`, { method: 'POST' });

    // 2️⃣ Open a NEW MJPEG stream connection
    if (streamImgElement) {
      streamImgElement.src = `${API_URL}/api/stream?ts=${Date.now()}`;
    }
  },

  /**
   * Stop live streaming
   */
  stopStream: async () => {
    // 1️⃣ CLOSE MJPEG stream (MOST IMPORTANT)
    if (streamImgElement) {
      streamImgElement.src = '';
    }

    // 2️⃣ Tell backend to stop camera
    await fetch(`${API_URL}/api/stop`, { method: 'POST' });
  },

  // ===== FILE UPLOAD =====

  /**
   * Upload file (image or video)
   */
  uploadFile: async (file, endpoint) => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
    });

    return await res.json();
  },

  /**
   * Request email report
   */
  requestReport: async () => {
    const res = await fetch(`${API_URL}/api/report`);
    return await res.json();
  },

  // ===== GEOFENCING =====

  /**
   * Enable geofence detection
   */
  enableGeofence: async () => {
    const res = await fetch(`${API_URL}/api/geofence/enable`, {
      method: 'POST',
    });
    return await res.json();
  },

  /**
   * Disable geofence detection
   */
  disableGeofence: async () => {
    const res = await fetch(`${API_URL}/api/geofence/disable`, {
      method: 'POST',
    });
    return await res.json();
  },

  /**
   * Get geofence status
   */
  getGeofenceStatus: async () => {
    const res = await fetch(`${API_URL}/api/geofence/status`);
    return await res.json();
  },

  /**
   * Save a geofence zone
   */
  saveZone: async (zone) => {
    const res = await fetch(`${API_URL}/api/geofence/zones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(zone),
    });
    return await res.json();
  },

  /**
   * Get all zones
   */
  getZones: async () => {
    const res = await fetch(`${API_URL}/api/geofence/zones`);
    return await res.json();
  },

  /**
   * Delete a specific zone
   */
  deleteZone: async (zoneName) => {
    const res = await fetch(`${API_URL}/api/geofence/zones/${zoneName}`, {
      method: 'DELETE',
    });
    return await res.json();
  },

  /**
   * Clear all zones
   */
  clearAllZones: async () => {
    const res = await fetch(`${API_URL}/api/geofence/zones`, {
      method: 'DELETE',
    });
    return await res.json();
  },
};
