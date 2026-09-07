import React, { useState } from 'react';
import { NavWorkspace } from '../../types/forensic';
import {
  LayoutDashboard,
  Video,
  Camera,
  AlertTriangle,
  SlidersHorizontal,
  Search,
  BarChart3,
  FileCheck2,
  FileText,
  Cpu,
  Shield,
  Sliders,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface SidebarProps {
  currentWorkspace: NavWorkspace;
  onSelectWorkspace: (workspace: NavWorkspace) => void;
}

interface NavItem {
  id: NavWorkspace;
  label: string;
  icon: React.ElementType;
  hotkey?: string;
}

interface NavGroup {
  category: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    category: 'SURVEILLANCE',
    items: [
      { id: 'situation_room', label: 'Situation Room', icon: LayoutDashboard, hotkey: '1' },
      { id: 'live_monitoring', label: 'Live Monitoring', icon: Video, hotkey: '2' },
      { id: 'cameras', label: 'Camera Library', icon: Camera, hotkey: '3' },
      { id: 'events', label: 'Event Stream', icon: AlertTriangle, hotkey: '4' },
    ],
  },
  {
    category: 'FORENSICS',
    items: [
      { id: 'enhancement_lab', label: 'Enhancement Lab', icon: SlidersHorizontal, hotkey: 'E' },
      { id: 'investigation', label: 'Investigation', icon: Search, hotkey: 'I' },
      { id: 'analytics', label: 'Benchmarks', icon: BarChart3, hotkey: 'A' },
    ],
  },
  {
    category: 'PROVENANCE',
    items: [
      { id: 'evidence', label: 'Evidence Vault', icon: FileCheck2, hotkey: 'V' },
      { id: 'reports', label: 'Case Reports', icon: FileText, hotkey: 'R' },
    ],
  },
  {
    category: 'SYSTEM',
    items: [
      { id: 'system_status', label: 'System Engine', icon: Cpu, hotkey: 'S' },
      { id: 'security', label: 'Integrity Audit', icon: Shield },
      { id: 'settings', label: 'Parameters', icon: Sliders },
    ],
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  currentWorkspace,
  onSelectWorkspace,
}) => {
  const [collapsed, setCollapsed] = useState(false);
  const [hoveredTooltip, setHoveredTooltip] = useState<{
    label: string;
    hotkey?: string;
    top: number;
  } | null>(null);

  const handleMouseEnter = (
    e: React.MouseEvent<HTMLButtonElement>,
    label: string,
    hotkey?: string
  ) => {
    if (collapsed) {
      const rect = e.currentTarget.getBoundingClientRect();
      setHoveredTooltip({
        label,
        hotkey,
        top: rect.top + rect.height / 2,
      });
    }
  };

  const handleMouseLeave = () => {
    setHoveredTooltip(null);
  };

  return (
    <aside
      className={`border-r border-[#141a24] bg-[#07090e] flex flex-col justify-between select-none transition-all duration-150 z-20 relative shrink-0 ${
        collapsed ? 'w-11' : 'w-44'
      }`}
      aria-label="Workstation instruments"
    >
      {/* Navigation Groups */}
      <div className="flex-1 py-2 overflow-y-auto space-y-3">
        {NAV_GROUPS.map((group) => (
          <div key={group.category} className="px-1.5">
            {!collapsed && (
              <div className="px-2 py-0.5 text-[9px] font-mono text-[#475569] uppercase tracking-wider">
                {group.category}
              </div>
            )}
            <div className="space-y-0.5 mt-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = currentWorkspace === item.id;

                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      onSelectWorkspace(item.id);
                      setHoveredTooltip(null);
                    }}
                    onMouseEnter={(e) => handleMouseEnter(e, item.label, item.hotkey)}
                    onMouseLeave={handleMouseLeave}
                    aria-label={`${item.label} ${item.hotkey ? `[${item.hotkey}]` : ''}`}
                    className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors cursor-pointer text-left ${
                      isActive
                        ? 'bg-[#10141a] text-[#f59e0b] border-l-2 border-[#d97706]'
                        : 'text-[#8b9bb0] hover:bg-[#0b0e14] hover:text-[#e6edf3] border-l-2 border-transparent'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-[#f59e0b]' : 'text-[#58687d]'}`} />
                    {!collapsed && (
                      <div className="flex-1 flex items-center justify-between overflow-hidden">
                        <span className="truncate font-sans font-normal text-[12px]">{item.label}</span>
                        {item.hotkey && (
                          <span className="text-[9px] font-mono text-[#475569] bg-[#0b0e14] border border-[#161c26] px-1 rounded">
                            {item.hotkey}
                          </span>
                        )}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Collapse / Expand Toggle Rail */}
      <div className="p-1 border-t border-[#141a24] bg-[#07090e]">
        <button
          onClick={() => {
            setCollapsed(!collapsed);
            setHoveredTooltip(null);
          }}
          onMouseEnter={(e) =>
            handleMouseEnter(e, collapsed ? 'Expand Sidebar' : 'Collapse Sidebar')
          }
          onMouseLeave={handleMouseLeave}
          className="w-full flex items-center justify-center p-1.5 rounded hover:bg-[#0b0e14] text-[#475569] hover:text-[#cbd5e1] text-xs transition-colors cursor-pointer"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Floating Tooltip Portal for Collapsed Mode (Unclipped) */}
      {collapsed && hoveredTooltip && (
        <div
          className="fixed z-50 pointer-events-none flex items-center gap-2 bg-[#0b0e14] border border-[#1e2634] text-[#e6edf3] text-xs font-sans px-2 py-1 rounded shadow-2xl -translate-y-1/2 left-[48px] animate-in fade-in duration-75"
          style={{ top: hoveredTooltip.top }}
        >
          <span className="font-normal text-[11px] whitespace-nowrap">{hoveredTooltip.label}</span>
          {hoveredTooltip.hotkey && (
            <span className="text-[9px] font-mono text-[#f59e0b] bg-[#10141a] border border-[#f59e0b]/30 px-1 rounded">
              {hoveredTooltip.hotkey}
            </span>
          )}
        </div>
      )}
    </aside>
  );
};
