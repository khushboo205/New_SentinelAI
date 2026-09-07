import React, { useState } from 'react';
import { EvidenceItem, SystemMode } from '../../types/forensic';
import { INITIAL_EVIDENCE_ITEMS } from '../../data/sampleEvidence';
import { HashBadge } from '../common/HashBadge';
import {
  FileCheck2,
  ShieldCheck,
  ArrowRight,
  Lock,
  CheckCircle,
  FileText,
  Search,
  ExternalLink,
} from 'lucide-react';

interface EvidenceViewProps {
  systemMode: SystemMode;
  evidenceList?: EvidenceItem[];
  onNavigateWorkspace: (ws: any) => void;
}

export const EvidenceView: React.FC<EvidenceViewProps> = ({
  systemMode,
  evidenceList = INITIAL_EVIDENCE_ITEMS,
  onNavigateWorkspace,
}) => {
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string>(
    evidenceList[0]?.evidence_id || 'EV-2026-001'
  );

  const activeEvidence =
    evidenceList.find((e) => e.evidence_id === selectedEvidenceId) || evidenceList[0];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Evidence Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-2">
          <FileCheck2 className="w-4 h-4 text-[#f59e0b]" />
          <span className="font-semibold text-[#e6edf3]">EVIDENCE PROVENANCE & CHAIN OF CUSTODY</span>
          <span className="text-[#334155]">|</span>
          <span className="text-[10px] font-mono text-[#64748b]">
            {evidenceList.length} VAULT ARTIFACTS
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-[#8b9bb0] flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-[#10b981]" />
            <span>NIST FIPS 180-4 SHA-256 AUDIT ACTIVE</span>
          </span>
        </div>
      </div>

      {/* Main Workspace Split: Evidence Registry (Left) | Provenance Workspace (Right) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Evidence Registry Rail (260px) */}
        <div className="w-64 border-r border-[#141a24] bg-[#0b0e14] p-2 flex flex-col gap-2 overflow-y-auto shrink-0">
          <div className="px-1 text-[10px] font-mono text-[#475569] uppercase tracking-wider flex justify-between">
            <span>SEALED EVIDENCE ARTIFACTS</span>
            <span>{evidenceList.length} ITEMS</span>
          </div>

          <div className="space-y-1">
            {evidenceList.map((item) => {
              const isSelected = item.evidence_id === selectedEvidenceId;
              return (
                <div
                  key={item.evidence_id}
                  onClick={() => setSelectedEvidenceId(item.evidence_id)}
                  className={`p-2 rounded transition-colors cursor-pointer flex flex-col gap-1 ${
                    isSelected
                      ? 'border border-[#d97706] bg-[#151a21]'
                      : 'border border-[#141a24] bg-[#07090e] hover:border-[#1e2634]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-semibold text-[#e6edf3]">
                      {item.evidence_id}
                    </span>
                    <span className="text-[9.5px] font-mono text-[#34d399] bg-[#064e3b]/20 px-1 rounded border border-[#065f46]">
                      {item.quality_delta_psnr}
                    </span>
                  </div>

                  <span className="text-[11px] text-[#cbd5e1] font-medium truncate">
                    {item.title}
                  </span>

                  <div className="flex items-center justify-between text-[10px] text-[#64748b] font-mono mt-0.5">
                    <span>{item.camera_id}</span>
                    <span>{item.created_at.split('T')[0]}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Technical Provenance Workspace */}
        <div className="flex-1 p-4 flex flex-col gap-3.5 overflow-y-auto bg-[#07090e]">
          {/* Active Artifact Header */}
          <div className="pb-3 border-b border-[#141a24] flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold text-[#e6edf3]">{activeEvidence.title}</h2>
                <span className="text-[11px] font-mono text-[#64748b]">({activeEvidence.case_id})</span>
              </div>
              <p className="text-xs text-[#8b9bb0] mt-0.5 max-w-3xl">{activeEvidence.notes}</p>
            </div>

            <span className="text-[10px] font-mono text-[#38bdf8] bg-[#0c4a6e]/15 border border-[#0369a1] px-2 py-0.5 rounded">
              {activeEvidence.classification.replace(/_/g, ' ')}
            </span>
          </div>

          {/* Provenance Chain Hierarchy (The Core Architectural Spine) */}
          <div className="p-3 bg-[#0b0e14] border border-[#141a24] rounded">
            <div className="text-[10px] font-mono text-[#475569] uppercase tracking-wider mb-2.5">
              CRYPTOGRAPHIC PROVENANCE & CHAIN OF CUSTODY PIPELINE
            </div>

            <div className="grid grid-cols-6 gap-2 text-xs font-mono items-center">
              {/* Node 1: Original */}
              <div className="p-2 rounded bg-[#07090e] border border-[#141a24] flex flex-col gap-1">
                <span className="text-[9px] text-[#64748b] font-sans">1. ORIGINAL</span>
                <span className="text-[#cbd5e1] font-semibold truncate">{activeEvidence.camera_id}</span>
                <HashBadge hash={activeEvidence.original_hash} truncateLength={4} />
              </div>

              {/* Node 2: Processing */}
              <div className="p-2 rounded bg-[#07090e] border border-[#141a24] flex flex-col gap-1">
                <span className="text-[9px] text-[#64748b] font-sans">2. PROCESSING</span>
                <span className="text-[#f59e0b] truncate text-[11px]">
                  {activeEvidence.processing_applied[0] || 'Adaptive CLAHE'}
                </span>
                <span className="text-[10px] text-[#34d399] font-medium">
                  {activeEvidence.quality_delta_psnr} PSNR
                </span>
              </div>

              {/* Node 3: Derivative */}
              <div className="p-2 rounded bg-[#07090e] border border-[#141a24] flex flex-col gap-1">
                <span className="text-[9px] text-[#64748b] font-sans">3. DERIVATIVE</span>
                <span className="text-[#cbd5e1] font-semibold truncate">Forensic Crop</span>
                <HashBadge hash={activeEvidence.derivative_hash} truncateLength={4} />
              </div>

              {/* Node 4: SHA-256 Digest */}
              <div className="p-2 rounded bg-[#07090e] border border-[#141a24] flex flex-col gap-1">
                <span className="text-[9px] text-[#64748b] font-sans">4. SHA-256 SEAL</span>
                <span className="text-[#34d399] flex items-center gap-1 text-[11px]">
                  <CheckCircle className="w-3 h-3" /> VERIFIED
                </span>
                <span className="text-[9.5px] text-[#64748b]">Deterministic</span>
              </div>

              {/* Node 5: Investigation Link */}
              <div className="p-2 rounded bg-[#07090e] border border-[#141a24] flex flex-col gap-1">
                <span className="text-[9px] text-[#64748b] font-sans">5. INVESTIGATION</span>
                <button
                  onClick={() => onNavigateWorkspace('investigation')}
                  className="text-[#f59e0b] hover:underline text-left text-[11px] truncate flex items-center gap-1"
                >
                  <span>Track #1</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
                <span className="text-[9.5px] text-[#64748b]">Dossier Attached</span>
              </div>

              {/* Node 6: Formal Report */}
              <div className="p-2 rounded bg-[#07090e] border border-[#141a24] flex flex-col gap-1">
                <span className="text-[9px] text-[#64748b] font-sans">6. REPORT</span>
                <button
                  onClick={() => onNavigateWorkspace('reports')}
                  className="text-[#38bdf8] hover:underline text-left text-[11px] truncate flex items-center gap-1"
                >
                  <span>Case Dossier</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
                <span className="text-[9.5px] text-[#64748b]">Archival Entry</span>
              </div>
            </div>
          </div>

          {/* Visual Evidence Pair: Raw vs Enhanced */}
          <div className="grid grid-cols-2 gap-3 flex-1">
            {/* Raw Sensor Frame */}
            <div className="rounded border border-[#141a24] bg-[#0b0e14] flex flex-col overflow-hidden">
              <div className="h-7 px-3 bg-[#07090e] border-b border-[#141a24] flex items-center justify-between text-[11px] font-mono">
                <span className="text-[#8b9bb0] font-sans uppercase">RAW SENSOR FRAME</span>
                <HashBadge hash={activeEvidence.original_hash} truncateLength={5} />
              </div>
              <div className="relative flex-1 bg-black flex items-center justify-center p-2 min-h-[260px] overflow-hidden">
                <img
                  src={activeEvidence.source_image_url}
                  alt="Raw Optical Capture"
                  className="w-full h-full object-contain"
                />
              </div>
            </div>

            {/* Enhanced Derivative */}
            <div className="rounded border border-[#141a24] bg-[#0b0e14] flex flex-col overflow-hidden">
              <div className="h-7 px-3 bg-[#07090e] border-b border-[#141a24] flex items-center justify-between text-[11px] font-mono">
                <span className="text-[#f59e0b] font-sans uppercase">ENHANCED DERIVATIVE</span>
                <HashBadge hash={activeEvidence.derivative_hash} truncateLength={5} />
              </div>
              <div className="relative flex-1 bg-black flex items-center justify-center p-2 min-h-[260px] overflow-hidden">
                <img
                  src={activeEvidence.enhanced_image_url || activeEvidence.source_image_url}
                  alt="Enhanced Derivative"
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          </div>

          {/* Integrity & Legal Notice */}
          <div className="p-2.5 rounded bg-[#0b0e14] border border-[#1e2634] text-xs text-[#8b9bb0] flex items-start gap-2 shrink-0">
            <Lock className="w-3.5 h-3.5 text-[#64748b] shrink-0 mt-0.5" />
            <div className="leading-relaxed text-[11px]">
              <strong className="text-[#e6edf3]">Chain of Custody Standard:</strong> All derivatives are
              cryptographically sealed with SHA-256 hashes generated from the raw output buffer. Original
              sensor feeds remain untouched in storage; derivatives exist as verified separate artifacts for
              forensic case reconstruction.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
