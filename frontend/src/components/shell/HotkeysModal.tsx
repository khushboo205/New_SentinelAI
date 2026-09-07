import React from 'react';
import { X, Keyboard } from 'lucide-react';

interface HotkeysModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HotkeysModal: React.FC<HotkeysModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const shortcuts = [
    { key: '1', action: 'Switch to Situation Room' },
    { key: '2', action: 'Switch to Live Monitoring' },
    { key: '3', action: 'Open Camera Source Library' },
    { key: '4', action: 'Open Forensic Event Stream' },
    { key: 'E', action: 'Open Enhancement Lab (Signature Workbench)' },
    { key: 'I', action: 'Open Incident Reconstruction' },
    { key: 'A', action: 'Open Controlled Benchmark Analytics' },
    { key: 'V', action: 'Open Evidence & Provenance Vault' },
    { key: 'R', action: 'Open Reports Dossier' },
    { key: 'S', action: 'Inspect System Status & Engine' },
    { key: '?', action: 'Toggle this Shortcuts Guide' },
    { key: 'Esc', action: 'Close any active overlay / modal' },
  ];

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-[2px] z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md bg-[#0b0e14] border border-[#222b3a] rounded p-4 text-xs select-none shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pb-3 border-b border-[#161c26] mb-3">
          <div className="flex items-center gap-2">
            <Keyboard className="w-4 h-4 text-[#f59e0b]" />
            <h3 className="font-medium text-[#e6edf3]">Workbench Keyboard Shortcuts</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-[#64748b] hover:text-[#e6edf3] rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 gap-1.5 font-sans">
          {shortcuts.map((sc) => (
            <div
              key={sc.key}
              className="flex items-center justify-between py-1 px-2 rounded hover:bg-[#10141a]"
            >
              <span className="text-[#94a3b8]">{sc.action}</span>
              <kbd className="px-1.5 py-0.5 rounded border border-[#222b3a] bg-[#151a21] text-[#cbd5e1] font-mono text-[10px] min-w-[20px] text-center">
                {sc.key}
              </kbd>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-3 border-t border-[#161c26] text-[11px] text-[#64748b]">
          Press any hotkey anywhere in the workbench to navigate directly.
        </div>
      </div>
    </div>
  );
};
