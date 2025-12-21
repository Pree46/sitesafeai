/**
 * Upload tab component - handles file uploads and displays results
 */

import { Upload, AlertTriangle, CheckCircle } from 'lucide-react';

export function UploadTab({ isUploading, processedResult, onFileChange }) {
  return (
    <div className="bg-black/40 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 shadow-xl space-y-4">
      <label className="cursor-pointer flex items-center gap-3 bg-purple-600 hover:bg-purple-700 transition px-6 py-4 rounded-xl w-fit">
        <Upload />
        Upload Image / Video
        <input
          hidden
          type="file"
          accept="image/*,video/*"
          onChange={onFileChange}
        />
      </label>

      {isUploading && <p className="text-purple-300">Processing…</p>}

      {processedResult?.annotated_image && (
        <img
          src={processedResult.annotated_image}
          className="rounded-xl border w-full"
          alt="Annotated"
        />
      )}

      {processedResult?.annotated_video && (
        <video
          key={processedResult.annotated_video}
          src={processedResult.annotated_video}
          controls
          preload="metadata"
          playsInline
          className="rounded-xl border w-full"
        />
      )}

      {processedResult?.violations && (
        <div
          className={`flex items-center gap-2 text-lg ${
            processedResult.violations.length
              ? 'text-red-400'
              : 'text-green-400'
          }`}
        >
          {processedResult.violations.length ? (
            <AlertTriangle />
          ) : (
            <CheckCircle />
          )}
          {processedResult.violations.length
            ? processedResult.violations.join(', ')
            : 'No violations detected'}
        </div>
      )}
    </div>
  );
}