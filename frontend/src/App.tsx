import React, { useState, useEffect, useCallback } from 'react';
import { api } from './services/api';
import { NavWorkspace, SystemMode, EvidenceItem } from './types/forensic';
import { INITIAL_EVIDENCE_ITEMS } from './data/sampleEvidence';

import { TopBar } from './components/shell/TopBar';
import { Sidebar } from './components/shell/Sidebar';
import { HotkeysModal } from './components/shell/HotkeysModal';

import { SituationRoomView } from './components/views/SituationRoomView';
import { LiveMonitoringView } from './components/views/LiveMonitoringView';
import { CamerasView } from './components/views/CamerasView';
import { EventsView } from './components/views/EventsView';
import { EnhancementLabView } from './components/views/EnhancementLabView';
import { InvestigationView } from './components/views/InvestigationView';
import { AnalyticsView } from './components/views/AnalyticsView';
import { EvidenceView } from './components/views/EvidenceView';
import { ReportsView } from './components/views/ReportsView';
import { SystemStatusView } from './components/views/SystemStatusView';
import { SecurityView } from './components/views/SecurityView';
import { SettingsView } from './components/views/SettingsView';

export default function App() {
  const [currentWorkspace, setCurrentWorkspace] = useState<NavWorkspace>('situation_room');
  const [systemMode, setSystemMode] = useState<SystemMode>('LIVE');
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [isHotkeysOpen, setIsHotkeysOpen] = useState<boolean>(false);
  const [selectedTrackId, setSelectedTrackId] = useState<number>(1);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>(INITIAL_EVIDENCE_ITEMS);

  // Poll backend health & load persistent evidence
  useEffect(() => {
    const check = () => {
      api.checkHealth().then((res) => {
        setIsBackendOnline(res.online);
      });
    };
    check();
    const interval = setInterval(check, 10000);

    // Initial load of sealed evidence from SQLite repository
    api.getEvidenceList().then((res) => {
      if (res.evidence && res.evidence.length > 0) {
        setEvidenceList(res.evidence);
      }
    });

    return () => clearInterval(interval);
  }, []);

  // Global Keyboard Navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Ignore key events when typing inside inputs
      const tag = (e.target as HTMLElement)?.tagName?.toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

      if (e.key === 'Escape') {
        setIsHotkeysOpen(false);
        return;
      }

      if (e.key === '?' || (e.key === '/' && e.shiftKey)) {
        e.preventDefault();
        setIsHotkeysOpen((prev) => !prev);
        return;
      }

      switch (e.key.toLowerCase()) {
        case '1':
          setCurrentWorkspace('situation_room');
          break;
        case '2':
          setCurrentWorkspace('live_monitoring');
          break;
        case '3':
          setCurrentWorkspace('cameras');
          break;
        case '4':
          setCurrentWorkspace('events');
          break;
        case 'e':
          setCurrentWorkspace('enhancement_lab');
          break;
        case 'i':
          setCurrentWorkspace('investigation');
          break;
        case 'a':
          setCurrentWorkspace('analytics');
          break;
        case 'v':
          setCurrentWorkspace('evidence');
          break;
        case 'r':
          setCurrentWorkspace('reports');
          break;
        case 's':
          setCurrentWorkspace('system_status');
          break;
        default:
          break;
      }
    },
    []
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleDispatchEvidence = (newEvidence: EvidenceItem) => {
    setEvidenceList((prev) => [newEvidence, ...prev]);
    api.saveEvidence(newEvidence).catch((err) => {
      console.warn('Failed to commit evidence to backend repository:', err);
    });
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#07090e] text-[#e6edf3]">
      {/* Top Contextual Header */}
      <TopBar
        currentWorkspace={currentWorkspace}
        systemMode={systemMode}
        onSetSystemMode={setSystemMode}
        isBackendOnline={isBackendOnline}
        onOpenHotkeys={() => setIsHotkeysOpen(true)}
      />

      {/* Main Operating Split: Sidebar Navigation + Active Workspace */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentWorkspace={currentWorkspace}
          onSelectWorkspace={setCurrentWorkspace}
        />

        {/* Primary Viewport Canvas */}
        <main className="flex-1 flex flex-col overflow-hidden bg-[#07090e]" role="main">
          {currentWorkspace === 'situation_room' && (
            <SituationRoomView
              systemMode={systemMode}
              onNavigateWorkspace={setCurrentWorkspace}
              onSelectTrackForInvestigation={setSelectedTrackId}
            />
          )}

          {currentWorkspace === 'live_monitoring' && (
            <LiveMonitoringView
              systemMode={systemMode}
              onNavigateWorkspace={setCurrentWorkspace}
            />
          )}

          {currentWorkspace === 'cameras' && (
            <CamerasView
              systemMode={systemMode}
              onNavigateWorkspace={setCurrentWorkspace}
            />
          )}

          {currentWorkspace === 'events' && (
            <EventsView
              systemMode={systemMode}
              onNavigateWorkspace={setCurrentWorkspace}
              onSelectTrackForInvestigation={setSelectedTrackId}
            />
          )}

          {currentWorkspace === 'enhancement_lab' && (
            <EnhancementLabView
              systemMode={systemMode}
              onDispatchEvidence={handleDispatchEvidence}
              onNavigateWorkspace={setCurrentWorkspace}
            />
          )}

          {currentWorkspace === 'investigation' && (
            <InvestigationView
              systemMode={systemMode}
              initialTrackId={selectedTrackId}
              onNavigateWorkspace={setCurrentWorkspace}
            />
          )}

          {currentWorkspace === 'analytics' && (
            <AnalyticsView systemMode={systemMode} />
          )}

          {currentWorkspace === 'evidence' && (
            <EvidenceView
              systemMode={systemMode}
              evidenceList={evidenceList}
              onNavigateWorkspace={setCurrentWorkspace}
            />
          )}

          {currentWorkspace === 'reports' && (
            <ReportsView
              systemMode={systemMode}
              onNavigateWorkspace={setCurrentWorkspace}
            />
          )}

          {currentWorkspace === 'system_status' && (
            <SystemStatusView systemMode={systemMode} />
          )}

          {currentWorkspace === 'security' && (
            <SecurityView systemMode={systemMode} />
          )}

          {currentWorkspace === 'settings' && (
            <SettingsView systemMode={systemMode} />
          )}
        </main>
      </div>

      {/* Keyboard Shortcuts Reference Overlay */}
      <HotkeysModal
        isOpen={isHotkeysOpen}
        onClose={() => setIsHotkeysOpen(false)}
      />
    </div>
  );
}
