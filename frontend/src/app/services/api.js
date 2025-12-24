/**
 * API service - handles all HTTP requests
 */

import { API_URL } from '../constants/config';

export const api = {
  // ===== STREAMING =====
  
  /**
   * Start live streaming
   */
  startStream: async () => {
    return await fetch(`${API_URL}/api/start`, { method: 'POST' });
  },

  /**
   * Stop live streaming
   */
  stopStream: async () => {
    return await fetch(`${API_URL}/api/stop`, { method: 'POST' });
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
      method: 'POST'
    });
    return await res.json();
  },

  /**
   * Disable geofence detection
   */
  disableGeofence: async () => {
    const res = await fetch(`${API_URL}/api/geofence/disable`, {
      method: 'POST'
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
      body: JSON.stringify(zone)
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
      method: 'DELETE'
    });
    return await res.json();
  },

  /**
   * Clear all zones
   */
  clearAllZones: async () => {
    const res = await fetch(`${API_URL}/api/geofence/zones`, {
      method: 'DELETE'
    });
    return await res.json();
  }
};