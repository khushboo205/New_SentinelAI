import React from 'react';

interface QualityBadgeProps {
  label: 'NOMINAL' | 'GOOD' | 'ACCEPTABLE' | 'DEGRADED' | 'POOR' | string;
  score?: number;
  size?: 'sm' | 'md';
  className?: string;
}

export const QualityBadge: React.FC<QualityBadgeProps> = ({
  label,
  score,
  size = 'sm',
  className = '',
}) => {
  const norm = label.toUpperCase();

  let borderStyle = 'border-[#222b3a] text-[#94a3b8] bg-[#10141a]';
  let dotColor = 'bg-[#64748b]';

  if (norm === 'NOMINAL' || norm === 'GOOD') {
    borderStyle = 'border-[#065f46] text-[#34d399] bg-[#064e3b]/20';
    dotColor = 'bg-[#10b981]';
  } else if (norm === 'ACCEPTABLE') {
    borderStyle = 'border-[#1e293b] text-[#cbd5e1] bg-[#1e293b]/40';
    dotColor = 'bg-[#94a3b8]';
  } else if (norm === 'DEGRADED') {
    borderStyle = 'border-[#78350f] text-[#fbbf24] bg-[#78350f]/20';
    dotColor = 'bg-[#f59e0b]';
  } else if (norm === 'POOR') {
    borderStyle = 'border-[#7f1d1d] text-[#f87171] bg-[#7f1d1d]/20';
    dotColor = 'bg-[#ef4444]';
  }

  const isSmall = size === 'sm';

  return (
    <span
      className={`inline-flex items-center gap-1.5 border rounded px-1.5 py-0.5 font-medium select-none ${
        isSmall ? 'text-[10px]' : 'text-xs px-2 py-1'
      } ${borderStyle} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      <span className="font-sans uppercase tracking-wider">{norm}</span>
      {score !== undefined && (
        <span className="font-mono text-[10px] text-[#94a3b8] opacity-80">
          ({Math.round(score)})
        </span>
      )}
    </span>
  );
};
