import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import {
  TargetTrack,
  InvestigationDossier,
  SystemMode,
  RiskEvaluationResult,
} from '../../types/forensic';
import { QualityBadge } from '../common/QualityBadge';
import {
  Clock,
  Crosshair,
  SlidersHorizontal,
  FileText,
  Plus,
  ArrowRight,
  ShieldAlert,
  Play,
  Film,
  Camera,
  Activity,
  CheckCircle2,
} from 'lucide-react';

interface InvestigationViewProps {
  systemMode: SystemMode;
  initialTrackId?: number;
  onNavigateWorkspace: (ws: any) => void;
}

export const InvestigationView: React.FC<InvestigationViewProps> = ({
  systemMode,
  initialTrackId = 1,
  onNavigateWorkspace,
}) => {
  const [tracks, setTracks] = useState<TargetTrack[]>([]);
  const [selectedTrackId, setSelectedTrackId] = useState<number>(initialTrackId);
  const [dossier, setDossier] = useState<InvestigationDossier | null>(null);
  const [trackRisk, setTrackRisk] = useState<RiskEvaluationResult | null>(null);
  const [selectedKeyframeIndex, setSelectedKeyframeIndex] = useState<number>(0);
  const [newTimelineEvent, setNewTimelineEvent] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState<boolean>(false);

  useEffect(() => {
    api.getTracks().then((res) => {
      setTracks(res.tracks);
    });
  }, []);

  useEffect(() => {
    if (selectedTrackId) {
      api.getInvestigation(selectedTrackId).then((res) => {
        setDossier(res.dossier);
        setSelectedKeyframeIndex(0);
      });
      api.getTrackRisk(selectedTrackId).then((res) => {
        setTrackRisk(res.result);
      });
    }
  }, [selectedTrackId]);

  const activeTrack =
    dossier?.track || tracks.find((t) => t.track_id === selectedTrackId) || tracks[0];

  const handleAddTimelineEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTimelineEvent.trim()) return;
    setIsSubmitting(true);
    await api.addTimelineEvent(selectedTrackId, newTimelineEvent);
    const res = await api.getInvestigation(selectedTrackId);
    setDossier(res.dossier);
    setNewTimelineEvent('');
    setIsSubmitting(false);
  };

  const timelineItems = dossier?.timeline || [
    { id: 1, timestamp: '21:31:04', description: 'OBJECT_ENTERED: Target observed at perimeter boundary', camera_id: 'CAM_01' },
    { id: 2, timestamp: '21:31:08', description: 'QUALITY_DIAGNOSIS: Severe low-light degradation (<40)', camera_id: 'CAM_01' },
    { id: 3, timestamp: '21:31:10', description: 'ZONE_INCURSION: Exclusion boundary crossed into restricted zone', camera_id: 'CAM_01' },
    { id: 4, timestamp: '21:31:17', description: 'LOITERING_ALERT: Dwell duration reached 14.2s (Threshold: 10s)', camera_id: 'CAM_01' },
  ];

  const currentTimelineItem = timelineItems[selectedKeyframeIndex] || timelineItems[0];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Investigation Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[#f59e0b] font-mono text-[10px] uppercase tracking-wider">
            <Crosshair className="w-3.5 h-3.5" />
            <span>RECONSTRUCTION TARGET:</span>
          </div>

          <div className="flex items-center gap-1">
            {tracks.map((t) => {
              const isSelected = selectedTrackId === t.track_id;
              return (
                <button
                  key={t.track_id}
                  onClick={() => setSelectedTrackId(t.track_id)}
                  className={`wb-btn text-[11px] py-0.5 px-2 ${
                    isSelected ? 'wb-btn-primary' : 'wb-btn-ghost'
                  }`}
                >
                  Track #{t.track_id} ({t.class_name})
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateWorkspace('enhancement_lab')}
            className="wb-btn"
            title="Inspect & enhance raw crop in Enhancement Lab"
          >
            <SlidersHorizontal className="w-3.5 h-3.5 text-[#f59e0b]" />
            <span>Enhance Target Crop [E]</span>
          </button>
          <button
            onClick={async () => {
              setIsGeneratingReport(true);
              try {
                await api.generateReport(selectedTrackId);
              } catch (err) {
                console.warn('Report generation error:', err);
              } finally {
                setIsGeneratingReport(false);
                onNavigateWorkspace('reports');
              }
            }}
            disabled={isGeneratingReport}
            className="wb-btn wb-btn-primary"
            title="Export investigation into formal report dossier"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>{isGeneratingReport ? 'Compiling Dossier...' : 'Generate Case Dossier [R]'}</span>
          </button>
        </div>
      </div>

      {/* Main Reconstruction Workspace Split: Target Canvas & Inspector (Top) | Forensic Timeline (Bottom) */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* UPPER REGION: Target Focal Stage + Inspector */}
        <div className="flex-1 flex overflow-hidden border-b border-[#141a24]">
          {/* Target Focal Stage (Center-Left) */}
          <div className="flex-1 flex flex-col p-3 bg-[#07090e] overflow-hidden justify-between">
            {/* Focal Header Readout */}
            <div className="flex items-center justify-between pb-1 text-xs">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-[#e6edf3]">
                  TARGET RECONSTRUCTION: TRACK #{activeTrack?.track_id || 1}
                </span>
                <span className="text-[10px] font-mono text-[#8b9bb0] uppercase">
                  ({activeTrack?.class_name || 'person'})
                </span>
                <span className="text-[#222b3a]">|</span>
                <span className="text-[11px] font-mono text-[#cbd5e1]">
                  ACTIVE KEYFRAME: {currentTimelineItem?.timestamp}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <QualityBadge
                  label={activeTrack?.is_blurry ? 'DEGRADED' : 'ACCEPTABLE'}
                  score={activeTrack?.quality_score}
                />
              </div>
            </div>

            {/* Visual Frame & Restored Crop Pair */}
            <div className="flex-1 grid grid-cols-2 gap-3 my-1.5 overflow-hidden">
              {/* Raw Optical Capture */}
              <div className="flex flex-col rounded border border-[#141a24] bg-black overflow-hidden relative">
                <div className="h-6 px-2.5 bg-[#0b0e14]/90 border-b border-[#141a24] flex items-center justify-between text-[10px] font-mono text-[#8b9bb0] z-10">
                  <span>RAW SENSOR CAPTURE ({activeTrack?.camera_id || 'CAM_01'})</span>
                  <span>{currentTimelineItem?.timestamp}</span>
                </div>
                <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden">
                  <img
                    src={api.getSampleImageUrl(
                      activeTrack?.camera_id === 'CAM_02' ? 'blur' : 'lowlight'
                    )}
                    alt="Raw Frame"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-2 left-2 bg-[#07090e]/85 border border-[#1e2634] px-1.5 py-0.5 rounded text-[9.5px] font-mono text-[#8b9bb0]">
                    RAW OPTICAL FEED
                  </div>
                </div>
              </div>

              {/* Adaptively Restored Derivative */}
              <div className="flex flex-col rounded border border-[#141a24] bg-black overflow-hidden relative">
                <div className="h-6 px-2.5 bg-[#0b0e14]/90 border-b border-[#141a24] flex items-center justify-between text-[10px] font-mono text-[#34d399] z-10">
                  <span>ADAPTIVELY RESTORED DERIVATIVE</span>
                  <span>+1.82 dB PSNR</span>
                </div>
                <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden">
                  <img
                    src={api.getSampleEnhancedUrl(
                      activeTrack?.camera_id === 'CAM_02' ? 'blur' : 'lowlight'
                    )}
                    alt="Enhanced Derivative"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-2 right-2 bg-[#07090e]/85 border border-[#d97706]/40 px-1.5 py-0.5 rounded text-[9.5px] font-mono text-[#f59e0b]">
                    RESTORED CROP
                  </div>
                </div>
              </div>
            </div>

            {/* Target Telemetry & Multi-Sensor Lineage Bar */}
            <div className="h-10 bg-[#0b0e14] border border-[#141a24] rounded px-3 flex items-center justify-between text-xs font-mono shrink-0">
              <div className="flex items-center gap-3">
                <span className="text-[#64748b] text-[10px] font-sans">CONFIDENCE:</span>
                <span className="text-[#34d399] font-medium">
                  {((activeTrack?.confidence || 0.912) * 100).toFixed(1)}%
                </span>
              </div>

              <span className="text-[#222b3a]">|</span>

              <div className="flex items-center gap-2">
                <span className="text-[#64748b] text-[10px] font-sans">BIOMETRIC CROP:</span>
                <span className={activeTrack?.face_detected ? 'text-[#34d399]' : 'text-[#64748b]'}>
                  {activeTrack?.face_detected ? 'ISOLATED (0.88 CONF)' : 'NOT ISOLATED'}
                </span>
              </div>

              <span className="text-[#222b3a]">|</span>

              <div className="flex items-center gap-2">
                <span className="text-[#64748b] text-[10px] font-sans">ANPR STRING:</span>
                <span className="text-[#cbd5e1]">
                  {activeTrack?.ocr_text || 'N/A (Pedestrian)'}
                </span>
              </div>

              <span className="text-[#222b3a]">|</span>

              <div className="flex items-center gap-2">
                <span className="text-[#64748b] text-[10px] font-sans">RE-ID EMBEDDING:</span>
                <span className="text-[#f59e0b]">
                  {activeTrack?.reid_matched_tracks?.length
                    ? 'CORRELATED (Track #4)'
                    : 'UNIQUE PROFILE'}
                </span>
              </div>
            </div>
          </div>

          {/* Contextual Target & Risk Inspector (Right 320px) */}
          <div className="w-80 border-l border-[#141a24] bg-[#0b0e14] flex flex-col justify-between shrink-0 p-3 text-xs overflow-y-auto">
            <div className="space-y-3">
              {/* Risk Evaluation */}
              <div className="pb-2 border-b border-[#141a24]">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono text-[#475569] uppercase tracking-wider">
                    COMPOSITE RISK LEVEL
                  </span>
                  <span
                    className={`font-mono text-xs font-bold ${
                      (trackRisk?.composite_score ?? activeTrack?.risk_score ?? 75) >= 75
                        ? 'text-[#ef4444]'
                        : (trackRisk?.composite_score ?? activeTrack?.risk_score ?? 75) >= 50
                        ? 'text-[#f59e0b]'
                        : 'text-[#34d399]'
                    }`}
                  >
                    {trackRisk?.composite_score ?? activeTrack?.risk_score ?? 75}/100 · {(trackRisk?.risk_level ?? 'High').toUpperCase()}
                  </span>
                </div>

                <div className="space-y-1 text-[11px] font-sans">
                  {(trackRisk?.factors || []).map((f, idx) => (
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

              {/* Multi-Camera Trajectory */}
              <div className="pb-2 border-b border-[#141a24]">
                <span className="text-[10px] font-mono text-[#475569] uppercase tracking-wider block mb-1.5">
                  CROSS-CAMERA TRAJECTORY
                </span>
                <div className="p-2 bg-[#07090e] border border-[#141a24] rounded flex items-center justify-between text-[11px] font-mono">
                  <span className="text-[#34d399]">CAM_01: Perimeter</span>
                  <ArrowRight className="w-3 h-3 text-[#475569]" />
                  <span className="text-[#f59e0b]">CAM_02: Checkpoint</span>
                </div>
              </div>

              {/* Log Timeline Note */}
              <form onSubmit={handleAddTimelineEvent} className="space-y-1.5">
                <span className="text-[10px] font-mono text-[#475569] uppercase tracking-wider block">
                  LOG INVESTIGATION NOTE
                </span>
                <div className="flex gap-1.5">
                  <input
                    type="text"
                    value={newTimelineEvent}
                    onChange={(e) => setNewTimelineEvent(e.target.value)}
                    placeholder="Log observation note..."
                    className="wb-input flex-1 text-[11px]"
                  />
                  <button
                    type="submit"
                    disabled={isSubmitting || !newTimelineEvent.trim()}
                    className="wb-btn wb-btn-primary px-2"
                  >
                    <Plus className="w-3 h-3" />
                  </button>
                </div>
              </form>
            </div>

            <div className="pt-2 border-t border-[#141a24] text-[10px] font-mono text-[#475569] flex justify-between">
              <span>TARGET RECONSTRUCTION ENGINE</span>
              <span>BYTETRACK PERSISTENT</span>
            </div>
          </div>
        </div>

        {/* LOWER REGION: Dominant Forensic Video / Incident Timeline */}
        <div className="h-44 bg-[#0b0e14] flex flex-col justify-between p-2.5 overflow-hidden shrink-0 select-none">
          <div className="flex items-center justify-between text-[10px] font-mono text-[#64748b] mb-1">
            <div className="flex items-center gap-2">
              <Film className="w-3.5 h-3.5 text-[#f59e0b]" />
              <span className="text-[#e6edf3] font-medium font-sans text-xs">
                INCIDENT EVENT RECONSTRUCTION TRACK
              </span>
              <span className="text-[#334155]">|</span>
              <span>TIME WINDOW: 21:31:00 — 21:31:30 UTC</span>
            </div>

            <span className="text-[#94a3b8]">
              {timelineItems.length} KEYFRAMES LOGGED (CLICK KEYFRAME TO SCRUB)
            </span>
          </div>

          {/* Video-Editing Multi-Track Timeline Ribbon */}
          <div className="flex-1 flex flex-col justify-center py-1">
            {/* Time Ticks */}
            <div className="flex justify-between px-2 text-[9px] font-mono text-[#475569] border-b border-[#141a24] pb-0.5">
              <span>21:31:00</span>
              <span>21:31:05</span>
              <span>21:31:10</span>
              <span>21:31:15</span>
              <span>21:31:20</span>
              <span>21:31:25</span>
              <span>21:31:30</span>
            </div>

            {/* Keyframe Track */}
            <div className="relative h-14 my-1 bg-[#07090e] border border-[#141a24] rounded flex items-center px-4 gap-3 overflow-x-auto">
              {/* Scrub Line */}
              <div
                className="absolute top-0 bottom-0 w-[2px] bg-[#d97706] z-10 pointer-events-none transition-all duration-200"
                style={{
                  left: `${Math.min(94, Math.max(6, (selectedKeyframeIndex / (timelineItems.length - 1 || 1)) * 90 + 5))}%`,
                }}
              />

              {timelineItems.map((item, idx) => {
                const isSelected = selectedKeyframeIndex === idx;
                return (
                  <button
                    key={item.id || idx}
                    onClick={() => setSelectedKeyframeIndex(idx)}
                    className={`flex-1 min-w-[170px] text-left p-1.5 rounded transition-all cursor-pointer relative z-20 flex flex-col justify-between h-11 ${
                      isSelected
                        ? 'bg-[#151a21] border border-[#d97706]'
                        : 'bg-[#0b0e14] border border-[#141a24] hover:border-[#1e2634]'
                    }`}
                  >
                    <div className="flex items-center justify-between font-mono text-[9.5px]">
                      <span className={isSelected ? 'text-[#f59e0b] font-semibold' : 'text-[#8b9bb0]'}>
                        {item.timestamp}
                      </span>
                      <span className="text-[#475569]">{item.camera_id || 'CAM_01'}</span>
                    </div>
                    <div className="text-[10px] text-[#cbd5e1] font-sans truncate mt-0.5">
                      {item.description.split(':')[0]}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Sensor Camera Interval Track */}
            <div className="flex gap-2 h-4 text-[9px] font-mono text-[#8b9bb0]">
              <div className="flex-1 bg-[#07090e] border border-[#141a24] rounded-xs px-2 flex items-center justify-between">
                <span>SENSOR: CAM_01 (PERIMETER)</span>
                <span className="text-[#34d399]">ACTIVE INTERVAL</span>
              </div>
              <div className="w-1/3 bg-[#07090e] border border-[#141a24] rounded-xs px-2 flex items-center justify-between">
                <span>HANDOFF: CAM_02</span>
                <span className="text-[#f59e0b]">CORRELATED</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
