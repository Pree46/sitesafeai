/**
 * File upload hook - manages file upload state and logic
 */

import { useState } from 'react';
import { api } from '../services/api';

export function useFileUpload() {
  const [processedResult, setProcessedResult] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setProcessedResult(null);
    setIsUploading(true);

    const endpoint = file.type.startsWith('video')
      ? '/api/upload/video'
      : '/api/upload';

    try {
      const data = await api.uploadFile(file, endpoint);
      setProcessedResult(data);
    } catch {
      alert('Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return { processedResult, isUploading, handleFileUpload };
}