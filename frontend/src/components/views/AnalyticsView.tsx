import React from 'react';
import { SystemMode } from '../../types/forensic';
import {
  CONTROLLED_BENCHMARKS,
  BENCHMARK_FPS_MEASUREMENTS,
} from '../../data/sampleEvidence';
import {
  BarChart3,
  Info,
  Cpu,
  TrendingUp,
  TrendingDown,
  Minus,
  FlaskConical,
} from 'lucide-react';

interface AnalyticsViewProps {
  systemMode: SystemMode;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ systemMode }) => {
  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Analytics Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-2">
          <FlaskConical className="w-4 h-4 text-[#f59e0b]" />
          <span className="font-semibold text-[#e6edf3]">EMPIRICAL BENCHMARK EVALUATION WORKSPACE</span>
          <span className="text-[#334155]">|</span>
          <span className="text-[10px] font-mono text-[#38bdf8] bg-[#0c4a6e]/15 border border-[#0369a1] px-1.5 py-0.2 rounded">
            CONTROLLED BENCHMARK / OFFLINE EVALUATION
          </span>
        </div>

        <div className="text-[11px] font-mono text-[#8b9bb0]">
          ENVIRONMENT: Intel Core CPU (Single Thread Execution)
        </div>
      </div>

      {/* Main Scientific Canvas */}
      <div className="flex-1 p-4 overflow-y-auto bg-[#07090e] space-y-4 max-w-6xl mx-auto w-full">
        {/* Empirical Throughput Table */}
        <div className="border border-[#141a24] bg-[#0b0e14] rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-[#141a24] pb-2">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-[#f59e0b]" />
              <h2 className="text-xs font-semibold text-[#e6edf3]">
                Empirical Engine Throughput Measurements (FPS)
              </h2>
            </div>
            <span className="text-[10px] font-mono text-[#64748b]">
              CONTROLLED BENCHMARK · CPU INFERENCE
            </span>
          </div>

          <div className="grid grid-cols-4 gap-3 font-mono text-xs">
            <div className="p-3 bg-[#07090e] border border-[#141a24] rounded">
              <span className="text-[10px] font-sans text-[#64748b] block mb-1">
                Adaptive Enhancement
              </span>
              <span className="text-lg font-bold text-[#e6edf3]">
                {BENCHMARK_FPS_MEASUREMENTS.enhancement_fps} FPS
              </span>
              <span className="text-[10px] text-[#8b9bb0] block mt-0.5">
                CLAHE + Bilateral + Sharpen
              </span>
            </div>

            <div className="p-3 bg-[#07090e] border border-[#141a24] rounded">
              <span className="text-[10px] font-sans text-[#64748b] block mb-1">
                YOLO11 Object Detector
              </span>
              <span className="text-lg font-bold text-[#34d399]">
                {BENCHMARK_FPS_MEASUREMENTS.yolo_fps} FPS
              </span>
              <span className="text-[10px] text-[#8b9bb0] block mt-0.5">
                Steady state CPU inference
              </span>
            </div>

            <div className="p-3 bg-[#07090e] border border-[#141a24] rounded">
              <span className="text-[10px] font-sans text-[#64748b] block mb-1">
                EasyOCR Text Extraction
              </span>
              <span className="text-lg font-bold text-[#f59e0b]">
                {BENCHMARK_FPS_MEASUREMENTS.ocr_fps} FPS
              </span>
              <span className="text-[10px] text-[#8b9bb0] block mt-0.5">
                License plate character recognition
              </span>
            </div>

            <div className="p-3 bg-[#07090e] border border-[#141a24] rounded">
              <span className="text-[10px] font-sans text-[#64748b] block mb-1">
                Full Composite Pipeline
              </span>
              <span className="text-lg font-bold text-[#cbd5e1]">
                {BENCHMARK_FPS_MEASUREMENTS.composite_fps} FPS
              </span>
              <span className="text-[10px] text-[#8b9bb0] block mt-0.5">
                End-to-end multi-agent loop
              </span>
            </div>
          </div>
        </div>

        {/* Quality Metrics & Trade-off Breakdown Table */}
        <div className="border border-[#141a24] bg-[#0b0e14] rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-[#141a24] pb-2">
            <div>
              <h2 className="text-xs font-semibold text-[#e6edf3]">
                Empirical Optical Reconstruction Metrics & Trade-off Analysis
              </h2>
              <span className="text-[10px] font-mono text-[#64748b]">
                OFFLINE BENCHMARK DATASET · LOW-LIGHT SURVEILLANCE RUN
              </span>
            </div>

            <span className="text-[10px] font-mono text-[#8b9bb0]">
              MEASURED AUGUST 2026
            </span>
          </div>

          <div className="border border-[#141a24] rounded overflow-hidden">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#07090e] border-b border-[#141a24] text-[#64748b] text-[10px] uppercase">
                <tr>
                  <th className="py-2.5 px-3">Metric Name</th>
                  <th className="py-2.5 px-3">Before Enhancement</th>
                  <th className="py-2.5 px-3">After Enhancement</th>
                  <th className="py-2.5 px-3">Measured Delta</th>
                  <th className="py-2.5 px-3">Scientific Explanation & Trade-off</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#141a24] bg-[#0b0e14]">
                {CONTROLLED_BENCHMARKS.map((bm, idx) => (
                  <tr key={idx} className="hover:bg-[#10141a]">
                    <td className="py-2.5 px-3 text-[#e6edf3] font-medium font-sans">
                      {bm.metric}
                    </td>
                    <td className="py-2.5 px-3 text-[#8b9bb0]">{bm.before}</td>
                    <td className="py-2.5 px-3 text-[#cbd5e1]">{bm.after}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`inline-flex items-center gap-1 font-semibold ${
                          bm.direction === 'improvement'
                            ? 'text-[#34d399]'
                            : bm.direction === 'degradation'
                            ? 'text-[#fbbf24]'
                            : 'text-[#8b9bb0]'
                        }`}
                      >
                        {bm.direction === 'improvement' ? (
                          <TrendingUp className="w-3.5 h-3.5" />
                        ) : bm.direction === 'degradation' ? (
                          <TrendingDown className="w-3.5 h-3.5" />
                        ) : (
                          <Minus className="w-3.5 h-3.5" />
                        )}
                        <span>{bm.delta}</span>
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[#8b9bb0] font-sans text-[11px] leading-relaxed">
                      {bm.explanation}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-3 rounded bg-[#07090e] border border-[#141a24] text-xs text-[#8b9bb0] flex items-start gap-2">
            <Info className="w-4 h-4 text-[#38bdf8] shrink-0 mt-0.5" />
            <div className="leading-relaxed text-[11px]">
              <strong className="text-[#e6edf3]">Scientific Transparency:</strong> In severe low-light
              restoration, the SSIM reduction (0.2334 → 0.1509) is mathematically expected. Aggressive contrast
              stretching and high-pass sharpening inevitably diverge from ground truth pixel correlations while
              maximizing downstream detection confidence (YOLO11 advanced from 0.41 to 0.91).
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
