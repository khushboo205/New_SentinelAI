import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { CameraFeed, SystemMode } from '../../types/forensic';
import { QualityBadge } from '../common/QualityBadge';
import {
  Video,
  Grid,
  Square,
  Crosshair,
  SlidersHorizontal,
  Volume2,
  VolumeX,
  AlertTriangle,
} from 'lucide-react';

interface LiveMonitoringViewProps {
  systemMode: SystemMode;
  onNavigateWorkspace: (ws: any) => void;
}

export const LiveMonitoringView: React.FC<LiveMonitoringViewProps> = ({
  systemMode,
  onNavigateWorkspace,
}) => {
  const [cameras, setCameras] = useState<CameraFeed[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<string>('CAM_01');
  const [layoutMode, setLayoutMode] = useState<'single' | 'grid'>('single');
  const [showDetections, setShowDetections] = useState<boolean>(true);
  const [isAudioMuted, setIsAudioMuted] = useState<boolean>(true);

  useEffect(() => {
    api.getCameras().then((res) => {
      setCameras(res.cameras);
      if (res.cameras.length > 0) setSelectedCameraId(res.cameras[0].id);
    });
  }, []);

  const activeCamera = cameras.find((c) => c.id === selectedCameraId) || cameras[0];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Live Monitoring Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Video className="w-4 h-4 text-[#f59e0b]" />
            <span className="font-semibold text-[#e6edf3]">LIVE VIDEO MONITORING INSTRUMENT</span>
          </div>
          <span className="text-[#222b3a]">|</span>
          <span className="text-[10px] font-mono text-[#f59e0b] bg-[#78350f]/15 border border-[#78350f] px-1.5 py-0.2 rounded">
            CALIBRATED OPERATIONAL TEST FOOTAGE
          </span>
        </div>

        {/* Layout Mode Toggles & Controls */}
        <div className="flex items-center gap-2">
          <div className="flex items-center border border-[#1e2634] rounded bg-[#07090e] p-0.5">
            <button
              onClick={() => setLayoutMode('single')}
              className={`p-1 rounded cursor-pointer ${
                layoutMode === 'single' ? 'bg-[#151a21] text-[#f59e0b]' : 'text-[#64748b] hover:text-[#cbd5e1]'
              }`}
              title="Single focus dominant stream"
            >
              <Square className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setLayoutMode('grid')}
              className={`p-1 rounded cursor-pointer ${
                layoutMode === 'grid' ? 'bg-[#151a21] text-[#f59e0b]' : 'text-[#64748b] hover:text-[#cbd5e1]'
              }`}
              title="2x2 Multi-view matrix"
            >
              <Grid className="w-3.5 h-3.5" />
            </button>
          </div>

          <button
            onClick={() => setShowDetections(!showDetections)}
            className={`wb-btn ${showDetections ? 'wb-btn-primary' : 'wb-btn-ghost'}`}
            title="Toggle YOLO11 target tracking bounding boxes"
          >
            <Crosshair className="w-3 h-3" />
            <span>Target Bounding Boxes</span>
          </button>

          <button
            onClick={() => setIsAudioMuted(!isAudioMuted)}
            className="wb-btn wb-btn-ghost p-1.5"
            title="Toggle alert chime"
          >
            {isAudioMuted ? (
              <VolumeX className="w-3.5 h-3.5 text-[#64748b]" />
            ) : (
              <Volume2 className="w-3.5 h-3.5 text-[#10b981]" />
            )}
          </button>
        </div>
      </div>

      {/* Main Grid: Source Rail (Left) | Dominant Feed or Multi-Matrix */}
      <div className="flex-1 flex overflow-hidden">
        {/* Source Rail (Left 200px) */}
        <div className="w-52 border-r border-[#141a24] bg-[#0b0e14] p-2 flex flex-col gap-1.5 overflow-y-auto shrink-0">
          <div className="px-1 py-0.5 text-[10px] font-mono text-[#475569] uppercase tracking-wider flex justify-between">
            <span>STREAMS</span>
            <span>{cameras.length} CONFIGURED</span>
          </div>

          {cameras.map((cam) => {
            const isSelected = cam.id === selectedCameraId;
            return (
              <div
                key={cam.id}
                onClick={() => setSelectedCameraId(cam.id)}
                className={`p-1.5 rounded transition-colors cursor-pointer flex flex-col gap-1 ${
                  isSelected
                    ? 'border border-[#d97706] bg-[#151a21]'
                    : 'border border-[#141a24] bg-[#07090e] hover:border-[#1e2634]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 font-mono text-xs font-semibold text-[#e6edf3]">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                    <span>{cam.id}</span>
                  </div>
                  <QualityBadge label={cam.quality_label} size="sm" />
                </div>

                <div className="relative aspect-video bg-black rounded-xs border border-[#141a24] overflow-hidden">
                  <img
                    src={api.getSampleImageUrl(cam.sample_id)}
                    alt={cam.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute bottom-1 right-1 bg-black/80 px-1 rounded text-[9px] font-mono text-[#94a3b8]">
                    {cam.fps} FPS
                  </div>
                </div>

                <div className="flex items-center justify-between text-[10px] text-[#64748b] font-mono">
                  <span className="truncate">{cam.name}</span>
                  <span className="shrink-0">{cam.resolution}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Dominant Viewport or Multi-Matrix */}
        <div className="flex-1 p-3 flex flex-col gap-2 bg-[#07090e] overflow-hidden">
          {layoutMode === 'single' ? (
            <div className="flex-1 flex flex-col rounded border border-[#141a24] bg-[#07090e] overflow-hidden">
              {/* Stream Header */}
              <div className="h-7 px-3 bg-[#0b0e14] border-b border-[#141a24] flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                  <span className="text-[#e6edf3] font-semibold">{activeCamera?.name}</span>
                  <span className="text-[#475569]">({activeCamera?.location})</span>
                </div>
                <div className="flex items-center gap-3 text-[11px] text-[#8b9bb0]">
                  <span>{activeCamera?.resolution}</span>
                  <span>{activeCamera?.fps} FPS</span>
                  <QualityBadge
                    label={activeCamera?.quality_label || 'DEGRADED'}
                    score={activeCamera?.quality_score}
                  />
                </div>
              </div>

              {/* Video Viewport */}
              <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden">
                <img
                  src={api.getSampleImageUrl(activeCamera?.sample_id || 'lowlight')}
                  alt={activeCamera?.name}
                  className="w-full h-full object-contain select-none"
                />

                {showDetections && (
                  <div
                    className="absolute border border-[#f59e0b] bg-[#f59e0b]/10"
                    style={{ top: '30%', left: '40%', width: '20%', height: '45%' }}
                  >
                    <div className="absolute -top-5 left-0 bg-[#0b0e14] border border-[#f59e0b] px-1.5 py-0.2 rounded text-[9.5px] font-mono text-[#f59e0b]">
                      #1 PERSON 0.91 CONF
                    </div>
                  </div>
                )}

                {activeCamera?.quality_label === 'DEGRADED' && (
                  <div className="absolute bottom-4 left-4 bg-[#0b0e14]/90 border border-[#78350f] px-2.5 py-1 rounded flex items-center gap-2.5 text-xs">
                    <span className="text-[#fbbf24] font-mono text-[10.5px]">
                      DEGRADED SENSOR: {activeCamera?.degradations[0] || 'LOW ILLUMINATION'}
                    </span>
                    <button
                      onClick={() => onNavigateWorkspace('enhancement_lab')}
                      className="wb-btn wb-btn-primary py-0.2 px-2 text-[10px]"
                    >
                      <SlidersHorizontal className="w-3 h-3" />
                      <span>Open in Enhancement Lab [E]</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 grid grid-cols-2 gap-2 overflow-hidden">
              {cameras.map((cam) => (
                <div
                  key={cam.id}
                  onClick={() => {
                    setSelectedCameraId(cam.id);
                    setLayoutMode('single');
                  }}
                  className="relative flex flex-col rounded border border-[#141a24] bg-black overflow-hidden cursor-pointer hover:border-[#d97706] transition-colors"
                >
                  <div className="h-6 px-2 bg-[#0b0e14] border-b border-[#141a24] flex items-center justify-between text-[10px] font-mono text-[#cbd5e1] z-10">
                    <span>{cam.name}</span>
                    <span>{cam.fps} FPS</span>
                  </div>
                  <div className="relative flex-1 overflow-hidden">
                    <img
                      src={api.getSampleImageUrl(cam.sample_id)}
                      alt={cam.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
