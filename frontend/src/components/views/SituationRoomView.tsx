import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import {
  CameraFeed,
  ForensicEvent,
  TargetTrack,
  SystemMode,
  RiskEvaluationResult,
} from '../../types/forensic';
import { QualityBadge } from '../common/QualityBadge';
import {
  SlidersHorizontal,
  Search,
  Crosshair,
  AlertTriangle,
  Layers,
  Camera,
  Clock,
  ArrowRight,
} from 'lucide-react';

interface SituationRoomViewProps {
  systemMode: SystemMode;
  onNavigateWorkspace: (ws: any) => void;
  onSelectTrackForInvestigation: (trackId: number) => void;
}

export const SituationRoomView: React.FC<SituationRoomViewProps> = ({
  systemMode,
  onNavigateWorkspace,
  onSelectTrackForInvestigation,
}) => {
  const [cameras, setCameras] = useState<CameraFeed[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<string>('CAM_01');
  const [events, setEvents] = useState<ForensicEvent[]>([]);
  const [tracks, setTracks] = useState<TargetTrack[]>([]);
  const [selectedTrackId, setSelectedTrackId] = useState<number>(1);
  const [trackRisk, setTrackRisk] = useState<RiskEvaluationResult | null>(null);
  const [showOverlays, setShowOverlays] = useState<boolean>(true);
  const [showMapOverlay, setShowMapOverlay] = useState<boolean>(false);

  useEffect(() => {
    api.getCameras().then((res) => {
      setCameras(res.cameras);
      if (res.cameras.length > 0) setSelectedCameraId(res.cameras[0].id);
    });
    api.getEvents(20).then((res) => setEvents(res.events));
    api.getTracks().then((res) => {
      setTracks(res.tracks);
      if (res.tracks.length > 0) setSelectedTrackId(res.tracks[0].track_id);
    });
  }, []);

  useEffect(() => {
    if (selectedTrackId) {
      api.getTrackRisk(selectedTrackId).then((res) => {
        setTrackRisk(res.result);
      });
    }
  }, [selectedTrackId]);

  const activeCamera = cameras.find((c) => c.id === selectedCameraId) || cameras[0];
  const activeTrack = tracks.find((t) => t.track_id === selectedTrackId) || tracks[0];

  const handleSelectEvent = (event: ForensicEvent) => {
    setSelectedCameraId(event.camera_id);
    if (event.target_id) {
      setSelectedTrackId(event.target_id);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Contextual Header Bar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
            <span className="font-mono font-semibold text-[#e6edf3]">
              {activeCamera?.name || 'Sector North — Perimeter'}
            </span>
          </div>

          <span className="text-[#222b3a]">|</span>

          <span className="text-[11px] text-[#8b9bb0] font-mono">
            {activeCamera?.resolution || '1920x1080'} @ {activeCamera?.fps || 25} FPS
          </span>

          <span className="text-[#222b3a]">|</span>

          <QualityBadge
            label={activeCamera?.quality_label || 'DEGRADED'}
            score={activeCamera?.quality_score}
          />
        </div>

        {/* View Options */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`wb-btn ${showOverlays ? 'wb-btn-primary' : 'wb-btn-ghost'}`}
            title="Toggle tracking boxes and sensor metadata overlays"
          >
            <Crosshair className="w-3 h-3" />
            <span>Target Bounding Boxes</span>
          </button>

          <button
            onClick={() => setShowMapOverlay(!showMapOverlay)}
            className={`wb-btn ${showMapOverlay ? 'wb-btn-primary' : 'wb-btn-ghost'}`}
            title="Toggle secondary tactical perimeter map"
          >
            <Layers className="w-3 h-3" />
            <span>GIS Map Layer</span>
          </button>
        </div>
      </div>

      {/* Main Operating Workspace: Sources Rail | CCTV Canvas | Contextual Inspector */}
      <div className="flex-1 flex overflow-hidden border-b border-[#141a24]">
        {/* Left Column: Optical Sources Rail (190px) */}
        <div className="w-48 border-r border-[#141a24] bg-[#0b0e14] p-2 flex flex-col gap-1.5 overflow-y-auto shrink-0">
          <div className="px-1 py-0.5 text-[10px] font-mono text-[#475569] uppercase tracking-wider">
            OPTICAL SOURCES ({cameras.length})
          </div>

          {cameras.map((cam) => {
            const isSelected = cam.id === selectedCameraId;
            return (
              <button
                key={cam.id}
                onClick={() => setSelectedCameraId(cam.id)}
                className={`w-full text-left p-1.5 rounded transition-colors cursor-pointer flex flex-col gap-1 ${
                  isSelected
                    ? 'border border-[#d97706] bg-[#151a21]'
                    : 'border border-[#141a24] bg-[#07090e] hover:border-[#1e2634]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-semibold text-[#e6edf3]">{cam.id}</span>
                  <QualityBadge label={cam.quality_label} size="sm" />
                </div>
                <span className="text-[11px] text-[#8b9bb0] truncate">{cam.name}</span>
                <div className="flex items-center justify-between text-[10px] text-[#64748b] font-mono mt-0.5">
                  <span>{cam.active_targets} TARGETS</span>
                  <span className={cam.risk_level === 'Critical' ? 'text-[#f87171]' : ''}>
                    {cam.risk_level.toUpperCase()}
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Center Column: Dominant CCTV Workspace Canvas */}
        <div className="flex-1 relative bg-[#07090e] flex items-center justify-center overflow-hidden">
          <div className="relative w-full h-full flex items-center justify-center p-2.5">
            <img
              src={api.getSampleImageUrl(activeCamera?.sample_id || 'lowlight')}
              alt={activeCamera?.name}
              className="w-full h-full object-contain rounded-xs border border-[#141a24] bg-black select-none"
            />

            {/* Subtle Precision Target Bounding Box Overlay */}
            {showOverlays && (
              <div
                className="absolute border border-[#f59e0b] bg-[#f59e0b]/10 cursor-pointer group transition-all"
                style={{
                  top: '32%',
                  left: '42%',
                  width: '18%',
                  height: '42%',
                }}
                onClick={() => setSelectedTrackId(1)}
              >
                <div className="absolute -top-5 left-0 bg-[#0b0e14] border border-[#f59e0b] px-1.5 py-0.2 rounded text-[9.5px] font-mono text-[#f59e0b] flex items-center gap-1.5 whitespace-nowrap">
                  <span>#1 PERSON</span>
                  <span className="text-[#8b9bb0]">0.91 CONF</span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onNavigateWorkspace('enhancement_lab');
                  }}
                  className="absolute bottom-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity bg-[#0b0e14]/95 border border-[#f59e0b] text-[#f59e0b] hover:bg-[#f59e0b] hover:text-black px-1.5 py-0.5 rounded text-[9px] font-mono flex items-center gap-1 z-20"
                  title="Enhance target crop in Enhancement Lab"
                >
                  <SlidersHorizontal className="w-2.5 h-2.5" />
                  <span>Enhance Crop [E]</span>
                </button>
              </div>
            )}

            {/* Secondary Tactical GIS Spatial Map Overlay (When toggled) */}
            {showMapOverlay && (
              <div className="absolute bottom-4 left-4 w-64 h-38 bg-[#0b0e14]/95 border border-[#1e2634] rounded p-2 flex flex-col justify-between shadow-2xl z-20">
                <div className="flex items-center justify-between text-[10px] font-mono text-[#8b9bb0] border-b border-[#141a24] pb-1">
                  <span>PERIMETER GIS MAP</span>
                  <span className="text-[#f59e0b]">31.6284°N 74.8723°E</span>
                </div>
                <div className="relative flex-1 bg-[#07090e] rounded border border-[#141a24] my-1 flex items-center justify-center">
                  <div className="w-full h-[1px] bg-[#141a24]" />
                  <div className="absolute inset-x-0 h-[1px] bg-[#d97706]/40 top-1/2" />
                  <div className="absolute top-1/2 left-1/3 w-2 h-2 rounded-full bg-[#ef4444] animate-ping" />
                  <div className="absolute top-1/2 left-1/3 w-2 h-2 rounded-full bg-[#ef4444]" />
                  <span className="absolute bottom-1 right-1 text-[9px] font-mono text-[#475569]">
                    SECTOR 04
                  </span>
                </div>
                <div className="text-[9px] font-mono text-[#475569] flex justify-between">
                  <span>LAT/LON WGS84</span>
                  <span>CAM_01 FOV</span>
                </div>
              </div>
            )}

            {/* In-Canvas Degradation Notice & Fast Enhancement CTA */}
            {activeCamera?.quality_label === 'DEGRADED' && (
              <div className="absolute top-4 left-4 bg-[#0b0e14]/90 border border-[#78350f] px-2.5 py-1 rounded flex items-center gap-2.5 text-xs z-10">
                <div className="flex items-center gap-1.5 text-[#fbbf24] font-mono text-[10.5px]">
                  <AlertTriangle className="w-3.5 h-3.5 text-[#f59e0b]" />
                  <span>DEGRADATION: {activeCamera.degradations[0] || 'LOW ILLUMINATION'}</span>
                </div>
                <button
                  onClick={() => onNavigateWorkspace('enhancement_lab')}
                  className="wb-btn wb-btn-primary py-0.2 px-2 text-[10px]"
                >
                  <SlidersHorizontal className="w-3 h-3" />
                  <span>Restore in Enhancement Lab [E]</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Contextual Target & Risk Inspector (280px) */}
        <div className="w-72 border-l border-[#141a24] bg-[#0b0e14] p-3 flex flex-col justify-between shrink-0 overflow-y-auto">
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-1.5 border-b border-[#141a24]">
              <span className="text-[10px] text-[#475569] font-mono uppercase tracking-wider">
                TARGET INSPECTOR
              </span>
              <span className="font-mono text-xs font-semibold text-[#f59e0b]">
                TRACK #{activeTrack?.track_id || 1}
              </span>
            </div>

            {/* Metadata Table */}
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between py-0.5 border-b border-[#141a24]/60">
                <span className="text-[#64748b] font-sans">Classification</span>
                <span className="text-[#e6edf3] uppercase font-semibold">
                  {activeTrack?.class_name || 'PERSON'}
                </span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#141a24]/60">
                <span className="text-[#64748b] font-sans">Confidence</span>
                <span className="text-[#34d399]">
                  {((activeTrack?.confidence || 0.912) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#141a24]/60">
                <span className="text-[#64748b] font-sans">Measured Velocity</span>
                <span className="text-[#cbd5e1]">{activeTrack?.velocity_kmh || 4.8} km/h</span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#141a24]/60">
                <span className="text-[#64748b] font-sans">Exclusion Dwell</span>
                <span className="text-[#f87171]">{activeTrack?.loitering_sec || 14.2}s</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-[#64748b] font-sans">Optical Quality</span>
                <QualityBadge
                  label={activeTrack?.is_blurry ? 'DEGRADED' : 'ACCEPTABLE'}
                  score={activeTrack?.quality_score}
                  size="sm"
                />
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="pt-2 border-t border-[#141a24] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-[#475569] font-mono uppercase tracking-wider">
                  DETERMINISTIC RISK
                </span>
                <span
                  className={`text-xs font-mono font-bold ${
                    (trackRisk?.composite_score ?? activeTrack?.risk_score ?? 75) >= 75
                      ? 'text-[#ef4444]'
                      : (trackRisk?.composite_score ?? activeTrack?.risk_score ?? 75) >= 50
                      ? 'text-[#f59e0b]'
                      : 'text-[#34d399]'
                  }`}
                >
                  {trackRisk?.composite_score ?? activeTrack?.risk_score ?? 75}/100 · {(trackRisk?.risk_level ?? 'Critical').toUpperCase()}
                </span>
              </div>

              <div className="space-y-1 text-[11px] font-sans">
                {(trackRisk?.factors || []).slice(0, 4).map((f, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between text-[#cbd5e1] py-0.5 border-b border-[#141a24]/50 last:border-b-0"
                  >
                    <span className="truncate pr-2">{f.name}</span>
                    <span className="font-mono text-[#f59e0b] shrink-0">+{f.weight}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Escalation CTAs */}
          <div className="space-y-1.5 pt-2 border-t border-[#141a24]">
            <button
              onClick={() => {
                onSelectTrackForInvestigation(activeTrack?.track_id || 1);
                onNavigateWorkspace('investigation');
              }}
              className="wb-btn wb-btn-primary w-full justify-center py-1.5"
              title="Open track in Incident Reconstruction workspace"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Reconstruct in Investigation [I]</span>
            </button>

            <button
              onClick={() => onNavigateWorkspace('enhancement_lab')}
              className="wb-btn w-full justify-center py-1.5"
              title="Open current frame in image enhancement lab"
            >
              <SlidersHorizontal className="w-3.5 h-3.5 text-[#f59e0b]" />
              <span>Enhance Target Frame [E]</span>
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Row: Chronological Event Timeline Stream */}
      <div className="h-24 bg-[#0b0e14] px-3 py-1.5 flex flex-col justify-between shrink-0 overflow-hidden">
        <div className="flex items-center justify-between text-[10px] font-mono text-[#475569]">
          <div className="flex items-center gap-1.5">
            <Clock className="w-3 h-3 text-[#f59e0b]" />
            <span className="uppercase tracking-wider">
              CHRONOLOGICAL SENSOR EVENT STREAM (CLICK TO FOCUS)
            </span>
          </div>
          <span>OPERATIONAL TIMELINE</span>
        </div>

        {/* Horizontal Event Row */}
        <div className="flex gap-2 overflow-x-auto pb-0.5">
          {events.map((evt) => (
            <button
              key={evt.id}
              onClick={() => handleSelectEvent(evt)}
              className="w-52 shrink-0 p-1.5 rounded bg-[#07090e] border border-[#141a24] hover:border-[#d97706] cursor-pointer flex flex-col justify-between text-xs transition-colors text-left"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9.5px] text-[#8b9bb0]">{evt.timestamp}</span>
                <span
                  className={`text-[9px] font-mono px-1 rounded ${
                    evt.severity === 'CRITICAL'
                      ? 'text-[#f87171] bg-[#7f1d1d]/20'
                      : 'text-[#fbbf24] bg-[#78350f]/20'
                  }`}
                >
                  {evt.severity}
                </span>
              </div>
              <span className="font-medium text-[#e6edf3] text-[11px] truncate">
                {evt.event_type.replace(/_/g, ' ')}
              </span>
              <div className="flex items-center justify-between text-[9.5px] text-[#64748b] font-mono">
                <span>{evt.camera_id}</span>
                <span>TRACK #{evt.target_id}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
