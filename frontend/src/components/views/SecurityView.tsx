import React, { useState } from 'react';
import { SystemMode } from '../../types/forensic';
import { HashBadge } from '../common/HashBadge';
import {
  Shield,
  ShieldCheck,
  CheckCircle,
  Terminal,
  Lock,
} from 'lucide-react';

interface SecurityViewProps {
  systemMode: SystemMode;
}

export const SecurityView: React.FC<SecurityViewProps> = ({ systemMode }) => {
  const [testHashInput, setTestHashInput] = useState<string>('');
  const [testHashResult, setTestHashResult] = useState<string | null>(null);

  const handleComputeDigest = async () => {
    if (!testHashInput) return;
    const encoder = new TextEncoder();
    const data = encoder.encode(testHashInput);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
    setTestHashResult(hashHex);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Security Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-[#f59e0b]" />
          <span className="font-semibold text-[#e6edf3]">CRYPTOGRAPHIC INTEGRITY & SENSOR AUDIT</span>
        </div>
        <span className="text-[10px] font-mono text-[#8b9bb0] flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5 text-[#10b981]" />
          <span>FIPS 180-4 SHA-256 ENGINE ACTIVE</span>
        </span>
      </div>

      {/* Main Security Canvas */}
      <div className="flex-1 p-4 overflow-y-auto bg-[#07090e] space-y-4 max-w-6xl mx-auto w-full">
        {/* Verification Overview */}
        <div className="grid grid-cols-3 gap-3 font-mono text-xs">
          <div className="p-3 bg-[#0b0e14] border border-[#141a24] rounded">
            <span className="text-[10px] font-sans text-[#64748b] block mb-1">Hashing Standard</span>
            <span className="text-sm font-semibold text-[#e6edf3]">SHA-256 (NIST FIPS 180-4)</span>
            <span className="text-[10px] text-[#8b9bb0] block mt-1">256-bit cryptographic digest</span>
          </div>

          <div className="p-3 bg-[#0b0e14] border border-[#141a24] rounded">
            <span className="text-[10px] font-sans text-[#64748b] block mb-1">Disk Derivative Storage</span>
            <span className="text-sm font-semibold text-[#34d399] flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> Hash-Indexed Persistence
            </span>
            <span className="text-[10px] text-[#8b9bb0] block mt-1">data/enhanced/{"<hash>"}.jpg</span>
          </div>

          <div className="p-3 bg-[#0b0e14] border border-[#141a24] rounded">
            <span className="text-[10px] font-sans text-[#64748b] block mb-1">Evidentiary Classification</span>
            <span className="text-sm font-semibold text-[#38bdf8]">Internal Verification Hash</span>
            <span className="text-[10px] text-[#64748b] block mt-1">Non-certified operational preview</span>
          </div>
        </div>

        {/* Live Cryptographic Verification Tool */}
        <div className="border border-[#141a24] bg-[#0b0e14] rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-[#141a24] pb-2">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#f59e0b]" />
              <h2 className="text-xs font-semibold text-[#e6edf3]">
                In-Workstation SHA-256 Cryptographic Verifier
              </h2>
            </div>
            <span className="text-[10px] font-mono text-[#64748b]">NATIVE WEB CRYPTO API</span>
          </div>

          <p className="text-xs text-[#8b9bb0]">
            Verify any raw image payload string, header metadata, or frame buffer against our deterministic SHA-256 digest engine.
          </p>

          <div className="flex gap-2">
            <input
              type="text"
              value={testHashInput}
              onChange={(e) => setTestHashInput(e.target.value)}
              placeholder="Enter test string or frame metadata e.g. CAM_01_FRAME_1842_2026-08-04"
              className="wb-input flex-1"
            />
            <button onClick={handleComputeDigest} className="wb-btn wb-btn-primary">
              Compute Digest
            </button>
          </div>

          {testHashResult && (
            <div className="p-2.5 rounded bg-[#07090e] border border-[#141a24] text-xs font-mono flex items-center justify-between">
              <span className="text-[#64748b] text-[10px]">COMPUTED DIGEST:</span>
              <HashBadge hash={testHashResult} truncateLength={16} />
            </div>
          )}
        </div>

        {/* Integrity Principles Notice */}
        <div className="border border-[#141a24] bg-[#0b0e14] rounded p-4 text-xs text-[#8b9bb0] space-y-2">
          <div className="flex items-center gap-2 text-[#e6edf3] font-semibold">
            <Lock className="w-4 h-4 text-[#f59e0b]" />
            <span>Forensic Evidence Preservation Standards</span>
          </div>
          <p className="leading-relaxed text-[11px]">
            SentinelAI automatically seals both the <strong>raw sensor frame</strong> and the <strong>enhanced derivative</strong> at the exact millisecond of inference. The original CCTV buffer is never overwritten; all enhancements are persisted as non-destructive separate derivatives indexed by their SHA-256 digest to ensure strict chain of custody.
          </p>
        </div>
      </div>
    </div>
  );
};
