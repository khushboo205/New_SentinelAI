import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { CameraFeed, SystemMode } from '../../types/forensic';
import { QualityBadge } from '../common/QualityBadge';
import {
  Camera,
  SlidersHorizontal,
  Video,
  CheckCircle,
} from 'lucide-react';

interface CamerasViewProps {
  systemMode: SystemMode;
  onNavigateWorkspace: (ws: any) => void;
  onSelectCameraFeed?: (camId: string) => void;
}

export const CamerasView: React.FC<CamerasViewProps> = ({
  systemMode,
  onNavigateWorkspace,
  onSelectCameraFeed,
}) => {
  const [cameras, setCameras] = useState<CameraFeed[]>([]);
  const [filterQuality, setFilterQuality] = useState<string>('ALL');

  useEffect(() => {
    api.getCameras().then((res) => setCameras(res.cameras));
  }, []);

  const filtered = cameras.filter((c) => {
    if (filterQuality === 'DEGRADED')
      return c.quality_label === 'DEGRADED' || c.quality_label === 'POOR';
    if (filterQuality === 'NOMINAL')
      return c.quality_label === 'NOMINAL' || c.quality_label === 'ACCEPTABLE';
    return true;
  });

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Cameras Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-2">
          <Camera className="w-4 h-4 text-[#f59e0b]" />
          <span className="font-semibold text-[#e6edf3]">MEDIA SOURCE BROWSER & OPTICAL FEEDS</span>
          <span className="text-[#334155]">|</span>
          <span className="text-[10px] font-mono text-[#64748b]">
            {cameras.length} CONFIGURED SENSORS
          </span>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-1.5 text-[11px] font-mono">
          <span className="text-[#64748b]">CONDITION:</span>
          {['ALL', 'DEGRADED', 'NOMINAL'].map((f) => (
            <button
              key={f}
              onClick={() => setFilterQuality(f)}
              className={`wb-btn py-0.5 px-2 text-[10px] ${
                filterQuality === f ? 'wb-btn-primary' : 'wb-btn-ghost'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Main Catalog View: Image-first media grid */}
      <div className="flex-1 p-4 overflow-y-auto bg-[#07090e]">
        <div className="grid grid-cols-2 lg:grid-cols-2 gap-4 max-w-6xl mx-auto">
          {filtered.map((cam) => (
            <div
              key={cam.id}
              className="border border-[#141a24] bg-[#0b0e14] rounded overflow-hidden flex flex-col hover:border-[#1e2634] transition-colors"
            >
              {/* Dominant Image Viewport */}
              <div className="relative aspect-video bg-black overflow-hidden group">
                <img
                  src={api.getSampleImageUrl(cam.sample_id)}
                  alt={cam.name}
                  className="w-full h-full object-cover group-hover:scale-102 transition-transform duration-300"
                />

                {/* Overlaid Sensor Header */}
                <div className="absolute top-2 left-2 flex items-center gap-1.5 bg-[#0b0e14]/90 border border-[#1e2634] px-2 py-0.5 rounded text-xs font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                  <span className="font-semibold text-[#e6edf3]">{cam.id}</span>
                  <span className="text-[#475569]">·</span>
                  <span className="text-[#cbd5e1]">{cam.resolution}</span>
                </div>

                {/* Overlaid Quality Badge */}
                <div className="absolute top-2 right-2">
                  <QualityBadge label={cam.quality_label} score={cam.quality_score} />
                </div>

                {/* Bottom Source State Tag */}
                <div className="absolute bottom-2 left-2 bg-[#0b0e14]/85 border border-[#1e2634] px-2 py-0.5 rounded text-[10px] font-mono text-[#8b9bb0]">
                  SAMPLE CCTV FOOTAGE · {cam.fps} FPS
                </div>
              </div>

              {/* Source Metadata & Diagnostics */}
              <div className="p-3 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold text-[#e6edf3]">{cam.name}</h3>
                  <span className="text-[10px] font-mono text-[#64748b]">{cam.location}</span>
                </div>

                {/* Optical Degradation Chips */}
                {cam.degradations.length > 0 ? (
                  <div className="flex flex-wrap gap-1">
                    {cam.degradations.map((deg, i) => (
                      <span
                        key={i}
                        className="text-[9.5px] font-mono px-1.5 py-0.2 rounded border border-[#78350f] text-[#fbbf24] bg-[#78350f]/15"
                      >
                        {deg}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-[10px] font-mono text-[#34d399] flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" /> Nominal Sensor Fidelity (No Degradation)
                  </span>
                )}

                {/* Recommended Pipeline Steps */}
                <div className="text-[11px] text-[#8b9bb0] font-mono bg-[#07090e] p-2 rounded border border-[#141a24]">
                  <span className="text-[9.5px] text-[#475569] uppercase block mb-0.5">
                    Recommended Enhancement Pipeline:
                  </span>
                  <span className="text-[#cbd5e1]">{cam.recommended_pipeline.join(' ⟶ ')}</span>
                </div>

                {/* Action Controls */}
                <div className="flex items-center gap-2 pt-1 border-t border-[#141a24] mt-0.5">
                  <button
                    onClick={() => {
                      onSelectCameraFeed?.(cam.id);
                      onNavigateWorkspace('live_monitoring');
                    }}
                    className="wb-btn flex-1 justify-center"
                  >
                    <Video className="w-3.5 h-3.5" />
                    <span>Monitor Stream</span>
                  </button>

                  <button
                    onClick={() => onNavigateWorkspace('enhancement_lab')}
                    className="wb-btn wb-btn-primary flex-1 justify-center"
                  >
                    <SlidersHorizontal className="w-3.5 h-3.5" />
                    <span>Enhance in Lab [E]</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
