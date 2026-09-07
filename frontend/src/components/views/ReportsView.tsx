import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { ForensicCaseReport, SystemMode } from '../../types/forensic';
import { INITIAL_REPORT } from '../../data/sampleEvidence';
import { HashBadge } from '../common/HashBadge';
import {
  FileText,
  Printer,
  Download,
  ShieldCheck,
  CheckCircle,
  Lock,
} from 'lucide-react';

interface ReportsViewProps {
  systemMode: SystemMode;
  report?: ForensicCaseReport;
  onNavigateWorkspace: (ws: any) => void;
}

export const ReportsView: React.FC<ReportsViewProps> = ({
  systemMode,
  report: propReport,
  onNavigateWorkspace,
}) => {
  const [reportsList, setReportsList] = useState<ForensicCaseReport[]>([]);
  const [activeReport, setActiveReport] = useState<ForensicCaseReport>(propReport || INITIAL_REPORT);
  const [loading, setLoading] = useState<boolean>(!propReport);

  useEffect(() => {
    if (propReport) {
      setActiveReport(propReport);
    } else {
      setLoading(true);
      api.getReports().then((res) => {
        if (res.reports && res.reports.length > 0) {
          setReportsList(res.reports);
          setActiveReport(res.reports[0]);
        }
      }).finally(() => setLoading(false));
    }
  }, [propReport]);

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(JSON.stringify(activeReport, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${activeReport.case_id}_forensic_dossier.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Reports Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0 print:hidden">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#f59e0b]" />
          <span className="font-semibold text-[#e6edf3]">TECHNICAL CASE REPORT VIEWER</span>
          <span className="text-[#334155]">|</span>
          <span className="text-[10px] font-mono text-[#64748b]">
            CASE DOSSIER: {activeReport.case_id}
          </span>
          {reportsList.length > 1 && (
            <select
              value={activeReport.case_id}
              onChange={(e) => {
                const found = reportsList.find((r) => r.case_id === e.target.value);
                if (found) setActiveReport(found);
              }}
              className="wb-input py-0.5 px-1 text-[10px] font-mono bg-[#07090e]"
            >
              {reportsList.map((r) => (
                <option key={r.case_id} value={r.case_id}>
                  {r.case_id} — Track #{r.primary_target_id}
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadJSON}
            className="wb-btn"
            title="Download dossier as structured JSON"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export JSON</span>
          </button>
          <button
            onClick={handlePrint}
            className="wb-btn wb-btn-primary"
            title="Print document or save as PDF"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Dossier</span>
          </button>
        </div>
      </div>

      {/* Formal Archival Document Canvas */}
      <div className="flex-1 p-6 overflow-y-auto bg-[#07090e] flex justify-center">
        <article className="w-full max-w-4xl bg-[#0b0e14] border border-[#1a2230] p-8 shadow-2xl space-y-6 text-[#cbd5e1] font-sans">
          {/* Official Document Header */}
          <header className="border-b border-[#1e2634] pb-4 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="w-2 h-2 bg-[#d97706] rounded-xs" />
                <span className="text-[10.5px] font-mono text-[#f59e0b] tracking-wider uppercase font-semibold">
                  SENTINELAI FORENSIC DOSSIER
                </span>
              </div>
              <h1 className="text-lg font-bold text-[#e6edf3] tracking-tight">
                {activeReport.incident_title}
              </h1>
              <span className="text-xs font-mono text-[#64748b]">
                CASE IDENTIFIER: {activeReport.case_id}
              </span>
            </div>

            <div className="text-right text-xs font-mono">
              <span className="inline-block px-2 py-0.5 rounded border border-[#0369a1] text-[#38bdf8] bg-[#0c4a6e]/20 text-[10px] font-semibold uppercase">
                {(activeReport.status || 'OPEN_INVESTIGATION').replace(/_/g, ' ')}
              </span>
              <div className="text-[10px] text-[#64748b] mt-1">
                SEALED: {activeReport.incident_datetime}
              </div>
            </div>
          </header>

          {/* Incident Metadata Grid */}
          <section className="grid grid-cols-3 gap-3 p-3 bg-[#07090e] border border-[#141a24] rounded text-xs font-mono">
            <div>
              <span className="text-[10px] text-[#64748b] block font-sans">Lead Unit</span>
              <span className="text-[#e6edf3] font-medium">{activeReport.lead_investigator}</span>
            </div>
            <div>
              <span className="text-[10px] text-[#64748b] block font-sans">Sector Location</span>
              <span className="text-[#e6edf3] font-medium">{activeReport.location_sector}</span>
            </div>
            <div>
              <span className="text-[10px] text-[#64748b] block font-sans">Target Involved</span>
              <span className="text-[#f59e0b] font-medium">{activeReport.target_classification}</span>
            </div>
          </section>

          {/* 1. Executive Incident Summary */}
          <section className="space-y-2">
            <h2 className="text-xs font-mono text-[#64748b] uppercase tracking-wider">
              1. Incident Executive Summary
            </h2>
            <p className="text-xs leading-relaxed text-[#cbd5e1] p-3 bg-[#07090e] border border-[#141a24] rounded font-sans">
              {activeReport.summary}
            </p>
          </section>

          {/* 2. Visual Forensic Artifacts */}
          <section className="space-y-2">
            <h2 className="text-xs font-mono text-[#64748b] uppercase tracking-wider">
              2. Attached Forensic Visual Artifacts
            </h2>
            <div className="grid grid-cols-2 gap-3">
              {(activeReport.evidence_items || []).map((ev) => (
                <div
                  key={ev.evidence_id}
                  className="border border-[#141a24] bg-[#07090e] rounded p-2.5 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between font-mono text-[11px]">
                    <span className="font-semibold text-[#e6edf3]">{ev.evidence_id}</span>
                    <span className="text-[#34d399] font-mono">{ev.quality_delta_psnr} PSNR</span>
                  </div>
                  <div className="relative aspect-video bg-black rounded border border-[#141a24] overflow-hidden">
                    <img
                      src={ev.enhanced_image_url || ev.source_image_url}
                      alt={ev.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="text-[11px] text-[#8b9bb0]">{ev.title}</div>
                  <div className="flex items-center justify-between text-[10px] font-mono pt-1 border-t border-[#141a24]">
                    <span className="text-[#64748b]">DERIVATIVE HASH:</span>
                    <HashBadge hash={ev.derivative_hash} truncateLength={4} />
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 3. Chronological Sequence Table */}
          <section className="space-y-2">
            <h2 className="text-xs font-mono text-[#64748b] uppercase tracking-wider">
              3. Chronological Incident Reconstruction Timeline
            </h2>
            <div className="border border-[#141a24] bg-[#07090e] rounded overflow-hidden">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#0b0e14] border-b border-[#141a24] text-[#64748b] text-[10px] uppercase">
                  <tr>
                    <th className="py-2 px-3">Time</th>
                    <th className="py-2 px-3">Camera Sensor</th>
                    <th className="py-2 px-3">Operational Event</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#141a24]">
                  {(activeReport.timeline || []).map((t, i) => (
                    <tr key={i} className="hover:bg-[#0b0e14]">
                      <td className="py-2 px-3 text-[#f59e0b]">{t.time}</td>
                      <td className="py-2 px-3 text-[#8b9bb0]">{t.camera}</td>
                      <td className="py-2 px-3 text-[#e6edf3]">{t.event}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* 4. Adaptive Restoration Step Log */}
          <section className="space-y-2">
            <h2 className="text-xs font-mono text-[#64748b] uppercase tracking-wider">
              4. Adaptive Image Restoration Execution Log
            </h2>
            <div className="border border-[#141a24] bg-[#07090e] rounded overflow-hidden">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#0b0e14] border-b border-[#141a24] text-[#64748b] text-[10px] uppercase">
                  <tr>
                    <th className="py-2 px-3">Restoration Step</th>
                    <th className="py-2 px-3">Empirical PSNR Delta</th>
                    <th className="py-2 px-3 text-right">Execution Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#141a24]">
                  {(activeReport.enhancement_log || []).map((step, i) => (
                    <tr key={i}>
                      <td className="py-2 px-3 text-[#cbd5e1]">{step.step}</td>
                      <td className="py-2 px-3 text-[#34d399]">{step.psnr_delta}</td>
                      <td className="py-2 px-3 text-right text-[#8b9bb0]">
                        {step.duration_ms} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Cryptographic Integrity Seal */}
          <footer className="pt-4 border-t border-[#1e2634] flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#10b981]" />
              <span className="text-[#8b9bb0]">CRYPTOGRAPHIC INTEGRITY SEAL (SHA-256):</span>
              <HashBadge hash={activeReport.integrity_seal_sha256} truncateLength={8} />
            </div>
            <span className="text-[10px] text-[#64748b]">NON-CERTIFIED OPERATIONAL PREVIEW</span>
          </footer>
        </article>
      </div>
    </div>
  );
};
