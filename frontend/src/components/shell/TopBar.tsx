import React, { useState, useEffect } from 'react';
import { NavWorkspace, SystemMode } from '../../types/forensic';
import { Server, HelpCircle, Maximize2, Minimize2, Clock } from 'lucide-react';

interface TopBarProps {
  currentWorkspace: NavWorkspace;
  systemMode: SystemMode;
  onSetSystemMode: (mode: SystemMode) => void;
  isBackendOnline: boolean;
  onOpenHotkeys: () => void;
}

const WORKSPACE_TITLES: Record<NavWorkspace, { title: string; category: string }> = {
  situation_room: { title: 'Situation Room', category: 'SURVEILLANCE' },
  live_monitoring: { title: 'Live Monitoring', category: 'SURVEILLANCE' },
  cameras: { title: 'Camera Source Library', category: 'SURVEILLANCE' },
  events: { title: 'Forensic Event Stream', category: 'SURVEILLANCE' },
  enhancement_lab: { title: 'Enhancement Lab', category: 'FORENSICS' },
  investigation: { title: 'Incident Reconstruction', category: 'FORENSICS' },
  analytics: { title: 'Benchmark Analytics', category: 'FORENSICS' },
  evidence: { title: 'Evidence & Provenance Vault', category: 'PROVENANCE' },
  reports: { title: 'Forensic Case Dossier', category: 'PROVENANCE' },
  system_status: { title: 'Engine & Hardware Status', category: 'SYSTEM' },
  security: { title: 'Cryptographic Audit', category: 'SYSTEM' },
  settings: { title: 'Surveillance Parameters', category: 'SYSTEM' },
};

export const TopBar: React.FC<TopBarProps> = ({
  currentWorkspace,
  systemMode,
  onSetSystemMode,
  isBackendOnline,
  onOpenHotkeys,
}) => {
  const current = WORKSPACE_TITLES[currentWorkspace];
  const [timeStr, setTimeStr] = useState<string>('');
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().split(' ')[0] + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen?.().catch(() => {});
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.().catch(() => {});
      setIsFullscreen(false);
    }
  };

  return (
    <header className="h-9 border-b border-[#141a24] bg-[#07090e] px-3 flex items-center justify-between select-none z-30 shrink-0">
      {/* Left: Brand Identity & Active Instrument */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 pr-3 border-r border-[#141a24]">
          <span className="w-1.5 h-1.5 rounded-xs bg-[#d97706]" />
          <span className="font-sans text-xs font-semibold tracking-wider text-[#e6edf3]">
            SENTINEL<span className="text-[#d97706]">AI</span>
          </span>
          <span className="text-[10px] text-[#475569] font-mono">v1.0</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[9px] text-[#475569] uppercase tracking-wider font-mono">
            {current.category}
          </span>
          <span className="text-[#2d3748] text-xs">/</span>
          <h1 className="text-xs font-medium text-[#cbd5e1]">{current.title}</h1>
        </div>
      </div>

      {/* Right: Operational Mode, Backend Status, Clock & Shortcuts */}
      <div className="flex items-center gap-2.5">
        {/* Workstation Time Clock */}
        <div className="hidden md:flex items-center gap-1.5 text-[10px] font-mono text-[#64748b] pr-2 border-r border-[#141a24]">
          <Clock className="w-3 h-3 text-[#f59e0b]" />
          <span className="text-[#94a3b8]">{timeStr}</span>
        </div>

        {/* Backend Online/Offline State */}
        <div
          className="flex items-center gap-1.5 px-2 py-0.5 rounded border border-[#141a24] bg-[#0b0e14] text-[10px] font-mono"
          title={isBackendOnline ? 'FastAPI Backend connected (127.0.0.1:8000)' : 'Backend offline — Using local calibrated datasets'}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${isBackendOnline ? 'bg-[#10b981]' : 'bg-[#ef4444]'}`} />
          <Server className="w-2.5 h-2.5 text-[#64748b]" />
          <span className={isBackendOnline ? 'text-[#94a3b8]' : 'text-[#f87171]'}>
            {isBackendOnline ? 'BACKEND LIVE' : 'BACKEND OFFLINE'}
          </span>
        </div>

        {/* Operational Mode Selector */}
        <div className="flex items-center border border-[#1e2634] rounded bg-[#0b0e14] p-0.5 text-[10px]">
          <button
            onClick={() => onSetSystemMode('LIVE')}
            className={`px-1.5 py-0.5 rounded transition-colors font-mono cursor-pointer ${
              systemMode === 'LIVE' ? 'bg-[#10141a] text-[#10b981] font-medium' : 'text-[#64748b] hover:text-[#94a3b8]'
            }`}
            title="Real-time operational video stream & backend telemetry"
          >
            ● LIVE
          </button>
          <button
            onClick={() => onSetSystemMode('DEMO')}
            className={`px-1.5 py-0.5 rounded transition-colors font-mono cursor-pointer ${
              systemMode === 'DEMO' ? 'bg-[#10141a] text-[#f59e0b] font-medium' : 'text-[#64748b] hover:text-[#94a3b8]'
            }`}
            title="Calibrated CCTV test samples (low-light, motion blur, fog)"
          >
            SAMPLE MEDIA
          </button>
          <button
            onClick={() => onSetSystemMode('BENCHMARK')}
            className={`px-1.5 py-0.5 rounded transition-colors font-mono cursor-pointer ${
              systemMode === 'BENCHMARK' ? 'bg-[#10141a] text-[#38bdf8] font-medium' : 'text-[#64748b] hover:text-[#94a3b8]'
            }`}
            title="Empirical controlled benchmark metrics"
          >
            BENCHMARK
          </button>
        </div>

        {/* Fullscreen Toggle */}
        <button
          onClick={toggleFullscreen}
          className="wb-btn wb-btn-ghost p-1 text-[#64748b] hover:text-[#cbd5e1]"
          title="Toggle Fullscreen Workstation"
          aria-label="Toggle Fullscreen"
        >
          {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
        </button>

        {/* Help & Hotkeys */}
        <button
          onClick={onOpenHotkeys}
          className="wb-btn wb-btn-ghost p-1 text-[#64748b] hover:text-[#cbd5e1]"
          title="Keyboard shortcuts & documentation (?)"
          aria-label="Help and shortcuts"
        >
          <HelpCircle className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};
