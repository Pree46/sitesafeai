import { Upload, AlertTriangle, CheckCircle, FileImage, FileVideo, Loader2, Download } from 'lucide-react';

export function UploadTab({ isUploading, processedResult, onFileChange }) {

  const hasResult = processedResult?.annotated_image || processedResult?.annotated_video;

  const downloadLink =
    processedResult?.annotated_image || processedResult?.annotated_video;

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">

      {/* ================= UPLOAD AREA ================= */}
      {!hasResult && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-10 backdrop-blur-sm text-center transition-all hover:bg-white/[0.07] hover:border-white/20">
          <label className="cursor-pointer flex flex-col items-center gap-4 w-full h-full">

            <div className="w-20 h-20 bg-purple-500/10 rounded-full flex items-center justify-center border border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
              {isUploading ? (
                <Loader2 className="w-10 h-10 text-purple-400 animate-spin" />
              ) : (
                <Upload className="w-10 h-10 text-purple-400" />
              )}
            </div>

            <div className="space-y-2">
              <h3 className="text-xl font-semibold text-white">
                {isUploading ? 'Analyzing Media...' : 'Upload Evidence'}
              </h3>

              <p className="text-gray-400 text-sm max-w-sm mx-auto">
                {isUploading
                  ? 'Our AI is scanning for safety violations. This may take a moment.'
                  : 'Select an image or video file to run a static safety audit.'}
              </p>
            </div>

            {!isUploading && (
              <span className="mt-4 px-6 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium shadow-lg shadow-purple-900/20 transition-all">
                Select File
              </span>
            )}

            <input
              hidden
              type="file"
              accept="image/*,video/*"
              onChange={onFileChange}
              disabled={isUploading}
            />

          </label>
        </div>
      )}

      {/* ================= RESULTS ================= */}
      {hasResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

          {/* ================= MEDIA VIEWER ================= */}
          <div className="lg:col-span-2 bg-black rounded-2xl overflow-hidden border border-white/10 shadow-2xl relative group" style={{minHeight:'3 00px', minWidth:'300px'}}>

            {/* MEDIA TYPE LABEL */}
            <div className="absolute top-4 left-4 z-10 px-3 py-1.5 bg-black/60 backdrop-blur-md rounded-lg border border-white/10 text-xs font-medium text-white flex items-center gap-2">
              {processedResult.annotated_video ? <FileVideo size={14} /> : <FileImage size={14} />}
              {processedResult.annotated_video ? 'PROCESSED VIDEO' : 'PROCESSED IMAGE'}
            </div>

            {/* DOWNLOAD BUTTON */}
            {downloadLink && (
              <a
                href={`http://127.0.0.1:8000${downloadLink}`}
                download
                className="absolute top-4 right-4 z-10 flex items-center gap-2 px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-sm transition-all shadow-lg"
              >
                <Download size={14} />
                Download
              </a>
            )}

            {/* IMAGE RESULT */}
            {processedResult.annotated_image && (
              <img
                src={`http://127.0.0.1:8000${processedResult.annotated_image}`}
                className="w-full h-auto object-contain bg-neutral-900"
                alt="Annotated Result"
              />
            )}

            {/* VIDEO RESULT */}
            {processedResult.annotated_video && (
              <div className="w-full bg-black rounded-2xl overflow-hidden" style={{ minHeight: '300px'}}>
                <video
                key = {processedResult.annotated_video} // Force re-render when video changes
                controls
                autoPlay
                width="100%"
                style={{ 
                  width: '100%', 
                  height: '100%',
                  display: 'block',
                  objectFit: 'cover',
                }}
                crossOrigin='anonymous'
                onLoadStart={() => console.log('Video loading started')}
                onCanPlay={() => console.log('Video can play')}
                onError={(e) => console.log('Video error type:', e.target.error?.code)}
                >
                  <source
                    src={`http://127.0.0.1:8000${processedResult.annotated_video}`}
                    type="video/mp4"
                    />
                    your browser does not support the video tag.
                    </video>
              </div>
            )}

          </div>

          {/* ================= ANALYSIS SIDEBAR ================= */}
          <div className="flex flex-col gap-4">

            {/* STATUS CARD */}
            <div className={`
              p-6 rounded-2xl border backdrop-blur-sm
              ${processedResult.violations?.length
                ? 'bg-rose-500/10 border-rose-500/20'
                : 'bg-emerald-500/10 border-emerald-500/20'}
            `}>

              <div className="flex items-center gap-3 mb-4">

                <div className={`p-3 rounded-full ${processedResult.violations?.length
                    ? 'bg-rose-500/20 text-rose-400'
                    : 'bg-emerald-500/20 text-emerald-400'
                  }`}>

                  {processedResult.violations?.length
                    ? <AlertTriangle size={24} />
                    : <CheckCircle size={24} />}

                </div>

                <div>
                  <h3 className={`font-bold text-lg ${processedResult.violations?.length
                      ? 'text-rose-400'
                      : 'text-emerald-400'
                    }`}>

                    {processedResult.violations?.length
                      ? 'Violations Found'
                      : 'Safety Compliant'}

                  </h3>

                  <p className="text-xs text-white/60 uppercase tracking-wider font-semibold">
                    AI Audit Result
                  </p>
                </div>
              </div>

              {processedResult.violations?.length > 0 ? (
                <div className="space-y-2">

                  <p className="text-sm text-rose-200/80 mb-2">
                    The following issues were detected:
                  </p>

                  <ul className="space-y-2">
                    {processedResult.violations.map((violation, idx) => (
                      <li
                        key={idx}
                        className="flex items-start gap-2 text-sm text-rose-100 bg-rose-500/10 px-3 py-2 rounded-lg border border-rose-500/10"
                      >
                        <span className="mt-1 w-1.5 h-1.5 rounded-full bg-rose-400 shrink-0" />
                        {violation}
                      </li>
                    ))}
                  </ul>

                </div>
              ) : (
                <p className="text-sm text-emerald-200/80">
                  No safety violations were detected in this frame. Good job!
                </p>
              )}

            </div>

            {/* UPLOAD ANOTHER FILE */}
            <label className="
              cursor-pointer
              flex items-center justify-center gap-2 
              w-full py-4 rounded-xl 
              bg-white/5 border border-white/10 
              text-gray-300 font-medium
              hover:bg-purple-600 hover:text-white hover:border-purple-500/50
              transition-all duration-300
            ">
              <Upload size={18} />
              Upload Another File

              <input
                hidden
                type="file"
                accept="image/*,video/*"
                onChange={onFileChange}
                disabled={isUploading}
              />
            </label>

          </div>
        </div>
      )}
    </div>
  );
}