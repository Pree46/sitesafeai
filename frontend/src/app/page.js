'use client';

/**
 * Main page component - orchestrates all child components
 */

import { useState } from 'react';
import { TABS } from './constants/config';

// Hooks
import { useWebSocket } from './hooks/useWebSocket';
import { useStreaming } from './hooks/useStreaming';
import { useFileUpload } from './hooks/useFileUpload';

// Components
import { Header } from './components/Header';
import { TabNavigation } from './components/TabNavigation';
import { LiveStreamTab } from './components/LiveStreamTab';
import { UploadTab } from './components/UploadTab';
import { AlertsSidebar } from './components/AlertsSidebar';

export default function SiteSafeAI() {
  const [activeTab, setActiveTab] = useState(TABS.LIVE);

  // Custom hooks for business logic
  const { isConnected, alerts } = useWebSocket();
  const { isStreaming, startStreaming, stopStreaming } = useStreaming();
  const { processedResult, isUploading, handleFileUpload } = useFileUpload();

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#3b0764] to-[#0f172a] text-white">
      <Header isConnected={isConnected} />

      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <section className="lg:col-span-2 space-y-6">
          <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

          {activeTab === TABS.LIVE && (
            <LiveStreamTab
              isStreaming={isStreaming}
              onStart={startStreaming}
              onStop={stopStreaming}
            />
          )}

          {activeTab === TABS.UPLOAD && (
            <UploadTab
              isUploading={isUploading}
              processedResult={processedResult}
              onFileChange={handleFileUpload}
            />
          )}
        </section>

        <AlertsSidebar alerts={alerts} />
      </main>
    </div>
  );
}