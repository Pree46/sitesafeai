/**
 * Application configuration constants
 */

const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
export const API_URL = process.env.NEXT_PUBLIC_API_URL || `http://${hostname}:8000`;
export const WS_URL = API_URL.replace('http', 'ws') + '/ws/alerts';

export const TABS = {
  DASHBOARD: 'dashboard',
  LIVE: 'live',
  UPLOAD: 'upload'
};

export const MAX_ALERTS = 10;