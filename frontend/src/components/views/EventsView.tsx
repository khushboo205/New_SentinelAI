import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { ForensicEvent, OperationalSeverity, SystemMode } from '../../types/forensic';
import {
  AlertTriangle,
  Clock,
  Crosshair,
  Search,
  Filter,
} from 'lucide-react';

interface EventsViewProps {
  systemMode: SystemMode;
  onNavigateWorkspace: (ws: any) => void;
  onSelectTrackForInvestigation: (trackId: number) => void;
}

export const EventsView: React.FC<EventsViewProps> = ({
  systemMode,
  onNavigateWorkspace,
  onSelectTrackForInvestigation,
}) => {
  const [events, setEvents] = useState<ForensicEvent[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<number>(1);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  useEffect(() => {
    api.getEvents(50).then((res) => {
      setEvents(res.events);
      if (res.events.length > 0) setSelectedEventId(res.events[0].id);
    });
  }, []);

  const filtered = events.filter((e) => {
    if (severityFilter === 'ALL') return true;
    return e.severity === severityFilter;
  });

  const activeEvent = events.find((e) => e.id === selectedEventId) || events[0];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#07090e] overflow-hidden select-none">
      {/* Events Toolbar */}
      <div className="h-10 border-b border-[#141a24] bg-[#0b0e14] px-3 flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-[#f59e0b]" />
          <span className="font-semibold text-[#e6edf3]">FORENSIC EVENT & INCIDENT STREAM</span>
          <span className="text-[#334155]">|</span>
          <span className="text-[10px] font-mono text-[#64748b]">
            {events.length} LOGGED OBSERVATIONS
          </span>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-1.5 text-[11px] font-mono">
          <span className="text-[#64748b]">SEVERITY:</span>
          {['ALL', 'CRITICAL', 'WARNING', 'WATCH'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`wb-btn py-0.5 px-2 text-[10px] ${
                severityFilter === sev ? 'wb-btn-primary' : 'wb-btn-ghost'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Dense Event Stream Table (Left) | Contextual Event Detail Inspector (Right) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Dense Event Table */}
        <div className="flex-1 border-r border-[#141a24] bg-[#07090e] flex flex-col overflow-hidden">
          <div className="h-7 px-3 bg-[#0b0e14] border-b border-[#141a24] grid grid-cols-12 items-center text-[9.5px] font-mono text-[#475569] uppercase tracking-wider">
            <span className="col-span-2">TIMESTAMP</span>
            <span className="col-span-2">SEVERITY</span>
            <span className="col-span-2">CAMERA</span>
            <span className="col-span-3">EVENT TYPE</span>
            <span className="col-span-3 text-right">TARGET / CONF</span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-[#141a24]/60">
            {filtered.map((evt) => {
              const isSelected = evt.id === selectedEventId;
              return (
                <div
                  key={evt.id}
                  onClick={() => setSelectedEventId(evt.id)}
                  className={`grid grid-cols-12 items-center px-3 py-2 text-xs font-mono cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-[#151a21] border-l-2 border-[#d97706]'
                      : 'hover:bg-[#0b0e14] border-l-2 border-transparent'
                  }`}
                >
                  <span className="col-span-2 text-[#8b9bb0] text-[11px]">{evt.timestamp}</span>

                  <span className="col-span-2">
                    <span
                      className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${
                        evt.severity === 'CRITICAL'
                          ? 'border border-[#7f1d1d] text-[#f87171] bg-[#7f1d1d]/20'
                          : evt.severity === 'WARNING'
                          ? 'border border-[#78350f] text-[#fbbf24] bg-[#78350f]/20'
                          : 'border border-[#1e2634] text-[#8b9bb0] bg-[#1e2634]/30'
                      }`}
                    >
                      {evt.severity}
                    </span>
                  </span>

                  <span className="col-span-2 text-[#cbd5e1] truncate">{evt.camera_id}</span>

                  <span className="col-span-3 text-[#e6edf3] font-sans font-medium text-[12px] truncate">
                    {evt.event_type.replace(/_/g, ' ')}
                  </span>

                  <span className="col-span-3 text-right text-[#8b9bb0] text-[11px]">
                    #{evt.target_id} ({((evt.confidence || 0.88) * 100).toFixed(0)}%)
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Contextual Event Detail Inspector (340px) */}
        <div className="w-84 p-3 flex flex-col justify-between overflow-y-auto bg-[#0b0e14] shrink-0 text-xs">
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-1.5 border-b border-[#141a24]">
              <span className="text-[10px] text-[#475569] font-mono uppercase tracking-wider">
                EVENT CONTEXT
              </span>
              <span className="font-mono text-xs text-[#f59e0b]">EVENT #{activeEvent?.id}</span>
            </div>

            {/* Event Metadata */}
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between py-0.5 border-b border-[#141a24]/60">
                <span className="text-[#64748b] font-sans">Timestamp</span>
                <span className="text-[#cbd5e1]">{activeEvent?.timestamp}</span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#141a24]/60">
                <span className="text-[#64748b] font-sans">Sensor Source</span>
                <span className="text-[#cbd5e1]">
                  {activeEvent?.camera_name || activeEvent?.camera_id}
                </span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#141a24]/60">
                <span className="text-[#64748b] font-sans">Classification</span>
                <span className="text-[#e6edf3] font-medium">
                  {activeEvent?.event_type.replace(/_/g, ' ')}
                </span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#141a24]/60">
                <span className="text-[#64748b] font-sans">Target Involved</span>
                <span className="text-[#f59e0b]">
                  TRACK #{activeEvent?.target_id} ({activeEvent?.target_type})
                </span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-[#64748b] font-sans">Confidence</span>
                <span className="text-[#34d399]">
                  {((activeEvent?.confidence || 0.912) * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Description & Rule Trigger */}
            <div className="p-2.5 rounded bg-[#07090e] border border-[#141a24] space-y-1.5">
              <span className="text-[9.5px] text-[#475569] font-mono uppercase block">
                OBSERVATION LOG
              </span>
              <p className="text-[#cbd5e1] leading-relaxed font-sans text-[11.5px]">
                {activeEvent?.description}
              </p>
              <div className="pt-1.5 border-t border-[#141a24] text-[10.5px] text-[#8b9bb0] font-mono">
                <span className="text-[#64748b]">RULE TRIGGERED:</span> {activeEvent?.rule_triggered}
              </div>
            </div>

            {/* Associated Sensor Frame Snapshot */}
            <div className="space-y-1">
              <span className="text-[9.5px] text-[#475569] font-mono uppercase block">
                ASSOCIATED SENSOR FRAME ({activeEvent?.camera_id})
              </span>
              <div className="relative aspect-video bg-black rounded border border-[#141a24] overflow-hidden">
                <img
                  src={api.getSampleImageUrl(
                    activeEvent?.camera_id === 'CAM_02' ? 'blur' : 'lowlight'
                  )}
                  alt="Event Snapshot"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>

          {/* Direct Escalation Action */}
          <div className="pt-2 border-t border-[#141a24]">
            <button
              onClick={() => {
                if (activeEvent?.target_id) {
                  onSelectTrackForInvestigation(activeEvent.target_id);
                }
                onNavigateWorkspace('investigation');
              }}
              className="wb-btn wb-btn-primary w-full justify-center py-2 text-xs"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Reconstruct Target #{activeEvent?.target_id} in Investigation [I]</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
