import React, { useState } from 'react';
import { Copy, Check, ShieldCheck } from 'lucide-react';

interface HashBadgeProps {
  hash: string;
  label?: string;
  truncateLength?: number;
  showIcon?: boolean;
  className?: string;
}

export const HashBadge: React.FC<HashBadgeProps> = ({
  hash,
  label,
  truncateLength = 8,
  showIcon = true,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);

  const displayHash =
    hash.length > truncateLength * 2
      ? `${hash.slice(0, truncateLength)}...${hash.slice(-truncateLength)}`
      : hash;

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(hash);
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  return (
    <button
      onClick={handleCopy}
      title={`Click to copy full SHA-256 digest:\n${hash}`}
      className={`inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded text-[11px] font-mono border border-[#222b3a] bg-[#0b0e14] text-[#94a3b8] hover:text-[#e6edf3] hover:border-[#334155] transition-colors cursor-pointer select-none ${className}`}
      aria-label="Copy cryptographic hash"
    >
      {showIcon && <ShieldCheck className="w-3 h-3 text-[#64748b]" />}
      {label && <span className="text-[10px] text-[#64748b] font-sans uppercase tracking-wider">{label}</span>}
      <span className="text-[#cbd5e1]">{displayHash}</span>
      {copied ? (
        <Check className="w-2.5 h-2.5 text-[#10b981]" />
      ) : (
        <Copy className="w-2.5 h-2.5 text-[#64748b] opacity-60 group-hover:opacity-100" />
      )}
    </button>
  );
};
