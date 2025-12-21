/**
 * API service - handles all HTTP requests
 */

import { API_URL } from '../constants/config';

export const api = {
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
  }
};