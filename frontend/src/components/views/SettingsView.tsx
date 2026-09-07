import React, { useState } from 'react';
import { SurveillanceSettings, SystemMode } from '../../types/forensic';
import { Sliders, Save, CheckCircle2, RotateCcw } from 'lucide-react';

interface SettingsViewProps {
  systemMode: SystemMode;
}

const DEFAULT_SETTINGS: SurveillanceSettings = {
  detectionConfidenceThreshold: 0.45,
  iouThreshold: 0.50,
  loiteringDwellTimeSec: 10.0,
  speedAnomalyThresholdKmh: 40.0,
  autoEnhanceDegradedThreshold: 45.0,
  restrictedZoneWeight: 35,
  nightMultiplier: 1.5,
  audibleAlerts: false,
};

export const SettingsView: React.FC<SettingsViewProps> = ({ systemMode }) => {
  const [settings, setSettings] = useState<SurveillanceSettings>(DEFAULT_SETTINGS);
  const [savedNotice, setSavedNotice] = useState<boolean>(false);

  const handleSave = () => {
    localStorage.setItem('sentinel_settings', JSON.stringify(settings));
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 2500);
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Settings Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-[#f59e0b]" />
          <span className="font-semibold text-[#e6edf3]">SURVEILLANCE & PIPELINE PARAMETERS</span>
        </div>

        <div className="flex items-center gap-2">
          {savedNotice && (
            <span className="text-[11px] text-[#34d399] flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> Parameters Saved
            </span>
          )}
          <button
            onClick={handleReset}
            className="wb-btn"
            title="Reset parameters to calibrated defaults"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>
          <button
            onClick={handleSave}
            className="wb-btn wb-btn-primary"
            title="Save parameters to local storage"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Configuration</span>
          </button>
        </div>
      </div>

      {/* Main Settings Form Canvas */}
      <div className="flex-1 p-6 overflow-y-auto bg-[#07090e] flex justify-center">
        <div className="w-full max-w-3xl space-y-4">
          {/* Section 1: Perception Engine Thresholds */}
          <div className="border border-[#141a24] bg-[#0b0e14] rounded p-4 space-y-3">
            <h2 className="text-xs font-semibold text-[#e6edf3] border-b border-[#141a24] pb-2">
              Detection & Tracking Thresholds
            </h2>

            <div className="space-y-3 text-xs font-mono">
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-[#8b9bb0] font-sans">YOLO11 Detection Confidence Cutoff</span>
                  <span className="text-[#e6edf3]">
                    {(settings.detectionConfidenceThreshold * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.90"
                  step="0.05"
                  value={settings.detectionConfidenceThreshold}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      detectionConfidenceThreshold: parseFloat(e.target.value),
                    })
                  }
                  className="wb-slider"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-[#8b9bb0] font-sans">ByteTrack IoU Association Threshold</span>
                  <span className="text-[#e6edf3]">
                    {(settings.iouThreshold * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0.20"
                  max="0.80"
                  step="0.05"
                  value={settings.iouThreshold}
                  onChange={(e) =>
                    setSettings({ ...settings, iouThreshold: parseFloat(e.target.value) })
                  }
                  className="wb-slider"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Adaptive Enhancement Triggers */}
          <div className="border border-[#141a24] bg-[#0b0e14] rounded p-4 space-y-3">
            <h2 className="text-xs font-semibold text-[#e6edf3] border-b border-[#141a24] pb-2">
              Adaptive Quality Enhancement Triggers
            </h2>

            <div className="space-y-3 text-xs font-mono">
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-[#8b9bb0] font-sans">
                    Optical Degradation Threshold (Trigger CLAHE/Denoise)
                  </span>
                  <span className="text-[#f59e0b]">
                    &lt; {settings.autoEnhanceDegradedThreshold.toFixed(0)} Score
                  </span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="70"
                  step="5"
                  value={settings.autoEnhanceDegradedThreshold}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      autoEnhanceDegradedThreshold: parseFloat(e.target.value),
                    })
                  }
                  className="wb-slider"
                />
              </div>
            </div>
          </div>

          {/* Section 3: Risk Engine Weights */}
          <div className="border border-[#141a24] bg-[#0b0e14] rounded p-4 space-y-3">
            <h2 className="text-xs font-semibold text-[#e6edf3] border-b border-[#141a24] pb-2">
              Deterministic Risk Engine Weights
            </h2>

            <div className="space-y-3 text-xs font-mono">
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-[#8b9bb0] font-sans">
                    Restricted Zone Entry Base Penalty
                  </span>
                  <span className="text-[#ef4444]">
                    +{settings.restrictedZoneWeight} Points
                  </span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="50"
                  step="5"
                  value={settings.restrictedZoneWeight}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      restrictedZoneWeight: parseInt(e.target.value),
                    })
                  }
                  className="wb-slider"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-[#8b9bb0] font-sans">
                    Loitering Dwell Duration Limit
                  </span>
                  <span className="text-[#e6edf3]">
                    {settings.loiteringDwellTimeSec.toFixed(1)} Seconds
                  </span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="60"
                  step="5"
                  value={settings.loiteringDwellTimeSec}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      loiteringDwellTimeSec: parseFloat(e.target.value),
                    })
                  }
                  className="wb-slider"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
