/**
 * Application configuration constants
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const WS_URL = API_URL.replace('http', 'ws') + '/ws/alerts';

export const TABS = {
  LIVE: 'live',
  UPLOAD: 'upload'
};

export const MAX_ALERTS = 10;